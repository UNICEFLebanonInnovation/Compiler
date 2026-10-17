"""The youth indicator figures for NeuroDB: unique youth per grouping, counts only, service access."""

import json
from unittest import mock

import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.db import connection
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from student_registration.adolescent.models import Adolescent
from student_registration.figures import power_bi, snapshots
from student_registration.figures.youth import Youth
from student_registration.locations.models import Location, LocationType
from student_registration.schools.models import PartnerOrganization
from student_registration.students.models import Nationality
from student_registration.youth import indicator_figures
from student_registration.youth.models import (
    Donor,
    EnrolledPrograms,
    MasterProgram,
    ProgramDocument,
    ProgramDocumentIndicator,
    Registration,
    SubProgram,
    Year,
)

URL = '/api/youth/indicator-figures/'


@pytest.fixture
def data(db):
    year = Year.objects.create(name='2026', current_year=True)
    gov_type = LocationType.objects.create(name='Governorate')
    district_type = LocationType.objects.create(name='District')
    akkar = Location.objects.create(name='Akkar', p_code='LB1', type=gov_type)
    beirut = Location.objects.create(name='Beirut', p_code='LB6', type=gov_type)
    halba = Location.objects.create(name='Halba', p_code='LB11', type=district_type, parent=akkar)
    syrian = Nationality.objects.create(name='Syrian', name_en='Syrian')
    partner = PartnerOrganization.objects.create(name='Youth Partner', is_youth=True)
    other_partner = PartnerOrganization.objects.create(name='Second Partner', is_youth=True)
    eu = Donor.objects.create(name='EU', active=True)
    japan = Donor.objects.create(name='Japan', active=True)
    skills = MasterProgram.objects.create(number='1', name='Skills', active=True)
    digital = SubProgram.objects.create(master_program=skills, number='1.1', name='Digital skills')
    life = SubProgram.objects.create(master_program=skills, number='1.2', name='Life skills')
    pd = ProgramDocument.objects.create(
        year=year, partner=partner, project_code='LEB/PCA2026001', project_name='Youth skills'
    )
    pd.donors.set([eu, japan])
    ProgramDocumentIndicator.objects.create(
        program_document=pd, master_indicator=skills, sub_indicator=digital, target=100
    )

    def youth(gender, born, gov=akkar, district=halba, deleted=False, reg_partner=partner):
        person = Adolescent.objects.create(
            first_name='x', gender=gender, birthday_year=str(born), nationality=syrian,
            governorate=gov, district=district,
        )
        return Registration.objects.create(
            year=year, adolescent=person, partner=reg_partner, deleted=deleted
        )

    def enrol(registration, sub, donor, **place):
        return EnrolledPrograms.objects.create(
            registration=registration, master_program=sub.master_program, sub_program=sub, donor=donor,
            program_document=pd, **place
        )

    a = youth('Female', 2008)  # 18 in 2026
    b = youth('Male', 2010)  # 16
    c = youth('Female', 2004, gov=beirut, district=None, reg_partner=other_partner)  # 22
    gone = youth('Male', 2009, deleted=True)
    enrol(a, digital, eu)  # "same location": the youth's address (Akkar, Halba)
    enrol(a, life, japan)  # a second sub indicator: still one youth for the master indicator
    enrol(a, digital, eu)  # enrolled twice in the same sub indicator: counted once
    enrol(b, digital, eu, governorate=beirut)  # enrolled in another place than home
    enrol(c, life, japan)
    enrol(gone, digital, eu)  # a deleted registration never counts
    return {
        'year': year, 'akkar': akkar, 'beirut': beirut, 'halba': halba, 'partner': partner,
        'other_partner': other_partner, 'eu': eu, 'japan': japan, 'skills': skills, 'digital': digital,
        'life': life, 'pd': pd,
    }


def table(payload, *by):
    grouping = next(g for g in payload['figures'] if g['by'] == sorted(by))
    return {tuple(row[:-1]): row[-1] for row in grouping['rows']}


def test_unique_youth_per_grouping(data):
    payload = indicator_figures.build(data['year'])
    assert table(payload)[()] == 3  # a, b, c; the deleted one is left out
    assert table(payload, 'master') == {(data['skills'].id,): 3}
    assert table(payload, 'sub') == {(data['digital'].id,): 2, (data['life'].id,): 2}
    assert table(payload, 'donor') == {(data['eu'].id,): 2, (data['japan'].id,): 2}
    assert table(payload, 'partner') == {(data['partner'].id,): 2, (data['other_partner'].id,): 1}
    # a counts in Akkar (home, same location), b where enrolled (Beirut), c at home (Beirut)
    assert table(payload, 'governorate') == {(data['akkar'].id,): 1, (data['beirut'].id,): 2}
    assert table(payload, 'sex') == {('Female',): 2, ('Male',): 1}
    assert table(payload, 'age_group') == {('15-17',): 1, ('18-24',): 2}


def test_groupings_combine_main_dimensions_with_one_detail(data):
    payload = indicator_figures.build(data['year'])
    by_donor_sub = table(payload, 'donor', 'sub')
    assert by_donor_sub[(data['digital'].id, data['eu'].id)] == 2
    assert by_donor_sub[(data['life'].id, data['japan'].id)] == 2
    assert len(indicator_figures.groupings()) == 16 * 7 + 1
    assert table(payload, 'program_document', 'sub') == {
        (data['pd'].id, data['digital'].id): 2, (data['pd'].id, data['life'].id): 2,
    }
    assert all(sorted(g['by']) == g['by'] for g in payload['figures'])


