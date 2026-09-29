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


def test_the_api_serves_snapshots_and_never_counts_in_the_request(makani):
    client = APIClient()
    user_model = get_user_model()
    service = user_model.objects.create_user(username='neurodb', password='x-pass-123456')
    service.groups.add(Group.objects.create(name='NeuroDB API'))
    client.credentials(HTTP_AUTHORIZATION='Token ' + Token.objects.create(user=service).key)

    with mock.patch('student_registration.figures.tasks.refresh_figures.delay') as queued, \
            mock.patch.object(education.Makani, 'build', side_effect=AssertionError('counted in a request')):
        response = client.get('/api/figures/mscc/')
        assert response.status_code == 202 and queued.call_count == 1
        client.get('/api/figures/mscc/')
        assert queued.call_count == 1  # one count queued, not one per request
    assert client.get('/api/figures/unknown/').status_code == 404
    assert client.get('/api/figures/mscc/', {'year': '1999'}).status_code == 404

    snapshots.refresh('mscc')
    response = client.get('/api/figures/mscc/')
    assert response.status_code == 200
    assert response.json()['year'] == '2025' and response.json()['counted_at']
    index = client.get('/api/figures/').json()['programmes']
    assert {p['programme'] for p in index} == {'mscc', 'bridging'}

    FiguresSnapshot.objects.update(created_at=datetime.datetime(2020, 1, 1, tzinfo=datetime.timezone.utc))
    with mock.patch('student_registration.figures.snapshots.request_refresh') as refresh:
        assert client.get('/api/figures/mscc/').status_code == 200  # the old one, while a new one is counted
        refresh.assert_called_once_with('mscc', '2025')


def test_only_the_service_account_reads(makani):
    client = APIClient()
    assert client.get('/api/figures/mscc/').status_code in (401, 403)
    partner_user = get_user_model().objects.create_user(username='partner', password='x-pass-123456')
    client.credentials(HTTP_AUTHORIZATION='Token ' + Token.objects.create(user=partner_user).key)
    assert client.get('/api/figures/mscc/').status_code == 403
    assert client.get('/api/figures/').status_code == 403


def test_refresh_keeps_the_last_three_snapshots(makani):
    for _ in range(5):
        snapshots.refresh('mscc')
    assert FiguresSnapshot.objects.filter(programme='mscc').count() == snapshots.KEEP
