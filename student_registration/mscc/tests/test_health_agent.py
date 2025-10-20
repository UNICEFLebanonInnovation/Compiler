import datetime
import json
import os
from types import SimpleNamespace
from unittest.mock import patch

os.environ.setdefault('DATABASE_URL', 'sqlite:///test.sqlite3')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.test')

import django
import pytest
from django.conf import settings
from django.test import RequestFactory
from django.test.utils import setup_databases, teardown_databases

django.setup()

from student_registration.attendances.models import (
    MSCCAttendance,
    MSCCAttendanceChild,
)
from student_registration.child.models import Child
from student_registration.mscc.models import (
    ProvidedServices,
    Registration,
    PSSService,
    HealthNutritionService,
    HealthNutritionReferral,
)
from student_registration.mscc.views import HealthSupportAgentView


_DATABASES = setup_databases(verbosity=0, interactive=False)


def teardown_module(module):
    teardown_databases(_DATABASES, verbosity=0)


def _create_child(first_name: str, father_name: str, last_name: str, age_years: int, gender: str):
    today = datetime.date.today()
    target_year = today.year - age_years
    return Child.objects.create(
        first_name=first_name,
        father_name=father_name,
        last_name=last_name,
        gender=gender,
        birthday_year=str(target_year),
        birthday_month="1",
        birthday_day="1",
    )


def _record_attendance(registration: Registration, child: Child, date: datetime.date, attended: str):
    attendance_day = MSCCAttendance.objects.create(attendance_date=date)
    return MSCCAttendanceChild.objects.create(
        registration=registration,
        child=child,
        attendance_day=attendance_day,
        attended=attended,
    )


def test_health_agent_view_without_api_key():
    settings.OPENAI_API_KEY = ''
    child = _create_child('Rami', 'Test', 'Child', age_years=10, gender='Male')
    registration = Registration.objects.create(child=child, type='Core-Package')

    PSSService.objects.create(registration=registration)
    HealthNutritionService.objects.create(registration=registration)
    ProvidedServices.objects.create(
        registration=registration,
        name='PSS',
        category='Child Protection',
        required=True,
        completed=False,
    )
    ProvidedServices.objects.create(
        registration=registration,
        name='Health and Nutrition',
        category='Health & Nutrition',
        required=True,
        completed=False,
    )

    _record_attendance(registration, child, datetime.date(2025, 1, 1), 'No')
    _record_attendance(registration, child, datetime.date(2025, 1, 2), 'No')
    _record_attendance(registration, child, datetime.date(2025, 1, 3), 'Yes')

    factory = RequestFactory()
    request = factory.get('/mscc/ai/health-support/', {'registration_id': str(registration.id)})
    request.user = SimpleNamespace(is_authenticated=True)

    response = HealthSupportAgentView.as_view()(request)

    assert response.status_code == 200

    payload = json.loads(response.content)
    assert payload['count'] == 1
    assert payload['analysis'] == ''
    assert 'error' in payload
    assert 'OpenAI API key is not configured' in payload['error']

    child_payload = payload['children'][0]
    assert child_payload['services']['pss']['required_pending'] == 1
    assert child_payload['services']['health']['required_pending'] == 1
    assert child_payload['attendance']['missed_sessions'] == 2
    assert child_payload['attendance']['attendance_rate'] == pytest.approx(0.33, rel=1e-2)
    assert child_payload['pss_details'] == []
    assert child_payload['health_details'] == []
    assert child_payload['health_referral_details'] == []
    assert child_payload['wellbeing_flags'] == []
    assert child_payload['life_quality']['label'] == 'Needs attention'
    assert child_payload['life_quality']['score'] < 0
    assert any(
        signal['message'].startswith('Attendance below')
        for signal in child_payload['life_quality']['signals']
    )


