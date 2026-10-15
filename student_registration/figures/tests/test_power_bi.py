"""Counting over the views the Power BI dashboards read (power_bi.py), with stand-in views.

The real views exist only in production; each test creates a stand-in under the real name inside the
test transaction (rolled back afterwards). The fixtures' children and teachers are named "Secret".
"""

import datetime
import hashlib
import json
import re
from unittest import mock

import pytest
from celery.exceptions import SoftTimeLimitExceeded
from django.db import OperationalError, connection, transaction
from psycopg.pq import TransactionStatus

from student_registration.child.models import Child
from student_registration.clm.models import Bridging
from student_registration.figures import education, engine, power_bi
from student_registration.locations.models import Center, ProgramStaff
from student_registration.mscc import models as m
from student_registration.schools.models import PartnerOrganization, School
from student_registration.students.models import Student, Teacher

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
                                  'same_partner_or_centre': 3, 'same_center': 3, 'deleted_rows': 1, 'null_keys': 0,
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
    assert power_bi.readable('mscc') is False  # what the snapshots' staleness asks (no data read)
    run('RESET ROLE')
    assert power_bi.readable('mscc') is True


def test_a_period_counted_without_the_view_is_stale_once_the_view_can_be_read(seeded, settings):
    """A past period counted with the rule because the view could not be read (missing, not a view, no SELECT
    permission) follows at the next run once it can be (a GRANT given, the view created again by hand), as
    the current period does, rather than a week later; a period counted with the rule for what the view's
    rows hold, or under the setting ``rule``, does not (no daily recount)."""
    from student_registration.figures import snapshots
    from student_registration.figures.models import FiguresSnapshot

    client = base._service_client()

    def stale():
        index = {p['programme']: p for p in client.get('/api/figures/').json()['programmes']}
        by_index = {y['year']: y['stale'] for y in index['mscc']['years']}
        by_snapshot = {year: snapshots.is_stale(snapshots.latest('mscc', year)) for year in ('2025', '2024')}
        assert by_index == by_snapshot
        return by_index

    def counted(year=None):
        power = snapshots.refresh('mscc', year).payload['power_bi']['base']
        return power['mode'], power['reason']

    assert counted() == counted('2024') == ('rule', 'view missing')
    assert stale() == {'2025': False, '2024': False}  # while the view stays missing: no recount
    mscc_view()  # created again by hand (SPEC E3)
    assert stale() == {'2025': True, '2024': True}
    assert counted() == counted('2024') == ('view', '')
    assert stale() == {'2025': False, '2024': False}
    # a table under the view's name (not a view): the same once a view replaces it
    FiguresSnapshot.objects.all().delete()
    run('DROP VIEW vw_mscc_data')
    run('CREATE TABLE vw_mscc_data (id integer, round_id integer)')
    assert counted('2024') == ('rule', 'vw_mscc_data is a table, not a view') and counted()[0] == 'rule'
    assert stale() == {'2025': False, '2024': False}
    run('DROP TABLE vw_mscc_data')
    mscc_view()
    assert stale() == {'2025': True, '2024': True}
    # counted with the rule for what the view's rows hold: the view can be read, nothing new until the week
    FiguresSnapshot.objects.all().delete()
    run('DROP VIEW vw_mscc_data')
    mscc_view(columns='r.id + 100000 AS id, r.round_id, r.partner_id, r.center_id')
    assert counted('2024')[1].startswith('key check') and counted()[0] == 'rule'
    assert stale() == {'2025': False, '2024': False}
    # counted under the setting ``rule`` while the view was missing: the view coming back changes nothing
    FiguresSnapshot.objects.all().delete()
    run('DROP VIEW vw_mscc_data')
    settings.FIGURES_POWER_BI = {'mscc': {'base': 'rule'}}
    assert counted('2024') == counted() == ('rule', 'view missing')
    mscc_view()
    assert stale() == {'2025': False, '2024': False}
    # no SELECT permission (a GRANT given later; test_no_select_permission checks power_bi.readable itself),
    # and the view's state asked once per programme in the index, only for a year counted without the view
    FiguresSnapshot.objects.all().delete()
    settings.FIGURES_POWER_BI = {}
    assert counted() == counted('2024') == ('view', '')
    denied = {'mode': 'rule', 'reason': 'no SELECT permission on vw_mscc_data', 'setting': 'auto',
              'deleted': 'exclude', 'period_rule': 'round_year'}
    past = FiguresSnapshot.objects.get(year='2024')
    past.payload['power_bi']['base'] = denied
    past.save()
    for readable in (False, True):
        with mock.patch.object(power_bi, 'readable', return_value=readable) as asked:
            assert stale() == {'2025': False, '2024': readable}
        assert asked.call_count == 2  # once for the whole index, once for is_stale of 2024


