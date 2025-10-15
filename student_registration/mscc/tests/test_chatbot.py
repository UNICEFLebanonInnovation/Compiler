import os
import pathlib
import sys
from datetime import date
from types import SimpleNamespace
from unittest.mock import patch

import django
import pytest
from django.test import Client, override_settings
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
from student_registration.mscc.chatbot.retriever import BMAInsightsRetriever  # noqa: E402
from student_registration.mscc.chatbot.services import BMAChatService  # noqa: E402
from student_registration.mscc.chatbot.views import BMAChatViewSet  # noqa: E402
from student_registration.mscc.models import Registration, Round  # noqa: E402
from student_registration.schools.models import PartnerOrganization  # noqa: E402
from student_registration.students.models import Nationality  # noqa: E402


@pytest.fixture()
def user(db):
    user_model = get_user_model()
    return user_model.objects.create_user(username='analyst', password='pwd12345')


def _build_locations():
    gov_type = LocationType.objects.create(name='Governorate')
    district_type = LocationType.objects.create(name='District')
    cadaster_type = LocationType.objects.create(name='Cadaster')

    governorate = Location.objects.create(name='Bekaa', type=gov_type)
    district = Location.objects.create(name='West Bekaa', type=district_type, parent=governorate)
    cadaster = Location.objects.create(name='Kamed', type=cadaster_type, parent=district)
    return governorate, district, cadaster


@pytest.mark.django_db
def test_snapshot_returns_basic_registration_records(user):
    partner = PartnerOrganization.objects.create(name='Partner A')
    user.partner = partner
    user.save(update_fields=['partner'])

    governorate, district, cadaster = _build_locations()

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

    snapshot = BMAInsightsRepository(user).build_snapshot()

    assert snapshot['registrations']['total'] == 1
    record = snapshot['registrations']['records'][0]
    assert record['id'] == registration.id
    assert record['child_name'] == 'Ali Hassan'
    assert record['partner'] == 'Partner A'
    assert record['center'] == 'Center 1'
    assert record['round'] == 'Round 2024'


def test_retriever_returns_relevant_metrics():
    snapshot = {
        'scope': {'type': 'scoped', 'username': 'analyst'},
        'registrations': {
            'total': 3,
            'by_partner': [
                {'partner': 'Partner A', 'count': 2},
                {'partner': 'Partner B', 'count': 1},
            ],
            'records': [
                {'id': 1, 'child_name': 'Ali Hassan', 'partner': 'Partner A', 'center': 'Center 1', 'round': 'Round 2024'}
            ],
        },
        'schools': {'total': 1, 'by_governorate': [{'governorate': 'Bekaa', 'count': 1}]},
        'centers': {'total': 1},
    }

    retriever = BMAInsightsRetriever(snapshot)
    context = retriever.build_context('registrations for partner a', top_k=3)

    assert 'Partner A' in context
    assert context.startswith('- **')


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


class _FakeResponse:
    def __init__(self, headers=None):
        self.headers = headers or {}


class _FakeRateLimitErrorWithHeaders(_FakeRateLimitError):
    def __init__(self, message="Request rate limited", headers=None):
        super().__init__(message)
        self.response = _FakeResponse(headers=headers)


class _SequenceChatCompletion:
    def __init__(self, results):
        self._results = list(results)
        self.calls = 0

    def create(self, **kwargs):
        if self.calls >= len(self._results):
            raise AssertionError("No more fake responses configured")
        result = self._results[self.calls]
        self.calls += 1
        if isinstance(result, Exception):
            raise result
        return result


class _SequenceClient:
    def __init__(self, results):
        self.chat = SimpleNamespace(completions=_SequenceChatCompletion(results))


@pytest.mark.django_db
def test_chat_service_uses_snapshot_and_returns_answer(user):
    partner = PartnerOrganization.objects.create(name='Partner A')
    governorate, district, cadaster = _build_locations()
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
    assert 'RELEVANT METRICS' in system_message
    assert 'Registrations' in system_message
    assert fake_client.chat.completions.last_kwargs['messages'][-1]['role'] == 'user'


def test_chat_service_maps_rate_limit_error(user):
    service = BMAChatService(user, client=_FakeClient())

    error = service._map_openai_exception(_FakeRateLimitError())

    assert isinstance(error, BMAChatService.ChatError)
    assert error.status_code == 429
    assert 'too many requests' in str(error).lower()


@pytest.mark.django_db
def test_chat_service_retries_rate_limit_then_succeeds(user):
    partner = PartnerOrganization.objects.create(name='Partner A')
    governorate, district, cadaster = _build_locations()
    Center.objects.create(name='Center 1', partner=partner, governorate=governorate, caza=district, cadaster=cadaster)

    success_message = SimpleNamespace(content='All good now.')
    success_choice = SimpleNamespace(message=success_message)
    success_response = SimpleNamespace(choices=[success_choice], usage=None)

    rate_limit_error = _FakeRateLimitErrorWithHeaders(headers={'Retry-After': '0.5'})
    sequence_client = _SequenceClient([rate_limit_error, success_response])

    sleep_calls = []

    service = BMAChatService(
        user,
        client=sequence_client,
        sleep=lambda delay: sleep_calls.append(delay),
    )

    result = service.chat(question='How many registrations?')

    assert result['answer'] == 'All good now.'
    assert sleep_calls == [0.5]
    assert sequence_client.chat.completions.calls == 2


@pytest.mark.django_db
@override_settings(OPENAI_BMA_MAX_RETRIES=1)
def test_chat_service_stops_retrying_after_limit(user):
    partner = PartnerOrganization.objects.create(name='Partner A')
    governorate, district, cadaster = _build_locations()
    Center.objects.create(name='Center 1', partner=partner, governorate=governorate, caza=district, cadaster=cadaster)

    errors = [_FakeRateLimitError('First'), _FakeRateLimitError('Second')]
    sequence_client = _SequenceClient(errors)

    sleep_calls = []
    service = BMAChatService(
        user,
        client=sequence_client,
        sleep=lambda delay: sleep_calls.append(delay),
    )

    with pytest.raises(BMAChatService.ChatError) as excinfo:
        service.chat(question='Retry please?')

    assert excinfo.value.status_code == 429
    assert sequence_client.chat.completions.calls == 2  # initial try + 1 retry
    assert len(sleep_calls) == 1


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
