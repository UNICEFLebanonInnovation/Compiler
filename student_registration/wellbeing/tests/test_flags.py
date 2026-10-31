"""Makani wellbeing flags: the rules, keeping flags in step with the data, follow-ups, summaries,
access and the back-test."""

import datetime

import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from rest_framework.test import APIClient

from student_registration.attendances.models import MSCCAttendance, MSCCAttendanceChild
from student_registration.child.models import Child
from student_registration.clm.models import Disability
from student_registration.locations.models import Center, Location, LocationType
from student_registration.mscc import models as m
from student_registration.schools.models import PartnerOrganization
from student_registration.students.models import Nationality
from student_registration.wellbeing import backtest, engine
from student_registration.wellbeing.models import CenterSummary, Flag

pytestmark = pytest.mark.django_db

TODAY = datetime.date(2025, 5, 30)  # a Friday


def days_back(n):
    """The last ``n`` weekdays up to TODAY, oldest first."""
    out, day = [], TODAY
    while len(out) < n:
        if day.weekday() < 5:
            out.append(day)
        day -= datetime.timedelta(days=1)
    return list(reversed(out))


@pytest.fixture
def world():
    gov = LocationType.objects.create(name='Governorate')
    akkar = Location.objects.create(name='Akkar', p_code='LB1', type=gov)
    syrian = Nationality.objects.create(name='Syrian', name_en='Syrian')
    no = Disability.objects.create(name='No', name_en='No', active=True)
    partner = PartnerOrganization.objects.create(name='Makani Partner', is_makani=True)
    other_partner = PartnerOrganization.objects.create(name='Other Partner', is_makani=True)
    the_round = m.Round.objects.create(name='Round 1 2025', year=2025, current_year=True,
                                       start_date=datetime.date(2025, 1, 6), end_date=datetime.date(2025, 6, 30))
    center = Center.objects.create(name='Center A', partner=partner, governorate=akkar, type='Community Hub')
    other_center = Center.objects.create(name='Center B', partner=other_partner, governorate=akkar)

    def register(center=center, partner=partner, name='Child', **registration):
        kid = Child.objects.create(first_name=name, gender='Female', birthday_year='2015', nationality=syrian,
                                   disability=no)
        reg = m.Registration.objects.create(child=kid, partner=partner, center=center, round=the_round,
                                            type='Core-Package', registration_date=datetime.date(2025, 1, 6),
                                            **registration)
        m.EducationService.objects.create(registration=reg, education_program='BLN Level 1', round=the_round,
                                          class_section='A', registration_date=datetime.date(2025, 1, 6))
        return reg

    return {'center': center, 'other_center': other_center, 'partner': partner, 'round': the_round,
            'register': register}


def sheet(center, day, marks, the_round):
    attendance = MSCCAttendance.objects.create(round_id=the_round.id, center=center, education_program='BLN Level 1',
                                               class_section='A', attendance_date=day, day_off='no')
    for reg, mark in marks.items():
        MSCCAttendanceChild.objects.create(attendance_day=attendance, registration=reg, child=reg.child,
                                           attended=mark, absence_reason='Sick' if mark == 'No' else '')
    return attendance


def attendance(world, pattern, *regs):
    """``pattern`` per class day, oldest first: 'P' present, 'A' absent, for every child given."""
    for day, mark in zip(days_back(len(pattern)), pattern):
        sheet(world['center'], day, {r: 'Yes' if mark == 'P' else 'No' for r in regs}, world['round'])


def flags(**kw):
    return list(Flag.objects.filter(**kw).values_list('kind', flat=True))


# ------------------------------------------------------------------------------------ attendance
def test_absent_three_class_days_in_a_row_raises_a_flag_that_clears_when_the_child_returns(world):
    reg = world['register']()
    attendance(world, 'PPPPPPPAAA', reg)
    engine.refresh(today=TODAY)
    flag = Flag.objects.get(registration=reg, kind=Flag.ABSENCE_STREAK)
    assert flag.status == Flag.OPEN and 'Absent 3 class days in a row' in flag.reason
    assert flag.center == world['center'] and flag.partner == world['partner']
    sheet(world['center'], TODAY + datetime.timedelta(days=3), {reg: 'Yes'}, world['round'])
    engine.refresh(today=TODAY + datetime.timedelta(days=3))
    flag.refresh_from_db()
    assert flag.status == Flag.RESOLVED and flag.resolved_on == TODAY + datetime.timedelta(days=3)


