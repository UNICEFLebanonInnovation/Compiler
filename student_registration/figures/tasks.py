"""Background counting of the NeuroDB figures (Celery worker).

NeuroDB asks for a count through the API (POST /api/figures/runs/) on its own schedule; the worker
runs it here. BMA keeps no schedule for these counts.
"""

import logging

from student_registration.taskapp.celery import app

from . import snapshots

logger = logging.getLogger(__name__)


@app.task(ignore_result=True, soft_time_limit=3600, time_limit=3800)
def run_figures(run_id):
    snapshots.execute_run(run_id)
