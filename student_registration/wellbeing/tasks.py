"""Nightly wellbeing flags (Celery). Celery beat runs it every day at 03:00 (CELERY_BEAT_SCHEDULE in
config/settings/base.py): after the day's attendance is in, away from the working day."""

import logging

from student_registration.taskapp.celery import app

from . import engine

logger = logging.getLogger(__name__)


@app.task(ignore_result=True, soft_time_limit=3600, time_limit=3800)
def refresh_wellbeing_flags():
    totals = engine.refresh()
    logger.info('wellbeing flags: %s', dict(totals))
