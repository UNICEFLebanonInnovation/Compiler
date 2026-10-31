"""Education figures for NeuroDB: unique children per grouping, stored snapshots, service access."""

import datetime
from unittest import mock

import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from student_registration.attendances.models import (
    CLMAttendance,
    CLMAttendanceStudent,
    MSCCAttendance,
    MSCCAttendanceChild,
)
from student_registration.child.models import Child
from student_registration.clm.models import Bridging, Disability
from student_registration.figures import education, engine, snapshots
from student_registration.figures.models import FiguresSnapshot
from student_registration.locations.models import Center, Location, LocationType, ProgramStaff
from student_registration.mscc import models as m
from student_registration.schools.models import CLMRound, PartnerOrganization, School
from student_registration.students.models import Nationality, Student, Teacher

pytestmark = pytest.mark.django_db


def table(block, *by):
    grouping = next(g for g in block['figures'] if g['by'] == sorted(by))
    return {tuple(row[:len(by)]): row[len(by):] for row in grouping['rows']}


@pytest.fixture
def places():
    gov = LocationType.objects.create(name='Governorate')
    district = LocationType.objects.create(name='District')
    akkar = Location.objects.create(name='Akkar', p_code='LB1', type=gov)
    beirut = Location.objects.create(name='Beirut', p_code='LB6', type=gov)
    halba = Location.objects.create(name='Halba', p_code='LB11', type=district, parent=akkar)
    return {'akkar': akkar, 'beirut': beirut, 'halba': halba,
            'syrian': Nationality.objects.create(name='Syrian', name_en='Syrian'),
            'no': Disability.objects.create(name='No', name_en='No', active=True)}


@pytest.fixture
def makani(places):
    partner = PartnerOrganization.objects.create(name='Makani Partner', is_makani=True)
    other = PartnerOrganization.objects.create(name='Other Partner', is_makani=True)
    current = m.Round.objects.create(name='Round 1 2025', year=2025, current_year=True,
                                     start_date=datetime.date(2025, 1, 1))
    old = m.Round.objects.create(name='Round 1 2024', year=2024)
    center = Center.objects.create(name='Center A', partner=partner, governorate=places['akkar'],
                                   caza=places['halba'], type='Community Hub')
    center_b = Center.objects.create(name='Center B', partner=other, governorate=places['beirut'])

    def child(gender, born):
        return Child.objects.create(first_name='Secret', gender=gender, birthday_year=str(born),
                                    nationality=places['syrian'], disability=places['no'])

    girl, boy, other_girl = child('Female', 2016), child('Male', 2012), child('Female', 2008)
    reg = lambda c, **kw: m.Registration.objects.create(child=c, **kw)  # noqa: E731
    r_girl = reg(girl, partner=partner, center=center, round=current, type='Core-Package')
    reg(girl, partner=other, center=center_b, round=current, type='Walk-in')  # same child, second partner
    r_boy = reg(boy, partner=partner, center=center, round=None, type='Core-Package')  # no round yet
    reg(other_girl, partner=other, center=center_b, round=old)  # another year
    reg(other_girl, partner=partner, center=center, round=current, deleted=True)  # deleted: never counts
    m.EducationService.objects.create(registration=r_girl, education_program='BLN Level 1', round=current)
    m.EducationService.objects.create(registration=r_boy, education_program='ABLN', round=current)
    m.PSSService.objects.create(registration=r_girl)
    m.PSSService.objects.create(registration=r_girl)  # twice: one child
    ProgramStaff.objects.create(facilitator_name='F', center=center, gender='Female', is_active_current_round='Yes')
    day = MSCCAttendance.objects.create(round_id=current.id, center=center, education_program='BLN Level 1',
                                        attendance_date=datetime.date(2025, 3, 3), day_off='no')
    MSCCAttendanceChild.objects.create(attendance_day=day, registration=r_girl, child=girl, attended='Yes')
    MSCCAttendanceChild.objects.create(attendance_day=day, registration=r_boy, child=boy, attended='No')
    return {'partner': partner, 'other': other, 'center': center, 'current': current}


