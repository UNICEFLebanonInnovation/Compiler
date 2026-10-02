"""The wellbeing calculation run by the Celery worker when NeuroDB asks for it (POST
/api/wellbeing/runs/). NeuroDB holds the schedule; BMA keeps none."""

from student_registration.taskapp.celery import app

from . import runs


@app.task(ignore_result=True, soft_time_limit=3600, time_limit=3800)
def run_wellbeing(run_id):
    runs.execute(run_id)
