"""Counting over the views the Power BI dashboards read (power_bi.py), with stand-in views.

The real views exist only in production; each test creates a stand-in under the real name inside the
test transaction (rolled back afterwards). The fixtures' children and teachers are named "Secret".
"""

import datetime
import hashlib
import json
from unittest import mock

import pytest
from django.db import connection, transaction

from student_registration.child.models import Child
from student_registration.clm.models import Bridging
from student_registration.figures import education, engine, power_bi
from student_registration.locations.models import Center, ProgramStaff
from student_registration.mscc import models as m
from student_registration.schools.models import PartnerOrganization
from student_registration.students.models import Student

from . import test_education_figures as base
from .test_education_figures import table, total

pytestmark = pytest.mark.django_db

# the fixtures of the education figures tests (children and teachers named "Secret")
places, makani, bridging, dirasa_more = base.places, base.makani, base.bridging, base.dirasa_more

CHILD, REGISTRATION = Child._meta.db_table, m.Registration._meta.db_table
STANDARD = "r.round_id IS NOT NULL AND r.type IS DISTINCT FROM 'TLS'"


def run(sql):
    with connection.cursor() as cursor:
        cursor.execute(sql)


def mscc_view(where=STANDARD, columns='r.id, r.round_id, r.partner_id, r.center_id', kind='VIEW'):
    """A stand-in vw_mscc_data: one row per registration with a round, TLS left out, deleted kept, and a
    column of children's names (which must never reach the payload)."""
    run('CREATE %s vw_mscc_data AS SELECT %s, r.deleted, r.type, ch.first_name AS child_first_name '
        'FROM %s r JOIN %s ch ON ch.id = r.child_id WHERE %s' % (kind, columns, REGISTRATION, CHILD, where))


@pytest.fixture
def seeded(makani):
    """The Makani fixture plus a TLS registration in the current round. In 2025 the view holds the girl's
    two registrations and a deleted one; the boy has no round; another registration is of 2024."""
    tls_child = Child.objects.create(first_name='Secret', gender='Male', birthday_year='2014')
    makani['tls'] = m.Registration.objects.create(child=tls_child, partner=makani['partner'],
                                                  center=makani['center'], round=makani['current'], type='TLS')
    makani['boy'] = m.Registration.objects.get(round__isnull=True)
    makani['deleted'] = m.Registration.objects.get(deleted=True)
    makani['old'] = m.Registration.objects.get(round__year=2024)
    return makani


def build(name='mscc', year='2025'):
    return education.PROGRAMMES[name].build(year)


def bucket(reconciliation):
    """{flags: measures} of the reconciliation rows."""
    width = len(reconciliation['by'])
    return {tuple(row[:width]): row[width:] for row in reconciliation['rows']}


# ------------------------------------------------------------------------------- view mode
def test_view_mode_counts_the_views_registrations_of_the_year(seeded):
    mscc_view()
    payload = build()
    power = payload['power_bi']
    assert power['base'] == {'mode': 'view', 'reason': '', 'setting': 'auto', 'key': 'id',
                             'period_column': 'round_id', 'period_rule': 'round_year', 'deleted': 'exclude',
                             'overrides': ['partner', 'center']}
    assert power['errors'] == [] and power['version'] == 1 and power['view'] == 'vw_mscc_data'
    # the view's 2025 rows: the girl twice and a deleted registration (left out); not the TLS one, not the
    # boy without a round, not the 2024 one
    enrolment = payload['cubes']['enrolment']
    assert enrolment['measures'][-1] == 'view_rows'
    assert total(enrolment, 'registrations') == 2 and total(enrolment, 'view_rows') == 2
    assert total(enrolment, 'registrations', package='TLS') == 0
    assert table(payload['blocks']['registrations'])[()] == [1]
    assert table(payload['blocks']['services'], 'service') == {('Child protection (PSS)',): [1], ('Education',): [1]}
    assert table(payload['blocks']['sites'])[()] == [2]
    assert power['key_check'] == {'rows': 3, 'ids': 3, 'found': 3, 'same_round': 3, 'same_partner': 3,
                                  'same_partner_or_centre': 3, 'same_center': 3, 'deleted_rows': 1,
                                  'max_rows_per_id': 1, 'conflicting': 0, 'verified': True}
    catalogue = power['catalogue']['vw_mscc_data']
    assert catalogue['exists'] and catalogue['kind'] == 'view' and catalogue['can_select']
    assert ['id', 'integer'] in catalogue['columns'] and 'child_first_name' in [n for n, _t in catalogue['columns']]
    assert ['public', REGISTRATION, 'table'] in catalogue['reads'] and ['public', CHILD, 'table'] in catalogue['reads']
    assert power['catalogue']['vw_mscc_data_no_round'] == {'exists': False}
    assert payload['pending_round'] == 1  # the boy: no round yet, his partner counted this year
    periods = {p['id']: p for p in power['periods']}
    assert periods[seeded['current'].id] == {
        'id': seeded['current'].id, 'name': 'Round 1 2025', 'year': 2025, 'current': True,
        'start_date': '2025-01-01', 'end_date': None, 'view_rows': 3, 'view_ids': 3, 'deleted_rows': 1}
    assert periods[seeded['old'].round_id]['view_rows'] == 1
    assert power['related']['vw_center_program_staff'] == {'exists': False}