@pytest.fixture
def bridging(places):
    partner = PartnerOrganization.objects.create(name='Dirasa Partner', is_dirasa=True)
    the_round = CLMRound.objects.create(name='Bridging 2025', current_round_bridging=True,
                                        start_date_bridging=datetime.date(2025, 9, 1))
    school = School.objects.create(number='1001', name='School A', governorate=places['akkar'])
    partner.schools.add(school)

    def student(sex, born):
        return Student.objects.create(first_name='Secret', sex=sex, birthday_year=str(born),
                                      nationality=places['syrian'])

    a, b = student('Female', 2014), student('Male', 2011)
    reg = Bridging.objects.create(student=a, round=the_round, partner=partner, school=school,
                                  governorate=places['akkar'], district=places['halba'],
                                  registration_level='level_one', pre_test={'score': 10},
                                  receiving_transportation_support='yes', using_digital_platform='yes_akelius)')
    Bridging.objects.create(student=b, round=the_round, partner=partner, school=school,
                            governorate=places['akkar'], registration_level='level_two',
                            learning_result='dropout', receiving_transportation_support='no')
    Bridging.objects.create(student=b, round=the_round, partner=partner, deleted=True)
    Teacher.objects.create(first_name='T', sex='Male', round=the_round, school=school,
                           is_active_current_round='yes')
    day = CLMAttendance.objects.create(round_id=the_round.id, school=school, registration_level='level_one',
                                       attendance_date=datetime.date(2025, 10, 6), day_off='no')
    CLMAttendanceStudent.objects.create(attendance_day=day, registration=reg, student=a, attended='yes')
    return {'partner': partner, 'round': the_round, 'school': school}


def test_groupings_combine_main_dimensions_with_one_detail():
    found = engine.groupings(('a', 'b'), ('c', 'd'), extra=(('d', 'c'), ('a',)))
    assert found[0] == () and ('a', 'b', 'd') in found and ('c', 'd') in found
    assert len(found) == len(set(found)) == 4 * 3 + 1


def test_makani_counts_unique_children_of_the_year(makani, places):
    payload = education.PROGRAMMES['mscc'].build('2025')
    registrations = payload['blocks']['registrations']
    assert table(registrations)[()] == [2]  # the girl (two partners) once, the boy without a round
    assert table(registrations, 'partner') == {(makani['partner'].id,): [2], (makani['other'].id,): [1]}
    assert table(registrations, 'governorate') == {(places['akkar'].id,): [2], (places['beirut'].id,): [1]}
    assert table(registrations, 'age_group', 'sex') == {('6-9', 'Female'): [1], ('10-14', 'Male'): [1]}
    services = payload['blocks']['services']
    assert table(services, 'service') == {('Child protection (PSS)',): [1], ('Education',): [2]}
    assert table(payload['blocks']['education_programmes'], 'education_programme') == {
        ('ABLN',): [1], ('BLN Level 1',): [1]}
    assert table(payload['blocks']['sites'])[()] == [2]
    assert table(payload['blocks']['staff'], 'sex') == {('Female',): [1]}
    attendance = payload['blocks']['attendance']
    assert attendance['measures'] == ['days_recorded', 'days_attended']
    assert table(attendance, 'month') == {('2025-03',): [2, 1]}

    older = education.PROGRAMMES['mscc'].build('2024')
    assert table(older['blocks']['registrations'])[()] == [1]  # the round-less child is not in 2024


def test_bridging_counts_children_tests_services_and_teachers(bridging):
    payload = education.PROGRAMMES['bridging'].build('Bridging 2025')
    registrations = payload['blocks']['registrations']
    assert registrations['measures'] == ['people', 'pre_tested', 'post_tested']
    assert table(registrations)[()] == [2, 1, 0]
    assert table(registrations, 'learning_result') == {('dropout',): [1, 0, 0], ('in_progress',): [1, 1, 0]}
    assert table(payload['blocks']['services'], 'service') == {
        ('Digital platform',): [1], ('Transportation support',): [1]}
    assert table(payload['blocks']['staff'], 'partner') == {(bridging['partner'].id,): [1]}
    assert table(payload['blocks']['attendance'])[()] == [1, 1]
    assert payload['sites'][0]['name'] == 'School A'


