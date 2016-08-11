__author__ = 'jcranwellward'

import datetime
import json
import os

import requests
from django.conf import settings
from django.db import connection
from requests.auth import HTTPBasicAuth
from student_registration.taskapp.celery import app


def set_docs(docs):

    payload_json = json.dumps(
        {
            'docs': docs,
            'all_or_nothing': True
        }
    )
    path = os.path.join(settings.COUCHBASE_URL, '_bulk_docs')
    response = requests.post(
        path,
        headers={'content-type': 'application/json'},
        auth=HTTPBasicAuth(settings.COUCHBASE_USER, settings.COUCHBASE_PASS),
        data=payload_json,
    )
    return response


@app.task
def set_app_user(username, password):

    user_docs = []
    user_docs.append(
        {
            "_id": username,
            "type": "user",
            "username": username,
            "password": password,
            "organisation": username,
        }
    )

    response = set_docs(user_docs)
    return response.text


@app.task
def set_app_attendances():
    """
    Creates or edits a attendance document in Couchbase
    """
    docs = []
    from student_registration.students.models import ClassRoom
    from student_registration.alp.models import Registration
    classes = ClassRoom.objects.all()
    for item in classes:
        students = []
        registrations = Registration.objects.filter(classroom_id=item.id)
        for reg in registrations:
            student = {
                "student": reg.student.id,
                "student_name": reg.student.full_name,
                "gender": reg.student.sex,
                "attendance": reg.student.attendance_list
            }
            students.append(student)

        doc = {
            "class": item.id,
            "class_name": item.name,
            "grade": item.grade.id,
            "grade_name": item.grade.name,
            "location": item.school.location.id,
            "location_name": item.school.location.name,
            "school": item.school.id,
            "school_name": item.school.name,
            "section": item.section.id,
            "section_name": item.section.name,
            "students": students
        }
        docs.append(doc)

    response = set_docs(docs)
    if response.status_code in [requests.codes.ok, requests.codes.created]:
        return response.text


@app.task
def import_docs(**kwargs):
    """
    Imports docs from couch base
    """
    from student_registration.attendances.models import Attendance

    data = requests.get(
        os.path.join(settings.COUCHBASE_URL, '_all_docs?include_docs=true'),
        auth=HTTPBasicAuth(settings.COUCHBASE_USER, settings.COUCHBASE_PASS)
    ).json()

