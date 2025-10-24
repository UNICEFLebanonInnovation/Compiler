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
from student_registration.mscc.ai_agent import HealthSupportAgent, PreAssessmentAgent
from student_registration.mscc.models import (
    ProvidedServices,
    Registration,
    PSSService,
    HealthNutritionService,
    HealthNutritionReferral,
    EducationProgrammeAssessment,
    Round,
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
    prior_round = Round.objects.create(name='2024 Round', year=2024)
    current_round = Round.objects.create(name='2025 Round', year=2025)
    Registration.objects.create(
        child=child,
        type='Core-Package',
        registration_date=datetime.date(2024, 1, 5),
        round=prior_round,
    )
    registration = Registration.objects.create(
        child=child,
        type='Core-Package',
        registration_date=datetime.date(2025, 1, 5),
        have_labour='Yes - Morning',
        labour_hours=18,
        labour_weekly_income='5-20 USD',
        source_of_identification='Dirassa',
        round=current_round,
    )

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
    assert child_payload['registration_details']
    assert any(
        entry['field'] == 'have_labour' and entry['value'] == 'Yes - Morning'
        for entry in child_payload['registration_details']
    )
    assert any(
        entry['field'] == 'labour_hours' and entry['value'] == 18
        for entry in child_payload['registration_details']
    )
    assert child_payload['education_progress'] is None
    assert child_payload['life_quality']['label'] in {'Needs attention', 'Critical concern'}
    assert child_payload['life_quality']['score'] < 0
    assert any(
        signal['message'].startswith('Attendance below')
        for signal in child_payload['life_quality']['signals']
    )
    programme_impact = child_payload['programme_impact']
    assert programme_impact
    assert programme_impact['label'] in {'Mixed impact', 'Negative impact'}
    assert programme_impact['total_registrations'] == 2
    history = child_payload['registration_history']
    assert history
    assert history['total_registrations'] == 2
    assert history['distinct_rounds'] == 2
    assert history['longest_consecutive_years'] >= 1
    assert any(entry['is_current'] for entry in history['entries'])


@patch('student_registration.mscc.views.HealthSupportAgent.analyze_children', return_value='analysis output')
def test_health_agent_view_calls_agent(mock_analyze):
    settings.OPENAI_API_KEY = 'test-key'
    settings.OPENAI_HEALTH_AGENT_MODEL = 'gpt-test-model'
    high_risk_child = _create_child('Layla', 'Risk', 'Child', age_years=11, gender='Female')
    low_risk_child = _create_child('Omar', 'Stable', 'Child', age_years=12, gender='Male')

    round_2024 = Round.objects.create(name='2024 Round', year=2024)
    round_2025 = Round.objects.create(name='2025 Round', year=2025)
    Registration.objects.create(
        child=high_risk_child,
        type='Core-Package',
        registration_date=datetime.date(2024, 1, 10),
        round=round_2024,
    )
    high_risk_registration = Registration.objects.create(
        child=high_risk_child,
        type='Core-Package',
        have_labour='Yes - Full Day',
        labour_hours=45,
        labour_weekly_income='20-50 USD',
        education_program='BLN Level 1',
        round=round_2025,
    )
    low_risk_registration = Registration.objects.create(
        child=low_risk_child,
        type='Core-Package',
        registration_date=datetime.date(2025, 2, 1),
        round=round_2025,
    )

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

    EducationProgrammeAssessment.objects.create(
        registration=high_risk_registration,
        programme_type='BLN Level 1',
        pre_test={
            'programme_type': 'BLN Level 1',
            'arabic_grade': '18',
            'math_grade': '15',
        },
        post_test={
            'programme_type': 'BLN Level 1',
            'arabic_grade': '10',
            'math_grade': '12',
            'participation': 'Absence for 10-15 days /equivlant remote learning sessions',
            'post_test_done': 'Yes',
            'school_year_completed': 'No',
            'barriers': 'Other',
            'barriers_other': 'Transport challenges',
        },
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
    payload = json.dumps({
        'registration_ids': [high_risk_registration.id, low_risk_registration.id],
        'limit': 1,
        'question': '  Focus on malnutrition risks  ',
    })
    request = factory.post('/mscc/ai/health-support/', data=payload, content_type='application/json')
    request.user = SimpleNamespace(is_authenticated=True)

    response = HealthSupportAgentView.as_view()(request)

    assert response.status_code == 200
    payload = json.loads(response.content)

    assessment = payload['question_assessment']
    assert assessment['question'] == 'Focus on malnutrition risks'
    assert assessment['focus_topics'] == ['nutrition']
    assert assessment['keywords'] == ['malnutrition', 'risks']
    assert assessment['is_meaningful'] is True
    assert assessment['should_abort'] is False
    assert assessment['quality_score'] >= 0.5
    assert assessment['recommended_action']

    mock_analyze.assert_called_once()
    called_context = mock_analyze.call_args[0][0]
    assert mock_analyze.call_args.kwargs['question'] == 'Focus on malnutrition risks'
    assert mock_analyze.call_args.kwargs['focus_topics'] == {'nutrition'}
    assert mock_analyze.call_args.kwargs['keywords'] == ['malnutrition', 'risks']
    assert len(called_context) == 1
    assert called_context[0]['registration_id'] == high_risk_registration.id
    assert called_context[0]['life_quality']['label'] == 'Critical concern'
    assert called_context[0]['registration_details']
    assert called_context[0]['registration_history']
    assert called_context[0]['registration_history']['total_registrations'] >= 2
    assert called_context[0]['programme_impact']
    assert called_context[0]['programme_impact']['direction'] in {'negative', 'mixed'}

    assert payload['analysis'] == 'analysis output'
    assert payload['model'] == 'gpt-test-model'
    assert payload['question'] == 'Focus on malnutrition risks'
    assert payload['focus_topics'] == ['nutrition']
    assert payload['question_keywords'] == ['malnutrition', 'risks']
    assert payload['count'] == 1
    assert payload['children'][0]['registration_id'] == high_risk_registration.id
    assert payload['children'][0]['focus_topics'] == ['nutrition']
    assert payload['children'][0]['question_keywords'] == ['malnutrition', 'risks']
    assert 'nutrition' in payload['children'][0]['focus_highlights']
    assert payload['children'][0]['risk_score'] > payload['children'][0]['services']['pss']['required_pending']
    assert payload['children'][0]['pss_details']
    assert payload['children'][0]['health_details']
    assert payload['children'][0]['registration_history']
    assert any('MUAC screening result' in alert for alert in payload['children'][0]['alerts'])
    assert any('Referred for malnutrition treatment' in alert for alert in payload['children'][0]['alerts'])
    assert any('PSS vulnerability' in flag for flag in payload['children'][0]['wellbeing_flags'])
    assert 'Significant decline in education grading outcomes' in payload['children'][0]['alerts']
    assert 'School year not completed' in payload['children'][0]['alerts']
    assert 'Education post-tests not completed' not in payload['children'][0]['alerts']
    assert any(
        flag == 'Learning outcomes declined across programme assessments'
        for flag in payload['children'][0]['wellbeing_flags']
    )
    education_progress = payload['children'][0]['education_progress']
    assert education_progress['programme_type'] == 'BLN Level 1'
    assert education_progress['trend'] == 'declined'
    assert education_progress['average_change'] == pytest.approx(-5.5, rel=1e-2)
    assert education_progress['barriers_detail'] == 'Transport challenges'
    subject_changes = {entry['field']: entry['change'] for entry in education_progress['subjects']}
    assert subject_changes['arabic_grade'] == pytest.approx(-8, rel=1e-2)
    assert subject_changes['math_grade'] == pytest.approx(-3, rel=1e-2)
    life_quality = payload['children'][0]['life_quality']
    assert life_quality['label'] == 'Critical concern'
    assert life_quality['score'] <= -6
    assert any('Child showing distress symptoms' == signal['message'] for signal in life_quality['signals'])
    assert any(
        signal['message'].startswith('Learning outcomes declined on average')
        for signal in life_quality['signals']
    )
    programme_impact = payload['children'][0]['programme_impact']
    assert programme_impact['direction'] in {'negative', 'mixed'}
    assert programme_impact['total_registrations'] >= 2
    assert any('decline' in (factor['message'] or '').lower() for factor in programme_impact['factors'])


def test_agent_infers_nutrition_focus():
    focus = HealthSupportAgent.infer_focus_topics('Need insights on nutrition and malnutrition risks')
    assert focus == {'nutrition'}


def test_agent_extracts_keywords():
    keywords = HealthSupportAgent.extract_keywords('How are nutrition and attendance improving this year?')
    assert keywords == ['nutrition', 'attendance', 'improving']


def test_pre_assessment_flags_gibberish_question():
    agent = PreAssessmentAgent()
    assessment = agent.evaluate('asdf qwer zxcv')

    assert assessment['should_abort'] is True
    assert assessment['is_meaningful'] is False
    assert assessment['quality_score'] < 0.35
    assert any(
        'gibberish' in issue.lower() or 'unclear' in issue.lower()
        for issue in assessment['issues']
    )


def test_agent_prompt_limits_scope_for_nutrition(settings):
    settings.OPENAI_API_KEY = 'test-key'
    agent = HealthSupportAgent(api_key='test-key')
    messages = agent._build_prompt(
        [{'registration_id': 1}],
        question='Need insights on nutrition status',
        focus_topics={'nutrition'},
    )

    assert len(messages) == 2
    user_content = messages[1]['content']
    assert 'Focus specifically on: Need insights on nutrition status' in user_content
    assert 'Limit your assessment strictly to the following domains: nutrition' in user_content
    assert 'Avoid reporting on attendance, PSS' in user_content
    assert 'Detected question keywords: nutrition' in user_content


def test_education_progress_positive_trend():
    settings.OPENAI_API_KEY = ''
    child = _create_child('Sara', 'Bright', 'Child', age_years=9, gender='Female')
    registration = Registration.objects.create(
        child=child,
        type='Core-Package',
        education_program='BLN Level 2',
    )

    PSSService.objects.create(registration=registration)
    HealthNutritionService.objects.create(registration=registration, eating_minimum_meals='Yes')
    ProvidedServices.objects.create(
        registration=registration,
        name='PSS',
        category='Child Protection',
        required=True,
        completed=True,
    )

    _record_attendance(registration, child, datetime.date(2025, 3, 1), 'Yes')
    _record_attendance(registration, child, datetime.date(2025, 3, 2), 'Yes')

    EducationProgrammeAssessment.objects.create(
        registration=registration,
        programme_type='BLN Level 2',
        pre_test={
            'programme_type': 'BLN Level 2',
            'arabic_grade': '20',
            'math_grade': '18',
        },
        post_test={
            'programme_type': 'BLN Level 2',
            'arabic_grade': '35',
            'math_grade': '33',
            'participation': 'No Absence',
            'post_test_done': 'Yes',
            'school_year_completed': 'Yes',
            'barriers': 'No barriers',
        },
    )

    factory = RequestFactory()
    request = factory.get('/mscc/ai/health-support/', {'registration_id': str(registration.id)})
    request.user = SimpleNamespace(is_authenticated=True)

    response = HealthSupportAgentView.as_view()(request)

    assert response.status_code == 200
    payload = json.loads(response.content)
    assert payload['count'] == 1
    child_payload = payload['children'][0]
    progress = child_payload['education_progress']
    assert progress['programme_type'] == 'BLN Level 2'
    assert progress['trend'] == 'improved'
    assert progress['average_change'] == pytest.approx(15.0, rel=1e-2)
    assert 'Learning outcomes improved across programme assessments' in child_payload['wellbeing_flags']
    assert 'Significant decline in education grading outcomes' not in child_payload['alerts']
    assert 'Education post-tests not completed' not in child_payload['alerts']
    life_quality = child_payload['life_quality']
    assert any(
        signal['message'].startswith('Learning outcomes improved on average')
        for signal in life_quality['signals']
    )
    programme_impact = child_payload['programme_impact']
    assert programme_impact
    assert programme_impact['direction'] in {'positive', 'mixed'}
    assert any('improved' in (factor['message'] or '').lower() for factor in programme_impact['factors'])