def test_payloads_hold_no_personal_data(makani, bridging):
    for name, year in (('mscc', '2025'), ('bridging', 'Bridging 2025')):
        text = str(education.PROGRAMMES[name].build(year))
        assert 'Secret' not in text and 'first_name' not in text


def test_a_failing_block_does_not_stop_the_others(makani):
    real = engine.figures_block

    def flaky(sql, params, dimensions, grouping_list, measures=engine.PEOPLE):
        if 'days_recorded' in [m for m, _ in measures]:
            raise RuntimeError('canceling statement due to statement timeout')
        return real(sql, params, dimensions, grouping_list, measures)

    with mock.patch.object(engine, 'figures_block', side_effect=flaky):
        payload = education.PROGRAMMES['mscc'].build('2025')
    assert payload['blocks']['attendance']['error'] == 'RuntimeError'
    assert table(payload['blocks']['registrations'])[()] == [2]


def _service_client():
    client = APIClient()
    service = get_user_model().objects.create_user(username='neurodb', password='x-pass-123456')
    service.groups.add(Group.objects.get_or_create(name='NeuroDB API')[0])
    client.credentials(HTTP_AUTHORIZATION='Token ' + Token.objects.create(user=service).key)
    return client


def test_the_api_serves_snapshots_and_never_counts_on_its_own(makani):
    client = _service_client()
    with mock.patch('student_registration.figures.tasks.run_figures.delay') as queued, \
            mock.patch.object(education.Makani, 'build', side_effect=AssertionError('counted in a request')):
        response = client.get('/api/figures/mscc/')
        assert response.status_code == 404 and 'POST /api/figures/runs/' in response.json()['detail']
        assert queued.call_count == 0  # reading never starts a count: NeuroDB decides when
    assert client.get('/api/figures/unknown/').status_code == 404
    assert client.get('/api/figures/mscc/', {'year': '1999'}).status_code == 404

    snapshots.refresh('mscc')
    response = client.get('/api/figures/mscc/')
    assert response.status_code == 200
    assert response.json()['year'] == '2025' and response.json()['counted_at']
    index = client.get('/api/figures/').json()['programmes']
    assert {p['programme'] for p in index} == {'mscc', 'bridging'}

    FiguresSnapshot.objects.update(created_at=datetime.datetime(2020, 1, 1, tzinfo=datetime.timezone.utc))
    with mock.patch('student_registration.figures.tasks.run_figures.delay') as queued:
        assert client.get('/api/figures/mscc/').status_code == 200  # an old one is served as it is
        assert queued.call_count == 0


def test_neurodb_asks_for_a_count_and_follows_it(makani, django_capture_on_commit_callbacks):
    from student_registration.figures.models import FiguresRun

    client = _service_client()
    with mock.patch('student_registration.figures.tasks.run_figures.delay') as queued, \
            django_capture_on_commit_callbacks(execute=True):
        response = client.post('/api/figures/runs/', {}, format='json')
        assert response.status_code == 202 and response.json()['status'] == 'queued'
        run_id = response.json()['id']
        assert sorted(t[0] for t in response.json()['targets']) == ['bridging', 'mscc']
        again = client.post('/api/figures/runs/', {'programme': 'mscc'}, format='json')
        assert again.status_code == 200 and again.json()['id'] == run_id  # one count at a time
    queued.assert_called_once_with(run_id)
    snapshots.execute_run(run_id)  # what the worker does
    status = client.get('/api/figures/runs/%s/' % run_id).json()
    assert status['status'] == 'succeeded' and status['finished_at']
    assert {c[0] for c in status['counted']} == {'mscc'}
    assert 'bridging current: no such year' in status['error']  # no Bridging round in this data
    assert client.get('/api/figures/mscc/').status_code == 200
    assert client.get('/api/figures/runs/999999/').status_code == 404
    assert client.post('/api/figures/runs/', {'programme': 'nope'}, format='json').status_code == 400
    assert client.post('/api/figures/runs/', {'year': '2025'}, format='json').status_code == 400
    assert FiguresRun.objects.get(pk=run_id).requested_by == 'neurodb'


