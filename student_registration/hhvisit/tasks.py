__author__ = 'yosr'

from student_registration.taskapp.celery import app

@app.task
def load_absences(**kwargs):
    import student_registration.hhvisit.management.commands.load_absences
    student_registration.hhvisit.management.commands.load_absences.LoadAbsences()