def test_all_present_sheets_count_neither_way(world):
    """Five or more children, all present: the form's default; such a sheet is left out."""
    absent = world['register'](name='Absent')
    others = [world['register'](name='Other %s' % n) for n in range(5)]
    days = days_back(4)
    for day in days[:3]:
        sheet(world['center'], day, {absent: 'No', **{o: 'Yes' for o in others}}, world['round'])
    sheet(world['center'], days[3], {absent: 'Yes', **{o: 'Yes' for o in others}}, world['round'])  # all present
    engine.refresh(today=TODAY)
    assert flags(registration=absent) == [Flag.ABSENCE_STREAK]  # the all-present day did not break the streak
    figures = CenterSummary.objects.get(center=world['center']).figures
    assert figures['attendance']['sheets'] == 4 and figures['attendance']['sheets_all_present'] == 1


def test_low_attendance_and_a_sudden_drop(world):
    low = world['register'](name='Low')
    attendance(world, 'PAPAPAPAPAP', low)  # 6 of 11
    drop = world['register'](name='Drop')
    attendance(world, 'PPPPPPPPPPPPPPPPAPAPA', drop)
    engine.refresh(today=TODAY)
    assert Flag.LOW_ATTENDANCE in flags(registration=low)
    assert flags(registration=drop) == [Flag.ATTENDANCE_DROP]


# ------------------------------------------------------------------------------------- services
def test_a_required_service_missing_after_six_weeks(world):
    reg = world['register']()
    m.ProvidedServices.objects.create(registration=reg, name='PSS', required=True, completed=False)
    m.ProvidedServices.objects.create(registration=reg, name='Digital component', required=False, completed=False)
    engine.refresh(today=TODAY)
    flag = Flag.objects.get(registration=reg, kind=Flag.SERVICE_GAP)
    assert flag.evidence['services'] == ['PSS']
    m.ProvidedServices.objects.filter(registration=reg, name='PSS').update(completed=True)
    engine.refresh(today=TODAY)
    flag.refresh_from_db()
    assert flag.status == Flag.RESOLVED


def test_a_dropout_without_follow_up_and_no_other_flags_for_children_who_left(world):
    reg = world['register']()
    attendance(world, 'PPPAAAA', reg)
    m.Referral.objects.create(registration=reg, recommended_learning_path='Drop out',
                              dropout_date=datetime.date(2025, 5, 20))
    engine.refresh(today=TODAY)
    assert flags(registration=reg) == [Flag.DROPOUT_NO_FOLLOWUP]
    m.FollowUpService.objects.create(registration=reg, follow_up_type='Phone call',
                                     follow_up_result='Follow-up with parents')
    engine.refresh(today=TODAY)
    assert flags(registration=reg, status=Flag.OPEN) == []


def test_health_screening_and_protection_concern_without_referral(world):
    sam = world['register'](name='Sam')
    m.HealthNutritionService.objects.create(registration=sam, muac_malnutrition_screening='SAM (MUAC <11.5 cm)',
                                            development_delays_identified='Language/Communication')
    referred = world['register'](name='Referred')
    m.HealthNutritionService.objects.create(registration=referred,
                                            child_malnutrition_screening='MAM (MUAC >11.5 and <12.5 cm)')
    m.HealthNutritionReferral.objects.create(registration=referred, referred_malnutrition='Yes')
    concern = world['register'](name='Concern')
    m.PSSService.objects.create(registration=concern, child_protection_concern='Suicidal ideation')
    handled = world['register'](name='Handled')
    m.PSSService.objects.create(registration=handled, child_protection_concern='Nightmares')
    m.Referral.objects.create(registration=handled, referred_service='CP')
    engine.refresh(today=TODAY)
    h1 = Flag.objects.get(registration=sam, kind=Flag.MALNUTRITION_NO_REFERRAL)
    assert h1.urgent and sorted(flags(registration=sam)) == [Flag.MALNUTRITION_NO_REFERRAL, Flag.DELAY_NO_REFERRAL]
    assert flags(registration=referred) == []
    p1 = Flag.objects.get(registration=concern)
    assert p1.kind == Flag.PROTECTION_NO_REFERRAL and p1.urgent
    assert flags(registration=handled) == []


def test_no_learning_progress_between_tests(world):
    stuck = world['register'](name='Stuck')
    m.TarlAssessment.objects.create(registration=stuck, programme_type='TaRL',
                                    pre_test={'arabic_level_reached': ['Word'], 'math_level_reached': ['1-digit']},
                                    post_test={'arabic_level_reached': ['Word'], 'math_level_reached': ['Beginner']})
    learning = world['register'](name='Learning')
    m.TarlAssessment.objects.create(registration=learning, pre_test={'arabic_level_reached': 'Word'},
                                    mid_test={'arabic_level_reached': 'Story'})
    top = world['register'](name='Top')
    m.TarlAssessment.objects.create(registration=top, pre_test={'math_level_reached': 'Division'},
                                    post_test={'math_level_reached': 'Division'})
    scored = world['register'](name='Scored')
    m.EducationProgrammeWLAssessment.objects.create(
        registration=scored, programme_type='BLN Level 1',
        pre_test={'english_letter_sound': 5, 'english_dictation': 3},
        post_test={'english_letter_sound': 4, 'english_dictation': 3})
    engine.refresh(today=TODAY)
    flag = Flag.objects.get(registration=stuck)
    assert flag.kind == Flag.NO_LEARNING_GAIN and flag.evidence['subjects'] == ['arabic', 'math']
    assert flags(registration=learning) == [] and flags(registration=top) == []
    assert flags(registration=scored) == [Flag.NO_LEARNING_GAIN]
    assert CenterSummary.objects.get().figures['learning'] == {'assessed': 3, 'no_progress': 2}


