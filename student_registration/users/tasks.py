__author__ = 'achamseddine'

from student_registration.taskapp.celery import app


@app.task
def generate_passwords():
    from student_registration.users.models import User

    users = User.objects.filter(is_staff=False, is_superuser=False)
    for user in users:
        try:
            user.update_password(user.username)
            user.save()
        except Exception as ex:
            print ex.messages
            pass