def test_payload_describes_what_it_counts_and_holds_no_personal_data(data):
    payload = indicator_figures.build(data['year'])
    assert payload['year'] == '2026'
    assert {i['name'] for i in payload['indicators']} == {'Skills', 'Digital skills', 'Life skills'}
    assert payload['program_documents'][0]['project_code'] == 'LEB/PCA2026001'
    assert payload['targets'] == [{
        'program_document': data['pd'].id, 'master': data['skills'].id, 'sub': data['digital'].id,
        'baseline': None, 'target': 100,
    }]
    assert {loc['p_code'] for loc in payload['locations']} == {'LB1', 'LB6', 'LB11'}
    text = str(payload)
    assert "'x'" not in text and 'first_name' not in text and 'adolescent' not in text


def test_age_group_rule():
    assert indicator_figures.age_group('2012', 2026) == 'Under 15'
    assert indicator_figures.age_group('2001', 2026) == '25 and over'
    assert indicator_figures.age_group(0, 2026) == 'Not specified'
    assert indicator_figures.age_group('abc', 2026) == 'Not specified'


def test_only_the_service_account_reads_the_figures(data):
    client = APIClient()
    assert client.get(URL).status_code in (401, 403)

    user_model = get_user_model()
    partner_user = user_model.objects.create_user(username='partner', password='x-pass-123456')
    client.credentials(HTTP_AUTHORIZATION='Token ' + Token.objects.create(user=partner_user).key)
    assert client.get(URL).status_code == 403

    service = user_model.objects.create_user(username='neurodb', password='x-pass-123456')
    service.groups.add(Group.objects.create(name='NeuroDB API'))
    client.credentials(HTTP_AUTHORIZATION='Token ' + Token.objects.create(user=service).key)
    response = client.get(URL, {'year': '2026'})
    assert response.status_code == 200
    assert response.json()['figures']
    assert client.get(URL, {'year': '1999'}).status_code == 404


# ------------------------------------------------------------------------- format 2 (Power BI views)
def block(payload, name, *by):
    grouping = next(g for g in payload['blocks'][name]['figures'] if g['by'] == sorted(by))
    return {tuple(row[:len(by)]): row[len(by):] for row in grouping['rows']}


@pytest.fixture
def more(data):
    """Beside the fixture's youth: ``d`` registered in 2026 without an enrolment, ``e`` enrolled but
    without a year (saved before the year existed), ``old`` enrolled in 2025."""
    syrian = Nationality.objects.get(name='Syrian')

    def youth(gender, born, **registration):
        person = Adolescent.objects.create(first_name='Secret', gender=gender, birthday_year=str(born),
                                           nationality=syrian, governorate=data['akkar'], district=data['halba'])
        return Registration.objects.create(adolescent=person, **registration)

    previous = Year.objects.create(name='2025')
    d = youth('Female', 2011, year=data['year'], partner=data['partner'])  # 15 in 2026
    e = youth('Male', 2007, partner=data['partner'])
    Registration.objects.filter(pk=e.pk).update(year=None)  # save() would give it the current year
    old = youth('Male', 2006, year=previous, partner=data['other_partner'])
    for registration in (e, old):
        EnrolledPrograms.objects.create(registration=registration, master_program=data['skills'],
                                        sub_program=data['digital'], donor=data['eu'], program_document=data['pd'])
    return dict(data, d=d, e=e, old=old, previous=previous,
                gone=Registration.objects.get(deleted=True))


def run(sql):
    with connection.cursor() as cursor:
        cursor.execute(sql)


def youth_view(columns='r.id, r.deleted, r.partner_id, r.year_id', source='youth_registration r', where='TRUE'):
    """A stand-in vw_youth_data_all with a column of names (which must never reach the payload)."""
    run('CREATE VIEW vw_youth_data_all AS SELECT %s, a.first_name AS adolescent_first_name FROM %s '
        'LEFT JOIN adolescent_adolescent a ON a.id = r.adolescent_id WHERE %s' % (columns, source, where))


def test_format_2_without_a_view_keeps_the_figures(data):
    payload = indicator_figures.build(data['year'])
    assert payload['format'] == 2 and payload['year'] == '2026'
    assert table(payload)[()] == 3 and table(payload, 'partner') == {
        (data['partner'].id,): 2, (data['other_partner'].id,): 1}
    power = payload['power_bi']
    assert power['view'] == 'vw_youth_data_all' and power['errors'] == []
    assert power['base'] == {'mode': 'rule', 'reason': 'view missing', 'setting': 'auto', 'key': None,
                             'period_column': None, 'period_rule': 'year', 'deleted': 'exclude', 'overrides': []}
    reconciliation = power['reconciliation']
    assert reconciliation['by'] == ['in_view', 'in_before', 'counted', 'deleted', 'no_year', 'other_year',
                                    'no_enrolment', 'no_master']
    assert reconciliation['measures'] == ['registrations', 'view_rows', 'people']
    assert reconciliation['totals'] == {
        'view_rows': None, 'view_ids': None, 'view_people': None, 'counted': 3, 'counted_people': 3, 'before': 3,
        'before_people': 3, 'in_view_not_counted': None, 'counted_not_in_view': None, 'deleted_in_view': None}