def test_the_view_decides_not_the_rule(seeded):
    mscc_view(where='r.round_id IS NOT NULL')  # this view keeps TLS: so would the Power BI
    payload = build()
    enrolment = payload['cubes']['enrolment']
    assert payload['power_bi']['base']['mode'] == 'view'
    assert total(enrolment, 'registrations') == 3 and total(enrolment, 'registrations', package='TLS') == 1
    assert table(payload['blocks']['registrations'])[()] == [2]


def test_partner_and_centre_come_from_the_view(seeded):
    other_center = Center.objects.get(name='Center B')
    m.Registration.objects.filter(partner=seeded['other']).update(partner=seeded['partner'])  # centre B's is other
    no_center = m.Registration.objects.create(child=Child.objects.create(first_name='Secret', gender='Female'),
                                              partner=seeded['partner'], round=seeded['current'])
    # the view's partner is the centre's, and a registration without a centre is given centre B
    run('CREATE VIEW vw_mscc_data AS SELECT r.id, r.round_id, c.partner_id AS partner_id, '
        'COALESCE(r.center_id, %(b)d) AS center_id, r.deleted, r.type, ch.first_name AS child_first_name '
        'FROM %(reg)s r JOIN %(child)s ch ON ch.id = r.child_id '
        'LEFT JOIN locations_center c ON c.id = COALESCE(r.center_id, %(b)d) WHERE %(where)s'
        % {'b': other_center.id, 'reg': REGISTRATION, 'child': CHILD, 'where': STANDARD})
    payload = build()
    assert payload['power_bi']['base']['mode'] == 'view'
    enrolment = payload['cubes']['enrolment']
    # the girl's second registration: the registration says Makani Partner, the view says the centre's
    assert total(enrolment, 'registrations', partner=seeded['other'].id) == 2  # her and the one without a centre
    assert total(enrolment, 'registrations', center=other_center.id) == 2
    assert table(payload['blocks']['registrations'], 'partner') == {(seeded['partner'].id,): [1],
                                                                    (seeded['other'].id,): [2]}
    assert table(payload['blocks']['sites'])[()] == [2]
    check = payload['power_bi']['key_check']
    assert check['rows'] == 4 and check['same_partner'] == 2 and check['same_center'] == 3
    assert no_center.center_id is None


def test_the_deleted_setting(seeded, settings):
    mscc_view()
    excluded = build()['power_bi']['reconciliation']['totals']
    settings.FIGURES_POWER_BI = {'mscc': {'deleted': 'include'}}
    payload = build()
    assert payload['power_bi']['base']['deleted'] == 'include'
    assert total(payload['cubes']['enrolment'], 'registrations') == 3
    assert table(payload['blocks']['registrations'])[()] == [2]  # the deleted registration's child
    included = payload['power_bi']['reconciliation']['totals']
    assert excluded['deleted_in_view'] == included['deleted_in_view'] == 1
    assert (excluded['counted'], included['counted']) == (2, 3)
    assert (excluded['in_view_not_counted'], included['in_view_not_counted']) == (1, 0)


