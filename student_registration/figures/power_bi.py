"""The views the Power BI dashboards read, and counting over their rows.

The Makani, Dirasa and Youth Power BI dashboards read three hand-made views of this database:
``vw_mscc_data``, ``vw_bridging_data`` and ``vw_youth_data_all``. Their definitions live only in the
production database (they are not in git and are re-created by hand), so the figures read them at count
time:

* ``describe(name)``: the catalogue entry of a view (no data): kind, columns, the relations it reads,
  its definition with every string literal and long number list masked, and the hash of the raw text;
* ``population(programme, period, ...)``: "view mode". The view's registration ids for the period (Makani: a
  year, the rounds of the year; Dirasa: a year, the CLM rounds of the year, ``bridging_year``), how
  many view rows each has, and the partner and centre/school the view gives it, held in the worker's
  memory for one count and joined into every count (``unnest`` of integer arrays). It is used only when
  a gate passes (the view exists and is a view, may be read, its key is the registration id, it has rows
  for the period or the rule has none either, and the setting allows it); otherwise "rule mode": the
  caller counts with its own rule, and the reason is given;
* ``block(...)``: the ``power_bi`` part of a payload: the mode and why, the catalogue, the key check, a
  reconciliation in counts (the view's registrations, what is counted, what was counted before, and why
  they differ), the view's rows per round or year, and counts of a few related views.

Privacy: ids never leave this module's SQL and the worker's memory; no row of a view is ever fetched
except the population (integers: registration ids, row counts, partner and centre/school ids); every
other query returns counts; the definitions are masked; logs never print SQL parameters.
"""

from __future__ import annotations

import hashlib
import logging
import re
from dataclasses import dataclass, field

from django.conf import settings
from django.db import connections
from django.utils import timezone

from . import engine

logger = logging.getLogger(__name__)

VERSION = 1
MAX_DEFINITION = 64 * 1024  # bytes (UTF-8) of masked definition kept
MAX_RELATED_ROWS = 50
READS_DEPTH = 3
INTEGER_TYPES = ('integer', 'bigint', 'smallint')
KINDS = {'r': 'table', 'v': 'view', 'm': 'materialized view', 'p': 'partitioned table', 'f': 'foreign table',
         'S': 'sequence', 'c': 'composite type', 'i': 'index', 'I': 'partitioned index', 't': 'TOAST table'}
FLAG_COLUMNS = ('round_id', 'year_id', 'deleted', 'is_active', 'is_active_current_round', 'current_year')
DEFAULTS = {
    'mscc': {'base': 'auto', 'deleted': 'exclude', 'period': 'round_year'},
    'bridging': {'base': 'auto', 'deleted': 'exclude', 'period': 'start_year'},
    'youth': {'base': 'auto', 'deleted': 'exclude'},
}
CHOICES = {'base': ('auto', 'view', 'rule'), 'deleted': ('exclude', 'include')}
# each programme's own period rules (the first is its default): Makani, the rounds whose year is Y or the rounds
# flagged current_year; Dirasa, the CLM rounds whose Bridging start date is in Y (bridging_year) or the Bridging
# rounds flagged current_year. Youth has none (its period is the Year).
PERIODS = {'mscc': ('round_year', 'current_rounds'), 'bridging': ('start_year', 'current_rounds')}
# The gate's reasons when the view cannot be read at all (rule mode, base.reason): what a later GRANT, or a missing
# view created again by hand (SPEC E3), changes without anything else changing (snapshots.stale, ``unreadable``).
# A view dropped and created again loses its grants (CREATE OR REPLACE keeps them): a counting role that does not
# own it can no longer read it ("no SELECT permission") until the grant is given again, or unless default
# privileges of the views' creator give it (docs: NeuroDB OPERATIONS.md, deploying the comparison, step 1).
VIEW_MISSING = 'view missing'
NOT_A_VIEW = ', not a view'  # '<view> is a <kind>, not a view'
NO_PERMISSION = 'no SELECT permission on '  # followed by the view's name


@dataclass(frozen=True)
class Source:
    programme: str            # 'mscc' | 'bridging' | 'youth'
    view: str                 # the view Power BI reads
    table: str                # the registrations table the view's key points to
    keys: tuple               # key column candidates, in order of preference
    periods: tuple            # period column candidates, in order of preference
    overrides: dict           # dimension -> view column, taken from the view when it has it
    related: tuple            # views described in the catalogue
    profiled: tuple           # related views whose rows are counted
    person: str               # the registration's person column (unique children / young people)
    person_label: str         # 'children' | 'people'
    period_of_registration: str  # the registration's own period column
    checks: tuple             # key check comparisons: (name, view column, SQL with {v} for the view's value)
    joins: str = ''           # extra joins of the key check (aliases: r = the registration)
    cross_checks: tuple = ()  # comparisons that must also agree (youth: ids of two tables overlap)
    # period columns whose check is required: the view's rows must have the registration's round for the key to
    # pass (youth: none, the view's own year decides)
    gated_periods: tuple = ('round_id',)
    # period columns whose check is shown, not required, and verifies the key when it reaches the threshold
    # (Dirasa's year: the view's own year decides)
    verifying_periods: tuple = ()
    # (period column, column used instead when the first gives the key check no row for the period and the view
    # has the second): Dirasa's year column may hold "2025-2026", which names no year
    period_fallbacks: tuple = ()
    round_profiled: tuple = ()  # profiled views whose round_id is the programme's round: the period's rows only


