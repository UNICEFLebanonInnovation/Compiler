"""Tests for the Dirasa (Bridging) child profile ID card."""

from io import BytesIO

import pytest
from PIL import Image
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.files.uploadedfile import SimpleUploadedFile
from django.template.loader import render_to_string

from student_registration.clm.bridging_views import bridging_profile_id_card
from student_registration.clm.bridging_forms import BridgingProfilePictureForm
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


def _bulk_html(response):
    assert response.status_code == 200
    assert response['Content-Type'] == 'application/pdf'
    assert response.content.startswith(b'%PDF-')
    return render_to_string('clm/bridging_profile_id_bulk.html', {
        'cards': response.context['cards'], 'pdf': True,
    })


def _sheets(html):
    return html.count('class="sheet"')


def test_bulk_profile_ids_one_page_per_visible_child(partner_client, registration, classmates):
    response = partner_client.get('/clm/bridging-profile-ids/?round={}'.format(registration.round_id))
    assert response.status_code == 200
    html = _bulk_html(response)
    assert _sheets(html) == 2
    assert 'data-registration-id="{}"'.format(registration.id) in html
    assert 'data-registration-id="{}"'.format(classmates['second'].id) in html
    assert 'data-registration-id="{}"'.format(classmates['other'].id) not in html
    assert 'ريهام علي الشمق' in html and 'أحمد خالد حسن' in html


def test_bulk_profile_ids_follow_list_filters(partner_client, registration, classmates):
    response = partner_client.get('/clm/bridging-profile-ids/?round={}&school={}'.format(registration.round_id, classmates['school'].id))
    html = _bulk_html(response)
    assert _sheets(html) == 1
    assert 'data-registration-id="{}"'.format(classmates['second'].id) in html

    response = partner_client.get('/clm/bridging-profile-ids/?round={}&ids={},999999'.format(registration.round_id, registration.id))
    html = _bulk_html(response)
    assert _sheets(html) == 1
    assert 'data-registration-id="{}"'.format(registration.id) in html


def test_bulk_profile_ids_all_group_sees_every_partner(bridging_client, registration, classmates):
    user = get_user_model().objects.get(username='dirasa')
    user.groups.add(Group.objects.get_or_create(name='CLM_BRIDGING_ALL')[0])
    response = bridging_client.get('/clm/bridging-profile-ids/?round={}'.format(registration.round_id))
    assert _sheets(_bulk_html(response)) == 3


def test_bulk_profile_ids_empty_list(partner_client, registration):
    response = partner_client.get('/clm/bridging-profile-ids/?round={}&student__first_name=nobody'.format(registration.round_id))
    assert response.status_code == 200
    html = _bulk_html(response)
    assert _sheets(html) == 0
    assert 'nothing to generate' in html


def test_bulk_profile_ids_requires_login(client):
    response = client.get('/clm/bridging-profile-ids/')
    assert response.status_code == 302
    assert response['Location'] == '/?next=/clm/bridging-profile-ids/'


def test_list_page_hides_bulk_profile_ids_from_non_superuser(partner_client, registration):
    response = partner_client.get('/clm/bridging-list/?school={}'.format(registration.school_id or ''))
    assert response.status_code == 200
    html = response.content.decode('utf-8')
    assert '/clm/bridging-profile-ids/' not in html
    assert 'Generate Profile IDs (PDF)' not in html


def test_list_page_links_to_bulk_profile_ids_for_superuser(partner_client, registration):
    user = get_user_model().objects.get(username='save')
    user.is_superuser = True
    user.save()
    response = partner_client.get('/clm/bridging-list/?school=')
    assert response.status_code == 200
    html = response.content.decode('utf-8')
    assert '/clm/bridging-profile-ids/?school=' in html
    assert 'Generate Profile IDs (PDF)' in html


def _profile_picture_upload(name, image_format):
    content = BytesIO()
    Image.new('RGB', (1, 1)).save(content, format=image_format)
    return SimpleUploadedFile(name, content.getvalue())


