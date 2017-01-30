# -*- coding: utf-8 -*-
__author__ = 'jcranwellward'

import json
import os
import unicodedata
from datetime import datetime, date, timedelta

import requests
from requests.auth import HTTPBasicAuth

from django.conf import settings
from django.db import transaction
from django.db.models import Count, Case, When, Value, BooleanField, Max

from student_registration.taskapp.celery import app

import logging
logger = logging.getLogger(__name__)


def convert_date(date_string):
    try:
        if 'ARABIC' in unicodedata.name(date_string[0]):
            date_out = date(*reversed(map(int, date_string.split('-'))))
        else:
            date_out = datetime.strptime(date_string, '%d-%m-%Y').date()
    except Exception as exp:
        logger.exception(exp)
        date_out = ''
    return date_out


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


def get_app_collection(bulk_name):

    data = requests.get(
        os.path.join(settings.COUCHBASE_URL, bulk_name),
        auth=HTTPBasicAuth(settings.COUCHBASE_USER, settings.COUCHBASE_PASS)
    ).json()

    if data['_rev']:
        return data['_rev']
    return 0


def get_docs():
    return requests.get(
        os.path.join(settings.COUCHBASE_URL, '_all_docs?include_docs=true'),
        auth=HTTPBasicAuth(settings.COUCHBASE_USER, settings.COUCHBASE_PASS)
    ).json()


def get_doc(doc_id):

    path = os.path.join(settings.COUCHBASE_URL, doc_id)
    response = requests.get(
        path,
        auth=HTTPBasicAuth(settings.COUCHBASE_USER, settings.COUCHBASE_PASS),
    )

    if response.status_code in [requests.codes.ok, requests.codes.created]:
        return response.json()
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
    from student_registration.alp.models import Outreach
    from student_registration.enrollments.models import Enrollment
    from student_registration.attendances.models import Attendance
    from student_registration.schools.models import School, ClassRoom, Section, EducationLevel

    docs = []
    enrollment_model = Outreach if school_type == 'alp' else Enrollment

    registrations = enrollment_model.objects.exclude(deleted=True)

    if school_type == 'alp':
        registrations = registrations.filter(
            registered_in_level__isnull=False,
            section__isnull=False
        ).distinct().values(
            'school__number',
            'school',
            'registered_in_level',
            'section'
        )
    else:
        registrations = registrations.filter(
            classroom__isnull=False,
            section__isnull=False
        ).distinct().values(
            'school__number',
            'school',
            'classroom',
            'section'
        )
    if school_number is not None:
        registrations = registrations.filter(school__number=school_number)

    logger.info('{} documents to process'.format(registrations.count()))
    for reg in registrations:
        school = School.objects.get(id=reg['school'])
        classroom = EducationLevel.objects.get(id=reg['registered_in_level']) if school_type == 'alp' \
                    else ClassRoom.objects.get(id=reg['classroom'])

        section = Section.objects.get(id=reg['section'])
        students = []
        attendances = {}
        doc_id = "{}-{}-{}".format(reg['school__number'], classroom.id, section.id)
        if school_type == 'alp':
            doc_id = "{}-{}".format(doc_id, 'alp')

        # build dictionary of currently enrolled students for this school, class, section
        total_enrolled = enrollment_model.objects.exclude(deleted=True).filter(**reg)
        logger.info('{} students in class {}'.format(total_enrolled.count(), doc_id))
        for enrolled in total_enrolled:
            student = {
                "student_id": str(enrolled.student.id),
                "student_name": enrolled.student.__unicode__(),
                "gender": enrolled.student.sex,
                "status": enrolled.student.status
            }
            students.append(student)

        #FIXME: Why are we updating the attendance here if it could potentially wipe out attendance records in the app
        # # build dictionary of current attendance records indexed by attendance day
        # reg.pop('section')
        # for att in Attendance.objects.filter(**reg):
        #     attendance_date = att.attendance_date.strftime('%d-%m-%Y')
        #     student_record = {
        #         "status": att.status,
        #         "reason": att.absence_reason
        #     }
        #     students_attended = attendances.setdefault(attendance_date, {"students":{}})
        #     students_attended['students'][str(att.student.id)] = student_record
        #     if att.validation_date:
        #         attendances[attendance_date]['validation_date'] = att.validation_date.strftime('%d-%m-%Y')

        # combine into a single doc representing students and attendance for a single school, class, section
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

        # get existing document if this document already exists in couchbase.
        # this prevents it being overwritten when updating an existing document.
        exisiting_doc = get_doc(doc_id)
        if exisiting_doc:
            doc['_rev'] = exisiting_doc['_rev']
            doc['attendance'] = exisiting_doc['attendance']
        docs.append(doc)

    response = set_docs(docs)
    logger.info(response)
    if response.status_code in [requests.codes.ok, requests.codes.created]:
        return response.text


@app.task
def set_app_schools():
    """
    Creates the schools lookup in the application
    :return:
    """
    docs = {}
    rev = get_app_collection('schools')

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
    from student_registration.schools.models import ClassRoom, EducationLevel

    try:
        data = get_docs()
        attendance_records = []
        logger.info('processing {} docs'.format(len(data['rows'])))
        with transaction.atomic():
            Attendance.objects.all().delete()
            for num,row in enumerate(data['rows']):
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
                            if type(student) is bool:
                                logger.info('bad doc: {}'.format(row['doc']['_id']))
                                continue
                            attendance_record = Attendance(
                                student_id=student_id,
                                school_id=school,
                                attendance_date=attendance_date
                            )
                            attendance_record.status = student['status']
                            attendance_record.absence_reason = student['value']
                            if school_type == 'alp':
                                attendance_record.classlevel_id = class_id
                            else:
                                attendance_record.classroom_id = class_id
                            if validation_date:
                                attendance_record.validation_date = validation_date
                                attendance_record.validation_status = True

                            attendance_records.append(attendance_record)

                    if num % 100 == 0:
                        Attendance.objects.bulk_create(attendance_records)
                        logger.info('processed {} docs'.format(num))
                        attendance_records = []

        logger.info('attendance updated')

        calculate_by_day_summary()
        logger.info('by day summary updated')

        calculate_absentees_in_date_range(
            date.today()-timedelta(days=10),
            date.today()
        )
        logger.info('absentees updated')
    except Exception as exp:
<<<<<<< HEAD
=======
        #TAREK EDIT: The below line was breaking the script since 'row' is undefined. commenting out for now since it is only a logger within the exception block.
        #logger.info('importing doc: {}'.format(row['doc']['_id']))
>>>>>>> develop
        logger.exception(exp)
        raise exp


def calculate_attendance_and_absentees():

    try:
        calculate_by_day_summary()
        calculate_absentees_in_date_range(
            date.today() - timedelta(days=10),
            date.today()
        )
    except Exception as exp:
        logger.exception(exp)


def calculate_by_day_summary():
    """
    Calculates the total attendances and absences for each school on each day.
    Utilises Django aggregation framework to execute this on the database.
    :return:
    """
    from student_registration.attendances.models import Attendance, BySchoolByDay

    days = Attendance.objects.values(
        # group by school and day
        'school_id',
    ).annotate(
        # create totals from raw data
        total_enrolled=Count('student'),
        total_attended=Count(Case(When(status=True, then=1))),
        total_absences=Count(Case(When(status=False, then=1))),
        total_attended_male=Count(Case(When(status=True, student__sex=u'Male', then=1))),
        total_attended_female=Count(Case(When(status=True, student__sex=u'Female', then=1))),
        total_absent_male=Count(Case(When(status=False, student__sex=u'Male', then=1))),
        total_absent_female=Count(Case(When(status=False, student__sex=u'Female', then=1))),
    )

    select_fields = (
        'school_id',
        'attendance_date',
        'total_enrolled',
        'total_attended',
        'total_absences',
        'total_attended_male',
        'total_attended_female',
        'total_absent_male',
        'total_absent_female',
        'validation_status'
    )

    days_valid = days.filter(validation_status=True).values(*select_fields)
    days_invalid = days.filter(validation_status=False).values(*select_fields)

    day_records = [BySchoolByDay(**day) for day in days_valid | days_invalid]

    BySchoolByDay.objects.all().delete()
    BySchoolByDay.objects.bulk_create(day_records)

    schools_valid = BySchoolByDay.objects.filter(
        validation_status=True
    ).values(
        'school_id',
    ).distinct().annotate(
        attended=Max('total_attended')
    )

    for school in schools_valid:
        school_instance = BySchoolByDay.objects.filter(
            school_id=school['school_id'],
            total_attended=school['attended']
        ).latest('attendance_date')
        school_instance.highest_attendance_rate = True
        school_instance.save()


def calculate_absentees_in_date_range(from_date, to_date, absent_threshold=10):
    """
    Calculate the consistent absentees in the last 10 days
    :return:
    """
    from student_registration.attendances.models import Attendance, Absentee

    absentees = Attendance.objects.filter(
        # select only validated attendances
        validation_status=True,
        attendance_date__gt=from_date,
        attendance_date__lte=to_date
    ).values(
        'student_id',
        'school_id'
    ).annotate(
        total_attended=Count(Case(When(status=True, then=1))),
        total_absents=Count(Case(When(status=False, then=1))),
    ).filter(
        total_absents__gt=absent_threshold
    )

    logger.info('{} absentees to process'.format(absentees.count()))
    for absentee in absentees:

        # for each absentee check if they have attended within the absent_threshold
        attendances = Attendance.objects.filter(
            validation_status=True,
            school_id=absentee['school_id'],
            student_id=absentee['student_id'],
        )

        last_attended_date = attendances.filter(status=True).latest('attendance_date').attendance_date \
        if attendances.filter(status=True).count() else attendances.filter(status=False).earliest('attendance_date').attendance_date

        late_threshold_date = (to_date - timedelta(days=absent_threshold))
        if last_attended_date >= late_threshold_date:

            first_absent_date=attendances.filter(
                status=False,
                attendance_date__lt=last_attended_date,
                attendance_date__gte=from_date,
            ).earliest('attendance_date').attendance_date

            total_school_days_absent = Attendance.objects.filter(
                attendance_date__lt=last_attended_date,
                attendance_date__gte=first_absent_date
            ).distinct('attendance_date').count()

            absent_record, new = Absentee.objects.get_or_create(
                school_id=absentee['school_id'],
                student_id=absentee['student_id'],
                last_attendance_date=first_absent_date,
            )

            absent_record.absent_days = total_school_days_absent
            absent_record.reattend_date = late_threshold_date
            absent_record.save()
            logger.info('student {} attended on {}'.format(absentee['school_id'], last_attended_date))

        else:

            total_school_days_absent = Attendance.objects.filter(
                attendance_date__gte=last_attended_date,
                attendance_date__lte=to_date
            ).distinct('attendance_date').count()

            absent_record, new = Absentee.objects.get_or_create(
                school_id=absentee['school_id'],
                student_id=absentee['student_id'],
                last_attendance_date=last_attended_date,
                reattend_date__isnull=True
            )
            absent_record.absent_days = total_school_days_absent
            absent_record.save()

        if new:
            logger.info('New absent record for student {}'.format(absentee['student_id']))



