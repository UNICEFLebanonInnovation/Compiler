import datetime
import io
import zipfile
from types import SimpleNamespace
from xml.etree import ElementTree as ET

import pytest
from PIL import Image

from student_registration.backends.child_photo_export import (
    HEADERS, ChildPhotoExportMixin, build_photo_roster,
)


TODAY = datetime.date(2026, 10, 20)
NS = {'s': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}


def registration(programme='makani', birthday=(2018, 3, 4), photo=None, **values):
    child = SimpleNamespace(
        first_name='=Ali', father_name='Hassan', last_name='Rahman',
        mother_fullname='Fatima Rahman', gender='Male', sex='Male',
        birthday_year=str(birthday[0]), birthday_month=str(birthday[1]),
        birthday_day=str(birthday[2]), nationality='Syrian', disability='None',
        first_phone_number='00123456',
    )
    child.__dict__.update(values)
    location = SimpleNamespace(governorate='Akkar', caza='District', cadaster='Town')
    picture = SimpleNamespace(name='photo.jpg', open=lambda mode: io.BytesIO(photo)) if photo else None
    return SimpleNamespace(
        pk=1, child=child, student=child, profile_picture=picture, center=location,
        governorate='Akkar', district='District', cadaster='Town',
        disability='None', partner='Partner A', phone_number='00123456',
    )


def read_rows(content):
    with zipfile.ZipFile(io.BytesIO(content)) as archive:
        strings = ET.fromstring(archive.read('xl/sharedStrings.xml'))
        labels = [''.join(si.itertext()) for si in strings]
        sheet = ET.fromstring(archive.read('xl/worksheets/sheet1.xml'))
        rows = []
        for row in sheet.findall('s:sheetData/s:row', NS):
            cells = {}
            for cell in row:
                assert cell.find('s:f', NS) is None
                value = cell.find('s:v', NS)
                cells[''.join(c for c in cell.attrib['r'] if c.isalpha())] = (
                    labels[int(value.text)] if value is not None else '')
            rows.append(cells)
        return rows, archive.namelist(), archive.read('xl/drawings/drawing1.xml') if 'xl/drawings/drawing1.xml' in archive.namelist() else b''


@pytest.mark.parametrize('programme', ['makani', 'dirasa'])
def test_headers_fields_and_embedded_photograph(programme):
    image = io.BytesIO()
    Image.new('RGB', (30, 50), 'red').save(image, format='JPEG')
    rows, files, drawing = read_rows(build_photo_roster(
        [registration(programme, photo=image.getvalue())], programme, TODAY))
    assert list(rows[0].values()) == list(HEADERS)
    assert rows[1]['B'] == '=Ali Hassan Rahman'
    assert rows[1]['C'] == '2018-03-04'
    assert rows[1]['R'] == '00123456'
    assert rows[1]['M'] == 'Akkar'
    assert rows[1]['N'] == 'District'
    assert rows[1]['O'] == 'Town'
    assert rows[1]['P'] == 'None'
    assert rows[1]['Q'] == 'Partner A'
    assert rows[1]['U'] == '1'
    assert any(name.startswith('xl/media/') for name in files)
    root = ET.fromstring(drawing)
    ns = {'x': 'http://schemas.openxmlformats.org/drawingml/2006/spreadsheetDrawing'}
    assert root.find('.//x:from/x:col', ns).text == '0'
    assert root.find('.//x:from/x:row', ns).text == '1'


@pytest.mark.parametrize('programme', ['makani', 'dirasa'])
def test_age_boundaries_and_invalid_birthdays(programme):
    birthdays = [(2019, 10, 20), (2019, 10, 21), (2015, 10, 21),
                 (2015, 10, 20), (2018, 2, 30), (0, 0, 0)]
    rows, _, _ = read_rows(build_photo_roster(
        [registration(programme, day) for day in birthdays], programme, TODAY))
    assert [row['C'] for row in rows[1:]] == ['2019-10-20', '2015-10-21']
    assert rows[1]['A'] == 'No photograph uploaded'


