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
def import_visits(**kwargs):
    """
    Imports docs from couch base
    """
    from student_registration.attendances.models import Attendance

    # data = requests.get(
    #     os.path.join(settings.COUCHBASE_URL, '_all_docs?include_docs=true'),
    #     auth=HTTPBasicAuth(settings.COUCHBASE_USER, settings.COUCHBASE_PASS)
    # ).json()

    data = Attendance.objects.get()

    for row in data['rows']:
        if 'attendance' in row['doc']:
            classroom = row['doc']['class_id']
            school = row['doc']['school']
            school_type = row['doc']['school_type']
            attendances = row['doc']['attendance']
            for key in attendances.keys():
                attendance = attendances[key]
                students = attendance['students']
                validation_date = ''
                if 'validation_date' in attendance:
                    validation_date = attendance['validation_date']
                attendance_date = key

                try:
                    validation_date = datetime.strptime(validation_date, '%d-%m-%Y').strftime('%Y-%m-%d')
                except Exception as exp:
                    pass
                try:
                    attendance_date = datetime.strptime(attendance_date, '%d-%m-%Y').strftime('%Y-%m-%d')
                except Exception as exp:
                    pass

                try:
                    for student_id in students.keys():
                        status = students[student_id]
                        if school_type == 'alp':
                            instance = Attendance.objects.get_or_create(
                                student_id=student_id,
                                class_level=classroom,
                                school_id=school,
                                attendance_date=attendance_date
                            )
                        else:
                            instance = Attendance.objects.get_or_create(
                                student_id=student_id,
                                classroom_id=classroom,
                                school_id=school,
                                attendance_date=attendance_date
                            )
                        instance.status = status

                        if validation_date:
                            instance.validation_date = validation_date
                            instance.validation_status = True
                        instance.save()
                except Exception as exp:
                    print exp.message
