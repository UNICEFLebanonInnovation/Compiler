"""Calculations NeuroDB asks for: NeuroDB holds the schedule (POST /api/wellbeing/runs/), a Celery
worker calculates, NeuroDB polls the run until it is done and then reads the flags. BMA keeps no
schedule for them."""

import datetime
import logging

from django.db import transaction
from django.utils import timezone

from . import engine
from .models import WellbeingRun

logger = logging.getLogger(__name__)

STALE_HOURS = 3  # a run still "queued" or "running" after this long was lost (worker restarted)


def start(center_ids=(), requested_by=''):
    """Queue a calculation, or return the one already queued or running. Returns (run, created)."""
    cutoff = timezone.now() - datetime.timedelta(hours=STALE_HOURS)
    WellbeingRun.objects.filter(
        status__in=(WellbeingRun.QUEUED, WellbeingRun.RUNNING), requested_at__lt=cutoff
    ).update(status=WellbeingRun.FAILED, finished_at=timezone.now(), error='never finished (worker stopped?)')
    with transaction.atomic():
        busy = (
            WellbeingRun.objects.select_for_update()
            .filter(status__in=(WellbeingRun.QUEUED, WellbeingRun.RUNNING))
            .order_by('requested_at')
            .first()
        )
        if busy is not None:
            return busy, False
        run = WellbeingRun.objects.create(center_ids=sorted(set(center_ids)), requested_by=requested_by[:150])
    from .tasks import run_wellbeing

    transaction.on_commit(lambda: run_wellbeing.delay(run.pk))
    return run, True


def execute(run_id):
    run = WellbeingRun.objects.get(pk=run_id)
    if run.status != WellbeingRun.QUEUED:
        return run
    run.status, run.started_at = WellbeingRun.RUNNING, timezone.now()
    run.save(update_fields=['status', 'started_at'])
    try:
        totals = engine.refresh(center_ids=run.center_ids or None)
    except Exception as exc:  # recorded on the run, for NeuroDB
        logger.exception('wellbeing run %s failed', run.pk)
        run.status, run.error = WellbeingRun.FAILED, ('%s: %s' % (type(exc).__name__, exc))[:5000]
    else:
        run.status, run.totals = WellbeingRun.SUCCEEDED, {k: v for k, v in dict(totals).items()}
    run.finished_at = timezone.now()
    run.save(update_fields=['status', 'error', 'totals', 'finished_at'])
    return run