@pytest.mark.parametrize('name,image_format', [
    ('child.png', 'PNG'),
    ('child.jpg', 'JPEG'),
    ('child.jpeg', 'JPEG'),
    ('child.PNG', 'PNG'),
    ('child.JPG', 'JPEG'),
    ('child.JPEG', 'JPEG'),
])
def test_profile_picture_accepts_png_and_jpeg(name, image_format):
    form = BridgingProfilePictureForm(
        data={}, files={'profile_picture': _profile_picture_upload(name, image_format)},
    )
    assert form.is_valid(), form.errors


@pytest.mark.parametrize('name,image_format', [
    ('child.gif', 'GIF'),
    ('child.bmp', 'BMP'),
    ('child.jpg', 'GIF'),
    ('child.png', 'BMP'),
    ('child.gif', 'PNG'),
    ('child', 'PNG'),
])
def test_profile_picture_rejects_other_extensions_and_image_formats(name, image_format):
    form = BridgingProfilePictureForm(
        data={}, files={'profile_picture': _profile_picture_upload(name, image_format)},
    )
    assert not form.is_valid()
    assert 'profile_picture' in form.errors


def test_profile_picture_rejects_non_image_content():
    form = BridgingProfilePictureForm(
        data={}, files={'profile_picture': SimpleUploadedFile('child.jpg', b'not an image')},
    )
    assert not form.is_valid()
    assert 'profile_picture' in form.errors


def test_profile_picture_can_keep_or_clear_existing_picture():
    instance = Bridging(profile_picture='existing/child.gif')
    keep = BridgingProfilePictureForm(data={}, files={}, instance=instance)
    assert keep.is_valid(), keep.errors
    assert keep.cleaned_data['profile_picture'].name == 'existing/child.gif'

    clear = BridgingProfilePictureForm(
        data={'profile_picture-clear': 'on'}, files={}, instance=instance,
    )
    assert clear.is_valid(), clear.errors
    assert clear.cleaned_data['profile_picture'] is False


def test_profile_picture_file_picker_limits_formats():
    field = BridgingProfilePictureForm().fields['profile_picture']
    assert field.widget.attrs['accept'] == '.png,.jpg,.jpeg,image/png,image/jpeg'


def test_bulk_profile_ids_selected_round_includes_previous_year(partner_client, registration):
    registration.round.current_year = False
    registration.round.save()
    other_round = CLMRound.objects.create(name='Another round', current_year=True)
    other = Bridging.objects.create(
        student=Student.objects.create(first_name='Wrong round'),
        round=other_round, partner=registration.partner,
    )
    response = partner_client.get('/clm/bridging-profile-ids/?round={}'.format(registration.round_id))
    html = _bulk_html(response)
    assert _sheets(html) == 1
    assert 'data-registration-id="{}"'.format(registration.id) in html
    assert 'data-registration-id="{}"'.format(other.id) not in html
    assert response['Content-Disposition'] == (
        'attachment; filename="bridging-profile-ids-round-{}.pdf"'.format(registration.round_id)
    )


@pytest.mark.parametrize('query', ['', '?round=invalid'])
def test_bulk_profile_ids_require_valid_round(partner_client, registration, query):
    response = partner_client.get('/clm/bridging-profile-ids/' + query)
    assert response.status_code == 400


def test_bulk_profile_ids_unknown_round_has_no_cards(partner_client, registration):
    response = partner_client.get('/clm/bridging-profile-ids/?round=999999')
    assert _sheets(_bulk_html(response)) == 0


def test_bulk_profile_ids_pdf_embeds_picture(partner_client, registration, settings, tmp_path):
    settings.STORAGES = {
        'default': {'BACKEND': 'django.core.files.storage.FileSystemStorage',
                    'OPTIONS': {'location': str(tmp_path)}},
        'staticfiles': {'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage'},
    }
    registration.profile_picture.save(
        'child.png', _profile_picture_upload('child.png', 'PNG'))
    response = partner_client.get('/clm/bridging-profile-ids/?round={}'.format(registration.round_id))
    html = _bulk_html(response)
    assert 'src="data:image/png;base64,' in html
    assert '/image/' not in html