def test_registered_and_enrolments_blocks(more):
    payload = indicator_figures.build(more['year'])
    assert table(payload)[()] == 3  # figures: young people with an enrolment under a master indicator
    registered = payload['blocks']['registered']
    assert registered['measures'] == ['people', 'registrations', 'enrolled_people']
    assert block(payload, 'registered')[()] == [4, 4, 3]  # d has no enrolment; e no year; old is of 2025
    assert block(payload, 'registered', 'partner') == {(more['partner'].id,): [3, 3, 2],
                                                       (more['other_partner'].id,): [1, 1, 1]}
    assert block(payload, 'registered', 'home_governorate') == {(more['akkar'].id,): [3, 3, 2],
                                                                (more['beirut'].id,): [1, 1, 1]}
    assert block(payload, 'registered', 'age_group') == {('15-17',): [2, 2, 1], ('18-24',): [2, 2, 2]}
    assert block(payload, 'registered', 'home_governorate', 'sex') == {
        (more['akkar'].id, 'Female'): [2, 2, 1], (more['akkar'].id, 'Male'): [1, 1, 1],
        (more['beirut'].id, 'Female'): [1, 1, 1]}
    assert block(payload, 'registered', 'home_district') == {(more['halba'].id,): [3, 3, 2], (None,): [1, 1, 1]}
    enrolments = payload['blocks']['enrolments']
    assert enrolments['measures'] == ['enrolments', 'people']
    assert block(payload, 'enrolments')[()] == [5, 3]  # a enrolled three times
    assert block(payload, 'enrolments', 'master', 'sub') == {
        (more['skills'].id, more['digital'].id): [3, 2], (more['skills'].id, more['life'].id): [2, 2]}
    assert block(payload, 'enrolments', 'governorate') == {(more['akkar'].id,): [3, 1], (more['beirut'].id,): [2, 2]}
    assert block(payload, 'enrolments', 'donor') == {(more['eu'].id,): [3, 2], (more['japan'].id,): [2, 2]}
    assert {tuple(g['by']) for g in enrolments['figures']} == {
        tuple(sorted(g)) for g in indicator_figures.ENROLMENT_GROUPINGS}
    assert {loc['id'] for loc in payload['locations']} >= {more['akkar'].id, more['beirut'].id, more['halba'].id}
    t, f = True, False
    rows = {tuple(r[:8]): r[8:] for r in payload['power_bi']['reconciliation']['rows']}
    assert rows[(f, f, t, f, f, f, t, f)] == [1, 0, 1]  # d: counted now, not before (no enrolment)


def test_the_all_period(more):
    payload = indicator_figures.build(None)
    assert payload['year'] == 'all' and payload['targets'] == []
    assert table(payload)[()] == 5  # a, b, c, e without a year, old of 2025
    assert block(payload, 'registered')[()] == [6, 6, 5]
    assert payload['power_bi']['base']['period_rule'] == 'all'
    assert {pd['id'] for pd in payload['program_documents']} == {more['pd'].id}
    t, f = True, False
    rows = {tuple(r[:8]): r[8:] for r in payload['power_bi']['reconciliation']['rows']}
    assert rows[(f, f, t, f, t, f, f, f)] == [1, 0, 1]  # e: no year, so in no year before
    youth = Youth()
    assert youth.years() == ['2026', '2025', 'all'] and youth.current_year() == '2026'
    assert youth.has_year('all') and youth.has_year('2025') and not youth.has_year('1999')
    assert youth.build('all')['year'] == 'all' and youth.format_version == 2


def test_the_view_decides_which_registrations_count(more):
    youth_view()
    payload = indicator_figures.build(more['year'])
    power = payload['power_bi']
    assert power['base'] == {'mode': 'view', 'reason': '', 'setting': 'auto', 'key': 'id',
                             'period_column': 'year_id', 'period_rule': 'year', 'deleted': 'exclude',
                             'overrides': ['partner']}
    assert power['key_check'] == {'rows': 5, 'ids': 5, 'found': 5, 'same_year': 5, 'same_partner': 5,
                                  'same_deleted': 5, 'deleted_rows': 1, 'null_keys': 0, 'max_rows_per_id': 1,
                                  'conflicting': 0, 'verified': True}
    assert table(payload)[()] == 3 and block(payload, 'registered')[()] == [4, 4, 3]
    assert block(payload, 'enrolments')[()] == [5, 3]
    totals = power['reconciliation']['totals']
    assert (totals['view_rows'], totals['view_ids'], totals['counted'], totals['deleted_in_view']) == (5, 5, 4, 1)
    assert totals['counted_not_in_view'] == 0 and totals['in_view_not_counted'] == 1
    periods = {p['name']: p for p in power['periods']}
    assert periods['2026'] == {'id': more['year'].id, 'name': '2026', 'current': True, 'view_rows': 5, 'view_ids': 5,
                               'deleted_rows': 1}
    assert periods[None]['view_rows'] == 1 and periods['2025']['view_rows'] == 1  # e without a year; old
    catalogue = power['catalogue']['vw_youth_data_all']
    assert catalogue['kind'] == 'view' and ['public', 'adolescent_adolescent', 'table'] in catalogue['reads']
    assert power['catalogue']['vw_youth_data'] == {'exists': False}

    everything = indicator_figures.build(None)  # every view row: e without a year counts
    assert everything['power_bi']['base']['period_column'] is None
    assert table(everything)[()] == 5 and block(everything, 'registered')[()] == [6, 6, 5]
    assert everything['power_bi']['periods'] == []  # the current year's payload only
    assert 'Secret' not in json.dumps(payload) + json.dumps(everything)


