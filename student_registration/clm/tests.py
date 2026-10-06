"""Tests for the Dirasa (Bridging) child profile ID card."""

import re

import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.files.uploadedfile import SimpleUploadedFile
from django.http import HttpResponse

from student_registration.backends.models import ExportHistory
from student_registration.clm import bridging_views, tasks
from student_registration.clm.bridging_views import bridging_profile_id_card
from student_registration.clm.profile_id import build_profile_ids_pdf, shape_text
from student_registration.schools.models import School
from student_registration.clm.models import Bridging, Disability
from student_registration.locations.models import Location, LocationType
from student_registration.schools.models import CLMRound, PartnerOrganization
from student_registration.students.models import Nationality, Student

pytestmark = pytest.mark.django_db

# Smallest valid 1x1 GIF, enough for ImageField validation.
GIF = (b'GIF89a\x01\x00\x01\x00\x80\x00\x00\x00\x00\x00\xff\xff\xff!\xf9\x04\x01\x00\x00\x00\x00,'
       b'\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;')


@pytest.fixture
def registration():
    governorate = LocationType.objects.create(name='Governorate')
    baalbek = Location.objects.create(name='بعلبك الهرمل', name_en='Baalbek-Hermel', p_code='LB2', type=governorate)
    student = Student.objects.create(
        first_name='ريهام', father_name='علي', last_name='الشمق',
        birthday_day='5', birthday_month='5', birthday_year='2014',
        place_of_birth='Hazmieh',
        nationality=Nationality.objects.create(name='سوري', name_en='Syrian'),
    )
    return Bridging.objects.create(
        student=student,
        round=CLMRound.objects.create(name='2026-2027', current_year=True, current_round_bridging=True),
        partner=PartnerOrganization.objects.create(name='SAVE', is_dirasa=True),
        governorate=baalbek,
        disability=Disability.objects.create(name='لا', name_en='No'),
    )


@pytest.fixture
def bridging_client(client):
    user = get_user_model().objects.create_user(username='dirasa', password='x-pass-123456')
    user.groups.add(Group.objects.get_or_create(name='CLM_Bridging')[0])
    client.force_login(user)
    return client


def test_card_data_matches_registration(registration):
    card = bridging_profile_id_card(registration)
    assert card == {
        'round': '2026-2027',
        'id': registration.id,
        'ngo': 'SAVE',
        'full_name': 'ريهام علي الشمق',
        'birthday': '5/5/14',
        'place_of_birth': 'Hazmieh',
        'nationality': 'Syrian',
        'governorate': 'Baalbek-Hermel',
        'physical_difficulties': 'No',
        'has_picture': False,
    }


def test_card_data_tolerates_missing_details():
    student = Student.objects.create(first_name='Only', birthday_day='0', birthday_month='0', birthday_year='0')
    bridging = Bridging.objects.create(student=student)
    card = bridging_profile_id_card(bridging)
    assert card['full_name'] == 'Only'
    assert card['birthday'] == ''
    assert card['nationality'] == ''
    assert card['governorate'] == ''
    assert card['ngo'] == ''
    assert card['round'] == ''
    assert card['physical_difficulties'] == 'No'
    assert bridging_profile_id_card(Bridging.objects.create())['full_name'] == ''


def test_profile_id_page_renders_card(bridging_client, registration):
    response = bridging_client.get('/clm/bridging-profile-id/{}/'.format(registration.id))
    assert response.status_code == 200
    html = response.content.decode('utf-8')
    for text in ('2026-2027', 'ID: {}'.format(registration.id), 'NGO: SAVE', 'ريهام علي الشمق',
                 'Date of Birth: 5/5/14', 'Place of Birth: Hazmieh', 'Nationality: Syrian',
                 'Governorate: Baalbek-Hermel', 'Physical difficulties: No',
                 'الامتحان الاستثنائي لطلاب التعليم الغير نظامي'):
        assert text in html
    assert '/clm/bridging-profile-picture/{}/image/'.format(registration.id) not in html


def test_profile_id_page_shows_uploaded_picture(bridging_client, registration, settings, tmp_path):
    settings.MEDIA_ROOT = str(tmp_path)
    settings.DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'
    settings.STORAGES = {
        'default': {'BACKEND': 'django.core.files.storage.FileSystemStorage'},
        'staticfiles': {'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage'},
    }
    registration.profile_picture.save('child.gif', SimpleUploadedFile('child.gif', GIF, content_type='image/gif'))

    response = bridging_client.get('/clm/bridging-profile-id/{}/'.format(registration.id))
    assert response.status_code == 200
    assert '/clm/bridging-profile-picture/{}/image/'.format(registration.id) in response.content.decode('utf-8')