def test_repeated_rows(seeded):
    girl = m.Registration.objects.get(partner=seeded['partner'], round=seeded['current'], deleted=False,
                                      type='Core-Package')
    m.EducationService.objects.create(registration=girl, education_program='BLN Level 2', round=seeded['current'])
    run('CREATE VIEW vw_mscc_data AS SELECT r.id, r.round_id, r.partner_id, r.center_id, es.education_program '
        'FROM %s r JOIN mscc_educationservice es ON es.registration_id = r.id WHERE %s' % (REGISTRATION, STANDARD))
    payload = build()
    power = payload['power_bi']
    assert power['base']['mode'] == 'view'
    assert power['key_check']['rows'] == 2 and power['key_check']['ids'] == 1
    assert power['key_check']['max_rows_per_id'] == 2
    enrolment = payload['cubes']['enrolment']
    assert total(enrolment, 'registrations') == 1 and total(enrolment, 'view_rows') == 2
    totals = power['reconciliation']['totals']
    assert (totals['view_rows'], totals['view_ids'], totals['counted']) == (2, 1, 1)


def test_reconciliation_buckets(seeded):
    mscc_view()
    reconciliation = build()['power_bi']['reconciliation']
    assert reconciliation['period'] == '2025'
    assert reconciliation['by'] == ['in_view', 'in_before', 'counted', 'deleted', 'tls', 'no_round', 'no_child',
                                    'other_year']
    assert reconciliation['measures'] == ['registrations', 'view_rows', 'children']
    t, f = True, False
    assert bucket(reconciliation) == {
        (t, t, t, f, f, f, f, f): [2, 2, 1],  # the girl's two registrations
        (t, f, f, t, f, f, f, f): [1, 1, 1],  # deleted, in the view
        (f, t, f, f, f, t, f, f): [1, 0, 1],  # the boy: counted before, without a round
        (f, t, f, f, t, f, f, f): [1, 0, 1],  # TLS: counted before
    }
    assert reconciliation['totals'] == {
        'view_rows': 3, 'view_ids': 3, 'view_children': 2, 'counted': 2, 'counted_children': 1, 'before': 4,
        'before_children': 3, 'in_view_not_counted': 1, 'counted_not_in_view': 0, 'deleted_in_view': 1}
    assert sum(r[-3] for r in reconciliation['rows']) == 5


def test_reconciliation_other_year_and_the_threshold(seeded, settings):
    """A view whose round is not the registration's (e.g. taken from a service record): below the key
    check's threshold it is not used; with a lower threshold it is, and the row shows as another year's."""
    mscc_view(columns='r.id, CASE WHEN r.id = %d THEN %d ELSE r.round_id END AS round_id, r.partner_id, '
                      'r.center_id' % (seeded['old'].id, seeded['current'].id))
    power = build()['power_bi']
    assert power['base']['mode'] == 'rule'
    assert power['base']['reason'] == "key check: 75% of the view's rows have the registration's round"
    settings.FIGURES_POWER_BI_MIN_MATCH = 0.5
    payload = build()
    reconciliation = payload['power_bi']['reconciliation']
    assert payload['power_bi']['base']['mode'] == 'view'
    t, f = True, False
    assert bucket(reconciliation)[(t, f, t, f, f, f, f, t)] == [1, 1, 1]
    assert total(payload['cubes']['enrolment'], 'registrations') == 3


def test_current_rounds_period(seeded, settings):
    m.Round.objects.filter(pk=seeded['old'].round_id).update(current_year=True)
    mscc_view()
    settings.FIGURES_POWER_BI = {'mscc': {'period': 'current_rounds'}}
    payload = build()
    assert payload['power_bi']['base']['period_rule'] == 'current_rounds'
    assert {r['name'] for r in payload['rounds']} == {'Round 1 2024', 'Round 1 2025'}
    assert total(payload['cubes']['enrolment'], 'registrations') == 3  # with the 2024 round's
    assert build('mscc', '2024')['power_bi']['base']['period_rule'] == 'round_year'  # not the current year