def test_a_failed_count_is_reported_and_a_lost_run_does_not_block(makani):
    from student_registration.figures.models import FiguresRun

    with mock.patch('student_registration.figures.tasks.run_figures.delay'):
        run, created = snapshots.start_run([('mscc', None)], 'neurodb')
    assert created
    with mock.patch.object(snapshots, 'refresh', side_effect=RuntimeError('database gone')):
        snapshots.execute_run(run.pk)
    run.refresh_from_db()
    assert run.status == FiguresRun.FAILED and 'RuntimeError: database gone' in run.error

    with mock.patch('student_registration.figures.tasks.run_figures.delay'):
        stuck, _ = snapshots.start_run([('mscc', None)], 'neurodb')
        FiguresRun.objects.filter(pk=stuck.pk).update(
            status=FiguresRun.RUNNING,
            requested_at=datetime.datetime(2020, 1, 1, tzinfo=datetime.timezone.utc),
        )
        fresh, created = snapshots.start_run([('mscc', None)], 'neurodb')
    assert created and fresh.pk != stuck.pk
    assert FiguresRun.objects.get(pk=stuck.pk).status == FiguresRun.FAILED


def test_only_the_service_account_reads(makani):
    client = APIClient()
    assert client.get('/api/figures/mscc/').status_code in (401, 403)
    partner_user = get_user_model().objects.create_user(username='partner', password='x-pass-123456')
    client.credentials(HTTP_AUTHORIZATION='Token ' + Token.objects.create(user=partner_user).key)
    assert client.get('/api/figures/mscc/').status_code == 403
    assert client.get('/api/figures/').status_code == 403


def test_a_snapshot_of_an_older_format_is_counted_again(makani):
    snapshot = snapshots.refresh('mscc')
    assert not snapshots.is_stale(snapshot)
    FiguresSnapshot.objects.filter(pk=snapshot.pk).update(payload=dict(snapshot.payload, format=1))
    assert snapshots.is_stale(snapshots.latest('mscc', '2025'))  # counted before the upgrade, however recent
    FiguresSnapshot.objects.filter(pk=snapshot.pk).update(payload={'year': '2025'})
    assert snapshots.is_stale(snapshots.latest('mscc', '2025'))


def test_refresh_keeps_the_last_three_snapshots(makani):
    for _ in range(5):
        snapshots.refresh('mscc')
    assert FiguresSnapshot.objects.filter(programme='mscc').count() == snapshots.KEEP


# ------------------------------------------------------------------------------------ cubes
def records(cube, **where):
    """The rows of ``cube`` as dicts, those matching ``where``."""
    names = cube['dims'] + cube['measures']
    rows = [dict(zip(names, row)) for row in cube['rows']]
    return [r for r in rows if all(r[k] == v for k, v in where.items())]


def total(cube, measure, **where):
    return sum(r[measure] for r in records(cube, **where))


def test_the_counting_cursor_is_read_only_and_bounded():
    with engine.read_only_cursor() as cursor:
        cursor.execute('SHOW transaction_read_only')
        assert cursor.fetchone()[0] == 'on'
        cursor.execute('SHOW max_parallel_workers_per_gather')
        assert cursor.fetchone()[0] == '0'
    with pytest.raises(ValueError):
        engine.cube('SELECT 1 AS a', [], (), (('n', 'COUNT(*)'),))