def test_partner_comes_from_the_view(more):
    youth_view(columns='r.id, r.deleted, CASE WHEN r.id = %d THEN %d ELSE r.partner_id END AS partner_id, '
                       'r.year_id' % (more['d'].id, more['other_partner'].id))
    with mock.patch.object(power_bi, 'CROSS_MATCH', 0.5):  # one row of five disagrees on purpose
        payload = indicator_figures.build(more['year'])
    assert payload['power_bi']['base']['mode'] == 'view'
    assert payload['power_bi']['key_check']['same_partner'] == 4
    assert block(payload, 'registered', 'partner') == {(more['partner'].id,): [2, 2, 2],
                                                       (more['other_partner'].id,): [2, 2, 1]}
    youth_registration = Registration.objects.get(adolescent__gender='Male', year=more['year'], deleted=False)
    run('DROP VIEW vw_youth_data_all')
    youth_view(columns='r.id, r.deleted, CASE WHEN r.id = %d THEN %d ELSE r.partner_id END AS partner_id, '
                       'r.year_id' % (youth_registration.id, more['other_partner'].id))
    with mock.patch.object(power_bi, 'CROSS_MATCH', 0.5):
        payload = indicator_figures.build(more['year'])
    # b's enrolment counts under the view's partner in the figures and the enrolments block alike
    assert table(payload, 'partner') == {(more['partner'].id,): 1, (more['other_partner'].id,): 2}
    assert block(payload, 'enrolments', 'partner') == {(more['partner'].id,): [3, 1],
                                                       (more['other_partner'].id,): [2, 2]}


def test_a_per_enrolment_view_is_keyed_by_the_registration(more):
    youth_view(columns='e.id, e.registration_id, r.partner_id, r.deleted, r.year_id',
               source='youth_enrolledprograms e JOIN youth_registration r ON r.id = e.registration_id')
    payload = indicator_figures.build(more['year'])
    power = payload['power_bi']
    assert (power['base']['mode'], power['base']['key']) == ('view', 'registration_id')
    assert power['key_check']['max_rows_per_id'] == 3  # a: three enrolments
    assert block(payload, 'registered')[()] == [3, 3, 3]  # d has no enrolment, so no row in this view
    totals = power['reconciliation']['totals']
    assert (totals['view_rows'], totals['view_ids'], totals['counted']) == (6, 4, 3)  # gone's row left out
    assert table(payload)[()] == 3


def test_an_enrolment_keyed_view_falls_back(more):
    """ids that happen to be registration ids, but the rows are someone else's: the partners disagree."""
    rows = ', '.join('(%d, %d, %d)' % (r.id, more['other_partner'].id + 1000, more['year'].id)
                     for r in Registration.objects.filter(year=more['year']))
    run('CREATE VIEW vw_youth_data_all AS SELECT v.id, v.partner_id, v.year_id FROM (VALUES %s) '
        'AS v(id, partner_id, year_id)' % rows)
    payload = indicator_figures.build(more['year'])
    power = payload['power_bi']
    assert power['base']['mode'] == 'rule'
    assert power['base']['reason'] == "key check: 0% of the view's rows have the registration's partner"
    assert power['key_check']['found'] == power['key_check']['rows'] == 5
    assert table(payload)[()] == 3 and block(payload, 'registered')[()] == [4, 4, 3]  # the rule


def test_the_youth_period_column_is_found(more):
    youth_view(columns='r.id, r.partner_id, y.name AS year', source='youth_registration r '
               'LEFT JOIN youth_year y ON y.id = r.year_id')
    payload = indicator_figures.build(more['year'])
    power = payload['power_bi']
    assert (power['base']['mode'], power['base']['period_column']) == ('view', 'year')
    assert power['key_check']['same_year'] == 5 and power['key_check']['same_deleted'] is None
    assert block(payload, 'registered')[()] == [4, 4, 3]
    assert {p['name']: p['id'] for p in power['periods'] if p['name']}['2025'] == more['previous'].id

    run('DROP VIEW vw_youth_data_all')
    youth_view(columns='r.id')  # no year column, nothing to cross-check
    power = indicator_figures.build(more['year'])['power_bi']
    assert (power['base']['mode'], power['base']['period_column']) == ('view', 'registration')
    assert power['key_check']['verified'] is False and power['key_check']['rows'] == 7  # the whole view
    assert power['reconciliation']['totals']['view_ids'] == 5  # the 2026 registrations


def test_a_year_the_view_does_not_cover_but_the_setting_can_force(more, settings):
    youth_view(where='r.year_id IS DISTINCT FROM %d' % more['year'].id)
    power = indicator_figures.build(more['year'])['power_bi']
    assert power['base']['mode'] == 'rule'
    assert power['base']['reason'] == 'the view has no rows for 2026 while 4 registrations do'
    settings.FIGURES_POWER_BI = {'youth': {'base': 'rule'}}
    assert indicator_figures.build(more['year'])['power_bi']['base']['reason'] == (
        'setting FIGURES_POWER_BI base = rule')
    settings.FIGURES_POWER_BI = {'youth': {'deleted': 'include'}}
    run('DROP VIEW vw_youth_data_all')
    youth_view()
    payload = indicator_figures.build(more['year'])
    assert block(payload, 'registered')[()] == [5, 5, 4]  # the deleted registration too
    assert payload['power_bi']['base']['deleted'] == 'include'