def test_a_timeout_reading_the_view(seeded, settings):
    mscc_view(where=STANDARD + ' AND pg_sleep(0.5) IS NOT NULL')
    settings.FIGURES_STATEMENT_TIMEOUT_MS = 300
    payload = build()
    power = assert_rule_mode(payload, 'QueryCanceled: canceling statement due to statement timeout')
    # one timeout: the view that just timed out is not read again for its rows per round
    assert power['errors'] == ['population: QueryCanceled: canceling statement due to statement timeout']
    assert power['periods'] == []
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
                                ('work_mem', '8MB'), ('max_parallel_workers_per_gather', '0'),
                                ('jit', 'off')):  # JIT compiled the counts for seconds (engine.py)
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
    settings.FIGURES_JIT = True
    with engine.read_only_cursor() as cursor:
        cursor.execute('SHOW jit')
        assert cursor.fetchone()[0] == 'on'


# ---------------------------------------------------------------------------------- Bridging
def test_bridging_counts_the_views_rows(bridging, dirasa_more):
    school_b, other = dirasa_more['school_b'], dirasa_more['other']
    # a name typed by mistake in a teacher's yes/no answer (10 characters at most): never sent
    Teacher.objects.create(first_name='Secret', sex='Female', round=bridging['round'], school=bridging['school'],
                           is_active_current_round='Zaynab-Tst')
    # a school only a non-Dirasa partner lists: in the "all" totals, not in the "listed" ones
    school_c = School.objects.create(number='1003', name='School C', number_children=7, number_children_male=3,
                                     number_children_female=4, number_children_lebanese=1,
                                     number_children_non_lebanese=6, number_children_sbp=2,
                                     number_total_children_disability=1, number_dirasa_children_disability=1)
    PartnerOrganization.objects.get(name='Not Dirasa').schools.add(school_c)
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
                          'null_keys', 'max_rows_per_id', 'conflicting', 'verified'}
    assert payload['school_totals'] == {
        'listed': {'schools': 2, 'children': 100, 'children_male': 40, 'children_female': 60,
                   'children_lebanese': 30, 'children_non_lebanese': 70, 'cwd': 5, 'dirasa_children': 12,
                   'dirasa_cwd': 2},
        'all': {'schools': 3, 'children': 107, 'children_male': 43, 'children_female': 64,
                'children_lebanese': 31, 'children_non_lebanese': 76, 'cwd': 6, 'dirasa_children': 14,
                'dirasa_cwd': 3}}
    period = power['periods'][0]
    assert (period['name'], period['current'], period['view_rows'], period['deleted_rows']) == (
        'Bridging 2025', True, 3, 1)
    staff = payload['blocks']['staff']
    assert {row[0] for g in staff['figures'] if g['by'] == ['active'] for row in g['rows']} == {
        'Yes', 'Not specified'}
    assert {row[g['by'].index('active')] for g in staff['figures'] if 'active' in g['by'] for row in g['rows']} <= {
        'Yes', 'No', 'Not specified'}
    text = json.dumps(payload)
    assert 'Secret' not in text and 'Zaynab' not in text


