web: gunicorn config.wsgi -w 4 -b "0.0.0.0:$PORT" --log-level=info --timeout=3200
worker: celery worker --app=student_registration.taskapp --loglevel=info
beater: celery beat --app=student_registration.taskapp --loglevel=info

