#!/bin/sh
<<<<<<< HEAD
python /app/manage.py collectstatic --noinput
/usr/local/bin/gunicorn config.wsgi -w 4 -b 0.0.0.0:5000 --chdir=/app
=======
/venv/bin/gunicorn config.wsgi -w 4 -b 0.0.0.0:80
>>>>>>> 3b9073c012bcdfc49afcb1d105deb56123ab5be1