def test_makani_enrolment_cube_adds_up_to_the_registrations(makani, places):
    payload = education.PROGRAMMES['mscc'].build('2025')
    assert payload['format'] == 2
    enrolment = payload['cubes']['enrolment']
    assert enrolment['dims'] == list(education.Makani.ENROLMENT)
    assert enrolment['measures'] == ['registrations', 'married', 'idp', 'counselling', 'immunized', 'screened',
                                     'minimum_meals', 'vaccinated']
    # three registrations of the year (the girl twice), where the unique count says two children
    assert total(enrolment, 'registrations') == 3
    assert table(payload['blocks']['registrations'])[()] == [2]
    assert total(enrolment, 'registrations', partner=makani['partner'].id) == 2
    assert total(enrolment, 'registrations', governorate=places['beirut'].id) == 1
    assert total(enrolment, 'registrations', sex='Female') == 2
    assert total(enrolment, 'registrations', package='Walk-in') == 1
    assert total(enrolment, 'registrations', programme='ABLN') == 1
    assert total(enrolment, 'registrations', programme=None) == 1  # the second partner's: no education record
    assert all(isinstance(v, int) for row in enrolment['rows'] for v in row[len(enrolment['dims']):])
    assert enrolment['rows'] == sorted(enrolment['rows'], key=lambda r: tuple('' if v is None else str(v) for v in r))
    # the old lists are still there, the new lookups cover the cubes
    assert {'blocks', 'sites', 'rounds', 'partners', 'locations', 'nationalities', 'disabilities'} <= set(payload)
    assert {p['id'] for p in payload['partners']} == {makani['partner'].id, makani['other'].id}
    assert {n['id'] for n in payload['nationalities']} == {places['syrian'].id}


def test_makani_uses_the_latest_education_and_health_records(makani):
    registration = m.Registration.objects.get(partner=makani['partner'], round=makani['current'], deleted=False)
    m.EducationService.objects.create(registration=registration, education_program='BLN Level 2',
                                      education_status='Never registered in any formal school before',
                                      round=makani['current'])
    health = m.HealthNutritionService.objects.create
    older = health(registration=registration, muac_malnutrition_screening='SAM (MUAC <11.5 cm)',
                   child_vaccinated='No', caregiver_counselling='Yes',
                   development_delays_identified='Social/Emotional')
    health(registration=registration, muac_malnutrition_screening='',
           child_malnutrition_screening='No malnutrition screening', child_vaccinated='Yes',
           eating_minimum_meals='yes', development_delays_identified='No', immunization_record_screened='No',
           child_immunization_screened='Yes', caregiver_counselling='No')
    # the latest is the highest id, even when an older record was edited after it
    edited = datetime.datetime(2030, 1, 1, tzinfo=datetime.timezone.utc)
    m.HealthNutritionService.objects.filter(pk=older.pk).update(created=edited, modified=edited)
    m.EducationService.objects.filter(registration=registration, education_program='BLN Level 1').update(
        created=edited, modified=edited)
    enrolment = education.PROGRAMMES['mscc'].build('2025')['cubes']['enrolment']
    [row] = records(enrolment, partner=makani['partner'].id, sex='Female')
    assert row['programme'] == 'BLN Level 2'
    assert row['education_status'] == 'Never registered in any formal school before'
    assert row['malnutrition'] == 'No malnutrition screening' and row['delay'] == 'No'
    assert (row['counselling'], row['immunized'], row['screened'], row['minimum_meals'], row['vaccinated']) == (
        1, 1, 1, 1, 1)  # counselling: any record; the others: the latest record
    assert total(enrolment, 'screened') == 1 and total(enrolment, 'vaccinated') == 1
    assert records(enrolment, malnutrition='SAM (MUAC <11.5 cm)') == []


