web: gunicorn config.wsgi:application --workers=4 --timeout=3200
worker: celery worker --app=student_registration.taskapp --loglevel=info