SOURCES = {
    'mscc': Source(
        'mscc', 'vw_mscc_data', 'mscc_registration', ('id',), ('round_id',),
        {'partner': 'partner_id', 'center': 'center_id'},
        related=('vw_mscc_data_no_round', 'vw_mscc_wl_data', 'vw_mscc_wl_data_no_round', 'vw_tls_data',
                 'vw_center_data', 'vw_center_program_staff'),
        profiled=('vw_center_program_staff', 'vw_center_data'),
        person='child_id', person_label='children', period_of_registration='round_id',
        checks=(('same_round', 'round_id', 'r.round_id IS NOT DISTINCT FROM {v}'),
                ('same_partner', 'partner_id', 'r.partner_id IS NOT DISTINCT FROM {v}'),
                ('same_partner_or_centre', 'partner_id',
                 'COALESCE(r.partner_id, c.partner_id) IS NOT DISTINCT FROM {v}'),
                ('same_center', 'center_id', 'r.center_id IS NOT DISTINCT FROM {v}')),
        joins='LEFT JOIN locations_center c ON c.id = r.center_id'),
    # Dirasa: the period is a year, the CLM rounds of the year (bridging_year). A view's year column (any type,
    # compared as text) chooses the year's rows when the view has one, as youth's, else its round_id; the year
    # agreement (the registration's round is a round of the year) is shown, not required.
    'bridging': Source(
        'bridging', 'vw_bridging_data', 'clm_bridging', ('id',), ('year', 'round_id'),
        {'partner': 'partner_id', 'school': 'school_id'},
        related=('vw_bridging_wl_data', 'vw_teacher_data', 'vw_outreach_data', 'vw_outreach_not_registered'),
        profiled=('vw_teacher_data',), round_profiled=('vw_teacher_data',),  # Teacher.round: a CLM round
        person='student_id', person_label='children', period_of_registration='round_id',
        checks=(('same_round', 'round_id', 'r.round_id IS NOT DISTINCT FROM {v}'),
                ('same_year', 'year', 'r.round_id = ANY({rounds})'),
                ('same_partner', 'partner_id', 'r.partner_id IS NOT DISTINCT FROM {v}'),
                ('same_school', 'school_id', 'r.school_id IS NOT DISTINCT FROM {v}')),
        verifying_periods=('year',), period_fallbacks=(('year', 'round_id'),)),
    # Youth: the period is a reporting year (youth rounds are not tied to a year, so a view's round_id cannot
    # choose one); the year agreement is shown, not required (the view's own year decides, SPEC D1); the key
    # must agree on partner or deleted, since enrolment and registration ids overlap as numbers.
    'youth': Source(
        'youth', 'vw_youth_data_all', 'youth_registration', ('registration_id', 'id'), ('year_id', 'year'),
        {'partner': 'partner_id'},
        related=('vw_youth_data', 'vw_youth_enrolledprograms', 'vw_youth_pd'), profiled=(),
        person='adolescent_id', person_label='people', period_of_registration='year_id',
        checks=(('same_year', 'year_id', 'r.year_id IS NOT DISTINCT FROM {v}'),
                ('same_year', 'year', 'yy.name IS NOT DISTINCT FROM {v}::text'),
                ('same_partner', 'partner_id', 'r.partner_id IS NOT DISTINCT FROM {v}'),
                ('same_deleted', 'deleted', 'r.deleted::text IS NOT DISTINCT FROM lower({v}::text)')),
        joins='LEFT JOIN youth_year yy ON yy.id = r.year_id',
        cross_checks=('same_partner', 'same_deleted'), gated_periods=()),
}
PERIOD_CHECKS = {'round_id': 'same_round', 'year_id': 'same_year', 'year': 'same_year'}
CROSS_MATCH = 0.95  # youth: share of rows whose partner / deleted agree with the registration's


def options(programme):
    """``FIGURES_POWER_BI[programme]`` over the defaults; unknown values fall back to the default, and a
    ``period`` is taken only from the programme's own list (``PERIODS``)."""
    chosen = dict(DEFAULTS.get(programme, {}))
    given = (getattr(settings, 'FIGURES_POWER_BI', None) or {}).get(programme) or {}
    choices = dict(CHOICES, period=PERIODS.get(programme, ()))
    for name, value in given.items():
        if name in choices and value in choices[name]:
            chosen[name] = value
    return chosen


YEAR_IN_NAME = re.compile(r'(?<!\d)((?:19|20)\d{2})(?!\d)')  # "Bridging 2025-2026" -> 2025


def bridging_year(the_round):
    """(year, how) of a CLM round for Dirasa: the year of its Bridging start date ('start_date'), else the
    first four-digit year in its name ('name'), else (None, None): the round is in no year. A round spanning
    two years belongs to the year of its start only."""
    start = getattr(the_round, 'start_date_bridging', None)
    if start is not None:
        return start.year, 'start_date'
    found = YEAR_IN_NAME.search(getattr(the_round, 'name', None) or '')
    if found:
        return int(found.group(1)), 'name'
    return None, None


def min_match():
    return float(getattr(settings, 'FIGURES_POWER_BI_MIN_MATCH', 0.99))


def related_on():
    return bool(getattr(settings, 'FIGURES_POWER_BI_RELATED', True))


def quote(name):
    return connections[engine.database_alias()].ops.quote_name(name)


def int_array(values):
    """An integer array as one text literal ('{1,2,NULL}'), cast to int[] in the SQL: parsed by the server
    in one go however long, unlike ARRAY[...] of separate constants."""
    return '{%s}' % ','.join('NULL' if v is None else str(int(v)) for v in values)


# -------------------------------------------------------------------------------- errors
QUOTED = re.compile(r'"[^"]*"|\'[^\']*\'')


def error_class(exc):
    """The database error's own class (QueryCanceled, InsufficientPrivilege...) rather than Django's wrapper."""
    cause = exc.__cause__
    if cause is not None and type(cause).__module__.split('.')[0] in ('psycopg', 'psycopg2'):
        return type(cause).__name__
    return type(exc).__name__


def error_message(exc):
    """The first line of the message, quoted text masked (a database message may quote a value)."""
    text = (str(exc).strip().splitlines() or [''])[0]
    return QUOTED.sub('"..."', text)[:200]