# ------------------------------------------------------------------------------- rule mode
def assert_rule_mode(payload, reason):
    power = payload['power_bi']
    assert power['base']['mode'] == 'rule' and power['base']['overrides'] == []
    assert power['base']['reason'] == reason or reason in power['base']['reason']
    enrolment = payload['cubes']['enrolment']
    assert 'view_rows' not in enrolment['measures']
    # the corrected rule: the girl twice; no TLS, no registration without a round
    assert total(enrolment, 'registrations') == 2 and total(enrolment, 'registrations', package='TLS') == 0
    assert table(payload['blocks']['registrations'])[()] == [1]
    return power


def test_no_view_is_rule_mode_without_error(seeded):
    power = assert_rule_mode(build(), 'view missing')
    assert power['errors'] == [] and power['catalogue']['vw_mscc_data'] == {'exists': False}
    assert power['key_check'] == {}
    totals = power['reconciliation']['totals']
    assert totals['view_rows'] is None and totals['view_ids'] is None and totals['deleted_in_view'] is None
    assert (totals['counted'], totals['before'], totals['counted_not_in_view']) == (2, 4, None)
    assert power['periods'] == []


def test_a_key_that_is_not_the_registration_id(seeded):
    mscc_view(columns='r.id + 100000 AS id, r.round_id, r.partner_id, r.center_id')
    power = assert_rule_mode(build(), "key check: 0% of the view's ids are registrations")
    assert power['key_check']['rows'] == 3 and power['key_check']['found'] == 0


def test_an_empty_view_for_a_year_that_has_registrations(seeded, settings):
    mscc_view(where=STANDARD + ' AND r.round_id <> %d' % seeded['current'].id)
    assert_rule_mode(build(), 'the view has no rows for 2025 while 2 registrations do')
    settings.FIGURES_POWER_BI = {'mscc': {'base': 'view'}}  # trusted even when empty
    payload = build()
    assert payload['power_bi']['base']['mode'] == 'view'
    assert total(payload['cubes']['enrolment'], 'registrations') == 0


def test_the_setting_switches_the_view_off(seeded, settings):
    mscc_view()
    settings.FIGURES_POWER_BI = {'mscc': {'base': 'rule'}}
    power = assert_rule_mode(build(), 'setting FIGURES_POWER_BI base = rule')
    assert power['base']['setting'] == 'rule' and power['periods'] == []
    assert power['catalogue']['vw_mscc_data']['exists']  # still described


def test_not_a_view_no_key_and_a_text_key(seeded):
    run('CREATE TABLE vw_mscc_data (id integer, round_id integer)')
    assert_rule_mode(build(), 'vw_mscc_data is a table, not a view')
    run('DROP TABLE vw_mscc_data')
    mscc_view(columns='r.round_id, r.partner_id')
    assert_rule_mode(build(), 'key column id missing')
    run('DROP VIEW vw_mscc_data')
    mscc_view(columns="r.id::text AS id, r.round_id")
    assert_rule_mode(build(), 'key column id is text, not an integer')


def test_no_select_permission(seeded):
    mscc_view()
    for sql in ('CREATE ROLE cmp_pbi_c1_reader NOLOGIN',  # rolled back with the test
                'GRANT SELECT ON ALL TABLES IN SCHEMA public TO cmp_pbi_c1_reader',
                'REVOKE SELECT ON vw_mscc_data FROM cmp_pbi_c1_reader', 'SET LOCAL ROLE cmp_pbi_c1_reader'):
        run(sql)
    power = assert_rule_mode(build(), 'no SELECT permission on vw_mscc_data')
    assert power['catalogue']['vw_mscc_data']['can_select'] is False
    assert power['catalogue']['vw_mscc_data']['definition']  # pg_get_viewdef needs no grant


def test_a_timeout_reading_the_view(seeded, settings):
    mscc_view(where=STANDARD + ' AND pg_sleep(0.5) IS NOT NULL')
    settings.FIGURES_STATEMENT_TIMEOUT_MS = 300
    payload = build()
    power = assert_rule_mode(payload, 'QueryCanceled: canceling statement due to statement timeout')
    assert any(e.startswith('population: QueryCanceled') for e in power['errors'])
    assert all(not c.get('error') for c in payload['cubes'].values())
    assert all(not b.get('error') for b in payload['blocks'].values())
    assert power['reconciliation']['totals']['counted'] == 2


