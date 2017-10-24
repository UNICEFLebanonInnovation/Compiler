
from student_registration.taskapp.celery import app


@app.task
def cleanup_old_data():
    from .models import Beneficiary

    registrations = Beneficiary.objects.all()
    print(registrations.count())
    registrations.delete()