# ------------------------------------------------------------------------------------ follow-up
def test_a_followed_up_flag_returns_only_with_new_absences(world):
    reg = world['register'](have_labour='Yes - Morning')  # a working child: priority
    attendance(world, 'PPPPAAA', reg)
    engine.refresh(today=TODAY)
    flag = Flag.objects.get(registration=reg)
    assert flag.priority
    flag.status, flag.followed_up_on, flag.result = Flag.FOLLOWED_UP, TODAY, 'reached_returning'
    flag.save()
    engine.refresh(today=TODAY)  # same data: stays closed
    assert Flag.objects.filter(registration=reg).count() == 1
    later = TODAY + datetime.timedelta(days=3)
    sheet(world['center'], later, {reg: 'No'}, world['round'])
    engine.refresh(today=later)  # still absent after the follow-up: a new flag (and now low attendance too)
    assert sorted(flags(registration=reg, status=Flag.OPEN)) == [Flag.ABSENCE_STREAK, Flag.LOW_ATTENDANCE]


def test_a_followed_up_protection_flag_returns_only_with_a_new_record(world):
    reg = world['register']()
    m.PSSService.objects.create(registration=reg, child_protection_concern='Distress')
    engine.refresh(today=TODAY)
    Flag.objects.filter(registration=reg).update(status=Flag.FOLLOWED_UP, followed_up_on=TODAY, result='referred')
    engine.refresh(today=TODAY + datetime.timedelta(days=1))
    assert flags(registration=reg, status=Flag.OPEN) == []
    m.PSSService.objects.create(registration=reg, child_protection_concern='Isolation')
    engine.refresh(today=TODAY + datetime.timedelta(days=2))
    assert flags(registration=reg, status=Flag.OPEN) == [Flag.PROTECTION_NO_REFERRAL]


# ----------------------------------------------------------------------------------------- API
def api_client(group='NeuroDB API'):
    u = get_user_model().objects.create_user(username='api-' + group.replace(' ', ''), password='x-' + group)
    u.groups.add(Group.objects.get_or_create(name=group)[0])
    client = APIClient()
    client.force_authenticate(u)
    return client


def test_neurodb_reads_flags_by_registration_number_without_names(world):
    reg = world['register'](name='Secret')
    attendance(world, 'PPPPAAA', reg)
    m.PSSService.objects.create(registration=reg, child_protection_concern='Distress')
    engine.refresh(today=TODAY)
    client = api_client()
    data = client.get('/api/wellbeing/flags/', {'limit': 1}).json()
    assert len(data['flags']) == 1 and data['next_after'] == data['flags'][0]['id']
    assert data['settings']['absence_streak'] == 3 and data['kinds']['A1']
    rest = client.get('/api/wellbeing/flags/', {'after': data['next_after']}).json()
    flags_ = data['flags'] + rest['flags']
    assert {f['kind'] for f in flags_} == {'A1', 'P1'} and rest['next_after'] is None
    first = flags_[0]
    assert first['registration'] == reg.id and first['bma_path'] == '/mscc/child-profile/%s/' % reg.id
    age = engine._age_band(reg.child, datetime.date.today())  # an age band, never the date of birth
    assert first['child'] == {'gender': 'Female', 'age_band': age, 'nationality': 'Syrian'}
    assert b'Secret' not in client.get('/api/wellbeing/flags/').content
    later = client.get('/api/wellbeing/flags/', {'modified_since': '2999-01-01T00:00:00'}).json()
    assert later['flags'] == []
    assert client.get('/api/wellbeing/flags/', {'modified_since': 'yesterday'}).status_code == 400


