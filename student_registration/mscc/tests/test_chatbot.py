import os
import pathlib
import sys
from datetime import date
from types import SimpleNamespace
from unittest.mock import patch

import django
import pytest
from django.test import Client
from django.urls import reverse
from rest_framework.test import APIRequestFactory

PROJECT_ROOT = pathlib.Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

os.environ.setdefault('DATABASE_URL', 'sqlite:///test.sqlite3')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.test')
django.setup()

from django.contrib.auth import get_user_model  # noqa: E402

from student_registration.child.models import Child  # noqa: E402
from student_registration.locations.models import Center, Location, LocationType  # noqa: E402
from student_registration.mscc.chatbot.repository import BMAInsightsRepository  # noqa: E402
from student_registration.mscc.chatbot.services import BMAChatService  # noqa: E402
from student_registration.mscc.chatbot.views import BMAChatViewSet  # noqa: E402
from student_registration.mscc.models import Registration, Round  # noqa: E402
from student_registration.schools.models import PartnerOrganization, School  # noqa: E402
from student_registration.students.models import Nationality  # noqa: E402


@pytest.fixture()
def user(db):
    user_model = get_user_model()
    return user_model.objects.create_user(username='analyst', password='pwd12345')


def _build_locations():
    gov_type = LocationType.objects.create(name='Governorate')
    district_type = LocationType.objects.create(name='District')
    cadaster_type = LocationType.objects.create(name='Cadaster')
    school_loc_type = LocationType.objects.create(name='School Location')

    governorate = Location.objects.create(name='Bekaa', type=gov_type)
    district = Location.objects.create(name='West Bekaa', type=district_type, parent=governorate)
    cadaster = Location.objects.create(name='Kamed', type=cadaster_type, parent=district)
    school_location = Location.objects.create(name='School Area', type=school_loc_type)
    return governorate, district, cadaster, school_location


@pytest.mark.django_db
def test_snapshot_contains_expected_counts(user):
    partner = PartnerOrganization.objects.create(name='Partner A')
    user.partner = partner
    user.save(update_fields=['partner'])

    governorate, district, cadaster, school_location = _build_locations()

    center = Center.objects.create(
        name='Center 1',
        partner=partner,
        governorate=governorate,
        caza=district,
        cadaster=cadaster,
    )

    nationality = Nationality.objects.create(name='Lebanese', name_en='Lebanese')
    child = Child.objects.create(
        first_name='Ali',
        last_name='Hassan',
        gender='Male',
        nationality=nationality,
    )
    round_obj = Round.objects.create(name='Round 2024', year=2024)

    registration = Registration.objects.create(
        center=center,
        child=child,
        partner=partner,
        round=round_obj,
        type='Core-Package',
        registration_date=date(2024, 5, 1),
        owner=user,
    )

    school = School.objects.create(
        number='12345',
        name='BMA School',
        location=school_location,
        governorate=governorate,
        district=district,
        cadaster=cadaster,
        is_bma=True,
    )
    school.partner_schools.add(partner)

    snapshot = BMAInsightsRepository(user).build_snapshot()

    assert snapshot['registrations']['total'] == 1
    assert snapshot['registrations']['by_round'][0]['round'] == 'Round 2024'
    assert snapshot['registrations']['by_gender'][0]['gender'] == 'Male'
    assert snapshot['registrations']['by_partner'][0]['partner'] == 'Partner A'
    assert snapshot['registrations']['monthly_trend'][0]['registrations'] == 1
    assert snapshot['schools']['total'] == 1
    assert snapshot['centers']['total'] == 1


class _FakeChatCompletion:
    def __init__(self):
        self.last_kwargs = None

    def create(self, **kwargs):
        self.last_kwargs = kwargs
        message = SimpleNamespace(content='We currently have 1 registration.')
        usage = SimpleNamespace(prompt_tokens=120, completion_tokens=30, total_tokens=150)
        choice = SimpleNamespace(message=message)
        return SimpleNamespace(choices=[choice], usage=usage)


