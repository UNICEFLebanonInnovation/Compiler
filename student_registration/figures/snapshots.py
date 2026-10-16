"""Building and reading the stored snapshots.

``refresh(programme, year)`` counts in the database (engine.py) and stores the result. NeuroDB asks
for a count (``start_run``: POST /api/figures/runs/), a Celery worker does it (``execute_run``) and
NeuroDB polls the run until it is done: the schedule lives in NeuroDB, BMA keeps none.

Programmes: ``programmes()`` are the education ones (Makani, Bridging), the only ones the education
index and /api/figures/<programme>/ list; ``all_programmes()`` adds Youth, which a run may count (its
snapshots are served by /api/youth/indicator-figures/). A snapshot is stale when it was counted in an
older payload format of its programme, under other FIGURES_POWER_BI settings than today's (the ``base``
switch, ``deleted``, the ``period`` setting of Makani and Bridging: a past period follows a change at the
next run, not a week later), with the rule because its view could not be read while it can be now (a GRANT
given since, or the view created again by hand: likewise), or is older than FIGURES_MAX_AGE_HOURS (the
current period, and youth's "all") or FIGURES_PAST_MAX_AGE_HOURS (a past period: recounted weekly).
"""

from __future__ import annotations

import datetime
import logging
import time

from django.conf import settings
from django.utils import timezone

from .models import FiguresSnapshot

logger = logging.getLogger(__name__)

KEEP = 3  # snapshots kept per programme and year
LOCK_SECONDS = 30 * 60


def programmes():
    """The education programmes: the only ones of the education index and /api/figures/<programme>/."""
    from . import education

    return education.PROGRAMMES


def all_programmes():
    """Every programme a run can count: the education ones and Youth."""
    from .youth import Youth

    return dict(programmes(), youth=Youth())


def refresh(programme, year=None):
    """Count ``programme`` for ``year`` (its current year when None) and store the snapshot; None when
    there is no such year."""
    definition = all_programmes()[programme]
    year = year or definition.current_year()
    if year is None or not definition.has_year(year):
        return None
    started = time.monotonic()
    payload = definition.build(year)
    snapshot = FiguresSnapshot.objects.create(
        programme=programme,
        year=str(payload['year']),
        seconds=round(time.monotonic() - started, 1),
        payload=payload,
    )
    old = FiguresSnapshot.objects.filter(programme=programme, year=snapshot.year).order_by('-created_at')[KEEP:]
    FiguresSnapshot.objects.filter(id__in=[s.id for s in old]).delete()
    logger.info('figures %s %s counted in %ss', programme, snapshot.year, snapshot.seconds)
    return snapshot


def latest(programme, year):
    return (
        FiguresSnapshot.objects.filter(programme=programme, year=str(year)).order_by('-created_at').first()
    )


def stale(definition, year, format_version, created_at, current_year=None, base=None, readable=None):
    """Whether a snapshot of ``definition``'s ``year`` counted at ``created_at`` in ``format_version`` must
    be counted again: never counted, counted in an older format of its programme (after an upgrade,
    however recent), counted under other FIGURES_POWER_BI settings (``base``: its ``power_bi.base``),
    counted with the rule because the view could not be read while it can be now (``view_readable_again``),
    or older than FIGURES_MAX_AGE_HOURS (the current period, and "all") or FIGURES_PAST_MAX_AGE_HOURS (a past
    period). ``current_year``: the programme's, when known; ``readable``: see ``view_readable_again``."""
    if definition is None or created_at is None or format_version != definition.format_version:
        return True
    current_year = definition.current_year() if current_year is None else current_year
    current = str(year) in (str(current_year), 'all')
    if settings_changed(definition.name, base, str(year) == str(current_year)):
        return True
    if view_readable_again(definition.name, base, readable):
        return True
    if current:
        hours = int(getattr(settings, 'FIGURES_MAX_AGE_HOURS', 26))
    else:
        hours = int(getattr(settings, 'FIGURES_PAST_MAX_AGE_HOURS', 168))
    return created_at < timezone.now() - datetime.timedelta(hours=hours)


def settings_changed(programme, base, current):
    """Whether the FIGURES_POWER_BI settings that chose a snapshot's rows (its ``power_bi.base``) differ
    from today's: the ``base`` switch (e.g. the way back to the rule), ``deleted``, and the ``period`` of
    Makani and Bridging (the current year only: a past year always counts the rounds of its year). With
    Bridging's ``current_rounds`` and no round flagged, the current year reports ``start_year`` and stays
    stale: NeuroDB asks for the current year at every run anyway."""
    from . import power_bi

    if not isinstance(base, dict) or programme not in power_bi.DEFAULTS:
        return False
    chosen = power_bi.options(programme)
    if base.get('setting') != chosen['base'] or base.get('deleted') != chosen['deleted']:
        return True
    return 'period' in chosen and current and base.get('period_rule') != chosen['period']