def test_neurodb_records_a_follow_up(world):
    reg = world['register']()
    m.PSSService.objects.create(registration=reg, child_protection_concern='Distress')
    engine.refresh(today=TODAY)
    flag = Flag.objects.get(registration=reg)
    client = api_client()
    url = '/api/wellbeing/flags/%s/follow-up/' % flag.pk
    bad = client.post(url, {'follow_up_type': 'Phone call', 'result': 'nope', 'followed_up_on': '2025-06-01',
                            'by': 'A. Officer'}, format='json')
    assert bad.status_code == 400
    ok = client.post(url, {'follow_up_type': 'Phone call', 'result': 'referred',
                           'followed_up_on': TODAY.isoformat(), 'note': 'Called the mother', 'by': 'A. Officer'},
                     format='json')
    assert ok.status_code == 200 and ok.json()['flag']['follow_up']['by'] == 'A. Officer'
    flag.refresh_from_db()
    assert flag.status == Flag.FOLLOWED_UP and flag.result == 'referred'
    again = client.post(url, {'follow_up_type': 'Phone call', 'result': 'referred',
                              'followed_up_on': TODAY.isoformat(), 'by': 'B'}, format='json')
    assert again.status_code == 409


def test_neurodb_reads_centre_summaries(world):
    reg = world['register']()
    attendance(world, 'PPPPAAA', reg)
    engine.refresh(today=TODAY)
    data = api_client().get('/api/wellbeing/summaries/').json()
    assert data['month'] == '2025-05-01' and data['months'] == ['2025-05-01']
    row = data['summaries'][0]
    assert row['center']['name'] == 'Center A' and row['figures']['flags']['children_flagged'] == 1


def test_only_the_neurodb_service_account_uses_the_api(world):
    assert APIClient().get('/api/wellbeing/flags/').status_code in (401, 403)
    assert api_client('MSCC_UNICEF').get('/api/wellbeing/summaries/').status_code == 403


# --------------------------------------------------------------------------------------- back-test
def test_the_backtest_counts_children_warned_before_they_left(world):
    left = world['register'](name='Left')
    stayed = world['register'](name='Stayed')
    pattern_left = 'P' * 25 + 'A' * 6
    for day, mark in zip(days_back(len(pattern_left)), pattern_left):
        sheet(world['center'], day, {left: 'Yes' if mark == 'P' else 'No', stayed: 'Yes'}, world['round'])
    m.Referral.objects.create(registration=left, recommended_learning_path='Drop out', dropout_date=TODAY)
    result = backtest.run(world['round'], every=1)
    assert result['left_recorded_dropout'] == 1 and result['left_and_flagged_before'] == 1
    assert result['flagged'] == 1 and result['flagged_and_stayed'] == 0
    assert result['median_days_of_warning'] >= 0


def test_neurodb_asks_for_a_calculation_and_follows_it(world, django_capture_on_commit_callbacks):
    from unittest import mock

    from student_registration.wellbeing import runs
    from student_registration.wellbeing.models import WellbeingRun

    attendance(world, 'PPPPPPPAAA', world['register']())
    client = api_client()
    with mock.patch('student_registration.wellbeing.tasks.run_wellbeing.delay') as queued, \
            django_capture_on_commit_callbacks(execute=True):
        response = client.post('/api/wellbeing/runs/', {}, format='json')
        assert response.status_code == 202 and response.json()['status'] == 'queued'
        run_id = response.json()['id']
        again = client.post('/api/wellbeing/runs/', {'center': world['center'].id}, format='json')
        assert again.status_code == 200 and again.json()['id'] == run_id  # one calculation at a time
    queued.assert_called_once_with(run_id)
    runs.execute(run_id)  # what the worker does
    status = client.get('/api/wellbeing/runs/%s/' % run_id).json()
    assert status['status'] == 'succeeded' and status['finished_at'] and 'totals' in status
    assert client.get('/api/wellbeing/runs/999999/').status_code == 404
    assert client.post('/api/wellbeing/runs/', {'center': 'x'}, format='json').status_code == 400
    assert WellbeingRun.objects.get(pk=run_id).requested_by


def test_a_failed_calculation_is_reported_and_a_lost_run_does_not_block(world):
    import datetime
    from unittest import mock

    from django.utils import timezone

    from student_registration.wellbeing import runs
    from student_registration.wellbeing.models import WellbeingRun

    with mock.patch('student_registration.wellbeing.tasks.run_wellbeing.delay'):
        run, created = runs.start([], 'neurodb')
    with mock.patch('student_registration.wellbeing.engine.refresh', side_effect=RuntimeError('db gone')):
        runs.execute(run.pk)
    run.refresh_from_db()
    assert created and run.status == WellbeingRun.FAILED and 'RuntimeError: db gone' in run.error

    with mock.patch('student_registration.wellbeing.tasks.run_wellbeing.delay'):
        stuck, _ = runs.start([], 'neurodb')
        WellbeingRun.objects.filter(pk=stuck.pk).update(
            status=WellbeingRun.RUNNING, requested_at=timezone.now() - datetime.timedelta(hours=4)
        )
        fresh, created = runs.start([], 'neurodb')
    assert created and fresh.pk != stuck.pk
    assert WellbeingRun.objects.get(pk=stuck.pk).status == WellbeingRun.FAILED