def test_the_teachers_profile_counts_the_rounds_of_the_period_however_many_rounds_the_view_has(bridging):
    """vw_teacher_data holds the teachers of every CLM round (Teacher.round: the rounds every CLM programme
    shares). Profiled over the whole view, by round and flag, more than 50 groups were cut at 50 in ascending
    round order: the current round, the newest, was the one dropped, and NeuroDB's teachers version 'view_rows'
    (the period's rows) was never available. The period's rounds only are counted; a view of every round with
    no round column to choose by keeps its newest groups when cut."""
    from student_registration.schools.models import CLMRound

    school, current = bridging['school'], bridging['round']
    for i in range(30):  # older rounds (lower ids than the period's), each with teachers active and not
        older = CLMRound.objects.create(id=-1 - i, name='Old round %d' % i,
                                        start_date_bridging=datetime.date(2000 + i % 20, 9, 1))
        for active in ('yes', 'no'):
            Teacher.objects.create(first_name='Secret', sex='Male', round=older, school=school,
                                   is_active_current_round=active)
    for _ in range(4):
        Teacher.objects.create(first_name='Secret', sex='Female', round=current, school=school,
                               is_active_current_round='yes')
    run('CREATE VIEW vw_bridging_data AS SELECT b.id, b.round_id, b.partner_id, b.school_id FROM %s b'
        % Bridging._meta.db_table)
    run('CREATE VIEW vw_teacher_data AS SELECT t.id, t.round_id, t.is_active_current_round FROM %s t'
        % Teacher._meta.db_table)
    payload = build('bridging', 'Bridging 2025')
    teachers = payload['power_bi']['related']['vw_teacher_data']
    assert teachers == {'exists': True, 'by': ['round_id', 'is_active_current_round'], 'measures': ['rows', 'ids'],
                        'rows': [[current.id, 'yes', 5, 5]], 'truncated': False, 'rounds': [current.id]}
    assert total(payload['cubes']['teachers'], 'teachers') == 5  # the fixture's teacher and these four

    # a view of every round with no round column: every row, as before
    run('DROP VIEW vw_teacher_data')
    run('CREATE VIEW vw_teacher_data AS SELECT t.id, t.is_active_current_round FROM %s t' % Teacher._meta.db_table)
    teachers = build('bridging', 'Bridging 2025')['power_bi']['related']['vw_teacher_data']
    assert teachers['rows'] == [['no', 30, 30], ['yes', 35, 35]] and 'rounds' not in teachers
    # Makani's related views are not by the programme's rounds (no round_profiled)
    assert power_bi.SOURCES['mscc'].round_profiled == ()


def test_a_cut_profile_keeps_the_newest_rounds(seeded):
    """A profiled view of every round, not chosen by the period's rounds (Makani's): when it has more than 50
    (round, flag) groups, the newest rounds are kept and the oldest cut."""
    run('CREATE VIEW vw_center_program_staff AS SELECT g AS id, g / 2 AS round_id, mod(g, 2) = 0 AS is_active '
        'FROM generate_series(1, 120) g')
    mscc_view()
    staff = build()['power_bi']['related']['vw_center_program_staff']
    assert staff['by'] == ['round_id', 'is_active'] and staff['truncated'] and 'rounds' not in staff
    # rounds 0 to 60 (60 alone active, 0 alone not): 121 groups, the newest 50 kept
    assert staff['rows'][0] == [60, True, 1, 1] and staff['rows'][1:3] == [[59, False, 1, 1], [59, True, 1, 1]]
    assert [row[0] for row in staff['rows']] == [60] + [r for r in range(59, 35, -1) for _ in 'ft'] + [35]


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


# ------------------------------------------------------------------- the limits of every read
# What a count reads: the views (and their catalogue entries), the registrations and their records, the
# rounds and years that choose the period (and their metadata), staff, teachers, and the schools' reported
# numbers it adds up
WATCHED = re.compile(r'\b(vw_\w+|mscc_\w+|schools_clmround|youth_year|clm_bridging|youth_registration|'
                     r'youth_enrolledprograms|'
                     r'attendances_\w+|locations_programstaff|students_teacher|pg_class|pg_rewrite|'
                     r'SUM\("schools_school)\b')
LIMITS = {'transaction_read_only': 'on', 'statement_timeout': '54321ms'}


