"""Building and reading the stored snapshots.

``refresh(programme, year)`` counts in the database (engine.py) and stores the result. NeuroDB asks
for a count (``start_run``: POST /api/figures/runs/), a Celery worker does it (``execute_run``) and
NeuroDB polls the run until it is done: the schedule lives in NeuroDB, BMA keeps none.
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
    from . import education

    return education.PROGRAMMES


def refresh(programme, year=None):
    """Count ``programme`` for ``year`` (its current year when None) and store the snapshot."""
    definition = programmes()[programme]
    year = year or definition.current_year()
    if year is None:
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


def is_stale(snapshot):
    """Missing, older than FIGURES_MAX_AGE_HOURS, or counted in an older payload format (after an
    upgrade it needs counting again however recent it is). NeuroDB decides when to count."""
    from .education import FORMAT_VERSION

    if snapshot is None or (snapshot.payload or {}).get('format') != FORMAT_VERSION:
        return True
    hours = int(getattr(settings, 'FIGURES_MAX_AGE_HOURS', 26))
    return snapshot.created_at < timezone.now() - datetime.timedelta(hours=hours)


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
    """Count every target of the run, one after the other; a failing target does not stop the others."""
    from .models import FiguresRun

    run = FiguresRun.objects.get(pk=run_id)
    if run.status != FiguresRun.QUEUED:
        return run
    run.status, run.started_at = FiguresRun.RUNNING, timezone.now()
    run.save(update_fields=['status', 'started_at'])
    counted, errors = [], []
    for programme, year in run.targets:
        try:
            snapshot = refresh(programme, year or None)
        except Exception as exc:  # recorded on the run
            logger.exception('figures run %s: %s %s failed', run.pk, programme, year)
            errors.append('%s %s: %s: %s' % (programme, year or 'current', type(exc).__name__, exc))
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