class _FakeClient:
    def __init__(self):
        self.chat = SimpleNamespace(completions=_FakeChatCompletion())


class _FakeRateLimitError(Exception):
    status_code = 429
    code = "rate_limit_exceeded"

    def __init__(self, message="Request rate limited"):
        super().__init__(message)


@pytest.mark.django_db
def test_chat_service_uses_snapshot_and_returns_answer(user):
    partner = PartnerOrganization.objects.create(name='Partner A')
    governorate, district, cadaster, school_location = _build_locations()
    center = Center.objects.create(name='Center 1', partner=partner, governorate=governorate)
    nationality = Nationality.objects.create(name='Lebanese', name_en='Lebanese')
    child = Child.objects.create(first_name='Sara', last_name='Hassan', gender='Female', nationality=nationality)
    round_obj = Round.objects.create(name='Round 2024', year=2024)
    Registration.objects.create(center=center, child=child, partner=partner, round=round_obj, type='Walk-in', owner=user)

    fake_client = _FakeClient()
    service = BMAChatService(user, client=fake_client)
    result = service.chat(question='How many registrations do we have?', history=[{'role': 'assistant', 'content': 'Hello!'}])

    assert result['answer'] == 'We currently have 1 registration.'
    assert result['usage']['total_tokens'] == 150
    system_message = fake_client.chat.completions.last_kwargs['messages'][0]['content']
    assert 'SNAPSHOT' in system_message
    assert '"total": 1' in system_message
    assert fake_client.chat.completions.last_kwargs['messages'][-1]['role'] == 'user'


def test_chat_service_maps_rate_limit_error(user):
    service = BMAChatService(user, client=_FakeClient())

    error = service._map_openai_exception(_FakeRateLimitError())

    assert isinstance(error, BMAChatService.ChatError)
    assert error.status_code == 429
    assert 'too many requests' in str(error).lower()


@pytest.mark.django_db
def test_chat_viewset_returns_response(user):
    request = APIRequestFactory().post(
        '/api/bma-chatbot/',
        data={'question': 'Hello there?', 'include_snapshot': True},
        format='json',
    )
    request.user = user

    with patch('student_registration.mscc.chatbot.views.BMAChatService') as service_cls:
        service_instance = service_cls.return_value
        service_instance.chat.return_value = {
            'answer': 'Mocked answer',
            'snapshot': {'registrations': {'total': 0}},
            'usage': {'total_tokens': 42},
        }
        view = BMAChatViewSet.as_view({'post': 'create'})
        response = view(request)

    service_cls.assert_called_once_with(user)
    service_instance.chat.assert_called_once_with(question='Hello there?', history=None)

    assert response.status_code == 200
    assert response.data['answer'] == 'Mocked answer'
    assert response.data['snapshot']['registrations']['total'] == 0
    assert response.data['usage']['total_tokens'] == 42


@pytest.mark.django_db
def test_chat_viewset_returns_specific_status_for_chat_errors(user):
    request = APIRequestFactory().post(
        '/api/bma-chatbot/',
        data={'question': 'Hello there?', 'include_snapshot': False},
        format='json',
    )
    request.user = user

    with patch('student_registration.mscc.chatbot.views.BMAChatService') as service_cls:
        service_instance = service_cls.return_value
        service_instance.chat.side_effect = BMAChatService.ChatError(
            'Please slow down.', status_code=429
        )
        view = BMAChatViewSet.as_view({'post': 'create'})
        response = view(request)

    assert response.status_code == 429
    assert response.data['detail'] == 'Please slow down.'


@pytest.mark.django_db
def test_chatbot_page_requires_authentication(user):
    client = Client()
    response = client.get(reverse('mscc:chatbot'))
    assert response.status_code == 302

    client.force_login(user)
    response = client.get(reverse('mscc:chatbot'))
    assert response.status_code == 200
    assert b'BMA Chatbot' in response.content
