#!/bin/sh
/venv/bin/python manage.py migrate
/venv/bin/python manage.py runserver_plus 0.0.0.0:8000
