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
    from student_registration.attendances.models import Attendance
    classes = ClassRoom.objects.all()
    for item in classes:
        students = []
        attstudent = {}
        attendances = {}
        registrations = Registration.objects.filter(classroom_id=item.id, school_id=item.school.id)
        for reg in registrations:
            student = {
                "student_id": reg.student.id,
                "student_name": reg.student.full_name,
                "gender": reg.student.sex,
            }
            attstudent[reg.student.id] = False
            students.append(student)

        attendqueryset = Attendance.objects.filter(classroom_id=item.id, school_id=item.school.id)
        for att in attendqueryset:
            attendances = {
                att.attendance_date.strftime('%Y-%m-%d'): {
                    "validation_date": att.validation_date.strftime('%Y-%m-%d'),
                    "students": attstudent
                }
            }
            attendances[att.attendance_date.strftime('%Y-%m-%d')]["students"][att.student.id] = att.status

        doc = {
            "class_id": item.id,
            "class_name": item.name,
            "grade_id": item.grade.id,
            "grade_name": item.grade.name,
            "location_id": item.school.location.id,
            "location_name": item.school.location.name,
            "location_pcode": item.school.location.p_code,
            "school_id": item.school.number,
            "school_name": item.school.name,
            "section_id": item.section.id,
            "section_name": item.section.name,
            "students": students,
            "attendance": attendances
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

    for row in data['rows']:
        if 'attendance' in row['doc']:
            classroom = row['doc']['class_id']
            school = row['doc']['school_id']
            attendance = row['doc']['attendance']
            if 'validation_date' in attendance:
                validation_date = attendance['validation_date']
                attendance_date = attendance[0]
                students = attendance['students']
                try:
                    for student_id, status in students:
                        instance = Attendance.objects.get(
                            student_id=student_id,
                            classroom_id=classroom,
                            school_id=school,
                            attendance_date=attendance_date
                        )
                    instance.status = status
                    instance.validation_date = validation_date
                    instance.save()
                except Attendance.DoesNotExist:
                    Attendance.objects.create(
                            student_id=student_id,
                            classroom_id=classroom,
                            school_id=school,
                            attendance_date=attendance_date,
                            status=status,
                            validation_date=validation_date
                    )
                except Exception as exp:
                    print exp.message
