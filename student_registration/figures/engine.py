"""Counting unique beneficiaries per grouping in the database, in one read-only query.

A programme describes its beneficiaries as one SELECT (``base_sql``) that returns a person
identifier and one column per dimension (partner, governorate, sex, ...). The engine wraps it in a
``GROUP BY GROUPING SETS`` query that counts distinct people for every grouping at once, so the
table is read once whatever the number of groupings, and returns the counts only.

Unique counts cannot be added up across rows (the same child can be registered by two partners), so
every question is answered from the grouping that matches it exactly: the groupings are every
combination of the main dimensions, alone or with one detail, plus a few extra ones.

A cube (``cube()``) is the other kind of answer: records (registrations, teachers...) counted per
combination of ALL its dimensions in one GROUP BY. Those counts add up, so a dashboard can filter
on any set of dimensions and sum the rows that match.

Safety for the running system: every query runs in a READ ONLY transaction with a statement timeout
(FIGURES_STATEMENT_TIMEOUT_MS), a bounded work_mem (FIGURES_WORK_MEM) and no parallel workers
(FIGURES_PARALLEL_WORKERS), on the database alias named by FIGURES_DATABASE (a read replica when one
is configured), and only from a background task. JIT compilation is off (FIGURES_JIT): the join with a
view's population (an array) has no statistics, so PostgreSQL overestimates its rows a hundredfold and
compiles the counts for seconds (3.4 s of a 4.3 s services count on 180,000 registrations) to save
milliseconds. The counting queries send their parameters apart from
the SQL text (server-side binding): a view's registration ids, passed as arrays, never appear in the
statement text PostgreSQL logs when a statement fails, nor in pg_stat_activity.

The worker's time limit (``INTERRUPTS``) is never caught as one part's failure: it stops the count at once,
and the query it interrupted is cancelled on the server.
"""

from __future__ import annotations

from contextlib import contextmanager
from itertools import combinations

from django.conf import settings
from django.db import connections, transaction

try:  # the Celery worker's soft time limit
    from celery.exceptions import SoftTimeLimitExceeded
except ImportError:  # pragma: no cover - Celery is a dependency of the project
    class SoftTimeLimitExceeded(Exception):
        pass

# Interruptions that stop a count: never turned into one block's or one part's error (``except INTERRUPTS:
# raise`` before every ``except Exception``), so the run stops and names the targets left.
INTERRUPTS = (SoftTimeLimitExceeded,)

MAX_DIMENSIONS = 31  # GROUPING() returns one bit per argument in an integer


def groupings(main, details, extra=()):
    """Every subset of ``main``, alone or with one of ``details``, plus ``extra``; each sorted."""
    out = []
    for size in range(len(main) + 1):
        for chosen in combinations(main, size):
            out.append(tuple(sorted(chosen)))
            for detail in details:
                out.append(tuple(sorted(chosen + (detail,))))
    for grouping in extra:
        out.append(tuple(sorted(grouping)))
    seen, unique = set(), []
    for grouping in out:
        if grouping not in seen:
            seen.add(grouping)
            unique.append(grouping)
    return unique


def database_alias():
    return getattr(settings, 'FIGURES_DATABASE', 'default')


def _limit(cursor):
    """The counting limits, for the current transaction only: READ ONLY, a statement timeout, a bounded
    work_mem, no parallel workers and no JIT compilation (see above)."""
    timeout = int(getattr(settings, 'FIGURES_STATEMENT_TIMEOUT_MS', 600000))
    work_mem = str(getattr(settings, 'FIGURES_WORK_MEM', '32MB'))
    workers = str(int(getattr(settings, 'FIGURES_PARALLEL_WORKERS', 0)))
    jit = 'on' if getattr(settings, 'FIGURES_JIT', False) else 'off'
    cursor.execute('SET TRANSACTION READ ONLY')
    cursor.execute("SELECT set_config('statement_timeout', %s, true)", [str(timeout)])
    cursor.execute("SELECT set_config('work_mem', %s, true)", [work_mem])
    # one CPU core: no parallel workers taken from the requests of the running system
    cursor.execute("SELECT set_config('max_parallel_workers_per_gather', %s, true)", [workers])
    cursor.execute("SELECT set_config('jit', %s, true)", [jit])


@contextmanager
def read_only_transaction():
    """The counting limits on the figures connection, for raw SQL and ORM queries alike; yields the
    database alias. ORM querysets inside must use ``.using(alias)``.

    Inside an outer transaction (a test, or a caller's atomic block) this is a savepoint: PostgreSQL gives
    the outer transaction back its read-write state when the savepoint is released, so a write that
    follows still works."""
    alias = database_alias()
    with transaction.atomic(using=alias):
        with connections[alias].cursor() as cursor:
            _limit(cursor)
        try:
            yield alias
        except INTERRUPTS:
            _cancel(alias)
            raise


def _cancel(alias):
    """Cancel the query still running on the server, if any. psycopg cancels it by itself only on
    KeyboardInterrupt: after the worker's time limit the query would otherwise go on until its timeout."""
    raw = connections[alias].connection
    try:
        from psycopg.pq import TransactionStatus

        if raw is not None and raw.info.transaction_status == TransactionStatus.ACTIVE:
            raw.cancel_safe(timeout=5.0)
    except Exception:  # psycopg 2, or the connection is already gone: nothing to cancel
        pass