def error_line(exc):
    """``<ExceptionClass>: <first line, quoted text masked>``: how a failure of the counting code is logged.
    Never the exception itself (``logger.exception``, ``exc_info``): an error reporter (Sentry, with its
    defaults) would send the variables of every frame, which hold the view's registration ids, rows and
    partners (SPEC §7: the population is never logged or sent)."""
    return '%s: %s' % (error_class(exc), error_message(exc))


def error_text(part, exc):
    return '%s: %s' % (part, error_line(exc))


# -------------------------------------------------------------------------------- catalogue
LITERAL = re.compile(
    r'(?P<ident>"(?:[^"]|"")*")'
    r"|(?P<literal>(?<![\w$])[Ee]'(?:[^'\\]|\\.|'')*'|'(?:[^']|'')*')"
    r'|(?P<list>\(\s*%(n)s(?:\s*,\s*%(n)s){10,}\s*\)|ARRAY\[\s*%(n)s(?:\s*,\s*%(n)s){10,}\s*\])'
    % {'n': r'-?\d+(?:\.\d+)?(?:::[a-z ]+?)?'}
)
NUMBER = re.compile(r'-?\d+(?:\.\d+)?')
DATE_OR_YEAR = re.compile(r'^\d{4}(-\d{2}){0,2}$')
FIXED = {'yes', 'no', 'true', 'false', 't', 'f', 'tls', 'core-package', 'walk-in', 'male', 'female', 'other',
         'mother', 'father', ''}


def mask(text, keep=frozenset()):
    """``text`` with every string literal replaced by ``'<masked text, N chars>'`` unless it is a code
    (FIXED, a date or year, an empty JSON, or a value of ``keep``), and every list of 11 or more numbers
    by ``(<N numbers>)``. Returns (masked text, literals masked, lists masked)."""
    counts = {'literals': 0, 'lists': 0}

    def replace(match):
        if match.group('ident'):
            return match.group('ident')
        if match.group('list'):
            counts['lists'] += 1
            numbers = len(NUMBER.findall(match.group('list')))
            if match.group('list').startswith('ARRAY'):
                return 'ARRAY[<%d numbers>]' % numbers
            return '(<%d numbers>)' % numbers
        literal = match.group('literal')
        body = literal[2:-1] if literal[0] in 'Ee' else literal[1:-1]
        value = body.replace("''", "'")
        folded = value.casefold()
        after = text[match.end():match.end() + 8].lower()
        if (folded in FIXED or DATE_OR_YEAR.match(value) or folded in keep
                or (value in ('{}', '[]') and after.startswith('::json'))):
            return literal
        counts['literals'] += 1
        return "'<masked text, %d chars>'" % len(value)

    return LITERAL.sub(replace, text), counts['literals'], counts['lists']


def choice_values(tables):
    """The choice values declared in code on the models of ``tables`` (casefolded): codes, not data."""
    from django.apps import apps

    by_table = {model._meta.db_table: model for model in apps.get_models()}
    found = set()
    for table in tables:
        model = by_table.get(table)
        if model is None:
            continue
        for model_field in model._meta.get_fields():
            for value, _label in getattr(model_field, 'flatchoices', None) or ():
                if isinstance(value, str):
                    found.add(value.casefold())
    return frozenset(found)


def _reads(cursor, oid):
    """[[schema, relation, kind], ...] the view reads, with what the ``vw_*`` views it reads read."""
    found, seen, todo = [], {oid}, [(oid, 1)]
    while todo:
        current, depth = todo.pop(0)
        cursor.execute(
            "SELECT DISTINCT cl.oid, n.nspname, cl.relname, cl.relkind FROM pg_rewrite rw "
            "JOIN pg_depend d ON d.objid = rw.oid AND d.classid = 'pg_rewrite'::regclass "
            "AND d.refclassid = 'pg_class'::regclass "
            "JOIN pg_class cl ON cl.oid = d.refobjid JOIN pg_namespace n ON n.oid = cl.relnamespace "
            "WHERE rw.ev_class = %s::oid AND d.refobjid <> %s::oid ORDER BY 2, 3", [current, current])
        for ref, schema, name, kind in cursor.fetchall():
            if ref in seen:
                continue
            seen.add(ref)
            found.append([schema, name, KINDS.get(kind, kind)])
            if kind in ('v', 'm') and name.startswith('vw_') and depth < READS_DEPTH:
                todo.append((ref, depth + 1))
    return found


def describe(name):
    """The catalogue entry of the view ``name`` (no data); ``{"exists": false}`` when there is none."""
    with engine.read_only_cursor() as cursor:
        cursor.execute(
            'SELECT c.oid, c.relkind, n.nspname FROM pg_class c JOIN pg_namespace n ON n.oid = c.relnamespace '
            'WHERE c.oid = to_regclass(%s::text)', [name])
        row = cursor.fetchone()
        if row is None:
            return {'exists': False}
        oid, relkind, schema = row
        cursor.execute("SELECT has_table_privilege(current_user, %s::oid, 'SELECT')", [oid])
        can_select = bool(cursor.fetchone()[0])
        cursor.execute(
            'SELECT a.attname, format_type(a.atttypid, a.atttypmod) FROM pg_attribute a '
            'WHERE a.attrelid = %s::oid AND a.attnum > 0 AND NOT a.attisdropped ORDER BY a.attnum', [oid])
        columns = [[column, kind] for column, kind in cursor.fetchall()]
        raw, reads = '', []
        if relkind in ('v', 'm'):
            cursor.execute('SELECT pg_get_viewdef(%s::oid, true)', [oid])
            raw = cursor.fetchone()[0] or ''
            reads = _reads(cursor, oid)
    masked, literals, lists = mask(raw, choice_values({relation for _s, relation, _k in reads}))
    encoded = masked.encode('utf-8')
    return {
        'exists': True,
        'kind': KINDS.get(relkind, relkind),
        'schema': schema,
        'can_select': can_select,
        'columns': columns,
        'reads': reads,
        'definition': encoded[:MAX_DEFINITION].decode('utf-8', 'ignore'),
        'definition_sha256': hashlib.sha256(raw.encode('utf-8')).hexdigest(),
        'masked_literals': literals,
        'masked_lists': lists,
        'truncated': len(encoded) > MAX_DEFINITION,
    }