# ------------------------------------------------------------------------------------ the youth API
def _service_client():
    service = get_user_model().objects.create_user(username='neurodb', password='x-pass-123456')
    service.groups.add(Group.objects.get_or_create(name='NeuroDB API')[0])
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION='Token ' + Token.objects.create(user=service).key)
    return client


def test_the_api_serves_the_fresh_snapshot_else_counts_now(data):
    import datetime

    from student_registration.figures.models import FiguresSnapshot

    client = _service_client()
    live = client.get(URL)  # no snapshot yet: counted now, as before
    assert live.status_code == 200 and live.json()['format'] == 2 and 'counted_at' not in live.json()
    never = mock.patch.object(Youth, 'build', side_effect=AssertionError('every year counted during a request'))
    with never:
        missing = client.get(URL, {'year': 'all'})
    assert missing.status_code == 404 and '["youth", "all"]' in missing.json()['detail']
    snapshots.refresh('youth', 'all')
    FiguresSnapshot.objects.filter(programme='youth', year='all').update(
        created_at=datetime.datetime(2020, 1, 1, tzinfo=datetime.timezone.utc))
    with never:
        served = client.get(URL, {'year': 'ALL'}).json()  # however old: never counted in a request
    assert served['year'] == 'all' and served['targets'] == [] and served['counted_at'].startswith('2020')

    youth = snapshots.refresh('youth', '2026')
    assert youth.payload['figures'] == live.json()['figures']
    with mock.patch.object(Youth, 'build', side_effect=AssertionError('counted although a snapshot is fresh')):
        served = client.get(URL, {'year': '2026'}).json()
    assert served['counted_at'] and served['counting_seconds'] >= 0 and served['figures'] == live.json()['figures']

    old = datetime.datetime(2020, 1, 1, tzinfo=datetime.timezone.utc)
    FiguresSnapshot.objects.filter(programme='youth', year='2026').update(created_at=old)  # stale: counted now
    with mock.patch.object(Youth, 'build', wraps=Youth().build) as build:
        assert 'counted_at' not in client.get(URL).json()
    build.assert_called_once_with('2026')

    snapshot = snapshots.refresh('youth', '2026')
    FiguresSnapshot.objects.filter(pk=snapshot.pk).update(payload=dict(snapshot.payload, format=1))
    assert snapshots.is_stale(snapshots.latest('youth', '2026'), 'youth')  # format 1: counted again
    assert 'counted_at' not in client.get(URL).json()
    FiguresSnapshot.objects.filter(programme='youth', year='all').update(payload={'format': 1, 'year': 'all'})
    assert client.get(URL, {'year': 'all'}).status_code == 404  # an older format is never served
    assert client.get(URL, {'year': '1999'}).status_code == 404


def test_a_failing_youth_count_never_hands_its_frames_to_the_error_reporter(more, caplog):
    """SPEC §7: the population is never logged or sent. The variables of the count's frames hold it (the id
    arrays of the queries, the view's partner per registration, the chunk of enrolment rows being read), and an
    error reporter with its defaults (Sentry in production: local variables on, the Django integration catching
    a request's unhandled exception) sends the variables of every frame. So a failure is logged by its class and
    first line only, never with ``exc_info``, and never raised out of a request or the command: a failing block,
    a failing read of the enrolment rows in a night run, the API counting on the spot, the command."""
    import logging

    import psycopg
    from django.core.management import CommandError, call_command
    from django.db import OperationalError

    from student_registration.figures import engine
    from student_registration.figures.models import FiguresRun

    youth_view()
    caplog.set_level(logging.DEBUG)
    real_block, real_fetch = engine.figures_block, psycopg.ServerCursor.fetchmany

    def enrolments_fail(sql, params, dimensions, *args):
        if 'master' in dimensions:
            raise OperationalError('canceling statement due to statement timeout')
        return real_block(sql, params, dimensions, *args)

    with mock.patch.object(engine, 'figures_block', enrolments_fail):
        payload = Youth().build('2026')
    assert payload['power_bi']['base']['mode'] == 'view' and payload['blocks']['enrolments']['error']

    def second_fetch_fails():
        calls = []

        def fetchmany(self, size=0):
            calls.append(size)
            if len(calls) == 2:
                raise psycopg.errors.QueryCanceled('canceling statement due to statement timeout')
            return real_fetch(self, size)

        return mock.patch.object(psycopg.ServerCursor, 'fetchmany', fetchmany)

    with second_fetch_fails():
        run_ = snapshots.execute_run(FiguresRun.objects.create(targets=[['youth', '2026']]).pk)
    assert run_.error == 'youth 2026: QueryCanceled: canceling statement due to statement timeout'
    with second_fetch_fails():  # no snapshot: counted on the spot, and the failure is answered, not raised
        answer = _service_client().get(URL, {'year': '2026'})
    assert answer.status_code == 503 and answer.json()['error'] == 'QueryCanceled'
    with second_fetch_fails(), pytest.raises(CommandError, match='youth 2026: QueryCanceled: canceling'):
        call_command('refresh_neurodb_figures', '--programme', 'youth', '--year', '2026')

    failures = [r.getMessage() for r in caplog.records if r.levelno >= logging.ERROR]
    for part in ('figures block enrolments failed: OperationalError', 'figures run %d: youth 2026 failed: '
                 'QueryCanceled' % run_.pk, 'youth figures 2026: counting on the spot failed: QueryCanceled'):
        assert part in failures or any(text.startswith(part) for text in failures), part
    assert [r for r in caplog.records if r.exc_info] == []  # nothing an error reporter could unfold
    ids = power_bi.int_array(sorted(Registration.objects.filter(year=more['year']).values_list('id', flat=True)))
    assert not any(ids in r.getMessage() for r in caplog.records)