def test_unreadable_photo_keeps_child_and_empty_export_has_headers():
    rows, files, _ = read_rows(build_photo_roster(
        [registration(photo=b'broken image')], 'makani', TODAY))
    assert rows[1]['A'] == 'Photograph unavailable'
    assert not any(name.startswith('xl/media/') for name in files)
    rows, _, _ = read_rows(build_photo_roster([], 'makani', TODAY))
    assert len(rows) == 1
    assert list(rows[0].values()) == list(HEADERS)


def test_both_language_columns_use_programme_language_when_available():
    record = registration('dirasa')
    record.language = 'english_arabic'
    record.get_language_display = lambda: 'English/Arabic'
    rows, _, _ = read_rows(build_photo_roster([record], 'dirasa', TODAY))
    assert rows[1]['S'] == rows[1]['T'] == 'English/Arabic'
    rows, _, _ = read_rows(build_photo_roster([registration()], 'makani', TODAY))
    assert rows[1]['S'] == rows[1]['T'] == ''


@pytest.mark.parametrize('programme', ['makani', 'dirasa'])
def test_all_ages_includes_outside_age_band_and_incomplete_birthdays(programme):
    birthdays = [(2022, 1, 1), (2010, 1, 1), (2018, 3, 4), (0, 0, 0)]
    rows, _, _ = read_rows(build_photo_roster(
        [registration(programme, birthday) for birthday in birthdays],
        programme, TODAY, all_ages=True))
    assert len(rows) == 5
    assert list(rows[0].values()) == list(HEADERS)
    assert [row['C'] for row in rows[1:]] == ['2022-01-01', '2010-01-01', '2018-03-04', '']


def test_unavailable_photos_do_not_emit_per_photo_logs(caplog):
    unreadable = registration(photo=b'broken image')
    unreachable = registration(photo=b'unused')

    def fail_open(mode):
        raise OSError('Storage unavailable')

    unreachable.profile_picture.open = fail_open
    rows, _, _ = read_rows(build_photo_roster([unreadable, unreachable], 'makani', TODAY))
    assert [row['A'] for row in rows[1:]] == ['Photograph unavailable'] * 2
    assert not caplog.records


@pytest.mark.parametrize('programme', ['makani', 'dirasa'])
def test_unavailable_report_keeps_format_and_filenames_without_available_photos(programme):
    image = io.BytesIO()
    Image.new('RGB', (30, 50), 'red').save(image, format='JPEG')
    unreadable = registration(programme, photo=b'broken image')
    unreadable.pk = 38585
    unreadable.profile_picture.name = 'uploads/profile_pictures/=photo.jpg'
    unreachable = registration(programme, photo=b'unused')
    unreachable.pk = 38586
    unreachable.profile_picture.name = 'uploads/profile_pictures/missing.jpg'

    def fail_open(mode):
        raise OSError('Storage unavailable')

    unreachable.profile_picture.open = fail_open
    rows, files, _ = read_rows(build_photo_roster([
        registration(programme, photo=image.getvalue()), unreadable, unreachable,
        registration(programme), registration(programme, birthday=(2010, 1, 1)),
    ], programme, TODAY, unavailable_only=True))
    assert list(rows[0].values()) == list(HEADERS)
    assert [row['A'] for row in rows[1:]] == [
        '=photo.jpg', 'missing.jpg', 'No photograph uploaded']
    assert all(row['B'] == '=Ali Hassan Rahman' for row in rows[1:])
    assert [row['U'] for row in rows[1:]] == ['38585', '38586', '1']
    assert not any(name.startswith('xl/media/') for name in files)


def test_export_uses_full_filtered_queryset_and_rejects_invalid_filters(monkeypatch):
    monkeypatch.setattr('student_registration.backends.child_photo_export.timezone.now',
                        lambda: datetime.datetime(2026, 10, 20, 12))
    class Rows:
        def iterator(self, chunk_size):
            return iter([registration() for _ in range(30)])

    view = ChildPhotoExportMixin()
    view.programme = 'makani'
    view.object_list = Rows()
    view.filterset = SimpleNamespace(is_bound=True, is_valid=lambda: True)
    response = view.render_to_response({})
    rows, _, _ = read_rows(response.content)
    assert len(rows) == 31
    assert response['Cache-Control'] == 'private, no-store'
    assert 'makani-children-7-10.xlsx' in response['Content-Disposition']
    view.filterset.is_valid = lambda: False
    assert view.render_to_response({}).status_code == 400


