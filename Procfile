web: gunicorn config.wsgi:application --workers=4 --bind=0.0.0.0:$PORT --timeout=60 --log-level=info
worker: celery -A student_registration.taskapp.celery worker --loglevel=info
beater: celery -A student_registration.taskapp.celery beat --loglevel=info