def test_makani_normalises_the_slicers_and_lists_the_centers(makani, places):
    from student_registration.students.models import IDType

    unhcr = IDType.objects.create(name='UNHCR Registered', active=True)
    Child.objects.filter(gender='Female', birthday_year='2016').update(
        main_caregiver='mother', marital_status='married', id_type=unhcr)
    Child.objects.filter(gender='Male').update(main_caregiver='FATHER')
    m.Registration.objects.filter(partner=makani['partner'], child__gender='Female').update(
        have_labour='Yes - Morning', child_is_idp='yes')
    m.Registration.objects.filter(partner=makani['other'], round=makani['current']).update(have_labour='No')
    m.Registration.objects.filter(child__gender='Male').update(have_labour='yes_all_day')
    Center.objects.filter(pk=makani['center'].pk).update(active_during_emergency='yes', latitude=34.5,
                                                          longitude=36.1, is_active=True)
    Center.objects.filter(name='Center B').update(active_during_emergency='NO', latitude=0, longitude=0)

    payload = education.PROGRAMMES['mscc'].build('2025')
    enrolment = payload['cubes']['enrolment']
    assert total(enrolment, 'registrations', caregiver='Mother') == 2
    assert total(enrolment, 'registrations', caregiver='Father') == 1
    assert total(enrolment, 'registrations', working='Yes') == 2  # 'Yes - Morning' and the old 'yes_all_day'
    assert total(enrolment, 'registrations', working='No') == 1
    assert total(enrolment, 'married') == 2 and total(enrolment, 'idp') == 1
    assert total(enrolment, 'registrations', id_type=unhcr.id) == 2
    assert payload['id_types'] == [{'id': unhcr.id, 'name': 'UNHCR Registered'}]
    centers = {c['id']: c for c in payload['centers']}
    a, b = centers[makani['center'].id], centers[Center.objects.get(name='Center B').id]
    assert set(a) == {'id', 'name', 'partner', 'governorate', 'district', 'cadaster', 'type', 'emergency',
                      'is_active', 'latitude', 'longitude'}
    assert (a['emergency'], a['latitude'], a['longitude'], a['is_active']) == ('Yes', 34.5, 36.1, True)
    assert (b['emergency'], b['latitude'], b['longitude']) == ('No', None, None)
    assert (a['partner'], a['governorate'], a['district'], a['type']) == (
        makani['partner'].id, places['akkar'].id, places['halba'].id, 'Community Hub')
    assert {loc['id'] for loc in payload['locations']} >= {places['akkar'].id, places['beirut'].id,
                                                           places['halba'].id}


def test_makani_staff_cube(makani, places):
    center_b = Center.objects.get(name='Center B')
    ProgramStaff.objects.create(facilitator_name='G', center=center_b, gender='Male', is_active_current_round='no')
    ProgramStaff.objects.create(facilitator_name='H', center=center_b, gender='Male')
    ProgramStaff.objects.create(facilitator_name='No center', gender='Male')  # not counted
    staff = education.PROGRAMMES['mscc'].build('2025')['cubes']['staff']
    assert staff['dims'] == ['center', 'partner', 'governorate', 'sex', 'active'] and staff['measures'] == ['staff']
    assert sorted(staff['rows'], key=str) == sorted([
        [makani['center'].id, makani['partner'].id, places['akkar'].id, 'Female', 'Yes', 1],
        [center_b.id, makani['other'].id, places['beirut'].id, 'Male', 'No', 1],
        [center_b.id, makani['other'].id, places['beirut'].id, 'Male', 'Not specified', 1],
    ], key=str)


@pytest.fixture
def dirasa_more(bridging, places):
    """A second school with teachers only, listed by a Dirasa partner and a non-Dirasa one; topics."""
    from student_registration.students.models import Training

    other = PartnerOrganization.objects.create(name='Second Dirasa Partner', is_dirasa=True)
    not_dirasa = PartnerOrganization.objects.create(name='Not Dirasa', is_dirasa=False)
    school_b = School.objects.create(number='1002', name='School B', governorate=places['beirut'],
                                     type='Private Free School', latitude=33.9, longitude=35.5)
    other.schools.add(school_b)
    not_dirasa.schools.add(school_b)
    School.objects.filter(pk=bridging['school'].pk).update(
        type='Private School', active_during_emergency='yes', number_children=100, number_children_male=40,
        number_children_female=60, number_children_lebanese=30, number_children_non_lebanese=70,
        number_children_sbp=12, number_total_children_disability=5, number_dirasa_children_disability=2)
    digital, sel = Training.objects.create(name='Digital Literacy'), Training.objects.create(name='SEL')
    Teacher.objects.get(round=bridging['round']).trainings.add(digital)
    teacher = Teacher.objects.create(first_name='Secret', sex='Female', round=bridging['round'], school=school_b)
    teacher.trainings.add(digital, sel)
    Bridging.objects.filter(student__sex='Female').update(barriers_single='family_moved')
    Bridging.objects.filter(student__sex='Male').update(barriers_single='')
    return {'school_b': school_b, 'other': other, 'digital': digital, 'sel': sel}