def test_profile_picture_page_links_to_profile_id(bridging_client, registration):
    response = bridging_client.get('/clm/bridging-profile-picture/{}/'.format(registration.id))
    assert response.status_code == 200
    assert '/clm/bridging-profile-id/{}/'.format(registration.id) in response.content.decode('utf-8')


def test_profile_id_requires_login(client, registration):
    response = client.get('/clm/bridging-profile-id/{}/'.format(registration.id))
    assert response.status_code == 302
    assert response['Location'] == '/?next=/clm/bridging-profile-id/{}/'.format(registration.id)


@pytest.fixture
def classmates(registration):
    """A second child of the same partner and one child of another partner."""
    school = School.objects.create(number='2001', name='School B', governorate=registration.governorate)
    registration.partner.schools.add(school)
    second = Bridging.objects.create(
        student=Student.objects.create(first_name='أحمد', father_name='خالد', last_name='حسن',
                                       birthday_day='1', birthday_month='2', birthday_year='2013',
                                       nationality=registration.student.nationality),
        round=registration.round, partner=registration.partner, school=school,
        governorate=registration.governorate,
    )
    other = Bridging.objects.create(
        student=Student.objects.create(first_name='Other', father_name='Partner', last_name='Child'),
        round=registration.round, partner=PartnerOrganization.objects.create(name='OTHER', is_dirasa=True),
        governorate=registration.governorate,
    )
    return {'second': second, 'other': other, 'school': school}


@pytest.fixture
def partner_client(client, registration):
    user = get_user_model().objects.create_user(username='save', password='x-pass-123456',
                                                partner=registration.partner)
    user.groups.add(Group.objects.get_or_create(name='CLM_Bridging')[0])
    client.force_login(user)
    return client


def _page_count(pdf_bytes):
    assert pdf_bytes.startswith(b'%PDF')
    return len(re.findall(rb'/Type\s*/Page\b(?!s)', pdf_bytes))


@pytest.fixture
def local_media(settings, tmp_path):
    settings.MEDIA_ROOT = str(tmp_path)
    settings.STORAGES = {
        'default': {'BACKEND': 'django.core.files.storage.FileSystemStorage'},
        'staticfiles': {'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage'},
    }


class FakeExportStorage(object):
    saved = {}

    def save(self, name, content):
        FakeExportStorage.saved[name] = content.read()
        return name


@pytest.fixture
def fake_storage(monkeypatch):
    FakeExportStorage.saved = {}
    monkeypatch.setattr(tasks, 'ExportStorage', FakeExportStorage)
    return FakeExportStorage


@pytest.fixture
def pushes(monkeypatch):
    sent = []
    monkeypatch.setattr(tasks, 'send_push_to_web', lambda user, title, body, data=None: sent.append(
        {'user': user, 'title': title, 'body': body, 'data': data}) or True)
    return sent


def test_shape_text_keeps_latin_and_reorders_arabic():
    assert shape_text('Nationality: Syrian') == 'Nationality: Syrian'
    shaped = shape_text('الاسم الثلاثي: ريهام')
    assert shaped != 'الاسم الثلاثي: ريهام'
    assert len(shaped) > 0


def test_pdf_has_one_page_per_child(registration, classmates, local_media):
    registration.profile_picture.save('child.gif', SimpleUploadedFile('child.gif', GIF, content_type='image/gif'))
    pdf_bytes = build_profile_ids_pdf(tasks.profile_ids_registrations([registration.id, classmates['second'].id]))
    assert _page_count(pdf_bytes) == 2
    assert _page_count(build_profile_ids_pdf([])) == 1


def test_generate_profile_ids_stores_pdf_and_notifies(registration, classmates, fake_storage, pushes):
    owner = get_user_model().objects.create_user(username='owner')
    export = ExportHistory.objects.create(export_type=tasks.PROFILE_IDS_EXPORT_TYPE, created_by=owner)
    file_url = tasks._generate_bridging_profile_ids(export.id, [registration.id, classmates['second'].id])

    export.refresh_from_db()
    assert export.status == 'done'
    assert export.file_url == file_url
    assert re.match(r'^/clm/bridging-profile-ids/download/bridging_profile_ids_[0-9a-f-]+[.]pdf/$', file_url)
    file_name = file_url.split('/')[-2]
    assert _page_count(fake_storage.saved[file_name]) == 2
    assert pushes == [{
        'user': export.created_by,
        'title': 'Dirasa profile IDs ready',
        'body': 'The PDF with 2 profile ID card(s) is ready to download.',
        'data': {'type': 'bridging_profile_ids_ready', 'url': file_url, 'export_id': export.id},
    }]