@patch('student_registration.mscc.views.HealthSupportAgent.analyze_children', return_value='analysis output')
def test_health_agent_view_calls_agent(mock_analyze):
    settings.OPENAI_API_KEY = 'test-key'
    settings.OPENAI_HEALTH_AGENT_MODEL = 'gpt-test-model'
    high_risk_child = _create_child('Layla', 'Risk', 'Child', age_years=11, gender='Female')
    low_risk_child = _create_child('Omar', 'Stable', 'Child', age_years=12, gender='Male')

    high_risk_registration = Registration.objects.create(child=high_risk_child, type='Core-Package')
    low_risk_registration = Registration.objects.create(child=low_risk_child, type='Core-Package')

    PSSService.objects.create(
        registration=high_risk_registration,
        child_vulnerability='Clear signs of distress',
        child_protection_concern='Isolation',
        child_distress='Yes',
        child_know_seek_help='No',
    )
    HealthNutritionService.objects.create(
        registration=high_risk_registration,
        muac_malnutrition_screening='SAM (MUAC <11.5 cm)',
        eating_minimum_meals='No',
        child_vaccinated='No',
        missing_vaccine='Polio booster',
    )
    HealthNutritionReferral.objects.create(
        registration=high_risk_registration,
        referred_development_delays='Yes',
        development_delays='Hospital',
        referred_malnutrition='Yes',
        malnutrition_treatment_center='To Hospital',
    )

    PSSService.objects.create(registration=low_risk_registration)
    HealthNutritionService.objects.create(registration=low_risk_registration, eating_minimum_meals='Yes', child_vaccinated='Yes')
    HealthNutritionReferral.objects.create(registration=low_risk_registration)

    ProvidedServices.objects.create(
        registration=high_risk_registration,
        name='PSS',
        category='Child Protection',
        required=True,
        completed=False,
    )
    ProvidedServices.objects.create(
        registration=low_risk_registration,
        name='PSS',
        category='Child Protection',
        required=True,
        completed=True,
    )

    _record_attendance(high_risk_registration, high_risk_child, datetime.date(2025, 1, 1), 'No')
    _record_attendance(high_risk_registration, high_risk_child, datetime.date(2025, 1, 2), 'No')
    _record_attendance(high_risk_registration, high_risk_child, datetime.date(2025, 1, 3), 'Yes')
    _record_attendance(low_risk_registration, low_risk_child, datetime.date(2025, 1, 1), 'Yes')

    factory = RequestFactory()
    payload = json.dumps({'registration_ids': [high_risk_registration.id, low_risk_registration.id], 'limit': 1})
    request = factory.post('/mscc/ai/health-support/', data=payload, content_type='application/json')
    request.user = SimpleNamespace(is_authenticated=True)

    response = HealthSupportAgentView.as_view()(request)

    assert response.status_code == 200
    payload = json.loads(response.content)

    mock_analyze.assert_called_once()
    called_context = mock_analyze.call_args[0][0]
    assert len(called_context) == 1
    assert called_context[0]['registration_id'] == high_risk_registration.id
    assert called_context[0]['life_quality']['label'] == 'Critical concern'

    assert payload['analysis'] == 'analysis output'
    assert payload['model'] == 'gpt-test-model'
    assert payload['count'] == 1
    assert payload['children'][0]['registration_id'] == high_risk_registration.id
    assert payload['children'][0]['risk_score'] > payload['children'][0]['services']['pss']['required_pending']
    assert payload['children'][0]['pss_details']
    assert payload['children'][0]['health_details']
    assert any('MUAC screening result' in alert for alert in payload['children'][0]['alerts'])
    assert any('Referred for malnutrition treatment' in alert for alert in payload['children'][0]['alerts'])
    assert any('PSS vulnerability' in flag for flag in payload['children'][0]['wellbeing_flags'])
    life_quality = payload['children'][0]['life_quality']
    assert life_quality['label'] == 'Critical concern'
    assert life_quality['score'] <= -6
    assert any('Child showing distress symptoms' == signal['message'] for signal in life_quality['signals'])