# ------------------------------------------------- the worker aborted during a count on the spot
def _abort_inside_the_count(where):
    """gunicorn's worker timeout (Procfile --timeout=60): the arbiter's SIGABRT, whose handler calls
    ``sys.exit(1)``, a SystemExit raised wherever the count is: in the enrolment loop (while it holds an
    enrolment row and the view's partner per registration) or while a block's query runs (its parameters: the
    arrays of the view's registration ids)."""
    import sys

    from student_registration.figures import engine

    real_age, real_block = indicator_figures.age_group, engine.figures_block
    calls = []

    def age_group(*args):
        calls.append(1)
        if where == 'enrolment loop' and len(calls) == 2:
            sys.exit(1)
        return real_age(*args)

    def figures_block(sql, params, dimensions, *args):
        if where == 'block query' and 'master' in dimensions:
            sys.exit(1)
        return real_block(sql, params, dimensions, *args)

    patches = mock.patch.object(indicator_figures, 'age_group', age_group), \
        mock.patch.object(engine, 'figures_block', figures_block)
    return patches


def _reachable_frames(exc):
    """Every frame an error reporter can walk from ``exc``: its traceback's and those of every exception
    chained to it (cause or context, shown or suppressed)."""
    seen, frames, pending = set(), [], [exc]
    while pending:
        current = pending.pop()
        if current is None or id(current) in seen:
            continue
        seen.add(id(current))
        tb = current.__traceback__
        while tb is not None:
            frames.append(tb.tb_frame)
            tb = tb.tb_next
        pending += [current.__cause__, current.__context__]
    return frames


@pytest.mark.parametrize('where', ['enrolment loop', 'block query'])
def test_a_worker_abort_during_a_count_on_the_spot_carries_no_frame_of_the_count(more, where):
    """SPEC §7. The abort is not an Exception: it passed through the count's ``except Exception`` and reached
    the error reporter's WSGI middleware (Sentry, production), which sends the variables of every frame: the
    view's partner per registration, the arrays of the view's registration ids. It still stops the worker
    (SystemExit(1) out of the request), but as a new exception raised by the answer itself: no frame of the
    count, no chained exception."""
    youth_view()
    ids = sorted(Registration.objects.filter(year=more['year']).values_list('id', flat=True))
    client = _service_client()
    first, second = _abort_inside_the_count(where)
    with first, second, pytest.raises(SystemExit) as raised:
        client.get(URL, {'year': '2026'})
    assert raised.value.code == 1  # the worker exits as gunicorn asked
    assert raised.value.__cause__ is None and raised.value.__context__ is None
    frames = [f for f in _reachable_frames(raised.value) if f.f_code.co_filename != __file__]
    assert frames[-1].f_code.co_name == 'count_now'  # raised there: nothing of the count below it
    counting = [(f.f_globals.get('__name__'), f.f_code.co_name) for f in frames
                if f.f_globals.get('__name__', '').startswith('student_registration.figures')
                or f.f_globals.get('__name__') == 'student_registration.youth.indicator_figures']
    assert counting == []
    array = power_bi.int_array(ids)
    assert not [f.f_code.co_name for f in frames if array in repr(f.f_locals)]


@pytest.fixture
def sentry():
    """Sentry as production sets it up (config/settings/production.py), sending into memory; skipped where
    sentry-sdk is not installed (it is a production requirement only)."""
    sentry_sdk = pytest.importorskip('sentry_sdk')
    from sentry_sdk.integrations.django import DjangoIntegration
    from sentry_sdk.transport import Transport

    class Memory(Transport):
        events = []

        def capture_envelope(self, envelope):
            self.events.extend(item.payload.json for item in envelope.items if item.type == 'event')

    def start(before_send=None):
        Memory.events = []
        sentry_sdk.init(dsn='https://public@sentry.invalid/1', transport=Memory, integrations=[DjangoIntegration()],
                        traces_sample_rate=1.0, send_default_pii=True, before_send=before_send)
        return Memory

    yield start
    sentry_sdk.get_client().close()
    sentry_sdk.init()


def _wsgi_get(path, query, token):
    """One request through Django's WSGI handler, as gunicorn calls it (Sentry's middleware included)."""
    import io
    import sys

    from django.core import signals
    from django.core.wsgi import get_wsgi_application
    from django.db import close_old_connections

    signals.request_started.disconnect(close_old_connections)  # the test's transaction stays open
    signals.request_finished.disconnect(close_old_connections)
    environ = {'REQUEST_METHOD': 'GET', 'PATH_INFO': path, 'QUERY_STRING': query, 'SERVER_NAME': 'testserver',
               'SERVER_PORT': '80', 'wsgi.url_scheme': 'http', 'wsgi.input': io.BytesIO(b''), 'wsgi.errors': sys.stderr,
               'HTTP_AUTHORIZATION': 'Token ' + token, 'HTTP_HOST': 'testserver'}
    try:
        return get_wsgi_application()(environ, lambda status, headers, exc_info=None: None)
    finally:
        signals.request_started.connect(close_old_connections)
        signals.request_finished.connect(close_old_connections)