@pytest.mark.django_db
@pytest.mark.parametrize('programme', ['makani', 'dirasa'])
@pytest.mark.parametrize('unavailable_only', [False, True])
@pytest.mark.parametrize('all_ages', [False, True])
def test_endpoint_respects_partner_scope_filters_and_login(programme, unavailable_only, all_ages, rf, django_user_model, monkeypatch):
    from django.contrib.auth.models import AnonymousUser, Group
    from student_registration.schools.models import PartnerOrganization, CLMRound
    from student_registration.mscc.models import Registration, Round
    from student_registration.child.models import Child
    from student_registration.students.models import Student
    from student_registration.clm.models import Bridging
    from student_registration.mscc.views import ChildPhotoExportView
    from student_registration.clm.bridging_views import BridgingChildPhotoExportView

    monkeypatch.setattr('student_registration.backends.child_photo_export.timezone.now',
                        lambda: datetime.datetime(2026, 10, 20, 12))
    partner = PartnerOrganization.objects.create(name='Partner A')
    other = PartnerOrganization.objects.create(name='Partner B')
    user = django_user_model.objects.create_user(username='roster-user', partner=partner)
    roles = ['MSCC', 'MSCC_PARTNER'] if programme == 'makani' else ['CLM_Bridging']
    user.groups.add(*(Group.objects.get_or_create(name=name)[0] for name in roles))
    if programme == 'makani':
        cycle = Round.objects.create(name='Current', current_year=True)
        model, person_model, relation, view = Registration, Child, 'child', ChildPhotoExportView
        query = {'child__first_name': 'Visible', 'page': '999'}
    else:
        cycle = CLMRound.objects.create(name='Current', current_year=True)
        model, person_model, relation, view = Bridging, Student, 'student', BridgingChildPhotoExportView
        query = {'student__first_name': 'Visible', 'page': '999'}
    for assigned_partner, name in [(partner, 'Visible'), (partner, 'Filtered'), (other, 'Visible outsider')]:
        person = person_model.objects.create(
            first_name=name, father_name='Father', last_name='Family',
            mother_fullname='Mother', birthday_year='2018', birthday_month='3', birthday_day='4')
        model.objects.create(**{relation: person}, partner=assigned_partner, round=cycle)
    request = rf.get('/photo-export/', query)
    if all_ages and not unavailable_only:
        from urllib.parse import urlencode
        request = rf.post('/photo-export/?' + urlencode(query))
    request.user = user
    response = view.as_view(unavailable_only=unavailable_only, all_ages=all_ages)(request)
    if all_ages and not unavailable_only:
        from student_registration.backends.models import ExportHistory
        from student_registration.backends.photo_batches import JOB_KIND, BATCH_KIND
        assert response.status_code == 302
        job = ExportHistory.objects.get(created_by=user, fields__kind=JOB_KIND)
        assert job.fields['total'] == 1
        batch = ExportHistory.objects.get(fields__kind=BATCH_KIND, fields__job_id=job.pk)
        expected = model.objects.get(**{relation + '__first_name': 'Visible'})
        assert batch.fields['ids'] == [expected.pk]
        request = rf.get('/photo-export/')
        request.user = AnonymousUser()
        assert view.as_view(all_ages=True)(request).status_code == 302
        return
    assert response.status_code == 200
    rows, _, _ = read_rows(response.content)
    assert [row['B'] for row in rows[1:]] == ['Visible Father Family']
    report = 'unavailable-photos' if unavailable_only else 'children'
    age_range = 'all-ages' if all_ages else '7-10'
    assert '{}-{}-{}.xlsx'.format(programme, report, age_range) in response['Content-Disposition']
    request.user = AnonymousUser()
    assert view.as_view(unavailable_only=unavailable_only, all_ages=all_ages)(request).status_code == 302