class LimitSpy:
    """For each statement reading a view or a table of WATCHED, the transaction's READ ONLY flag and
    statement timeout, asked on the raw connection just before the statement runs."""

    def __init__(self):
        self.seen = []

    def __call__(self, execute, sql, params, many, context):
        found = WATCHED.search(sql)
        if found:
            raw, state = context['connection'].connection, {}
            if raw.info.transaction_status in (TransactionStatus.IDLE, TransactionStatus.INTRANS):
                for name in LIMITS:
                    state[name] = raw.execute('SHOW %s' % name).fetchone()[0]
            self.seen.append((found.group(1), state, sql[:90]))
        return execute(sql, params, many, context)

    def outside(self):
        return [(table, state, sql) for table, state, sql in self.seen if state != LIMITS]


def read_under_the_limits(build, settings):
    """``build()`` run in autocommit, as in the worker (a test transaction would hide a statement run
    outside the limits behind the transaction's own settings): every read of WATCHED is READ ONLY and
    under the statement timeout. Returns the payload and the tables read."""
    settings.FIGURES_STATEMENT_TIMEOUT_MS = 54321
    spy = LimitSpy()
    with connection.execute_wrapper(spy):
        payload = build()
    assert spy.seen and spy.outside() == []
    return payload, {table for table, _state, _sql in spy.seen}


@pytest.mark.django_db(transaction=True)
@pytest.mark.parametrize('empty', [False, True], ids=['view', 'empty view'])
def test_every_read_of_a_makani_count_runs_under_the_limits(seeded, settings, empty):
    mscc_view(where=STANDARD + (' AND r.round_id <> %d' % seeded['current'].id if empty else ''))
    run('CREATE VIEW vw_center_program_staff AS SELECT ps.id, ps.is_active_current_round FROM '
        'locations_programstaff ps')
    try:
        payload, tables = read_under_the_limits(build, settings)
    finally:
        run('DROP VIEW vw_mscc_data')
        run('DROP VIEW vw_center_program_staff')
    power = payload['power_bi']
    if empty:  # the gate counted the rule's registrations: under the limits too
        assert power['base']['reason'] == 'the view has no rows for 2025 while 2 registrations do'
    else:
        assert power['base']['mode'] == 'view' and power['periods']
    assert payload['power_bi']['related']['vw_center_program_staff']['rows']
    assert {'vw_mscc_data', 'vw_center_program_staff', 'mscc_registration', 'mscc_round', 'locations_programstaff',
            'pg_class', 'pg_rewrite'} <= tables


@pytest.mark.django_db(transaction=True)
@pytest.mark.parametrize('empty', [False, True], ids=['view', 'empty view'])
def test_every_read_of_a_bridging_count_runs_under_the_limits(bridging, dirasa_more, settings, empty):
    run('CREATE VIEW vw_bridging_data AS SELECT b.id, b.round_id, b.partner_id, b.school_id FROM %s b%s'
        % (Bridging._meta.db_table, ' WHERE FALSE' if empty else ''))
    run('CREATE VIEW vw_teacher_data AS SELECT t.id, t.round_id FROM students_teacher t')
    try:
        payload, tables = read_under_the_limits(lambda: build('bridging', 'Bridging 2025'), settings)
    finally:
        run('DROP VIEW vw_bridging_data')
        run('DROP VIEW vw_teacher_data')
    reason = payload['power_bi']['base']['reason']
    assert reason == ('the view has no rows for Bridging 2025 while 2 registrations do' if empty else '')
    assert payload['power_bi']['related']['vw_teacher_data']['rows'] and payload['school_totals']
    assert {'vw_bridging_data', 'vw_teacher_data', 'clm_bridging', 'schools_clmround', 'students_teacher',
            'SUM("schools_school', 'pg_class'} <= tables


# ------------------------------------------------------------- the ids never in the SQL text
def statements_sent(build):
    """``build()``'s statements: (the parameters, the statement text psycopg sent to the server)."""
    sent = []

    def spy(execute, sql, params, many, context):
        try:
            return execute(sql, params, many, context)
        finally:
            query = getattr(context['cursor'].cursor, '_query', None)
            sent.append((list(params or ()), bytes(getattr(query, 'query', b'') or b'').decode('utf-8', 'replace')))

    with connection.execute_wrapper(spy):
        payload = build()
    return payload, sent


