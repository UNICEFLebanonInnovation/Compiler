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
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import RequestFactory
from django.test.utils import setup_databases, teardown_databases
from django.utils import timezone

django.setup()

from student_registration.attendances.models import (
    MSCCAttendance,
    MSCCAttendanceChild,
)
from student_registration.child.models import Child
from student_registration.mscc.ai_agent import (
    HealthSupportAgent,
    MSCCKnowledgeEngine,
    PreAssessmentAgent,
)
from student_registration.mscc.knowledge import KnowledgeCompilation, MSCCKnowledgeCompiler
from student_registration.mscc.models import (
    ProvidedServices,
    Registration,
    PSSService,
    HealthNutritionService,
    HealthNutritionReferral,
    EducationProgrammeAssessment,
    FollowUpService,
    Round,
    MSCCKnowledgeSnapshot,
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


def _record_followup(
    registration: Registration,
    *,
    follow_up_type: str = 'Phone call',
    follow_up_result: str = 'Follow-up with parents',
    parent_attended: str = 'Yes',
    caregiver_attended: str = 'Mother & Father',
    meeting_number: int = 1,
    pfss_sessions: str = 'No',
    pfss_sessions_number: int = 0,
) -> FollowUpService:
    return FollowUpService.objects.create(
        registration=registration,
        follow_up_type=follow_up_type,
        follow_up_result=follow_up_result,
        parent_attended_meeting=parent_attended,
        caregiver_attended=caregiver_attended,
        meeting_number=meeting_number,
        pfss_sessions=pfss_sessions,
        pfss_sessions_number=pfss_sessions_number,
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

    _record_followup(
        registration,
        follow_up_type='Phone call',
        follow_up_result='Follow-up with parents',
        parent_attended='Yes',
        caregiver_attended='Mother & Father',
        meeting_number=2,
        pfss_sessions='Yes',
        pfss_sessions_number=2,
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
    assert any(
        'Family relies on child labour income' in flag
        for flag in child_payload['wellbeing_flags']
    )
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
    family_context = child_payload['family_context']
    assert family_context
    assert family_context['follow_up']['total_followups'] == 1
    assert family_context['follow_up']['recent_follow_up']['result'] == 'Follow-up with parents'
    assert any(entry['field'] == 'have_labour' for entry in family_context['socioeconomic'])
    assert any('Family relies on child labour income' in flag for flag in family_context['flags'])
    vulnerability_profile = child_payload['vulnerability_profile']
    assert vulnerability_profile
    assert vulnerability_profile['top_concerns']
    assert child_payload['vulnerability_tags']
    assert vulnerability_profile['severity'] in {'elevated', 'moderate', 'high', 'critical', 'low'}
    assert any('attendance rate' in concern.lower() for concern in vulnerability_profile['top_concerns'])
    assert any('pss pending' in concern.lower() for concern in vulnerability_profile['top_concerns'])
    assert any('labour' in concern.lower() for concern in vulnerability_profile['top_concerns'])
    assert 'vulnerability_overview' in payload
    assert payload['vulnerability_overview']['severity_counts']


def test_mscc_knowledge_compiler_creates_daily_snapshot():
    settings.OPENAI_API_KEY = ''
    child = _create_child('Layla', 'Test', 'Child', age_years=11, gender='Female')
    round_2024 = Round.objects.create(name='2024 Round', year=2024)
    registration = Registration.objects.create(
        child=child,
        type='Core-Package',
        registration_date=datetime.date(2024, 3, 12),
        have_labour='No',
        round=round_2024,
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

    _record_followup(
        registration,
        follow_up_type='Centre visit',
        follow_up_result='Discussed attendance with caregivers',
        meeting_number=1,
    )
    _record_attendance(registration, child, datetime.date(2024, 3, 10), 'No')
    _record_attendance(registration, child, datetime.date(2024, 3, 11), 'Yes')

    EducationProgrammeAssessment.objects.create(
        registration=registration,
        overall_comment='Improving engagement.',
        academic_progress='Steady',
    )

    compiler = MSCCKnowledgeCompiler(limit=5)
    snapshot = compiler.create_snapshot()

    assert snapshot.summary
    assert snapshot.children
    assert snapshot.metadata.get('children_count') == len(snapshot.children)
    assert snapshot.document_count >= 1

    payload = snapshot.as_openai_payload()
    assert payload['summary'] == snapshot.summary
    assert payload['children'] == snapshot.children
    assert payload['metadata'].get('digest')

    latest_snapshot = MSCCKnowledgeSnapshot.latest_snapshot()
    assert latest_snapshot == snapshot

    assert snapshot.children
    child_summary = snapshot.children[0]
    history = child_summary.get('registration_history') or {}
    assert history.get('total_registrations') == 1
    assert child_summary.get('vulnerability_profile')
    assert child_summary['vulnerability_profile']['top_concerns']
    metadata = snapshot.metadata
    assert metadata.get('vulnerability_overview')
    assert metadata['document_index'][0]['vulnerability_concerns']
    assert metadata['document_index'][0]['vulnerability_severity']

    knowledge_engine = MSCCKnowledgeEngine(payload['children'])
    compiled_summary = knowledge_engine.render_compiled_summary()
    assert f"registration_id = {registration.id}" in compiled_summary
    assert 'attendance.missed_sessions = 2' in compiled_summary
    overview = knowledge_engine.vulnerability_overview
    assert overview.get('severity_counts')

    search_results = knowledge_engine.search('attendance 2')
    assert search_results
    assert search_results[0].registration_id == registration.id
    assert any('missed_sessions' in result.snippet for result in search_results)

    numeric_results = knowledge_engine.search(str(registration.id))
    assert any(result.registration_id == registration.id for result in numeric_results)


@patch('student_registration.mscc.management.commands.compile_mscc_knowledge.MSCCKnowledgeCompiler')
def test_compile_mscc_knowledge_command_creates_snapshot(mock_compiler, capsys):
    snapshot = SimpleNamespace(
        pk=42,
        generated_for=datetime.date(2024, 4, 1),
        document_count=3,
    )
    snapshot.as_openai_payload = lambda: {
        'summary': 'compiled summary',
        'children': [{'registration_id': 10}],
        'metadata': {'digest': 'abc123'},
    }

    mock_compiler.return_value.create_snapshot.return_value = snapshot

    call_command('compile_mscc_knowledge')

    mock_compiler.assert_called_once()
    mock_compiler.return_value.create_snapshot.assert_called_once()
    output = capsys.readouterr().out
    assert 'snapshot created' in output
    assert '"document_count": 3' in output


@patch('student_registration.mscc.management.commands.compile_mscc_knowledge.MSCCKnowledgeCompiler')
def test_compile_mscc_knowledge_command_dry_run(mock_compiler, capsys):
    compilation = KnowledgeCompilation(
        generated_at=timezone.now(),
        summary='Daily summary content',
        documents=[{'registration_id': 1, 'numbers': [1]}],
        children=[{'registration_id': 1, 'child_name': 'Layla'}],
        vulnerability_overview={'severity_counts': {'high': 1}},
    )

    mock_compiler.return_value.compile.return_value = compilation

    call_command('compile_mscc_knowledge', '--dry-run', '--limit', '5')

    mock_compiler.assert_called_once_with(limit=5)
    mock_compiler.return_value.compile.assert_called_once()
    output = capsys.readouterr().out
    assert 'Compiled MSCC knowledge' in output
    assert 'Daily summary content' in output
    assert '"children_count": 1' in output


def test_compile_mscc_knowledge_command_include_documents_requires_dry_run():
    with pytest.raises(CommandError):
        call_command('compile_mscc_knowledge', '--include-documents')


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

    _record_followup(
        high_risk_registration,
        follow_up_type='Home Visits',
        follow_up_result='Child returned to program',
        parent_attended='Yes',
        caregiver_attended='Mother & Father',
        meeting_number=3,
        pfss_sessions='Yes',
        pfss_sessions_number=3,
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
    assert called_context[0]['family_context']['follow_up']['total_followups'] == 1
    assert called_context[0]['family_context']['socioeconomic']

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
    assert payload['children'][0]['family_context']['follow_up']['total_followups'] == 1
    assert payload['children'][0]['family_context']['flags']
    assert any('MUAC screening result' in alert for alert in payload['children'][0]['alerts'])
    assert any('Referred for malnutrition treatment' in alert for alert in payload['children'][0]['alerts'])
    assert any('PSS vulnerability' in flag for flag in payload['children'][0]['wellbeing_flags'])
    assert any(
        'Family relies on child labour income' in flag
        for flag in payload['children'][0]['wellbeing_flags']
    )
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
    vulnerability_profile = payload['children'][0]['vulnerability_profile']
    assert vulnerability_profile
    assert vulnerability_profile['severity'] in {'high', 'critical', 'moderate', 'elevated'}
    assert any('attendance' in concern.lower() for concern in vulnerability_profile['top_concerns'])
    assert any('pss' in concern.lower() or 'psychosocial' in concern.lower() for concern in vulnerability_profile['top_concerns'])
    assert payload['children'][0]['vulnerability_tags']
    assert payload['vulnerability_overview']['severity_counts']


def test_agent_infers_nutrition_focus():
    focus = HealthSupportAgent.infer_focus_topics('Need insights on nutrition and malnutrition risks')
    assert focus == {'nutrition'}


def test_agent_infers_family_focus():
    focus = HealthSupportAgent.infer_focus_topics('Review family follow-up and household poverty barriers')
    assert focus == {'family'}


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
