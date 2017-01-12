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


def get_app_revision(bulk_name):

    data = requests.get(
        os.path.join(settings.COUCHBASE_URL, bulk_name),
        auth=HTTPBasicAuth(settings.COUCHBASE_USER, settings.COUCHBASE_PASS)
    ).json()

    if data['_rev']:
        return data['_rev']
    return 0


def get_docs(docs):

    payload_json = json.dumps(
        {
            'docs': docs,
        }
    )
    path = os.path.join(settings.COUCHBASE_URL, '_bulk_get')
    response = requests.post(
        path,
        # headers={'content-type': 'multipart/mixed'},
        auth=HTTPBasicAuth(settings.COUCHBASE_USER, settings.COUCHBASE_PASS),
        data=payload_json,
    )
    try:
        text = response.text
        return json.loads(text.splitlines()[3])
    except Exception as ex:
        print text, ex.message


def get_doc_rev(doc_id):

    path = os.path.join(settings.COUCHBASE_URL, doc_id)
    response = requests.get(
        path,
        auth=HTTPBasicAuth(settings.COUCHBASE_USER, settings.COUCHBASE_PASS),
    )

    if response.status_code in [requests.codes.ok, requests.codes.created]:
        doc = json.loads(response.text)
        return doc['_rev']
    return False


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
def set_app_attendances(school_number=None):
    """
    Creates or edits a attendance document in Couchbase
    """
    from student_registration.schools.models import School
    from student_registration.enrollments.models import Enrollment
    from student_registration.attendances.models import Attendance

    docs = []
    if not school_number:
        schools = School.objects.all().order_by('id')
    else:
        schools = School.objects.filter(number=school_number)
    for school in schools:
        students = []
        attstudent = {}
        attendances = {}
        registrations = Enrollment.objects.exclude(deleted=True).filter(school_id=school.id).values_list('classroom', 'section').distinct().order_by('classroom', 'section')
        for reg in registrations:
            classroom_id = reg[0]
            section_id = reg[1]
            students = []
            attendances = {}
            if not classroom_id or not section_id:
                continue
            students_per_class = Enrollment.objects.exclude(deleted=True).filter(classroom_id=classroom_id, section_id=section_id, school_id=school.id)
            for reg_std in students_per_class:
                std = reg_std.student
                student = {
                    "student_id": str(std.id),
                    "student_name": std.__unicode__(),
                    "gender": std.sex,
                    "status": std.status
                }
                attstudent[str(std.id)] = {
                    "status": False,
                    "reason": "none"
                }
                students.append(student)

                attendqueryset = Attendance.objects.filter(classroom_id=reg_std.classroom_id, school_id=school.id)
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

            doc_id = "{}-{}-{}".format(school.number, reg_std.classroom_id, reg_std.section_id)
            doc = {
                "_id": doc_id,
                "class_id": str(reg_std.classroom.id),
                "class_name": reg_std.classroom.name,
                "location_id": str(school.location.id),
                "location_name": school.location.name,
                "location_pcode": school.location.p_code,
                "school": str(school.id),
                "school_id": school.number,
                "school_type": "2ndshift",
                "school_name": school.name,
                "section_id": str(reg_std.section.id),
                "section_name": reg_std.section.name,
                "students": students,
                "attendance": attendances
            }
            doc_rev = get_doc_rev(doc_id)
            if doc_rev:
                doc['_rev'] = doc_rev
            docs.append(doc)

    # print json.dumps(docs)

    response = set_docs(docs)
    print response
    if response.status_code in [requests.codes.ok, requests.codes.created]:
        return response.text


@app.task
def set_app_attendances_alp(school_number=None):
    """
    Creates or edits a attendance document in Couchbase
    """
    from student_registration.schools.models import School
    from student_registration.alp.models import Outreach
    from student_registration.attendances.models import Attendance

    docs = []
    if not school_number:
        schools = School.objects.all().order_by('id')
    else:
        schools = School.objects.filter(number=school_number)
    for school in schools:
        students = []
        attstudent = {}
        attendances = {}
        registrations = Outreach.objects.exclude(deleted=True).filter(school_id=school.id).values_list('registered_in_level', 'section').distinct().order_by('registered_in_level', 'section')
        for reg in registrations:
            registered_in_level_id = reg[0]
            section_id = reg[1]
            students = []
            attendances = {}
            if not registered_in_level_id or not section_id:
                continue
            students_per_class = Outreach.objects.exclude(deleted=True).filter(registered_in_level_id=registered_in_level_id, section_id=section_id, school_id=school.id)
            for reg_std in students_per_class:
                std = reg_std.student
                student = {
                    "student_id": str(std.id),
                    "student_name": std.__unicode__(),
                    "gender": std.sex,
                    "status": std.status
                }
                attstudent[str(std.id)] = {
                    "status": False,
                    "reason": "none"
                }
                students.append(student)

                attendqueryset = Attendance.objects.filter(classlevel_id=reg_std.registered_in_level_id, school_id=school.id)
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

            doc_id = "{}-{}-{}".format(school.number, reg_std.registered_in_level_id, reg_std.section_id)
            doc = {
                "_id": doc_id,
                "class_id": str(reg_std.registered_in_level.id),
                "class_name": reg_std.registered_in_level.name,
                "location_id": str(school.location.id),
                "location_name": school.location.name,
                "location_pcode": school.location.p_code,
                "school": str(school.id),
                "school_id": school.number,
                "school_type": "alp",
                "school_name": school.name,
                "section_id": str(reg_std.section.id),
                "section_name": reg_std.section.name,
                "students": students,
                "attendance": attendances
            }
            doc_rev = get_doc_rev(doc_id)
            if doc_rev:
                doc['_rev'] = doc_rev
            docs.append(doc)

    # print json.dumps(docs)

    response = set_docs(docs)
    print response
    if response.status_code in [requests.codes.ok, requests.codes.created]:
        return response.text


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
            for key,attendance in attendances.items():
                students = attendance['students']
                attendance_date = convert_date(key)
                validation_date = ''
                if 'validation_date' in attendance:
                    validation_date = convert_date(attendance['validation_date'])

                try:
                    for student_id, student in students.items():

                        attendance_record = Attendance.objects.get_or_create(
                            student_id=student_id,
                            school_id=school,
                            classroom=classroom,
                            attendance_date=attendance_date
                        )
                        attendance_record.status = student['status']
                        attendance_record.absence_reason = student['reason']
                        if school_type == 'alp':
                            attendance_record.class_level = classroom
                        if validation_date:
                            attendance_record.validation_date = validation_date
                            attendance_record.validation_status = True

                        attendance_record.save()
                except Exception as exp:
                    print exp.message


def convert_date(date):
    try:
        date = datetime.strptime(
            date,
            '%d-%m-%Y'
        ).strftime('%Y-%m-%d')
    except Exception as exp:
        date = ''
    return date