def test_the_views_registration_ids_are_never_in_the_sql_text(seeded, bridging):
    """PostgreSQL logs the text of a failing statement (log_min_error_statement): the arrays of the view's
    registration ids are sent as parameters, apart from the text."""
    mscc_view()
    run('CREATE VIEW vw_bridging_data AS SELECT b.id, b.round_id, b.partner_id, b.school_id FROM %s b'
        % Bridging._meta.db_table)
    cases = (('mscc', '2025', m.Registration.objects.filter(round=seeded['current']).exclude(type='TLS')),
             ('bridging', 'Bridging 2025', Bridging.objects.filter(round=bridging['round'])))
    for name, year, in_view in cases:
        payload, sent = statements_sent(lambda: build(name, year))
        assert payload['power_bi']['base']['mode'] == 'view'
        ids = power_bi.int_array(sorted(in_view.values_list('id', flat=True)))
        carrying = [text for params, text in sent if ids in params]
        assert len(carrying) >= 5  # the blocks, the cubes and the reconciliation
        assert all(text and ids not in text and '$1' in text for text in carrying)
        assert not any(ids in text for _params, text in sent)


# ------------------------------------------------------ the services' branches read the period only
def _rows_out(node, kind):
    """The rows the plan's ``kind`` nodes returned, over every loop."""
    own = node['Actual Rows'] * node['Actual Loops'] if node['Node Type'] == kind else 0
    return own + sum(_rows_out(child, kind) for child in node.get('Plans') or ())


@pytest.mark.parametrize('name, year', [('mscc', '2025'), ('bridging', 'Bridging 2025')])
def test_each_services_branch_reads_the_views_registrations_only(seeded, bridging, name, year):
    """The services block is one UNION ALL branch per service table (Makani) or per service answer (Bridging).
    PostgreSQL does not push the join with the view's population, outside the union, into its branches: each
    branch read its whole table, every year's records, and the union of them all was sorted before the join
    (8.5 times slower on 180,000 registrations over 8 years, growing with the history). Each branch is
    restricted by itself: the union returns the period's rows only."""
    from student_registration.schools.models import CLMRound

    mscc_view()
    run('CREATE VIEW vw_bridging_data AS SELECT b.id, b.round_id, b.partner_id, b.school_id FROM %s b'
        % Bridging._meta.db_table)
    for registration in (seeded['old'], seeded['tls']):  # services of registrations outside the view's 2025
        m.EducationService.objects.create(registration=registration, education_program='ABLN')
        m.PSSService.objects.create(registration=registration)
    Bridging.objects.create(student=Bridging.objects.filter(deleted=False).first().student,
                            round=CLMRound.objects.create(name='Bridging 2024'), partner=bridging['partner'],
                            school=bridging['school'], receiving_transportation_support='yes',
                            using_digital_platform='yes')
    captured = []
    real = engine.figures_block

    def figures_block(sql, params, dimensions, *args):
        if 'service' in dimensions:
            captured.append((sql, params))
        return real(sql, params, dimensions, *args)

    with mock.patch.object(engine, 'figures_block', figures_block):
        payload = build(name, year)
    assert payload['power_bi']['base']['mode'] == 'view' and not payload['blocks']['services'].get('error')
    [(sql, params)] = captured
    with engine.read_only_cursor(bind_on_server=True) as cursor:
        cursor.execute('EXPLAIN (ANALYZE, FORMAT JSON) ' + sql, params)
        found = cursor.fetchone()[0]
    plan = (json.loads(found) if isinstance(found, str) else found)[0]['Plan']
    counted = plan['Actual Rows'] * plan['Actual Loops']  # the period's service rows (the join's output)
    assert counted == {'mscc': 3, 'bridging': 2}[name]  # the girl's education and PSS records; a's two answers
    assert _rows_out(plan, 'Append') == counted  # no other year's record read into the union


def _timeout(*args, **kwargs):
    raise OperationalError('canceling statement due to statement timeout')


