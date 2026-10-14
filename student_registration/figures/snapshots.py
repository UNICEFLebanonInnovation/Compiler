"""Building and reading the stored snapshots.

``refresh(programme, year)`` counts in the database (engine.py) and stores the result. NeuroDB asks
for a count (``start_run``: POST /api/figures/runs/), a Celery worker does it (``execute_run``) and
NeuroDB polls the run until it is done: the schedule lives in NeuroDB, BMA keeps none.

Programmes: ``programmes()`` are the education ones (Makani, Bridging), the only ones the education
index and /api/figures/<programme>/ list; ``all_programmes()`` adds Youth, which a run may count (its
snapshots are served by /api/youth/indicator-figures/). A snapshot is stale when it was counted in an
older payload format of its programme, or is older than FIGURES_MAX_AGE_HOURS (the current period, and
youth's "all") or FIGURES_PAST_MAX_AGE_HOURS (a past period: recounted weekly).
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


def stale(definition, year, format_version, created_at, current_year=None):
    """Whether a snapshot of ``definition``'s ``year`` counted at ``created_at`` in ``format_version`` must
    be counted again: never counted, counted in an older format of its programme (after an upgrade,
    however recent), or older than FIGURES_MAX_AGE_HOURS (the current period, and "all") or
    FIGURES_PAST_MAX_AGE_HOURS (a past period). ``current_year``: the programme's, when known."""
    if definition is None or created_at is None or format_version != definition.format_version:
        return True
    current_year = definition.current_year() if current_year is None else current_year
    if str(year) in (str(current_year), 'all'):
        hours = int(getattr(settings, 'FIGURES_MAX_AGE_HOURS', 26))
    else:
        hours = int(getattr(settings, 'FIGURES_PAST_MAX_AGE_HOURS', 168))
    return created_at < timezone.now() - datetime.timedelta(hours=hours)


def is_stale(snapshot, programme=None):
    """Whether ``snapshot`` (of ``programme``, by default its own) must be counted again (``stale``);
    a missing snapshot is. NeuroDB decides when to count."""
    if snapshot is None:
        return True
    definition = all_programmes().get(programme or snapshot.programme)
    return stale(definition, snapshot.year, (snapshot.payload or {}).get('format'), snapshot.created_at)


def counted_years(programme):
    """{year: (format, counted at)} of the latest snapshot of each year, without reading the payloads."""
    found = {}
    rows = (FiguresSnapshot.objects.filter(programme=programme).order_by('year', '-created_at')
            .values_list('year', 'payload__format', 'created_at'))
    for year, format_version, created_at in rows:
        found.setdefault(year, (format_version, created_at))
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
        except Exception as exc:  # recorded on the run
            logger.exception('figures run %s: %s %s failed', run.pk, programme, year)
            errors.append('%s %s: %s: %s' % (programme, year or 'current', power_bi.error_class(exc),
                                             power_bi.error_message(exc)))
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
