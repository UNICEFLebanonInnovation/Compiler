"""Counting unique beneficiaries per grouping in the database, in one read-only query.

A programme describes its beneficiaries as one SELECT (``base_sql``) that returns a person
identifier and one column per dimension (partner, governorate, sex, ...). The engine wraps it in a
``GROUP BY GROUPING SETS`` query that counts distinct people for every grouping at once, so the
table is read once whatever the number of groupings, and returns the counts only.

Unique counts cannot be added up across rows (the same child can be registered by two partners), so
every question is answered from the grouping that matches it exactly: the groupings are every
combination of the main dimensions, alone or with one detail, plus a few extra ones.

Safety for the running system: the query runs in a READ ONLY transaction with a statement timeout
(FIGURES_STATEMENT_TIMEOUT_MS), a bounded work_mem (FIGURES_WORK_MEM) and no parallel workers
(FIGURES_PARALLEL_WORKERS), on the database alias named by FIGURES_DATABASE (a read replica when one
is configured), and only from a background task.
"""

from __future__ import annotations

from itertools import combinations

from django.conf import settings
from django.db import connections, transaction

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
    alias = database_alias()
    timeout = int(getattr(settings, 'FIGURES_STATEMENT_TIMEOUT_MS', 600000))
    work_mem = str(getattr(settings, 'FIGURES_WORK_MEM', '32MB'))
    workers = str(int(getattr(settings, 'FIGURES_PARALLEL_WORKERS', 0)))
    with transaction.atomic(using=alias):
        with connections[alias].cursor() as cursor:
            cursor.execute('SET TRANSACTION READ ONLY')
            cursor.execute("SELECT set_config('statement_timeout', %s, true)", [str(timeout)])
            cursor.execute("SELECT set_config('work_mem', %s, true)", [work_mem])
            # one CPU core: no parallel workers taken from the requests of the running system
            cursor.execute("SELECT set_config('max_parallel_workers_per_gather', %s, true)", [workers])
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


def _json(value):
    if value is None or isinstance(value, (int, float, str, bool)):
        return value
    return str(value)


def _sort_key(row):
    return tuple('' if v is None else str(v) for v in row)