def test_generate_profile_ids_failure_marks_export_failed(registration, fake_storage, pushes, monkeypatch):
    def boom(registrations):
        raise RuntimeError('font missing')
    monkeypatch.setattr(tasks, 'build_profile_ids_pdf', boom)
    user = get_user_model().objects.create_user(username='owner2')
    export = ExportHistory.objects.create(export_type=tasks.PROFILE_IDS_EXPORT_TYPE, created_by=user)

    assert tasks._generate_bridging_profile_ids(export.id, [registration.id]) is None
    export.refresh_from_db()
    assert export.status == 'failed'
    assert export.file_url is None
    assert pushes[0]['title'] == 'Dirasa profile IDs failed'
    assert pushes[0]['data'] == {'type': 'bridging_profile_ids_failed', 'reason': 'font missing',
                                 'export_id': export.id}
    assert tasks._generate_bridging_profile_ids(999999, [registration.id]) is None


@pytest.fixture
def queued(monkeypatch):
    calls = []
    monkeypatch.setattr(bridging_views, 'queue_bridging_profile_ids',
                        lambda export_id, ids: calls.append((export_id, list(ids))))
    return calls


def test_bulk_profile_ids_queues_visible_children(partner_client, registration, classmates, queued):
    response = partner_client.post('/clm/bridging-profile-ids/')
    assert response.status_code == 200
    export = ExportHistory.objects.get()
    assert response.json() == {'status': 'started', 'export_id': export.id, 'count': 2}
    assert export.export_type == 'Bridging Profile IDs'
    assert export.status == 'pending'
    assert export.file_format == 'pdf'
    assert export.created_by.username == 'save'
    assert export.partner_name == 'SAVE'
    assert export.fields == {'count': 2, 'filters': {}}
    assert len(queued) == 1
    assert queued[0][0] == export.id
    assert sorted(queued[0][1]) == sorted([registration.id, classmates['second'].id])


def test_bulk_profile_ids_follow_list_filters(partner_client, registration, classmates, queued):
    response = partner_client.post('/clm/bridging-profile-ids/?school={}'.format(classmates['school'].id))
    assert response.json()['count'] == 1
    assert queued[-1][1] == [classmates['second'].id]

    response = partner_client.post('/clm/bridging-profile-ids/?ids={},999999'.format(registration.id))
    assert response.json()['count'] == 1
    assert queued[-1][1] == [registration.id]


def test_bulk_profile_ids_all_group_sees_every_partner(bridging_client, registration, classmates, queued):
    user = get_user_model().objects.get(username='dirasa')
    user.groups.add(Group.objects.get_or_create(name='CLM_BRIDGING_ALL')[0])
    assert bridging_client.post('/clm/bridging-profile-ids/').json()['count'] == 3


def test_bulk_profile_ids_empty_list_and_methods(partner_client, registration, queued):
    response = partner_client.post('/clm/bridging-profile-ids/?student__first_name=nobody')
    assert response.status_code == 400
    assert 'nothing to generate' in response.json()['error']
    assert partner_client.get('/clm/bridging-profile-ids/').status_code == 405
    assert queued == []
    assert not ExportHistory.objects.exists()


def test_bulk_profile_ids_requires_login(client):
    response = client.post('/clm/bridging-profile-ids/')
    assert response.status_code == 302
    assert response['Location'] == '/?next=/clm/bridging-profile-ids/'


def test_profile_ids_download(bridging_client, monkeypatch):
    calls = []
    monkeypatch.setattr(bridging_views, 'download_file',
                        lambda name, returned, content_type=None: calls.append((name, returned, content_type))
                        or HttpResponse(b'%PDF', content_type=content_type))
    name = 'bridging_profile_ids_0f1e2d3c-4b5a-6978-8a9b-0c1d2e3f4a5b.pdf'
    response = bridging_client.get('/clm/bridging-profile-ids/download/{}/'.format(name))
    assert response.status_code == 200
    assert calls == [(name, 'bridging_profile_ids.pdf', 'application/pdf')]
    assert bridging_client.get('/clm/bridging-profile-ids/download/..%2Fsecret.pdf/').status_code == 400
    assert bridging_client.get('/clm/bridging-profile-ids/download/export.csv/').status_code == 400


def test_list_page_links_to_bulk_profile_ids(partner_client, registration):
    response = partner_client.get('/clm/bridging-list/')
    assert response.status_code == 200
    html = response.content.decode('utf-8')
    assert 'data-url="/clm/bridging-profile-ids/"' in html
    assert 'Generate Profile IDs (PDF)' in html
    assert 'function generateProfileIds' in html