def test_a_failing_population_is_rule_mode(seeded):
    mscc_view()
    with mock.patch.object(power_bi, 'key_check', side_effect=RuntimeError('boom')):
        power = assert_rule_mode(build(), 'RuntimeError: boom')
    assert power['errors'] == ['population: RuntimeError: boom']


# ------------------------------------------------------------------------- catalogue and privacy
def test_a_materialized_view(seeded):
    mscc_view(kind='MATERIALIZED VIEW')
    payload = build()
    catalogue = payload['power_bi']['catalogue']['vw_mscc_data']
    assert catalogue['kind'] == 'materialized view' and ['round_id', 'integer'] in catalogue['columns']
    assert payload['power_bi']['base']['mode'] == 'view'
    assert total(payload['cubes']['enrolment'], 'registrations') == 2


def test_masking_and_privacy(seeded):
    ProgramStaff.objects.create(facilitator_name='Secret', center=seeded['center'], gender='Male',
                                is_active_current_round='yes, until the end of the round')
    # a short word in a flag column is not a code either (it could be a name): never sent
    ProgramStaff.objects.create(facilitator_name='Secret', center=seeded['center'], gender='Female',
                                is_active_current_round='Zaynab-Test')
    numbers = ', '.join(str(900000 + i) for i in range(1, 13))
    mscc_view(where="%s AND ch.first_name <> 'Zaynab-Test' AND r.id NOT IN (%s)" % (STANDARD, numbers))
    run('CREATE VIEW vw_center_program_staff AS SELECT ps.id, ps.facilitator_name, ps.is_active_current_round '
        'FROM locations_programstaff ps')
    payload = build()
    catalogue = payload['power_bi']['catalogue']['vw_mscc_data']
    definition = catalogue['definition']
    assert 'Zaynab' not in definition and '900001' not in definition
    assert "'<masked text, 11 chars>'" in definition and 'ARRAY[<12 numbers>]' in definition
    assert "'TLS'" in definition
    assert (catalogue['masked_literals'], catalogue['masked_lists']) == (1, 1)
    with connection.cursor() as cursor:
        cursor.execute("SELECT pg_get_viewdef('vw_mscc_data'::regclass, true)")
        raw = cursor.fetchone()[0]
    assert 'Zaynab-Test' in raw and catalogue['definition_sha256'] == hashlib.sha256(raw.encode()).hexdigest()
    staff = payload['power_bi']['related']['vw_center_program_staff']
    assert staff['by'] == ['is_active_current_round'] and staff['measures'] == ['rows', 'ids']
    assert sorted(staff['rows'], key=str) == [['<other>', 1, 1], ['<other>', 1, 1], ['Yes', 1, 1]]
    text = json.dumps(payload)
    assert 'Zaynab' not in text and 'Secret' not in text and '900001' not in text
    assert payload['power_bi']['base']['mode'] == 'view'


def test_mask_keeps_codes_and_masks_the_rest():
    text = ("SELECT \"it's\" FROM t WHERE a = 'Ali O''Neil'::text AND b = E'x\\'y' AND c = 'TLS'::text "
            "AND d = '2025-01-01'::date AND e = '{}'::jsonb AND f = 'level_one' AND g = '{}'::text "
            "AND h IN (1, 2, 3, 4, 5, 6, 7, 8, 9, 10) AND i IN (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11)")
    masked, literals, lists = power_bi.mask(text, keep=frozenset({'level_one'}))
    assert masked == ("SELECT \"it's\" FROM t WHERE a = '<masked text, 10 chars>'::text AND b = "
                      "'<masked text, 4 chars>' AND c = 'TLS'::text AND d = '2025-01-01'::date AND e = '{}'::jsonb "
                      "AND f = 'level_one' AND g = '<masked text, 2 chars>'::text "
                      "AND h IN (1, 2, 3, 4, 5, 6, 7, 8, 9, 10) AND i IN (<11 numbers>)")
    assert (literals, lists) == (3, 1)
    assert power_bi.error_message(RuntimeError('invalid input syntax for type integer: "Zaynab"\nmore')) == (
        'invalid input syntax for type integer: "..."')