def _server_binding(connection):
    """The backend's cursor class that sends the parameters apart from the SQL text (psycopg 3); None
    when there is none (psycopg 2, another database)."""
    if connection.vendor != 'postgresql':
        return None
    from django.db.backends.postgresql import base

    return getattr(base, 'ServerBindingCursor', None) if base.is_psycopg3 else None


@contextmanager
def read_only_cursor(bind_on_server=False):
    """A cursor in a READ ONLY transaction with the counting limits, on the figures database.

    ``bind_on_server``: the parameters are sent apart from the SQL text, so that the text PostgreSQL logs
    when the statement fails (and shows in pg_stat_activity) holds ``$1``... rather than the values: for
    the queries that carry a view's registration ids."""
    with read_only_transaction() as alias:
        connection = connections[alias]
        factory = _server_binding(connection) if bind_on_server else None
        if factory is None:
            cursor = connection.cursor()
        else:  # the backend's own cursor creation (time zone, wrappers), with the server-binding class
            raw = connection.connection  # open: the transaction above uses it
            saved, raw.cursor_factory = raw.cursor_factory, factory
            try:
                cursor = connection.cursor()
            finally:
                raw.cursor_factory = saved
        with cursor:
            yield cursor


def stream(sql, params, size=5000):
    """The rows of ``sql``, read ``size`` at a time through a server-side cursor (psycopg 3 binds its
    parameters on the server), under the counting limits."""
    with read_only_transaction() as alias:
        connection = connections[alias]
        if _server_binding(connection) is None:
            cursor = connection.chunked_cursor()
        else:
            cursor = connection.make_cursor(connection.connection.cursor(
                'figures_stream', scrollable=False, withhold=False))
        with cursor:
            cursor.execute(sql, params)
            while True:
                rows = cursor.fetchmany(size)
                if not rows:
                    break
                yield from rows


PEOPLE = (('people', 'COUNT(DISTINCT b.person)'),)


def count(base_sql, params, dimensions, grouping_list, measures=PEOPLE):
    """``[{'by': [...], 'rows': [[value, ..., measure, ...], ...]}]`` for each grouping.

    ``base_sql`` must return a column ``person`` and one column per name in ``dimensions``;
    ``measures`` are (name, aggregate SQL over ``b``), unique people by default.
    """
    dimensions = list(dimensions)
    if len(dimensions) > MAX_DIMENSIONS:
        raise ValueError('too many dimensions')
    columns = ', '.join('b.%s' % d for d in dimensions)
    sets = ', '.join('(%s)' % ', '.join('b.%s' % d for d in g) for g in grouping_list)
    sql = (
        'SELECT GROUPING(%(columns)s) AS g, %(columns)s, %(measures)s '
        'FROM (%(base)s) AS b GROUP BY GROUPING SETS (%(sets)s)'
    ) % {
        'columns': columns,
        'base': base_sql,
        'sets': sets,
        'measures': ', '.join(sql for _name, sql in measures),
    }
    # GROUPING() sets the bit of every argument NOT in the row's grouping; the first argument is
    # the most significant bit.
    width = len(dimensions)
    by_mask = {}
    for grouping in grouping_list:
        mask = 0
        for position, name in enumerate(dimensions):
            if name not in grouping:
                mask |= 1 << (width - 1 - position)
        by_mask[mask] = grouping
    rows = {g: [] for g in grouping_list}
    with read_only_cursor(bind_on_server=True) as cursor:
        cursor.execute(sql, params)
        for record in cursor.fetchall():
            grouping = by_mask[record[0]]
            values = dict(zip(dimensions, record[1:1 + width]))
            rows[grouping].append([_json(values[d]) for d in grouping] + list(record[1 + width:]))
    return [{'by': list(g), 'rows': sorted(rows[g], key=_sort_key)} for g in grouping_list]


def figures_block(base_sql, params, dimensions, grouping_list, measures=PEOPLE):
    """One block of a payload: which measures the rows end with, and the rows per grouping."""
    return {
        'measures': [name for name, _sql in measures],
        'figures': count(base_sql, params, dimensions, grouping_list, measures),
    }


def cube(base_sql, params, dimensions, measures):
    """``{'dims': [...], 'measures': [...], 'rows': [[value, ..., measure, ...], ...]}``: one row per
    combination of ``dimensions`` found, ending with its ``measures`` as integers.

    ``base_sql`` returns one column per dimension and whatever the measures read; ``measures`` are
    (name, aggregate SQL over ``b``), e.g. ``('registrations', 'COUNT(*)')``.
    """
    dimensions = list(dimensions)
    if not dimensions:
        raise ValueError('a cube needs at least one dimension')
    columns = ', '.join('b.%s' % d for d in dimensions)
    sql = 'SELECT %(columns)s, %(measures)s FROM (%(base)s) AS b GROUP BY %(columns)s' % {
        'columns': columns,
        'base': base_sql,
        'measures': ', '.join(sql for _name, sql in measures),
    }
    width = len(dimensions)
    with read_only_cursor(bind_on_server=True) as cursor:
        cursor.execute(sql, params)
        rows = [[_json(v) for v in record[:width]] + [int(v or 0) for v in record[width:]]
                for record in cursor.fetchall()]
    return {'dims': dimensions, 'measures': [name for name, _sql in measures], 'rows': sorted(rows, key=_sort_key)}


def _json(value):
    if value is None or isinstance(value, (int, float, str, bool)):
        return value
    return str(value)


def _sort_key(row):
    return tuple('' if v is None else str(v) for v in row)
