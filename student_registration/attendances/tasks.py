__author__ = 'jcranwellward'

import datetime
import json
import os
from datetime import datetime

import requests
from requests.auth import HTTPBasicAuth

from django.conf import settings
from django.db.models import Count, Case, When

from student_registration.taskapp.celery import app


def convert_date(date):
    try:
        date = datetime.strptime(
            date,
            '%d-%m-%Y'
        ).strftime('%Y-%m-%d')
    except Exception as exp:
        date = ''
    return date


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
def set_app_attendances(school_number=None, school_type=None):
    """
    Creates or edits a attendance document in Couchbase for each school, class, section
    """
    from student_registration.enrollments.models import Enrollment
    from student_registration.attendances.models import Attendance
    from student_registration.schools.models import School, ClassRoom, Section

    docs = []
    registrations = Enrollment.objects.exclude(
        deleted=True
    ).filter(
        classroom__isnull=False,
        section__isnull=False
    ).distinct().values(
        'school__number',
        'school',
        'classroom',
        'section'
    )
    if school_number is not None:
        registrations.filter(school__number=school_number)

    for reg in registrations:
        school = School.objects.get(id=reg['school'])
        classroom = ClassRoom.objects.get(id=reg['classroom'])
        section = Section.objects.get(id=reg['section'])
        students = []
        attendances = {}

        # build dictionary of currently enrolled students for this school, class, section
        for enrolled in Enrollment.objects.exclude(deleted=True).filter(**reg):
            student = {
                "student_id": str(enrolled.student.id),
                "student_name": enrolled.student.__unicode__(),
                "gender": enrolled.student.sex,
                "status": enrolled.student.status
            }
            students.append(student)

        # build dictionary of current attendance records indexed by attendance day
        reg.pop('section')
        for att in Attendance.objects.filter(**reg):
            attendance_date = att.attendance_date.strftime('%d-%m-%Y')
            student_record = {
                "status": att.status,
                "reason": att.absence_reason
            }
            students_attended = attendances.setdefault(attendance_date, {"students":{}})
            students_attended['students'][str(att.student.id)] = student_record
            if att.validation_date:
                attendances[attendance_date]['validation_date'] = att.validation_date.strftime('%d-%m-%Y')

        # combine into a single doc representing students and attendance for a single school, class, section
        doc_id = "{}-{}-{}".format(reg['school__number'], classroom.id, section.id)
        doc = {
            "_id": doc_id,
            "class_id": str(classroom.id),
            "class_name": classroom.name,
            "location_id": str(school.location.id),
            "location_name": school.location.name,
            "location_pcode": school.location.p_code,
            "school": str(school.id),
            "school_id": school.number,
            "school_type": school_type if school_type else "2ndshift",
            "school_name": school.name,
            "section_id": str(section.id),
            "section_name": section.name,
            "students": students,
            "attendance": attendances
        }

        # get existing document rev id if this document already exists in couchbase.
        # this prevents it being overwritten when needed to update an existing document.
        doc_rev = get_doc_rev(doc_id)
        if doc_rev:
            doc['_rev'] = doc_rev
        docs.append(doc)

    response = set_docs(docs)
    print response
    if response.status_code in [requests.codes.ok, requests.codes.created]:
        return response.text


@app.task
def set_app_schools():
    """
    Creates the schools lookup in the application
    :return:
    """
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
    """
    Creates a lookup
    :return:
    """
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
    Imports attendance docs from couch base server
    """
    from student_registration.attendances.models import Attendance
    from student_registration.schools.models import ClassRoom, ClassLevel

    try:
        data = requests.get(
            os.path.join(settings.COUCHBASE_URL, '_all_docs?include_docs=true'),
            auth=HTTPBasicAuth(settings.COUCHBASE_USER, settings.COUCHBASE_PASS)
        ).json()

        for row in data['rows']:
            if 'attendance' in row['doc']:
                class_id = row['doc']['class_id']
                school = row['doc']['school']
                school_type = row['doc']['school_type']
                attendances = row['doc']['attendance']

                for key, attendance in attendances.items():
                    students = attendance['students']
                    attendance_date = convert_date(key)
                    validation_date = ''
                    if 'validation_date' in attendance:
                        validation_date = convert_date(attendance['validation_date'])

                    for student_id, student in students.items():
                        attended = student['status']
                        attendance_record, new = Attendance.objects.get_or_create(
                            student_id=student_id,
                            school_id=school,
                            attendance_date=attendance_date
                        )
                        attendance_record.status = attended
                        attendance_record.absence_reason = student['reason']
                        if school_type == 'alp':
                            classlevel = ClassLevel.objects.get(id=class_id)
                            attendance_record.class_level = classlevel
                        else:
                            classroom = ClassRoom.objects.get(id=class_id)
                            attendance_record.classroom = classroom
                        if validation_date:
                            attendance_record.validation_date = validation_date
                            attendance_record.validation_status = True

                        attendance_record.save()

        calculate_by_day_summary()
    except Exception as exp:
        # TODO: Add proper logging here
        print exp.message


def calculate_by_day_summary():
    """
    Calculates the total attendances and absences for each school on each day.
    Utilises Django aggregation framework to execute this on the database.
    :return:
    """
    from student_registration.attendances.models import Attendance, BySchoolByDay

    days = Attendance.objects.filter(
        # select only validated attendances
        validation_status=True
    ).values(
        # group by school and day
        'school_id',
        'attendance_date'
    ).annotate(
        # create totals from raw data
        total_enrolled=Count('student'),
        total_attended=Count(Case(When(status=True, then=1))),
        total_absences=Count(Case(When(status=False, then=1))),
        vcalidated=True
    )

    day_records = [BySchoolByDay(**day) for day in days]

    BySchoolByDay.objects.all().delete()
    BySchoolByDay.objects.bulk_create(day_records)