def test_a_failing_part_is_logged_by_its_class_never_with_the_exception(seeded, bridging, caplog):
    """SPEC §7: the population is never logged or sent. The variables of a count's frames hold it (the SQL
    parameters: every registration id of the view for the period, its rows, partner and centre or school), and
    an error reporter with its defaults (Sentry in production: local variables on) sends the variables of every
    frame of an exception it is given. So a failing part (a timeout is an ordinary failure) is logged by its
    class and first line only, never with ``exc_info``."""
    import logging

    mscc_view()
    run('CREATE VIEW vw_bridging_data AS SELECT b.id, b.round_id, b.partner_id, b.school_id FROM %s b'
        % Bridging._meta.db_table)
    caplog.set_level(logging.DEBUG)
    failing = [(engine, 'figures_block'), (engine, 'cube'), (power_bi, 'block'), (power_bi, 'population'),
               (education.Makani, '_pending_round'), (education.Bridging, '_school_totals')]
    for target, name in failing:
        with mock.patch.object(target, name, _timeout):
            for programme, year in (('mscc', '2025'), ('bridging', 'Bridging 2025')):
                build(programme, year)
    failures = [r.getMessage() for r in caplog.records if r.levelno >= logging.ERROR]
    for part in ('figures block registrations failed', 'figures cube enrolment failed',
                 'the view population failed', 'the power_bi block failed', 'figures mscc 2025: pending_round failed',
                 'figures bridging Bridging 2025: school_totals failed'):
        assert any(text.startswith(part) or (': ' + part) in text for text in failures), part
    assert all(text.endswith('OperationalError: canceling statement due to statement timeout') for text in failures)
    assert [r for r in caplog.records if r.exc_info] == []  # nothing an error reporter could unfold
    ids = [power_bi.int_array(sorted(q.values_list('id', flat=True))) for q in (
        m.Registration.objects.filter(round=seeded['current']).exclude(type='TLS'),
        Bridging.objects.filter(round=bridging['round']))]
    assert not any(i in r.getMessage() for i in ids for r in caplog.records)


# ------------------------------------------------------------- what Sentry may send (error_reports.py)
def test_an_error_report_passing_through_a_count_loses_the_variables_of_its_frames():
    """Production's Sentry ``before_send``: an exception that passes through a count anyway (an abort of the
    worker inside a query, a failure in code added later) is sent without the variables of any of its frames
    (Django's and psycopg's below the count hold the same SQL parameters); any other event is left as it is."""
    from student_registration.figures.error_reports import drop_count_variables

    def frame(module, path='', **variables):
        return {'module': module, 'abs_path': path, 'function': 'f', 'lineno': 1, 'vars': variables}

    def event(*frames, chained=()):
        values = [{'type': 'RuntimeError', 'stacktrace': {'frames': list(chained)}}] if chained else []
        values.append({'type': 'SystemExit', 'value': '1', 'stacktrace': {'frames': list(frames)}})
        return {'exception': {'values': values}, 'threads': {'values': [{'stacktrace': {'frames': [
            frame('threading', lock='<lock>')]}}]}}

    ids = "'{57,58,59,60,61}'"
    through = [
        event(frame('django.core.handlers.base', request='<WSGIRequest GET>'),
              frame('student_registration.youth.indicator_figures', view_partner="{'57': '52'}"),
              frame('django.db.backends.utils', params='[%s]' % ids)),
        event(frame('django.core.handlers.base'), frame('django.db.backends.utils', params='[%s]' % ids),
              chained=[frame('student_registration.figures.engine', params='[%s]' % ids)]),  # in a chained one
        event(frame('django.db.backends.utils', params='[%s]' % ids),
              frame(None, '/app/student_registration/figures/education.py', sql_params='[%s]' % ids)),  # by path
        event(frame('rest_framework.views'), frame('student_registration.youth.indicator_figures_api', name='2026')),
    ]
    for sent in through:
        sent = drop_count_variables(sent, {})
        frames = [f for part in ('exception', 'threads') for v in sent[part]['values']
                  for f in v['stacktrace']['frames']]
        assert frames and not [f for f in frames if 'vars' in f] and ids not in json.dumps(sent)
        assert all(f['function'] == 'f' and f['lineno'] == 1 for f in frames)  # the rest is kept

    other = event(frame('student_registration.mscc.views', registration_id=57), frame('django.db.backends.utils'))
    assert drop_count_variables(json.loads(json.dumps(other)), {}) == other  # not a count: left as it is


