# -*- coding: utf-8 -*-
__author__ = 'jcranwellward'

import json
import os
import unicodedata
from datetime import datetime, date, timedelta

import requests
import re
from requests.auth import HTTPBasicAuth

from django.conf import settings
from django.db import transaction
from django.db.models import Count, Case, When, Value, BooleanField, Max

from student_registration.taskapp.celery import app

from mongoengine import *
from bson.code import Code
from bson import SON

client = connect(host=settings.MONGODB_URI)

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


def get_docs(all_docs=True):
    logger.info('Connecting to: {}'.format(settings.COUCHBASE_URL))
    return requests.get(
        os.path.join(settings.COUCHBASE_URL, '_all_docs?include_docs={}'.format('true' if all_docs else 'false')),
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
def set_app_attendances(school_number=None, school_type=None):
    """
    Creates or edits a attendance document in Couchbase for each school, class, section
    """
    from student_registration.alp.models import Outreach, ALPRound
    from student_registration.enrollments.models import Enrollment
    from student_registration.attendances.models import Attendance
    from student_registration.schools.models import School, ClassRoom, Section, EducationLevel

    docs = []
    enrollment_model = Outreach if school_type == 'alp' else Enrollment

    registrations = enrollment_model.objects.exclude(deleted=True).exclude(dropout_status=True)

    if school_type == 'alp':
        alp_round = ALPRound.objects.get(current_round=True)
        registrations = registrations.filter(
            registered_in_level__isnull=False,
            section__isnull=False,
            alp_round=alp_round
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
        total_enrolled = enrollment_model.objects.exclude(deleted=True).exclude(dropout_status=True).filter(**reg)
        logger.info('{} students in class {}'.format(total_enrolled.count(), doc_id))
        for enrolled in total_enrolled:
            student = {
                "student_id": str(enrolled.student.id),
                "student_name": enrolled.student.__unicode__(),
                "gender": enrolled.student.sex,
                "status": enrolled.student.status
            }
            students.append(student)

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
    try:
        # get all docs form couchbase
        logger.info('Importing...')
        couchbase_docs = get_docs(all_docs=False)

        ids = []
        for num, row in enumerate(couchbase_docs['rows']):
            if re.match('^\d+-\d+-\d+(-alp)?$', row["id"]):
                ids.append(row["id"])

        batches = [ids[x: x + 1000] for x in xrange(0, len(ids), 1000)]

        database = client.get_default_database()
        database.attendances.drop()
        for num, batch in enumerate(batches):
            logger.info('Requesting batch: {} of length {} keys'.format(num + 1, len(batch)))
            data = requests.post(
                os.path.join(settings.COUCHBASE_URL, '_all_docs?include_docs=true'),
                headers={'content-type': 'application/json'},
                auth=HTTPBasicAuth(settings.COUCHBASE_USER, settings.COUCHBASE_PASS),
                data=json.dumps({'keys': batch})
            ).json()

            logger.info("Prefilter attendance")
            cleaned = [row['doc'] for row in data['rows'] if 'attendance' in row['doc']]

            logger.info("refresing attendance in mongo")
            database.attendances.insert_many(cleaned)

        logger.info('Import Finished')

    except Exception as exp:
        logger.exception(exp)
        raise exp


def flatten_attendance():
    try:
        map_function = Code(
            """
            function () {

                var lookup = {};
                for (var index in this.students) {
                    student = this.students[index];
                    lookup[student.student_id] = student;
                }

                for (var date in this.attendance) {
                    day = this.attendance[date];
                    for (var student in day['students']) {

                        var key = this.school + '-' + date + '-' + student;
                        record = day['students'][student];

                        var gender = ((lookup.hasOwnProperty(student)) ? lookup[student].gender : null);

                        var valid = ((day.hasOwnProperty('validation_date')) ? new Date(day.validation_date.split("-").reverse().join("-")) : null)

                        var doc = {
                            date: new Date(date.split("-").reverse().join("-")),
                            school: this.school,
                            class: this.class_id,
                            section: this.section_id,
                            location: this.location_id,
                            student: student,
                            gender: gender,
                            attended: record.status,
                            reason: record.reason,
                            validation_date: valid

                        };
                        emit(key, doc);
                    }
                }
            }
            """
        )
        reduce_function = Code(
            """
            function (key, values) {
                return values[0];
            }
            """
        )

        logger.info('Performing map_reduce...')
        database = client.get_default_database()
        database.attendances.map_reduce(
            map_function,
            reduce_function,
            out=SON([("replace", "attendances_by_day")])
        )
        logger.info('Finished')
        logger.info('Replace root document')
        database.attendances_by_day.aggregate([
            {
                '$replaceRoot': {'newRoot': '$value'}
            },
            {'$out': "attendances_by_day"}
        ])
        logger.info('Finished')

    except Exception as exp:
        logger.exception(exp)


def aggregate_attendace():
    try:
        database = client.get_default_database()
        attendances = database.attendances_by_day

        logger.info('aggregate attendance by school and day')
        attendances.aggregate([
            {
                '$project': {
                    'school': '$value.school',
                    'date': '$value.date',
                    'validation_date': '$value.validation_date',
                    'student': '$value.student',
                    'gender': '$value.gender',
                    'Attended': {"$cond": ["$value.attended", 1, 0]},
                    'Absent': {"$cond": [{"$not": "$value.attended"}, 1, 0]},
                    'Attended Male': {
                        "$cond": [{'$and': [{"$eq": ["$value.gender", "Male"]}, "$value.attended"]}, 1, 0]
                    },
                    'Attended Female': {
                        "$cond": [{'$and': [{"$eq": ["$value.gender", "Female"]}, "$value.attended"]}, 1, 0]
                    },
                    'Absent Male': {
                        "$cond": [{'$and': [{"$eq": ["$value.gender", "Male"]}, {"$not": "$value.attended"}]}, 1, 0]
                    },
                    'Absent Female': {
                        "$cond": [{'$and': [{"$eq": ["$value.gender", "Female"]}, {"$not": "$value.attended"}]}, 1, 0]
                    },
                }
            },
            {
                '$group': {
                    '_id': {'school': '$school', 'date': '$date'},
                    'school_id': {'$first': '$school'},
                    'attendance_date': {'$first': '$date'},
                    'total_enrolled': {'$sum': 1},
                    'total_attended': {'$sum': "$Attended"},
                    'total_absences': {'$sum': "$Absent"},
                    'total_attended_male': {'$sum': "$Attended Male"},
                    'total_attended_female': {'$sum': "$Attended Female"},
                    'total_absent_male': {'$sum': "$Absent Male"},
                    'total_absent_female': {'$sum': "$Absent Female"},
                    'validation_date': {'$first': "$validation_date"},
                }
            },
            {
                "$project": {
                    "_id": 0,
                    'school_id': 1,
                    'attendance_date': 1,
                    'total_enrolled': 1,
                    'total_attended': 1,
                    'total_absences': 1,
                    'total_attended_male': 1,
                    'total_attended_female': 1,
                    'total_absent_male': 1,
                    'total_absent_female': 1,
                    'validation_date': 1,
                    'validation_status': {
                        '$cond': [
                            {'$eq': ['$validation_date', None]}, False, True
                        ]
                    }
                }
            },
            {'$out': 'attendances_by_day_school'}
        ], useCursor=False)
    except Exception as exp:
        logger.exception(exp)


def calculate_by_day_summary():
    """
    Calculates the total attendances and absences for each school on each day.
    Utilises Django aggregation framework to execute this on the database.
    :return:
    """
    from student_registration.attendances.models import BySchoolByDay

    class School(DynamicDocument):
        meta = {'collection': 'attendances_by_day_school'}

    day_records = [BySchoolByDay(**day.to_mongo()) for day in School.objects.exclude('_id')]

    logger.info('Inserting {} new by school and day summaries'.format(len(day_records)))
    BySchoolByDay.objects.all().delete()
    BySchoolByDay.objects.bulk_create(day_records)

    schools_valid = BySchoolByDay.objects.filter(
        validation_date__isnull=False
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
    logger.info('Finished')


def calculate_absentees_in_date_range(from_date, to_date, absent_threshold=10):
    """
    Calculate the consistent absentees in the last 10 days
    :return:
    """
    from student_registration.attendances.models import Absentee

    class Attendance(DynamicDocument):
        meta = {'collection': 'attendances_by_day'}

    database = client.get_default_database()

    absentees = database.attendances_by_day.aggregate([
        {
            '$match': {
                'validation_date': {'$not': {'$type': 'null'}},
                'date': {'$gt': from_date},
            }
        },
        {'$sort': {'value.date': 1}},
        {
            '$project': {
                'date': '$date',
                'school_id': '$school',
                'student_id': '$student',
                'attended': {'$cond': [{'$eq': ['$attended', True]}, 1, 0]},
                'absent': {'$cond': [{'$eq': ['$attended', False]}, 1, 0]},
            }
        },
        {
            '$group': {
                '_id': {'school_id': '$school_id', 'student_id': '$student_id'},
                'total_attended': {'$sum': "$attended"},
                'total_absences': {'$sum': "$absent"},
            }
        },
        {
            '$match': {
                'total_absences': {'$gt': absent_threshold},
            }
        },
    ], allowDiskUse=True)

    absentees = list(absentees)

    late_threshold_date = (to_date - timedelta(days=absent_threshold))

    logger.info('{} absentees to process'.format(len(absentees)))
    for num,absentee in enumerate(absentees):

        logger.info('processing {}'.format(num))
        school = absentee['_id']['school_id']
        student = absentee['_id']['student_id']

        # for each absentee check if they have attended within the absent_threshold
        attendances = Attendance.objects.filter(
            school=school,
            student=student,
        )

        last_attended_date = attendances.order_by('-date').filter(
            attended=True,
            validation_date__ne=None,
        )
        if not last_attended_date:
            logger.info('Student {} did not attend school {}'.format(student, school))
            continue
        last_attended_date = last_attended_date[0].date

        first_absent_date = attendances.order_by('date').filter(
            attended=False,
            validation_date__ne=None,
            date__lt=to_date,
            date__gte=last_attended_date,
        )
        if not first_absent_date:
            logger.info('Student {} was not absent in school {}'.format(student, school))
            continue
        first_absent_date = first_absent_date[0].date
        last_absent_date = first_absent_date[-1].date

        total_school_days_absent = attendances.filter(
            attended=False,
            validation_date__ne=None,
            date__gte=first_absent_date,
            date__lte=to_date
        ).count()

        if total_school_days_absent <= absent_threshold:
            logger.info('Student {} only {} days absent'.format(
                student, total_school_days_absent
            ))
            continue

        if last_attended_date >= late_threshold_date:

            absent_record, new = Absentee.objects.get_or_create(
                school_id=school,
                student_id=student,
                last_attendance_date=first_absent_date
            )
            absent_record.last_absent_date = last_absent_date
            absent_record.absent_days = total_school_days_absent
            absent_record.reattend_date = last_attended_date
            absent_record.save()
            logger.info('student {} reattended on {}'.format(student, last_attended_date))

        else:

            absent_record, new = Absentee.objects.get_or_create(
                school_id=school,
                student_id=student,
                last_attendance_date=last_attended_date,
                reattend_date__isnull=True
            )
            absent_record.last_absent_date = last_absent_date
            absent_record.absent_days = total_school_days_absent
            absent_record.save()

        if new:
            logger.info('New absent record for student {}'.format(student))
