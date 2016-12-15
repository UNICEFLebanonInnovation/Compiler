__author__ = 'yosr'

import datetime
import json
import os
from datetime import datetime

import requests
from django.conf import settings
from django.db import connection
from requests.auth import HTTPBasicAuth
from student_registration.taskapp.celery import app

@app.task
def load_absences(**kwargs):
    import student_registration.hhvisit.commands.load_absences
    student_registration.hhvisit.commands.load_absences.LoadAbsences()
