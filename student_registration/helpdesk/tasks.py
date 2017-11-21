

from student_registration.taskapp.celery import app


@app.task
def cleanup_old_data():
    from .models import Ticket

    tickets = Ticket.objects.all()
    tickets.delete()
