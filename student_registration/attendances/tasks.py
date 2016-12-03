__author__ = 'jcranwellward'

import datetime
import json
import os
from datetime import datetime

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
    from student_registration.schools.models import School
    from student_registration.enrollments.models import Enrollment
    from student_registration.attendances.models import Attendance
    schools = School.objects.all()
    for school in schools:
        students = []
        attstudent = {}
        attendances = {}
        registrations = Enrollment.objects.filter(school_id=school.id)
        for reg in registrations:
            if not reg.classroom_id or not reg.section_id:
                continue
            student = {
                "student_id": str(reg.student.id),
                "student_name": reg.student.full_name if reg.student.full_name else 'Student',
                "gender": reg.student.sex,
                "status": reg.student.status
            }
            attstudent[str(reg.student.id)] = {
                "status": False,
                "reason": "none"
            }
            students.append(student)

            attendqueryset = Attendance.objects.filter(classroom_id=reg.classroom.id, school_id=school.id)
            for att in attendqueryset:
                attendances = {
                    att.attendance_date.strftime('%d-%m-%Y'): {
                        "validation_date": att.validation_date.strftime('%d-%m-%Y'),
                        "students": attstudent
                    }
                }
                attendances[att.attendance_date.strftime('%d-%m-%Y')]["students"][str(att.student.id)] = {
                    "status": att.status,
                    "reason": att.absence_reason
                }

            doc = {
                "class_id": str(reg.classroom.id),
                "class_name": reg.classroom.name,
                "location_id": str(school.location.id),
                "location_name": school.location.name,
                "location_pcode": school.location.p_code,
                "school": str(school.id),
                "school_id": school.number,
                "school_type": "2ndshift",
                "school_name": school.name,
                "section_id": str(reg.section.id),
                "section_name": reg.section.name,
                "students": students,
                "attendance": attendances
            }
            docs.append(doc)

    # print json.dumps(docs)

    response = set_docs(docs)
    print response
    if response.status_code in [requests.codes.ok, requests.codes.created]:
        return response.text


@app.task
def set_app_attendances_alp():
    """
    Creates or edits a attendance document in Couchbase
    """
    docs = []
    from student_registration.schools.models import School
    from student_registration.alp.models import Outreach
    from student_registration.attendances.models import Attendance
    schools = School.objects.all()
    for school in schools:
        students = []
        attstudent = {}
        attendances = {}
        registrations = Outreach.objects.filter(school_id=school.id)
        for reg in registrations:
            if not reg.registered_in_level_id or not reg.section_id:
            # if not reg.assigned_to_level_id:
                continue
            student = {
                "student_id": str(reg.student.id),
                "student_name": reg.student.full_name if reg.student.full_name else 'Student',
                "gender": reg.student.sex,
                "status": reg.student.status
            }
            attstudent[str(reg.student.id)] = {
                "status": False,
                "reason": "none"
            }
            students.append(student)

            attendqueryset = Attendance.objects.filter(classlevel_id=reg.registered_in_level.id, school_id=school.id)
            for att in attendqueryset:
                attendances = {
                    att.attendance_date.strftime('%d-%m-%Y'): {
                        "validation_date": att.validation_date.strftime('%d-%m-%Y'),
                        "students": attstudent
                    }
                }
                attendances[att.attendance_date.strftime('%d-%m-%Y')]["students"][str(att.student.id)] = {
                    "status": att.status,
                    "reason": att.absence_reason
                }

            doc = {
                "class_id": str(reg.registered_in_level.id) if reg.registered_in_level else 0,
                "class_name": reg.registered_in_level.name if reg.registered_in_level else '',
                "location_id": str(school.location.id),
                "location_name": school.location.name,
                "location_pcode": school.location.p_code,
                "school": str(school.id),
                "school_id": school.number,
                "school_type": "alp",
                "school_name": school.name,
                "section_id": str(reg.section.id) if reg.section else 0,
                "section_name": reg.section.name if reg.section else '',
                "students": students,
                "attendance": attendances
            }
            docs.append(doc)

    response = set_docs(docs)
    print response
    if response.status_code in [requests.codes.ok, requests.codes.created]:
        return response.text


def get_app_revision(block_name):

    data = requests.get(
        os.path.join(settings.COUCHBASE_URL, block_name),
        auth=HTTPBasicAuth(settings.COUCHBASE_USER, settings.COUCHBASE_PASS)
    ).json()

    if data['_rev']:
        return data['_rev']
    return 0


@app.task
def set_app_schools():

    docs = {}
    rev = get_app_revision('schools')

    from student_registration.schools.models import School
    schools = School.objects.all()
    for school in schools:
        if not school.location:
            continue
        if school.location.name not in docs:
            docs[school.location.name] = []

        docs[school.location.name].append({
            "caza": school.location.name,
            "mouhafaza": school.location.parent.name if school.location.parent else '',
            "cerd_id": str(school.number),
            "school_name": school.name
        })
    if rev:
        docs2 = {
            "_rev": rev,
            "_id": "schools",
            "type": "schools",
            "schools": docs
        }
    else:
        docs2 = {
            "_id": "schools",
            "type": "schools",
            "schools": docs
        }

    response = set_docs([docs2])

    if response.status_code in [requests.codes.ok, requests.codes.created]:
        return response.text


@app.task
def set_app_users():

    docs = []

    # rev = get_app_revision('users')

    from student_registration.users.models import User
    from student_registration.users.utils import get_user_token, user_main_role
    users = User.objects.filter(is_active=True, is_staff=False, is_superuser=False)
    for user in users:
        if not user.school:
            continue
        doc = {
            "_id": user.username,
            "cerd_id": user.school.number,
            "location_id": user.location_id,
            "username": user.username,
            "password": user.password,
            "token": get_user_token(user.id),
            "role": user_main_role(user)
        }
        docs.append(doc)

    response = set_docs(docs)
    print response
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
                        status = students[student_id]['status']
                        reason = students[student_id]['reason']
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
                        instance.absence_reason = reason

                        if validation_date:
                            instance.validation_date = validation_date
                            instance.validation_status = True
                        instance.save()
                except Exception as exp:
                    print exp.message