def test_production_sends_its_error_reports_through_drop_count_variables():
    """config/settings/production.py (not importable in tests: it starts Sentry) gives Sentry the before_send."""
    import ast
    import pathlib

    path = pathlib.Path(__file__).resolve().parents[3] / 'config' / 'settings' / 'production.py'
    tree = ast.parse(path.read_text())
    imported = {(node.module, alias.name) for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)
                for alias in node.names}
    assert ('student_registration.figures.error_reports', 'drop_count_variables') in imported
    [init] = [node for node in ast.walk(tree) if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
              and node.func.attr == 'init' and getattr(node.func.value, 'id', None) == 'sentry_sdk']
    keywords = {k.arg: k.value for k in init.keywords}
    assert isinstance(keywords['before_send'], ast.Name) and keywords['before_send'].id == 'drop_count_variables'


# ---------------------------------------------------------------- the worker's time limit
def _interrupt(*args, **kwargs):
    raise SoftTimeLimitExceeded()


def _interrupt_related(name):
    if name != 'vw_mscc_data':
        raise SoftTimeLimitExceeded()
    return REAL_DESCRIBE(name)


def _interrupt_own(name):
    if name == 'vw_mscc_data':
        raise SoftTimeLimitExceeded()
    return REAL_DESCRIBE(name)


REAL_DESCRIBE = power_bi.describe


@pytest.mark.parametrize('programme, target, name, side_effect', [
    ('mscc', engine, 'figures_block', _interrupt),  # education.block
    ('mscc', engine, 'cube', _interrupt),  # education.cube
    ('mscc', power_bi, 'describe', _interrupt_own),  # the population's description of the view
    ('mscc', power_bi, 'key_check', _interrupt),  # the population's key check
    ('mscc', power_bi, 'population', _interrupt),  # view_population
    ('mscc', power_bi, 'describe', _interrupt_related),  # the block's related views
    ('mscc', power_bi, 'reconcile', _interrupt),
    ('mscc', power_bi, 'periods', _interrupt),
    ('mscc', power_bi, 'profile', _interrupt),
    ('mscc', power_bi, 'block', _interrupt),  # power_bi_block
    ('mscc', education.Makani, '_pending_round', _interrupt),
    ('bridging', education.Bridging, '_school_totals', _interrupt),
], ids=lambda value: getattr(value, '__name__', None) if callable(value) else None)
def test_the_time_limit_is_never_one_parts_failure(seeded, bridging, programme, target, name, side_effect):
    """The worker's soft time limit stops the count at once (snapshots.execute_run then names the targets
    left), wherever it strikes: never stored as one block's, cube's or part's error."""
    mscc_view()
    with mock.patch.object(target, name, side_effect=side_effect):
        with pytest.raises(SoftTimeLimitExceeded):
            build(programme, '2025' if programme == 'mscc' else 'Bridging 2025')


# ---------------------------------------------------------------- a view not described
def test_a_view_that_could_not_be_described_is_unknown_not_missing(seeded):
    mscc_view()
    run('CREATE VIEW vw_tls_data AS SELECT 1 AS id')

    def describe(name):
        if name in ('vw_mscc_data', 'vw_tls_data'):
            raise RuntimeError('canceling statement due to statement timeout')
        return REAL_DESCRIBE(name)

    with mock.patch.object(power_bi, 'describe', side_effect=describe):
        power = build()['power_bi']
    assert power['base']['mode'] == 'rule' and power['periods'] == []
    # NeuroDB must not take these for views that were dropped
    assert power['catalogue']['vw_mscc_data'] == {'exists': None, 'error': 'RuntimeError'}
    assert power['catalogue']['vw_tls_data'] == {'exists': None, 'error': 'RuntimeError'}
    assert power['catalogue']['vw_mscc_data_no_round'] == {'exists': False}
    assert power['errors'] == ['catalogue: RuntimeError: canceling statement due to statement timeout',
                               'catalogue vw_tls_data: RuntimeError: canceling statement due to statement timeout']
    with mock.patch.object(power_bi, 'population', side_effect=RuntimeError('boom')):
        assert build()['power_bi']['catalogue']['vw_mscc_data'] == {'exists': None, 'error': 'not described'}
