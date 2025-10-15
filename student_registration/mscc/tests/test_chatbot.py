import os
import pathlib
import sys
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

from student_registration.mscc.chatbot.repository import BMAInsightsRepository  # noqa: E402
from student_registration.mscc.chatbot.retriever import BMAInsightsRetriever  # noqa: E402
from student_registration.mscc.chatbot.services import BMAChatService  # noqa: E402
from student_registration.mscc.chatbot.views import BMAChatViewSet  # noqa: E402


@pytest.fixture()
def user(db):
    user_model = get_user_model()
    return user_model.objects.create_user(username='analyst', password='pwd12345')


class _StubRepository:
    """Simple repository stub returning a deterministic snapshot."""

    def __init__(self, user):
        self.user = user

    def build_snapshot(self):
        username = getattr(self.user, 'username', None)
        snapshot_time_range = {'start': '2024-01-01', 'end': '2024-06-01'}
        return {
            'generated_at': '2024-06-01T00:00:00',
            'time_range': snapshot_time_range,
            'scope': {'type': 'scoped', 'username': username},
            'source': 'metrics',
            'registrations': {
                'total': 1,
                'time_range': snapshot_time_range,
                'records': [],
                'by_round': [{'round': 'Round 2024', 'count': 1}],
                'by_gender': [{'gender': 'Female', 'count': 1}],
                'by_nationality': [{'nationality': 'Lebanese', 'count': 1}],
                'by_partner': [{'partner': 'Partner A', 'count': 1}],
                'by_package_type': [{'package_type': 'Core-Package', 'count': 1}],
                'by_governorate': [{'governorate': 'Bekaa', 'count': 1}],
                'by_round_gender_nationality': [
                    {
                        'round': 'Round 2024',
                        'gender': 'Female',
                        'nationality': 'Lebanese',
                        'count': 1,
                    }
                ],
                'monthly_trend': [{'month': '2024-05', 'registrations': 1}],
            },
            'schools': {'total': 0, 'by_governorate': [], 'by_type': []},
            'centers': {'total': 0, 'by_governorate': [], 'by_partner': []},
        }


@patch('student_registration.mscc.chatbot.repository.execute_metric')
def test_snapshot_uses_materialised_metrics(mock_execute_metric, user):
    responses = {
        'none': {'total': 3, 'rows': []},
        'partner_id': {'rows': [{'label': 'Partner A', 'value': 2}, {'label': 'Partner B', 'value': 1}]},
        'child_gender_norm': {'rows': [{'label': 'Female', 'value': 2}]},
        'child_nationality_name': {'rows': [{'label': 'Lebanese', 'value': 3}]},
        'cycle': {'rows': [{'label': 'Core-Package', 'value': 3}]},
        'governorate': {'rows': [{'label': 'Bekaa', 'value': 3}]},
        'round_id': {'rows': [{'label': 'Round 2024', 'value': 3}]},
        'month': {'rows': [{'label': '2024-04-01', 'value': 1}, {'label': '2024-05-01', 'value': 2}]},
        'round_id,child_gender_norm,child_nationality_name': {
            'rows': [
                {
                    'labels': {
                        'round_id': 'Round 2024',
                        'child_gender_norm': 'Female',
                        'child_nationality_name': 'Lebanese',
                    },
                    'value': 2,
                }
            ]
        },
    }

    def side_effect(**kwargs):
        breakdown = kwargs.get('breakdown_by', 'none')
        payload = responses.get(breakdown, {'rows': []})
        result = {'metric_key': kwargs['metric_key'], 'breakdown_by': breakdown}
        result.update(payload)
        return result

    mock_execute_metric.side_effect = side_effect

    snapshot = BMAInsightsRepository(user).build_snapshot()

    assert snapshot['source'] == 'metrics'
    assert snapshot['registrations']['total'] == 3
    assert snapshot['registrations']['by_partner'][0]['partner'] == 'Partner A'
    assert snapshot['registrations']['monthly_trend'][-1] == {'month': '2024-05', 'registrations': 2}
    assert snapshot['registrations']['by_round_gender_nationality'][0]['gender'] == 'Female'

    called_breakdowns = {kwargs['breakdown_by'] for _, kwargs in mock_execute_metric.call_args_list}
    assert {
        'none',
        'partner_id',
        'month',
        'round_id,child_gender_norm,child_nationality_name',
    }.issubset(called_breakdowns)

    for _, kwargs in mock_execute_metric.call_args_list:
        assert kwargs['metric_key'] == 'mscc_registrations_total'
        assert kwargs['time_start'] == snapshot['time_range']['start']
        assert kwargs['time_end'] == snapshot['time_range']['end']
        assert kwargs['user_ctx']['partner_ids'] == []


def test_retriever_returns_relevant_metrics():
    snapshot = {
        'scope': {'type': 'scoped', 'username': 'analyst'},
        'registrations': {
            'total': 3,
            'by_partner': [
                {'partner': 'Partner A', 'count': 2},
                {'partner': 'Partner B', 'count': 1},
            ],
            'records': [],
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
    fake_client = _FakeClient()
    service = BMAChatService(user, client=fake_client, repository_class=_StubRepository)
    result = service.chat(
        question='How many registrations do we have?',
        history=[{'role': 'assistant', 'content': 'Hello!'}],
    )

    assert result['answer'] == 'We currently have 1 registration.'
    assert result['usage']['total_tokens'] == 150
    system_message = fake_client.chat.completions.last_kwargs['messages'][0]['content']
    assert 'SNAPSHOT' in system_message
    assert '"total": 1' in system_message
    assert 'RELEVANT METRICS' in system_message
    assert 'Registrations' in system_message
    assert fake_client.chat.completions.last_kwargs['messages'][-1]['role'] == 'user'


def test_chat_service_maps_rate_limit_error(user):
    service = BMAChatService(user, client=_FakeClient(), repository_class=_StubRepository)

    error = service._map_openai_exception(_FakeRateLimitError())

    assert isinstance(error, BMAChatService.ChatError)
    assert error.status_code == 429
    assert 'too many requests' in str(error).lower()


@pytest.mark.django_db
def test_chat_service_retries_rate_limit_then_succeeds(user):
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
        repository_class=_StubRepository,
    )

    result = service.chat(question='How many registrations?')

    assert result['answer'] == 'All good now.'
    assert sleep_calls == [0.5]
    assert sequence_client.chat.completions.calls == 2


@pytest.mark.django_db
@override_settings(OPENAI_BMA_MAX_RETRIES=1)
def test_chat_service_stops_retrying_after_limit(user):
    errors = [_FakeRateLimitError('First'), _FakeRateLimitError('Second')]
    sequence_client = _SequenceClient(errors)

    sleep_calls = []
    service = BMAChatService(
        user,
        client=sequence_client,
        sleep=lambda delay: sleep_calls.append(delay),
        repository_class=_StubRepository,
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