def view_readable_again(programme, base, readable=None):
    """Whether a snapshot counted with the rule because its view could not be read at all (missing, not a
    view, no SELECT permission: its ``power_bi.base``) would now be counted from the view: the view can be
    read (a GRANT given since, or a missing view created again by hand, SPEC E3; a view dropped and created
    again loses its grants, see power_bi.VIEW_MISSING) and the setting does not force the
    rule. A past period then follows at the next run, as the current one does, rather than at its weekly
    count. ``readable``: a callable answering ``power_bi.readable(programme)``, when the caller asks once for
    many snapshots (``readability``); asked only for such a snapshot. A failing check answers no (the weekly
    count still comes)."""
    from . import engine, power_bi

    if programme not in power_bi.SOURCES or not power_bi.unreadable(base):
        return False
    if power_bi.options(programme)['base'] == 'rule':
        return False
    try:
        return bool((readable or readability(programme))())
    except engine.INTERRUPTS:
        raise
    except Exception as exc:  # the catalogue could not be read: no data involved, the class is enough
        logger.warning('figures: checking whether %s can be read failed: %s', programme, power_bi.error_class(exc))
        return False


def readability(programme):
    """A callable answering, once, whether ``programme``'s view can be read now (``power_bi.readable``)."""
    from . import power_bi

    answer = []

    def readable():
        if not answer:
            answer.append(power_bi.readable(programme))
        return answer[0]

    return readable


def is_stale(snapshot, programme=None):
    """Whether ``snapshot`` (of ``programme``, by default its own) must be counted again (``stale``);
    a missing snapshot is. NeuroDB decides when to count."""
    if snapshot is None:
        return True
    definition = all_programmes().get(programme or snapshot.programme)
    payload = snapshot.payload or {}
    return stale(definition, snapshot.year, payload.get('format'), snapshot.created_at,
                 base=(payload.get('power_bi') or {}).get('base'))


def counted_years(programme):
    """{year: (format, counted at, power_bi.base)} of the latest snapshot of each year, without reading
    the payloads into Python."""
    found = {}
    rows = (FiguresSnapshot.objects.filter(programme=programme).order_by('year', '-created_at')
            .values_list('year', 'payload__format', 'created_at', 'payload__power_bi__base'))
    for year, format_version, created_at, base in rows:
        found.setdefault(year, (format_version, created_at, base))
    return found


RUN_STALE_HOURS = 3  # a run still "queued" or "running" after this long was lost (worker restarted)


def start_run(targets, requested_by=''):
    """A run counting ``targets`` ([(programme, year or None)]), queued for the worker; the run already
    queued or running is returned instead of starting a second count. Returns (run, created)."""
    from django.db import transaction

    from .models import FiguresRun

    cutoff = timezone.now() - datetime.timedelta(hours=RUN_STALE_HOURS)
    FiguresRun.objects.filter(
        status__in=(FiguresRun.QUEUED, FiguresRun.RUNNING), requested_at__lt=cutoff
    ).update(status=FiguresRun.FAILED, finished_at=timezone.now(), error='never finished (worker stopped?)')
    with transaction.atomic():
        busy = (
            FiguresRun.objects.select_for_update()
            .filter(status__in=(FiguresRun.QUEUED, FiguresRun.RUNNING))
            .order_by('requested_at')
            .first()
        )
        if busy is not None:
            return busy, False
        run = FiguresRun.objects.create(targets=[list(t) for t in targets], requested_by=requested_by[:150])
    from .tasks import run_figures

    transaction.on_commit(lambda: run_figures.delay(run.pk))
    return run, True


def execute_run(run_id):
    """Count every target of the run, one after the other; a failing target does not stop the others.
    The run's error (read by NeuroDB) gives each failure's class and first line, quoted text masked.
    At the worker's soft time limit the run stops and names the targets left (they stay stale, so the
    next run asks for them again) rather than going on until the hard limit kills it mid-count and
    leaves it "running", which would hold every count back until RUN_STALE_HOURS."""
    from celery.exceptions import SoftTimeLimitExceeded

    from . import power_bi
    from .models import FiguresRun

    run = FiguresRun.objects.get(pk=run_id)
    if run.status != FiguresRun.QUEUED:
        return run
    run.status, run.started_at = FiguresRun.RUNNING, timezone.now()
    run.save(update_fields=['status', 'started_at'])
    counted, errors = [], []
    for position, (programme, year) in enumerate(run.targets):
        try:
            snapshot = refresh(programme, year or None)
        except SoftTimeLimitExceeded:
            _reset_interrupted_connections()  # the limit may have struck mid-query
            left = run.targets[position:]
            logger.warning('figures run %s: time limit reached, %d targets not counted', run.pk, len(left))
            errors.append('time limit reached; not counted: %s' % ', '.join(
                '%s %s' % (name, when or 'current') for name, when in left))
            break
        except Exception as exc:  # recorded on the run; logged by its class only (power_bi.error_line)
            logger.error('figures run %s: %s %s failed: %s', run.pk, programme, year, power_bi.error_line(exc))
            errors.append('%s %s: %s' % (programme, year or 'current', power_bi.error_line(exc)))
            continue
        if snapshot is None:
            errors.append('%s %s: no such year' % (programme, year or 'current'))
        else:
            counted.append([programme, snapshot.year, snapshot.seconds])
    run.counted, run.error = counted, '\n'.join(errors)[:5000]
    run.status = FiguresRun.FAILED if errors and not counted else FiguresRun.SUCCEEDED
    run.finished_at = timezone.now()
    run.save(update_fields=['counted', 'error', 'status', 'finished_at'])
    return run


def _reset_interrupted_connections():
    """Close the run's and the counting's database connections when an interruption left them unusable
    (a query still running): Django opens a new one for the next query, so the run can still be saved."""
    from django.db import connections

    from . import engine

    for alias in {'default', engine.database_alias()}:
        connection = connections[alias]
        if connection.connection is not None and not connection.is_usable():
            connection.close()