def readable(programme):
    """Whether the programme's view exists, is a view or a materialized view, and may be read by the counting
    role now: the gate's first conditions (D2), from the catalogue only (no data, one query)."""
    with engine.read_only_cursor() as cursor:
        cursor.execute(
            "SELECT c.relkind IN ('v', 'm') AND has_table_privilege(current_user, c.oid, 'SELECT') "
            'FROM pg_class c WHERE c.oid = to_regclass(%s::text)', [SOURCES[programme].view])
        row = cursor.fetchone()
    return bool(row and row[0])


def unreadable(base):
    """Whether a payload's ``power_bi.base`` says it was counted with the rule because the view could not be
    read at all (missing, not a view, no SELECT permission), rather than for what its rows hold (key check,
    no rows for the period) or the setting."""
    if not isinstance(base, dict) or base.get('mode') != 'rule':
        return False
    reason = str(base.get('reason') or '')
    return reason == VIEW_MISSING or reason.startswith(NO_PERMISSION) or reason.endswith(NOT_A_VIEW)


# ------------------------------------------------------------------------------- population
@dataclass
class Population:
    mode: str = 'rule'           # 'view' | 'rule'
    reason: str = ''             # why rule mode; '' in view mode
    view: str = ''
    key: str | None = None       # the key column used
    period_column: str | None = None  # the view column that chose the period, or 'registration'
    # registration ids of the period, view rows per id, and dimension -> values from the view (parallel to
    # ids): worker memory only, and out of repr() so that no log or error report can print them
    ids: list = field(default_factory=list, repr=False)
    rows: list = field(default_factory=list, repr=False)
    overrides: dict = field(default_factory=dict, repr=False)
    deleted: str = 'exclude'     # 'exclude' | 'include'
    key_check: dict = field(default_factory=dict)  # counts only
    setting: str = 'auto'        # FIGURES_POWER_BI[programme]['base']
    read: bool = False           # the view's rows of the period were read (ids hold them)
    failed: bool = False         # reading the view failed (e.g. a timeout): not read again in this count
    catalogue: dict = field(default_factory=dict)  # describe(view)
    errors: list = field(default_factory=list)
    period_values: list = field(default_factory=list)  # the period's round or year ids (None: every row)

    @property
    def joined(self):
        """Whether the counts are restricted to the view's registrations."""
        return self.mode == 'view'

    def arrays(self):
        """The SQL parameters of ``pv(id, n, <dimension>...)``: one int[] literal per column, built once
        per population (every block and cube of the count passes the same ones)."""
        columns = [self.ids, self.rows] + list(self.overrides.values())
        key = tuple(len(c) for c in columns)
        if getattr(self, '_arrays_key', None) != key:
            self._arrays, self._arrays_key = [int_array(c) for c in columns], key
        return list(self._arrays)

    def base(self, period_rule):
        return {'mode': self.mode, 'reason': self.reason, 'setting': self.setting, 'key': self.key,
                'period_column': self.period_column, 'period_rule': period_rule, 'deleted': self.deleted,
                'overrides': list(self.overrides) if self.joined else []}


def _columns(info):
    return {name: kind for name, kind in info.get('columns') or ()}


def _period_condition(column, values, names, alias='v'):
    """The SQL and params choosing the period's rows on ``alias``.``column`` (None: every row)."""
    if values is None:
        return 'TRUE', []
    if column == 'year':
        return '%s.%s::text = ANY(%%s::text[])' % (alias, quote(column)), [list(names or [])]
    return '%s.%s = ANY(%%s::int[])' % (alias, quote(column)), [int_array(values)]


def _from_view(source, key, period_column, values, names, whole=False):
    """FROM ... WHERE ... of the view's rows of the period (``whole``: every row)."""
    view = quote(source.view)
    if values is None or whole:
        return '%s v' % view, 'TRUE', []
    if period_column == 'registration':
        return ('%s v JOIN %s p ON p.id = v.%s' % (view, quote(source.table), quote(key)),
                *_period_condition(source.period_of_registration, values, names, 'p'))
    return ('%s v' % view, *_period_condition(period_column, values, names))


def key_check(source, key, period_column, values, names, columns):
    """Counts comparing the view's rows of the period with the registrations their key points to.
    Over the whole view when the period comes from the registration (else "found" would be certain).
    ``rows`` and the comparisons count the rows with a key; ``null_keys`` the rows whose key is blank
    (e.g. an enrolment whose registration was removed): they point to no registration, the population
    leaves them out, and they say nothing about whether the column is the registration id. A check's SQL may
    name the period's rounds (``{rounds}``, Dirasa's ``same_year``): computed only when ``values`` lists them."""
    sources, where, params = _from_view(source, key, period_column, values, names,
                                        whole=period_column == 'registration')
    checks = []  # (name, column, sql): the first comparison of each name whose column the view has
    for name, column, sql in source.checks:
        if '{rounds}' in sql and not isinstance(values, list):
            continue
        if column in columns and name not in {c[0] for c in checks}:
            checks.append((name, column, sql))
    keyed = 'v.%s IS NOT NULL' % quote(key)
    select = ['COUNT(*) FILTER (WHERE %s)' % keyed, 'COUNT(DISTINCT v.%s)' % quote(key), 'COUNT(r.id)']
    select_params = []  # the SELECT list's parameters, before the WHERE's
    for name, column, sql in checks:
        if '{rounds}' in sql:
            select_params.append(int_array(values))
        select.append('COUNT(*) FILTER (WHERE %s AND %s)' % (
            keyed, sql.format(v='v.%s' % quote(column), rounds='%s::int[]')))
    select.append('COUNT(*) FILTER (WHERE r.deleted)')
    select.append('COUNT(*) FILTER (WHERE v.%s IS NULL)' % quote(key))
    sql = 'SELECT %s FROM %s LEFT JOIN %s r ON r.id = v.%s %s WHERE %s' % (
        ', '.join(select), sources, quote(source.table), quote(key), source.joins, where)
    params = select_params + list(params)
    with engine.read_only_cursor() as cursor:
        cursor.execute(sql, params)
        record = cursor.fetchone()
    out = {'rows': record[0], 'ids': record[1], 'found': record[2]}
    out.update({name: None for name, _column, _sql in source.checks})
    out.update({name: value for (name, _column, _sql), value in zip(checks, record[3:-2])})
    out.update({'deleted_rows': record[-2], 'null_keys': record[-1], 'max_rows_per_id': None, 'conflicting': None,
                'verified': False})
    return out


