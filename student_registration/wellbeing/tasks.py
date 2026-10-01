"""Nightly wellbeing flags (Celery). Schedule it in admin → Periodic tasks:
"student_registration.wellbeing.tasks.refresh_wellbeing_flags", e.g. at 03:00 (after attendance
is in, away from the working day)."""

import logging

from student_registration.taskapp.celery import app

from . import engine

logger = logging.getLogger(__name__)


@app.task(ignore_result=True, soft_time_limit=3600, time_limit=3800)
def refresh_wellbeing_flags():
    totals = engine.refresh()
    logger.info('wellbeing flags: %s', dict(totals))