def test_bridging_cubes_schools_and_trainings(bridging, dirasa_more, places):
    payload = education.PROGRAMMES['bridging'].build('Bridging 2025')
    assert payload['format'] == 2
    enrolment = payload['cubes']['enrolment']
    assert enrolment['dims'] == list(education.Bridging.ENROLMENT)
    assert enrolment['measures'] == ['registrations', 'pre_tested', 'post_tested']
    assert total(enrolment, 'registrations') == 2 and total(enrolment, 'pre_tested') == 1
    assert total(enrolment, 'registrations', learning_result='in_progress') == 1
    assert total(enrolment, 'registrations', level='level_two', sex='Male', learning_result='dropout') == 1
    assert total(enrolment, 'registrations', barrier='family_moved') == 1
    assert total(enrolment, 'registrations', barrier=None) == 1
    school_a, school_b = bridging['school'].id, dirasa_more['school_b'].id

    assert payload['cubes']['teachers']['rows'] == sorted([[school_a, 'Male', 1], [school_b, 'Female', 1]], key=str)
    trainings = payload['cubes']['trainings']
    assert trainings['dims'] == ['school', 'sex', 'training'] and trainings['measures'] == ['teachers']
    assert total(trainings, 'teachers', training=dirasa_more['digital'].id) == 2
    assert total(trainings, 'teachers', training=dirasa_more['sel'].id, sex='Female') == 1
    assert {t['name'] for t in payload['trainings']} == {'Digital Literacy', 'SEL'}

    schools = {s['id']: s for s in payload['schools']}
    assert set(schools) == {school_a, school_b}
    a, b = schools[school_a], schools[school_b]
    assert set(a) == {'id', 'name', 'number', 'type', 'governorate', 'district', 'emergency', 'latitude',
                      'longitude', 'partners', 'counts'}
    assert a['partners'] == [bridging['partner'].id]  # registered children there
    assert b['partners'] == [dirasa_more['other'].id]  # no children: the Dirasa partners listing it
    assert a['counts'] == {'children': 100, 'children_male': 40, 'children_female': 60, 'children_lebanese': 30,
                           'children_non_lebanese': 70, 'cwd': 5, 'dirasa_children': 12, 'dirasa_cwd': 2}
    assert b['counts']['children'] is None
    assert (a['emergency'], a['type'], a['latitude']) == ('Yes', 'Private School', None)
    assert (b['emergency'], b['type'], b['latitude'], b['longitude']) == (
        'Not specified', 'Private Free School', 33.9, 35.5)
    assert {p['id'] for p in payload['partners']} >= {bridging['partner'].id, dirasa_more['other'].id}
    assert places['beirut'].id in {loc['id'] for loc in payload['locations']}  # school B's governorate