def judge(source, check, period_column, key='id'):
    """Why the key fails ('' when it passes), and whether it was cross-checked. Over the rows with a key:
    a blank key points to no registration and is left out of the population; but a column blank on most
    rows is not the registration id."""
    rows, threshold, blank = check['rows'], min_match(), check.get('null_keys') or 0
    if blank and blank >= rows:
        return "key check: %d%% of the view's rows have no %s" % (100 * blank // (rows + blank), key), False
    if not rows:
        return '', False
    if check['found'] < threshold * rows:
        return "key check: %d%% of the view's ids are registrations" % (100 * check['found'] // rows), False
    verified = False
    period_check = PERIOD_CHECKS.get(period_column)
    if period_check and check.get(period_check) is not None:
        reached = check[period_check] >= threshold * rows
        if period_column in source.gated_periods:
            if not reached:
                what = 'round' if period_check == 'same_round' else 'year'
                return "key check: %d%% of the view's rows have the registration's %s" % (
                    100 * check[period_check] // rows, what), False
            verified = True
        elif period_column in source.verifying_periods:  # shown, not required: the view's own year decides
            verified = reached
    for name in source.cross_checks:
        if check.get(name) is not None:
            if check[name] < CROSS_MATCH * rows:
                return "key check: %d%% of the view's rows have the registration's %s" % (
                    100 * check[name] // rows, name[len('same_'):]), False
            verified = True
    return '', verified


def _read(source, population, columns, values, names):
    """The population: one row per id of the period with its view rows and override values."""
    key = population.key
    dims = [(dim, column) for dim, column in source.overrides.items()
            if column in columns and columns[column] in INTEGER_TYPES]
    sources, where, params = _from_view(source, key, population.period_column, values, names)
    conflict = ' OR '.join('COUNT(DISTINCT v.%s) > 1' % quote(column) for _dim, column in dims) or 'FALSE'
    sql = ('SELECT v.%(key)s, COUNT(*)%(dims)s, (%(conflict)s) FROM %(from)s '
           'WHERE v.%(key)s IS NOT NULL AND %(where)s GROUP BY v.%(key)s ORDER BY v.%(key)s') % {
              'key': quote(key), 'from': sources, 'where': where, 'conflict': conflict,
              'dims': ''.join(', MIN(v.%s)' % quote(column) for _dim, column in dims)}
    ids, rows, overrides, conflicting = [], [], {dim: [] for dim, _column in dims}, 0
    with engine.read_only_cursor() as cursor:
        cursor.execute(sql, params)
        while True:
            chunk = cursor.fetchmany(20000)
            if not chunk:
                break
            for record in chunk:
                ids.append(record[0])
                rows.append(record[1])
                for position, dim in enumerate(overrides):
                    overrides[dim].append(record[2 + position])
                conflicting += bool(record[-1])
    population.ids, population.rows, population.overrides, population.read = ids, rows, overrides, True
    population.key_check.update({'max_rows_per_id': max(rows) if rows else 0, 'conflicting': conflicting})


def population(programme, period, *, round_ids=None, year=None, rule=None):
    """The view's population for ``period`` (view mode), or rule mode with the reason.

    ``round_ids``: the period's rounds (Makani's year, Bridging's year); ``year``: the youth Year (None with no
    ``round_ids``: every row, the "all" period); ``rule``: a queryset of the registrations the caller's
    own rule counts for the period (asked only when the view has no row for the period)."""
    source, chosen = SOURCES[programme], options(programme)
    out = Population(view=source.view, deleted=chosen['deleted'], setting=chosen['base'])
    if round_ids is not None:
        values, names = list(round_ids), [str(period)]
    elif year is not None:
        values, names = [year.id], [year.name]
    else:
        values, names = None, None
    out.period_values = values
    try:
        out.catalogue = info = describe(source.view)
    except engine.INTERRUPTS:
        raise
    except Exception as exc:  # recorded; the count goes on with the rule
        logger.warning('power_bi: describing %s failed: %s', source.view, error_class(exc))
        out.errors.append(error_text('catalogue', exc))
        out.reason = '%s: %s' % (error_class(exc), error_message(exc))
        out.catalogue, out.failed = {'exists': None, 'error': error_class(exc)}, True  # unknown, not missing
        return out
    columns = _columns(info)
    if not info['exists']:
        out.reason = VIEW_MISSING
        return out
    if info['kind'] not in ('view', 'materialized view'):
        out.reason = '%s is a %s%s' % (source.view, info['kind'], NOT_A_VIEW)
        return out
    if not info['can_select']:
        out.reason = NO_PERMISSION + source.view
        return out
    if chosen['base'] == 'rule':
        out.reason = 'setting FIGURES_POWER_BI base = rule'
        return out
    keys = [k for k in source.keys if k in columns]
    if not keys:
        out.reason = 'key column %s missing' % ' or '.join(source.keys)
        return out
    integer_keys = [k for k in keys if columns[k] in INTEGER_TYPES]
    if not integer_keys:
        out.reason = 'key column %s is %s, not an integer' % (keys[0], columns[keys[0]])
        return out
    out.period_column = next((c for c in source.periods if c in columns), 'registration') if values else None
    try:
        reason, preferred = '', None
        fallbacks = dict(source.period_fallbacks)
        for key in integer_keys:
            out.key = key
            out.key_check = key_check(source, key, out.period_column, values, names, columns)
            instead = fallbacks.get(out.period_column)
            if not out.key_check['rows'] and instead in columns:
                # a year column that cannot name the year (e.g. "2025-2026"): the view's rounds of the year
                out.period_column = instead
                out.key_check = key_check(source, key, instead, values, names, columns)
            reason, verified = judge(source, out.key_check, out.period_column, key)
            out.key_check['verified'] = verified
            if not reason:
                break
            preferred = preferred or (key, out.key_check, reason)
        if reason:  # every key failed: the preferred key's result says why
            out.key, out.key_check, out.reason = preferred
            return out
        if not out.key_check['rows'] and chosen['base'] != 'view':
            counted = 0
            if rule is not None:
                with engine.read_only_transaction() as alias:  # the limits, and a savepoint of its own
                    counted = rule.using(alias).count()
            if counted:
                out.read = True
                out.reason = 'the view has no rows for %s while %s registrations do' % (
                    'all years' if values is None else period, format(counted, ','))
                return out
        _read(source, out, columns, values, names)
    except engine.INTERRUPTS:
        raise
    except Exception as exc:  # a timeout, a permission or an SQL error: rule mode, recorded
        logger.warning('power_bi: reading %s failed: %s', source.view, error_class(exc))
        out.errors.append(error_text('population', exc))
        out.reason = '%s: %s' % (error_class(exc), error_message(exc))
        out.ids, out.rows, out.overrides, out.read, out.failed = [], [], {}, False, True
        return out
    out.mode = 'view'
    return out


# ----------------------------------------------------------------------------- reconciliation
def _flags(programme, population):
    """(name, SQL over the registration ``r``, params) of the reconciliation's reasons."""
    values = population.period_values
    if programme == 'mscc':
        other = ('r.round_id IS NOT NULL AND r.round_id <> ALL(%s::int[])', [int_array(values or [])])
        return [('deleted', 'r.deleted', []), ('tls', "COALESCE(r.type = 'TLS', FALSE)", []),
                ('no_round', 'r.round_id IS NULL', []), ('no_child', 'r.child_id IS NULL', []),
                ('other_year', *other)]
    if programme == 'bridging':
        other = ('r.round_id IS NOT NULL AND r.round_id <> ALL(%s::int[])', [int_array(values or [])])
        return [('deleted', 'r.deleted', []), ('no_student', 'r.student_id IS NULL', []),
                ('no_round', 'r.round_id IS NULL', []), ('other_year', *other)]
    enrolled = 'SELECT 1 FROM youth_enrolledprograms e WHERE e.registration_id = r.id'
    other = ('r.year_id IS NOT NULL AND r.year_id <> ALL(%s::int[])', [int_array(values)]) if values else ('FALSE', [])
    return [('deleted', 'r.deleted', []), ('no_year', 'r.year_id IS NULL', []), ('other_year', *other),
            ('no_enrolment', 'NOT EXISTS (%s)' % enrolled, []),
            ('no_master', 'EXISTS (%s) AND NOT EXISTS (%s AND e.master_program_id IS NOT NULL)' % (enrolled, enrolled),
             [])]


def reconcile(programme, period, population, before, counted):
    """Counts comparing the view's registrations, the old rule's (``before``) and the counted ones
    (``counted``), per reason. ``before`` and ``counted`` are querysets of registrations; in view mode
    ``counted`` is restricted to the view's ids."""
    source = SOURCES[programme]
    flags = _flags(programme, population)
    before_sql, before_params = before.values('id').query.sql_with_params()
    counted_sql, counted_params = counted.values('id').query.sql_with_params()
    join = ' JOIN vw ON vw.id = c.id' if population.joined else ''
    flag_sql = ', '.join('CASE WHEN r.id IS NULL THEN NULL ELSE (%s) END AS f_%s' % (sql, name)
                         for name, sql, _params in flags)
    names = ['in_view', 'in_before', 'is_counted'] + ['f_%s' % name for name, _sql, _params in flags]
    sql = (
        'WITH vw AS (SELECT x.id, x.n FROM unnest(%%s::int[], %%s::int[]) AS x(id, n)), '
        'before AS (SELECT DISTINCT b.id FROM (%(before)s) AS b), '
        'counted AS (SELECT DISTINCT c.id FROM (%(counted)s) AS c%(join)s), '
        'u AS (SELECT id FROM vw UNION SELECT id FROM before UNION SELECT id FROM counted), '
        't AS (SELECT (vw.id IS NOT NULL) AS in_view, (before.id IS NOT NULL) AS in_before, '
        '(counted.id IS NOT NULL) AS is_counted, %(flags)s, vw.n, r.%(person)s AS person, r.deleted AS gone '
        'FROM u LEFT JOIN vw ON vw.id = u.id LEFT JOIN before ON before.id = u.id '
        'LEFT JOIN counted ON counted.id = u.id LEFT JOIN %(table)s r ON r.id = u.id) '
        'SELECT GROUPING(%(names)s), %(names)s, COUNT(*), COALESCE(SUM(n), 0), COUNT(DISTINCT person), '
        'COUNT(DISTINCT person) FILTER (WHERE in_view), COUNT(*) FILTER (WHERE is_counted), '
        'COUNT(DISTINCT person) FILTER (WHERE is_counted), COUNT(*) FILTER (WHERE in_before), '
        'COUNT(DISTINCT person) FILTER (WHERE in_before), COUNT(*) FILTER (WHERE in_view AND NOT is_counted), '
        'COUNT(*) FILTER (WHERE is_counted AND NOT in_view), COUNT(*) FILTER (WHERE in_view AND gone) '
        'FROM t GROUP BY GROUPING SETS ((%(names)s), ())'
    ) % {'before': before_sql, 'counted': counted_sql,
         'join': join, 'flags': flag_sql, 'person': quote(source.person), 'table': quote(source.table),
         'names': ', '.join(names)}
    params = population.arrays()[:2] + list(before_params) + list(counted_params)
    for _name, _sql, flag_params in flags:
        params += flag_params
    width = len(names)
    rows, totals = [], {}
    with engine.read_only_cursor(bind_on_server=True) as cursor:  # the ids never in the SQL text
        cursor.execute(sql, params)
        for record in cursor.fetchall():
            if record[0]:  # the grand total
                view_rows = record[2 + width]
                (view_people, counted, counted_people, before_n, before_people, view_not_counted,
                 counted_not_view, deleted_in_view) = record[4 + width:]
                totals = {'view_rows': int(view_rows), 'view_ids': len(population.ids),
                          'view_' + source.person_label: view_people, 'counted': counted,
                          'counted_' + source.person_label: counted_people, 'before': before_n,
                          'before_' + source.person_label: before_people, 'in_view_not_counted': view_not_counted,
                          'counted_not_in_view': counted_not_view, 'deleted_in_view': deleted_in_view}
            else:
                rows.append(list(record[1:1 + width]) + [record[1 + width], int(record[2 + width]),
                                                          record[3 + width]])
    if not population.read:  # nothing to compare with: unknown, not zero
        for name in ('view_rows', 'view_ids', 'view_' + source.person_label, 'in_view_not_counted',
                     'counted_not_in_view', 'deleted_in_view'):
            totals[name] = None
    return {
        'period': str(period),
        'by': ['in_view', 'in_before', 'counted'] + [name for name, _sql, _params in flags],
        'measures': ['registrations', 'view_rows', source.person_label],
        'rows': sorted(rows, key=lambda r: tuple('' if v is None else str(v) for v in r)),
        'totals': totals,
    }


# ------------------------------------------------------------------------- periods, related views
def _period_meta(programme, values, column=None):
    """Non-personal metadata of the rounds (years) ``values`` ({value: dict}); youth ``values`` are year
    names when ``column`` is the view's ``year``, else year ids. Read under the counting limits."""
    with engine.read_only_transaction() as alias:
        return _period_meta_of(programme, values, column, alias)


def _period_meta_of(programme, values, column, alias):
    if programme == 'mscc':
        from student_registration.mscc.models import Round

        return {r.id: {'id': r.id, 'name': r.name, 'year': r.year, 'current': r.current_year,
                       'start_date': _iso(r.start_date), 'end_date': _iso(r.end_date)}
                for r in Round.objects.using(alias).filter(id__in=[v for v in values if isinstance(v, int)])}
    if programme == 'bridging':
        from student_registration.schools.models import CLMRound

        out = {}
        for r in CLMRound.objects.using(alias).filter(id__in=[v for v in values if isinstance(v, int)]):
            year, year_from = bridging_year(r)
            out[r.id] = {'id': r.id, 'name': r.name, 'current': r.current_round_bridging,
                         'current_year': r.current_year, 'start_date': _iso(r.start_date_bridging),
                         'end_date': _iso(r.end_date_bridging), 'year': year, 'year_from': year_from}
        return out
    from student_registration.youth.models import Year

    years = list(Year.objects.using(alias))
    by_id = {y.id: y for y in years}
    by_name = {y.name: y for y in years}
    out = {}
    for value in values:
        found = by_name.get(str(value)) if column == 'year' or not isinstance(value, int) else by_id.get(value)
        if found is not None:
            out[value] = {'id': found.id, 'name': found.name, 'current': found.current_year}
    return out


def periods(programme, population):
    """The view's rows per round (year) over the whole view, with each round's metadata. Dirasa's are always
    per round (the view's round_id, else the registration's), even when the view's year chose the period: the
    rounds of every year, each with its own year."""
    source = SOURCES[programme]
    key, column = quote(population.key), population.period_column
    if programme == 'bridging':
        column = 'round_id' if 'round_id' in _columns(population.catalogue) else 'registration'
    group = 'v.%s' % quote(column) if column not in (None, 'registration') else 'r.%s' % quote(
        source.period_of_registration)
    sql = ('SELECT %(group)s, COUNT(*), COUNT(DISTINCT v.%(key)s), COUNT(*) FILTER (WHERE r.deleted) '
           'FROM %(view)s v LEFT JOIN %(table)s r ON r.id = v.%(key)s GROUP BY 1 ORDER BY 1') % {
        'group': group, 'key': key, 'view': quote(source.view), 'table': quote(source.table)}
    with engine.read_only_cursor() as cursor:
        cursor.execute(sql, [])
        found = cursor.fetchall()
    meta = _period_meta(programme, [v for v, *_rest in found if v is not None], column)
    empty = {'mscc': ('id', 'name', 'year', 'current', 'start_date', 'end_date'),
             'bridging': ('id', 'name', 'current', 'current_year', 'start_date', 'end_date', 'year', 'year_from'),
             'youth': ('id', 'name', 'current')}[programme]
    out = []
    for value, rows, ids, deleted in found:
        entry = dict(meta.get(value) or {name: None for name in empty})
        entry.update({'view_rows': rows, 'view_ids': ids, 'deleted_rows': deleted})
        out.append(entry)
    return sorted(out, key=lambda e: (e.get('start_date') or '9999', str(e.get('name') or ''), e['id'] or 0))


SAFE_VALUE = re.compile(r'^[A-Za-z0-9 _-]{0,20}$')


def _safe(value, keep=frozenset()):
    """A flag column's value as sent: booleans and integers as they are; text only when it is a code
    (yes/no and the other fixed words, a date or year, or a choice value declared in code on the tables
    the view reads), else ``"<other>"``: a free-text column could hold a name."""
    if value is None or isinstance(value, (bool, int)):
        return value
    text = str(value)
    folded = text.strip().casefold()
    if SAFE_VALUE.match(text) and (folded in FIXED or folded in keep or DATE_OR_YEAR.match(text.strip())):
        return text
    return '<other>'


def profile(name, info, rounds=None):
    """Counts of a related view's rows by its low-cardinality flag columns (at most 50 rows).

    ``rounds``: the period's rounds, for a view whose ``round_id`` is the programme's round (Source.round_profiled):
    only their rows are counted (``"rounds"`` in the answer), the rows NeuroDB reads. A view of every round can
    have more than 50 (round, flag) groups (Dirasa's teachers are those of every CLM round), and a cut would drop
    the period's. Otherwise the newest rounds (years) come first, so that a cut drops the oldest."""
    if not info.get('exists'):
        return {'exists': False}
    keep = choice_values({relation for _s, relation, _k in info.get('reads') or ()})
    columns = _columns(info)
    by = [c for c in FLAG_COLUMNS if c in columns]
    measures = ['rows', 'ids'] if 'id' in columns else ['rows']
    select = ['v.%s' % quote(c) for c in by] + ['COUNT(*)'] + (['COUNT(DISTINCT v.id)'] if 'id' in columns else [])
    sql, params = 'SELECT %s FROM %s v' % (', '.join(select), quote(name)), []
    if rounds is not None and columns.get('round_id') not in INTEGER_TYPES:
        rounds = None  # no round column to choose them by: every row, the newest first
    if rounds is not None:
        rounds = sorted({int(r) for r in rounds})
        sql += ' WHERE v.%s = ANY(%%s::int[])' % quote('round_id')
        params.append(int_array(rounds))
    if by:
        order = ['%d DESC' % (i + 1) if c in ('round_id', 'year_id') else str(i + 1) for i, c in enumerate(by)]
        sql += ' GROUP BY %s ORDER BY %s' % (', '.join(str(i + 1) for i in range(len(by))), ', '.join(order))
    sql += ' LIMIT %d' % (MAX_RELATED_ROWS + 1)
    with engine.read_only_cursor() as cursor:
        cursor.execute(sql, params)
        found = cursor.fetchall()
    rows = [[_safe(v, keep) for v in record[:len(by)]] + [int(v) for v in record[len(by):]]
            for record in found[:MAX_RELATED_ROWS]]
    out = {'exists': True, 'by': by, 'measures': measures, 'rows': rows, 'truncated': len(found) > MAX_RELATED_ROWS}
    if rounds is not None:
        out['rounds'] = rounds
    return out


# -------------------------------------------------------------------------------- the block
def block(programme, period, population, before, counted, *, current=False, period_rule=''):
    """The payload's ``power_bi`` part: each part in its own try, a failing one listed in ``errors``."""
    source = SOURCES[programme]
    out = {
        'version': VERSION,
        'checked_at': timezone.now().isoformat(),
        'view': source.view,
        'base': population.base(period_rule),
        'catalogue': {},
        'key_check': population.key_check,
        'reconciliation': {},
        'periods': [],
        'related': {},
        'errors': list(population.errors),
    }
    # a view not described (an error) is unknown, never "missing": NeuroDB would take it as dropped
    out['catalogue'][source.view] = population.catalogue or {'exists': None, 'error': 'not described'}
    if related_on():
        for name in source.related:
            try:
                out['catalogue'][name] = describe(name)
            except engine.INTERRUPTS:
                raise
            except Exception as exc:
                out['catalogue'][name] = {'exists': None, 'error': error_class(exc)}
                out['errors'].append(error_text('catalogue %s' % name, exc))
    try:
        out['reconciliation'] = reconcile(programme, period, population, before, counted)
    except engine.INTERRUPTS:
        raise
    except Exception as exc:
        logger.warning('power_bi: reconciliation of %s failed: %s', programme, error_class(exc))
        out['errors'].append(error_text('reconciliation', exc))
    # the view's rows per round: not when reading the view just failed (a second timeout for nothing)
    readable = (population.catalogue.get('can_select') and population.key and population.setting != 'rule'
                and population.catalogue.get('kind') in ('view', 'materialized view') and not population.failed)
    if current and readable:
        try:
            out['periods'] = periods(programme, population)
        except engine.INTERRUPTS:
            raise
        except Exception as exc:
            out['errors'].append(error_text('periods', exc))
    if current and related_on():
        for name in source.profiled:
            info = out['catalogue'].get(name) or {}
            if info.get('exists') is None and info.get('error'):
                out['related'][name] = {'exists': None, 'error': info['error']}
                continue
            if info.get('exists') and not info.get('can_select'):
                out['related'][name] = {'exists': True, 'error': 'no SELECT permission'}
                continue
            rounds = (population.period_values or None) if name in source.round_profiled else None
            try:
                out['related'][name] = profile(name, info, rounds)
            except engine.INTERRUPTS:
                raise
            except Exception as exc:
                out['related'][name] = {'exists': True, 'error': error_class(exc)}
                out['errors'].append(error_text('related %s' % name, exc))
    return out


def failed_block(programme, period, exc, period_rule=''):
    """The block when even assembling it failed: rule mode and the error."""
    source = SOURCES[programme]
    return {'version': VERSION, 'checked_at': timezone.now().isoformat(), 'view': source.view,
            'base': Population(view=source.view, reason=error_text('power_bi', exc),
                               deleted=options(programme)['deleted'],
                               setting=options(programme)['base']).base(period_rule),
            'catalogue': {}, 'key_check': {}, 'reconciliation': {}, 'periods': [], 'related': {},
            'errors': [error_text('power_bi', exc)]}


def _iso(value):
    return value.isoformat() if value else None