@pytest.mark.parametrize('before_send', [False, True], ids=['the abort alone', 'production'])
@pytest.mark.parametrize('where', ['enrolment loop', 'block query'])
def test_a_worker_abort_during_a_count_on_the_spot_sends_no_id_to_sentry(more, sentry, settings, where, before_send):
    """The same abort through Sentry's WSGI middleware: reported, with none of the view's ids, whether or not
    production's ``before_send`` (figures/error_reports.py) is set."""
    from student_registration.figures.error_reports import drop_count_variables

    transport = sentry(drop_count_variables if before_send else None)
    settings.ALLOWED_HOSTS = ['testserver']
    youth_view()
    ids = sorted(Registration.objects.filter(year=more['year']).values_list('id', flat=True))
    service = get_user_model().objects.create_user(username='neurodb', password='x-pass-123456')
    service.groups.add(Group.objects.get_or_create(name='NeuroDB API')[0])
    first, second = _abort_inside_the_count(where)
    with first, second, pytest.raises(SystemExit):
        _wsgi_get(URL, 'year=2026', Token.objects.create(user=service).key)
    import sentry_sdk

    sentry_sdk.flush()
    # the abort, reported (and the logged line, an event of its own without a stack)
    assert [e['exception']['values'][-1]['type'] for e in transport.events if 'exception' in e] == ['SystemExit']
    text = json.dumps(transport.events)
    assert power_bi.int_array(ids) not in text and 'view_partner' not in text


def test_an_error_passing_through_a_count_reaches_sentry_without_the_variables(more, sentry):
    """Production's ``before_send``: an exception that passes through a count anyway (a failure in code added
    later, an abort inside a query) is sent without the variables of any frame, Django's and psycopg's below
    the count included (they hold the same parameters)."""
    import sentry_sdk

    from student_registration.figures.error_reports import drop_count_variables

    youth_view()
    ids = sorted(Registration.objects.filter(year=more['year']).values_list('id', flat=True))
    for before_send, holds in ((None, True), (drop_count_variables, False)):
        transport = sentry(before_send)
        with mock.patch.object(indicator_figures, 'age_group', side_effect=RuntimeError('not caught')):
            try:
                Youth().build('2026')
            except RuntimeError:
                sentry_sdk.capture_exception()
        sentry_sdk.flush()
        [event] = transport.events
        frames = event['exception']['values'][-1]['stacktrace']['frames']
        assert any(f.get('module') == 'student_registration.youth.indicator_figures' for f in frames)
        assert (power_bi.int_array(ids) in json.dumps(event)) is holds  # without it: the view's ids are sent
        assert any('vars' in f for f in frames) is holds


def test_the_youth_api_has_a_throttle_of_its_own():
    from student_registration.figures.api import FiguresView
    from student_registration.youth.indicator_figures_api import YouthIndicatorFiguresView

    [youth] = YouthIndicatorFiguresView.throttle_classes
    [education] = FiguresView.throttle_classes
    assert youth.scope == 'neurodb_youth' != education.scope
    assert youth().get_rate() == '120/hour'


def test_the_night_count_reads_under_the_read_only_limits(data, settings):
    settings.FIGURES_STATEMENT_TIMEOUT_MS = 54321
    seen = {}

    def spy(year, alias=None, population=None):
        with connection.cursor() as cursor:
            for name in ('transaction_read_only', 'statement_timeout'):
                cursor.execute('SHOW %s' % name)
                seen[name] = cursor.fetchone()[0]
        seen['alias'], seen['year'] = alias, year
        return {'year': 'x'}

    with mock.patch.object(indicator_figures, 'build', side_effect=spy):
        Youth().build('2026')
    assert seen == {'transaction_read_only': 'on', 'statement_timeout': '54321ms', 'alias': 'default',
                    'year': data['year']}
    Registration.objects.create(year=data['year'])  # the outer transaction can write again
    with pytest.raises(Year.DoesNotExist):
        Youth().build('1999')


def test_a_timeout_reading_the_view_falls_back_inside_the_night_count(more, settings):
    youth_view(where='pg_sleep(0.3) IS NOT NULL')
    settings.FIGURES_STATEMENT_TIMEOUT_MS = 200
    payload = Youth().build('2026')  # one read-only transaction: the failed view read must not abort it
    power = payload['power_bi']
    assert power['base']['mode'] == 'rule'
    assert power['base']['reason'] == 'QueryCanceled: canceling statement due to statement timeout'
    assert any(e.startswith('population: QueryCanceled') for e in power['errors'])
    assert table(payload)[()] == 3 and block(payload, 'registered')[()] == [4, 4, 3]
    assert all('error' not in b for b in payload['blocks'].values())
    assert power['reconciliation']['totals']['counted'] == 4


def test_an_empty_view_for_all_years(more):
    youth_view(where='FALSE')
    power = indicator_figures.build(None)['power_bi']
    assert power['base']['reason'] == 'the view has no rows for all years while 6 registrations do'