def test_outreach_cubes_merge_spellings_and_read_the_year(bridging):
    from student_registration.outreach.models import OutreachCaregiver, OutreachChild

    first = OutreachCaregiver.objects.create(
        father_name='Secret', partner_name=' Partner X ', governorate='Akkar',
        interview_date='2024-05-01T10:00:00', id_type='UNHCR registered')
    second = OutreachCaregiver.objects.create(partner_name='Partner X', governorate='Akkar',
                                              interview_date='2025-01-02', id_type='unhcr_registered')
    undated = OutreachCaregiver.objects.create(interview_date='', id_type='No_papers', partner_name='')
    OutreachChild.objects.create(outreach_caregiver=first, first_name='Secret', child_referral='Referred_to_Dirasa',
                                 education_status='Never been engaged in any type of learning',
                                 dropout_reason='family needs more income')
    OutreachChild.objects.create(outreach_caregiver=second, education_status='never_been_engaged_in_any_type_of_learni',
                                 child_referral='referred to Dirasa')
    OutreachChild.objects.create(outreach_caregiver=undated, education_status='  ')

    cubes = education.PROGRAMMES['bridging'].build('Bridging 2025')['outreach']['cubes']
    assert set(cubes) == {'education_status', 'referral', 'dropout_reason', 'id_type'}
    status = cubes['education_status']
    assert status['dims'] == ['year', 'partner', 'governorate', 'value'] and status['measures'] == ['children']
    key = 'never_been_engaged_in_any_type_of_learni'
    assert sorted(status['rows'], key=str) == sorted([
        ['2024', 'Partner X', 'Akkar', key, 1], ['2025', 'Partner X', 'Akkar', key, 1], [None, None, None, None, 1],
    ], key=str)
    assert total(cubes['referral'], 'children', value='referred_to_dirasa') == 2
    assert total(cubes['dropout_reason'], 'children', value='family_needs_more_income') == 1
    assert total(cubes['id_type'], 'children', value='unhcr_registered') == 2
    assert total(cubes['id_type'], 'children', value='no_papers', year=None) == 1


def test_outreach_keys_keep_their_length_after_leading_punctuation():
    from student_registration.outreach.models import OutreachCaregiver, OutreachChild

    caregiver = OutreachCaregiver.objects.create(interview_date='2025-03-01')
    for status in ('Never been engaged in any type of learning', '"Never been engaged in any type of learning"',
                   '- never_been_engaged_in_any_type_of_learni', '\tNever been engaged in any type of learning'):
        OutreachChild.objects.create(outreach_caregiver=caregiver, education_status=status)
    rows = education.outreach()['cubes']['education_status']['rows']
    assert rows == [['2025', None, None, 'never_been_engaged_in_any_type_of_learni', 4]]


def test_cubes_hold_no_personal_data(makani, bridging, dirasa_more):
    from student_registration.outreach.models import OutreachCaregiver, OutreachChild

    caregiver = OutreachCaregiver.objects.create(father_name='Secret', caregiver_first_name='Secret',
                                                 partner_name='Partner X', interview_date='2025-02-02')
    OutreachChild.objects.create(outreach_caregiver=caregiver, first_name='Secret', education_status='out')
    ProgramStaff.objects.create(facilitator_name='Secret', center=makani['center'], gender='Male')
    for name, year in (('mscc', '2025'), ('bridging', 'Bridging 2025')):
        payload = education.PROGRAMMES[name].build(year)
        assert payload['cubes'] and all(not c.get('error') for c in payload['cubes'].values())
        text = str(payload)
        assert 'Secret' not in text and 'first_name' not in text and 'birthday' not in text


def test_a_failing_cube_does_not_stop_the_others(makani, bridging):
    real = engine.cube

    def flaky(sql, params, dimensions, measures):
        if 'malnutrition' in dimensions or list(dimensions) == ['school', 'sex']:
            raise RuntimeError('canceling statement due to statement timeout')
        return real(sql, params, dimensions, measures)

    with mock.patch.object(engine, 'cube', side_effect=flaky):
        makani_payload = education.PROGRAMMES['mscc'].build('2025')
        bridging_payload = education.PROGRAMMES['bridging'].build('Bridging 2025')
    failed = makani_payload['cubes']['enrolment']
    assert failed['error'] == 'RuntimeError' and failed['rows'] == []
    assert failed['dims'] == list(education.Makani.ENROLMENT) and failed['measures'][0] == 'registrations'
    assert total(makani_payload['cubes']['staff'], 'staff') == 1
    assert table(makani_payload['blocks']['registrations'])[()] == [2]
    assert bridging_payload['cubes']['teachers']['error'] == 'RuntimeError'
    assert total(bridging_payload['cubes']['enrolment'], 'registrations') == 2
    assert 'error' not in bridging_payload['outreach']['cubes']['id_type']