def test_choice_values_of_the_tables_read_are_kept():
    from student_registration.clm.models import Bridging as Model

    values = power_bi.choice_values({Model._meta.db_table, 'no_such_table'})
    assert values and all(v == v.casefold() for v in values)


# -------------------------------------------------------------------------------- read only
def test_the_read_only_transaction(settings):
    settings.FIGURES_STATEMENT_TIMEOUT_MS = 12345
    settings.FIGURES_WORK_MEM = '8MB'
    with engine.read_only_transaction() as alias:
        with connection.cursor() as cursor:
            for name, value in (('transaction_read_only', 'on'), ('statement_timeout', '12345ms'),
                                ('work_mem', '8MB'), ('max_parallel_workers_per_gather', '0')):
                cursor.execute('SHOW %s' % name)
                assert cursor.fetchone()[0] == value
        assert PartnerOrganization.objects.using(alias).count() >= 0  # the ORM reads under the same limits
        with pytest.raises(Exception, match='read-only transaction'):
            with transaction.atomic():
                PartnerOrganization.objects.create(name='Not written')
    PartnerOrganization.objects.create(name='Written after')  # the outer transaction can write again
    with engine.read_only_cursor() as cursor:
        cursor.execute('SHOW transaction_read_only')
        assert cursor.fetchone()[0] == 'on'


# ---------------------------------------------------------------------------------- Bridging
def test_bridging_counts_the_views_rows(bridging, dirasa_more):
    school_b, other = dirasa_more['school_b'], dirasa_more['other']
    run('CREATE VIEW vw_bridging_data AS SELECT b.id, b.round_id, '
        "CASE WHEN b.learning_result = 'dropout' THEN %d ELSE b.partner_id END AS partner_id, "
        "CASE WHEN b.learning_result = 'dropout' THEN %d ELSE b.school_id END AS school_id, "
        's.first_name AS student_first_name FROM %s b JOIN %s s ON s.id = b.student_id'
        % (other.id, school_b.id, Bridging._meta.db_table, Student._meta.db_table))
    payload = build('bridging', 'Bridging 2025')
    power = payload['power_bi']
    assert power['base']['mode'] == 'view' and power['base']['overrides'] == ['partner', 'school']
    assert power['base']['period_rule'] == 'round'
    enrolment = payload['cubes']['enrolment']
    assert enrolment['measures'] == ['registrations', 'pre_tested', 'post_tested', 'view_rows']
    assert total(enrolment, 'registrations') == 2  # the deleted one in the view is left out
    assert total(enrolment, 'registrations', partner=other.id, school=school_b.id) == 1
    assert table(payload['blocks']['registrations'], 'partner') == {(bridging['partner'].id,): [1, 1, 0],
                                                                    (other.id,): [1, 0, 0]}
    assert table(payload['blocks']['sites'])[()] == [2]
    schools = {s['id']: s for s in payload['schools']}
    assert schools[school_b.id]['partners'] == [other.id]
    totals = power['reconciliation']['totals']
    assert (totals['view_rows'], totals['deleted_in_view'], totals['counted'], totals['counted_children']) == (
        3, 1, 2, 2)
    assert power['reconciliation']['by'] == ['in_view', 'in_before', 'counted', 'deleted', 'no_student',
                                             'other_round']
    check = power['key_check']
    assert (check['rows'], check['same_round'], check['same_partner'], check['same_school']) == (3, 3, 2, 2)
    assert set(check) == {'rows', 'ids', 'found', 'same_round', 'same_partner', 'same_school', 'deleted_rows',
                          'max_rows_per_id', 'conflicting', 'verified'}
    assert payload['school_totals'] == {
        'listed': {'schools': 2, 'children': 100, 'children_male': 40, 'children_female': 60,
                   'children_lebanese': 30, 'children_non_lebanese': 70, 'cwd': 5, 'dirasa_children': 12,
                   'dirasa_cwd': 2},
        'all': {'schools': 2, 'children': 100, 'children_male': 40, 'children_female': 60,
                'children_lebanese': 30, 'children_non_lebanese': 70, 'cwd': 5, 'dirasa_children': 12,
                'dirasa_cwd': 2}}
    period = power['periods'][0]
    assert (period['name'], period['current'], period['view_rows'], period['deleted_rows']) == (
        'Bridging 2025', True, 3, 1)
    assert 'Secret' not in json.dumps(payload)


