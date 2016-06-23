web: gunicorn config.wsgi:application
worker: celery worker --app=student_registration.taskapp --loglevel=info