# ------------------------------------------------------------------ limits, keys, the year "all"
def test_a_failed_gate_count_leaves_the_youth_count_going(more, settings):
    """The view is empty for the year, so the gate counts the rule's registrations: when that count fails
    (a timeout), it fails in a savepoint of its own and the rest of the night count goes on."""
    from django.db.models.expressions import RawSQL

    from student_registration.figures import education

    youth_view(where='FALSE')
    slow = RawSQL('SELECT id FROM youth_registration WHERE pg_sleep(0.3) IS NOT NULL', [])

    def population_of(year):
        return education.view_population('youth', year.name, year=year,
                                         rule=indicator_figures.rule(year).filter(id__in=slow))

    settings.FIGURES_STATEMENT_TIMEOUT_MS = 100
    with mock.patch.object(indicator_figures, 'population_of', side_effect=population_of):
        payload = Youth().build('2026')  # one read-only transaction: the failed count must not abort it
    power = payload['power_bi']
    assert power['base']['mode'] == 'rule'
    assert power['base']['reason'] == 'QueryCanceled: canceling statement due to statement timeout'
    assert power['errors'] == ['population: QueryCanceled: canceling statement due to statement timeout']
    assert table(payload)[()] == 3 and block(payload, 'registered')[()] == [4, 4, 3]
    assert all('error' not in b for b in payload['blocks'].values())


@pytest.mark.django_db(transaction=True)
@pytest.mark.parametrize('empty', [False, True], ids=['view', 'empty view'])
def test_every_read_of_a_youth_count_runs_under_the_limits(more, settings, empty):
    from student_registration.figures.tests.test_power_bi import read_under_the_limits

    youth_view(where='FALSE' if empty else 'TRUE')
    try:
        payload, tables = read_under_the_limits(lambda: Youth().build('2026'), settings)
    finally:
        run('DROP VIEW vw_youth_data_all')
    reason = payload['power_bi']['base']['reason']
    assert reason == ('the view has no rows for 2026 while 4 registrations do' if empty else '')
    assert {'vw_youth_data_all', 'youth_registration', 'youth_enrolledprograms', 'youth_year'} <= tables


def test_the_views_registration_ids_are_never_in_the_youth_sql_text(more):
    from student_registration.figures.tests.test_power_bi import statements_sent

    youth_view()
    payload, sent = statements_sent(lambda: indicator_figures.build(more['year']))
    assert payload['power_bi']['base']['mode'] == 'view'
    ids = power_bi.int_array(sorted(Registration.objects.filter(year=more['year']).values_list('id', flat=True)))
    carrying = [text for params, text in sent if ids in params]
    assert len(carrying) >= 4  # the enrolments read for the figures, the two blocks, the reconciliation
    assert any(text.startswith('DECLARE') for text in carrying)  # read a chunk at a time
    assert all(text and ids not in text and '$1' in text for text in carrying)
    assert not any(ids in text for _params, text in sent)


PER_ENROLMENT = 'youth_enrolledprograms e LEFT JOIN youth_registration r ON r.id = e.registration_id'


def test_rows_without_a_registration_do_not_fail_the_key(more):
    """A per-enrolment view keeps the enrolments whose registration was removed (on_delete SET_NULL): their
    blank key points to no registration, is left out of the population, and is no evidence against the key."""
    EnrolledPrograms.objects.create(registration=None, master_program=more['skills'])
    youth_view(columns='e.id, e.registration_id, r.partner_id, r.deleted, r.year_id', source=PER_ENROLMENT)
    for year in (more['year'], None):
        population = power_bi.population('youth', year.name if year else 'all', year=year)
        assert (population.mode, population.key, population.reason) == ('view', 'registration_id', '')
    check = population.key_check  # "all": every view row
    assert (check['rows'], check['found'], check['null_keys'], check['verified']) == (8, 8, 1, True)
    payload = indicator_figures.build(None)
    assert payload['power_bi']['base']['key'] == 'registration_id' and table(payload)[()] == 5


def test_when_every_key_fails_the_preferred_keys_result_is_shown(more):
    youth_view(columns='e.id + 100000 AS id, CASE WHEN e.id % 2 = 0 THEN e.registration_id '
                       'ELSE e.registration_id + 100000 END AS registration_id, r.partner_id, r.deleted, r.year_id',
               source=PER_ENROLMENT)
    population = power_bi.population('youth', '2026', year=more['year'])
    check = population.key_check
    assert population.mode == 'rule' and population.key == 'registration_id'
    assert 0 < check['found'] < check['rows']  # the enrolment-id key would show 0
    assert population.reason == "key check: %d%% of the view's ids are registrations" % (
        100 * check['found'] // check['rows'])


def test_a_key_blank_on_most_rows_is_not_the_key(more):
    """Blank keys are tolerated, not a column blank on most rows: here ``id`` is the registration id."""
    youth_view(columns='e.registration_id AS id, CASE WHEN e.id % 3 = 0 THEN e.registration_id END '
                       'AS registration_id, r.partner_id, r.deleted, r.year_id', source=PER_ENROLMENT)
    population = power_bi.population('youth', '2026', year=more['year'])
    assert (population.mode, population.key) == ('view', 'id')
    assert sorted(population.ids) == sorted(
        Registration.objects.filter(year=more['year'], enrolled_programs__isnull=False).distinct()
        .values_list('id', flat=True))


def test_the_year_all_in_any_case(data):
    from student_registration.figures.api import read_targets

    youth = Youth()
    assert youth.has_year('ALL') and youth.has_year(' All ') and not youth.has_year('alll')
    assert read_targets([['youth', 'ALL'], ['youth', 'all']], snapshots.all_programmes()) == (
        [('youth', 'all')], None)
    assert snapshots.refresh('youth', 'ALL').year == 'all'
    assert youth.build('All')['year'] == 'all'