def test_bridging_without_a_view_counts_as_before(bridging):
    payload = build('bridging', 'Bridging 2025')
    power = payload['power_bi']
    assert power['base']['mode'] == 'rule' and power['base']['reason'] == 'view missing'
    assert total(payload['cubes']['enrolment'], 'registrations') == 2
    assert payload['school_totals']['all']['schools'] == 1
    t, f = True, False
    assert bucket(power['reconciliation']) == {(f, t, t, f, f, f): [2, 0, 2]}


# ------------------------------------------------------------------------------------- youth
def test_youth_population_picks_the_registration_key(db):
    from student_registration.adolescent.models import Adolescent
    from student_registration.youth.models import EnrolledPrograms, MasterProgram, Registration, Year

    year = Year.objects.create(name='2026', current_year=True)
    partner = PartnerOrganization.objects.create(name='Youth Partner', is_youth=True)
    master = MasterProgram.objects.create(number='1', name='Skills', active=True)
    registrations = []
    for index in range(4):
        person = Adolescent.objects.create(first_name='Secret', gender='Female', birthday_year='2008')
        registrations.append(Registration.objects.create(year=year, adolescent=person, partner=partner))
    for registration in registrations[:3]:
        for _ in range(2):
            EnrolledPrograms.objects.create(registration=registration, master_program=master)
    enrolments = EnrolledPrograms._meta.db_table
    run('CREATE VIEW vw_youth_data_all AS SELECT e.id, e.registration_id, r.partner_id, r.deleted, r.year_id '
        'FROM %s e JOIN youth_registration r ON r.id = e.registration_id' % enrolments)
    population = power_bi.population('youth', '2026', year=year)
    assert (population.mode, population.key, population.period_column) == ('view', 'registration_id', 'year_id')
    assert sorted(zip(population.ids, population.rows)) == [(r.id, 2) for r in registrations[:3]]
    assert population.key_check['verified'] is True
    shown = repr(population)  # what a log line or an error report would print: never the ids
    assert 'ids=' not in shown and 'rows=' not in shown and 'overrides=' not in shown and "mode='view'" in shown
    everything = power_bi.population('youth', 'all')
    assert everything.mode == 'view' and everything.period_column is None and len(everything.ids) == 3
    counted = Registration.objects.filter(deleted=False)
    power = power_bi.block('youth', '2026', population, counted, counted, current=True, period_rule='year')
    assert power['reconciliation']['measures'] == ['registrations', 'view_rows', 'people']
    assert power['reconciliation']['totals']['view_people'] == 3 and power['periods'][0]['name'] == '2026'
    t, f = True, False
    assert bucket(power['reconciliation'])[(f, t, f, f, f, f, t, f)] == [1, 0, 1]  # no enrolment

    run('DROP VIEW vw_youth_data_all')  # keyed by the enrolment id: ids overlap as numbers but are not the key
    run('CREATE VIEW vw_youth_data_all AS SELECT e.id, %d AS partner_id, r.year_id FROM %s e '
        'JOIN youth_registration r ON r.id = e.registration_id' % (partner.id + 1000, enrolments))
    fallback = power_bi.population('youth', '2026', year=year)
    assert fallback.mode == 'rule' and fallback.reason.startswith('key check:')


def test_options_ignore_unknown_values(settings):
    settings.FIGURES_POWER_BI = {'mscc': {'base': 'nonsense', 'deleted': 'include'}}
    assert power_bi.options('mscc') == {'base': 'auto', 'deleted': 'include', 'period': 'round_year'}
    del settings.FIGURES_POWER_BI
    assert power_bi.options('bridging') == {'base': 'auto', 'deleted': 'exclude'}


def test_a_past_year_has_no_periods_nor_related_profiles(seeded):
    mscc_view()
    power = build('mscc', '2024')['power_bi']
    assert power['base']['mode'] == 'view' and power['periods'] == [] and power['related'] == {}
    assert power['reconciliation']['totals']['counted'] == 1
    assert datetime.datetime.fromisoformat(power['checked_at'])
