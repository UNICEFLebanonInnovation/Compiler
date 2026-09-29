"""Background counting of the NeuroDB figures (Celery).

``refresh_all_figures`` is meant for Celery beat, at night: admin → Periodic tasks → add
"student_registration.figures.tasks.refresh_all_figures" with a crontab such as 02:30.
"""

import logging

from student_registration.taskapp.celery import app

from . import snapshots

logger = logging.getLogger(__name__)


@app.task(ignore_result=True, soft_time_limit=1800, time_limit=2000)
def refresh_figures(programme, year=None):
    snapshots.refresh(programme, year or None)


@app.task(ignore_result=True, soft_time_limit=3600, time_limit=3800)
def refresh_all_figures():
    """The current year of every programme, one after the other (never in parallel)."""
    for programme in snapshots.programmes():
        try:
            snapshots.refresh(programme)
        except Exception:  # one programme's failure does not stop the others
            logger.exception('figures %s failed', programme)
