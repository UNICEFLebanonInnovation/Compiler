__author__ = 'achamseddine'

import json
import os
import tablib
from datetime import datetime
from django.db.models import Q
from django.utils.translation import ugettext as _
from import_export.formats import base_formats
from student_registration.taskapp.celery import app


@app.task
def assign_section(section):
    from student_registration.enrollments.models import Enrollment
    from student_registration.schools.models import Section
    registrations = Enrollment.objects.exclude(deleted=True).filter(section__isnull=True)
    section = Section.objects.get(id=section)

    print len(registrations), " registration found"
    print "Start assignment"

    for registry in registrations:
        registry.section = section
        registry.save()

    print "End assignment"


@app.task
def generate_2ndshift_report(school=0, location=0, email=None, user=None):
    from student_registration.enrollments.models import Enrollment

    offset = 120000
    limit = 180000
    queryset = Enrollment.objects.exclude(deleted=True)[offset:limit]

    data = tablib.Dataset()
    data.headers = [
        _('ALP result'),
        _('ALP round'),
        _('ALP level'),
        _('Is the child participated in an ALP/2016-2 program'),
        _('Result'),
        _('Education year'),
        _('School'),
        _('Last education level'),
        _('Current Section'),
        _('Current Class'),
        _('Phone prefix'),
        _('Phone number'),
        _('Student living address'),
        _('Student ID Number'),
        _('Student ID Type'),
        _('Registered in UNHCR'),
        _('Mother nationality'),
        _('Mother fullname'),
        _('Student nationality'),
        _('Student age'),
        _('Student birthday'),
        _('year'),
        _('month'),
        _('day'),
        _('Sex'),
        _('Student fullname'),
        _('School'),
        _('School number'),
        _('District'),
        _('Governorate')
    ]

    content = []
    for line in queryset:
        if not line.student or not line.school:
            continue
        content = [
            line.last_informal_edu_final_result.name if line.last_informal_edu_final_result else '',
            line.last_informal_edu_round.name if line.last_informal_edu_round else '',
            line.last_informal_edu_level.name if line.last_informal_edu_level else '',
            _(line.participated_in_alp) if line.participated_in_alp else '',

            _(line.last_year_result) if line.last_year_result else '',
            line.last_education_year if line.last_education_year else '',
            _(line.last_school_type) if line.last_school_type else '',
            line.last_education_level.name if line.last_education_level else '',

            line.section.name if line.section else '',
            line.classroom.name if line.classroom else '',

            line.student.phone_prefix,
            line.student.phone,
            line.student.address,

            line.student.id_number,
            line.student.id_type.name if line.student.id_type else '',
            line.registered_in_unhcr,

            line.student.mother_nationality.name if line.student.mother_nationality else '',
            line.student.mother_fullname,
            line.student.nationality_name(),

            line.student.calc_age,
            line.student.birthday,
            line.student.birthday_year,
            line.student.birthday_month,
            line.student.birthday_day,
            _(line.student.sex) if line.student.sex else '',
            line.student.__unicode__(),

            line.school.name,
            line.school.number,
            line.school.location.name,
            line.school.location.parent.name,
        ]
        data.append(content)

    file_format = base_formats.XLS()
    file_object = open("enrolment_data_120000_180000.xls", "w")
    file_object.write(file_format.export_data(data))
    file_object.close()
