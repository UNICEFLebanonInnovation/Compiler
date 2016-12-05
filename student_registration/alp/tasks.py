__author__ = 'achamseddine'

import json
import os

from datetime import datetime
from student_registration.taskapp.celery import app


@app.task
def assign_alp_level():
    from student_registration.alp.models import Outreach
    from student_registration.schools.models import EducationLevel

    records = Outreach.objects.all()
    for record in records:
        try:
            level = record.level
            to_level = 0
            if not level:
                continue
            if level.id == 1 or level.id == 2 or level.id == 3:
                total = record.exam_total
                if total <= 40:
                    to_level = 1
                elif total > 40 and total <= 80:
                    to_level = 2
                elif total > 80 and total <= 120:
                    to_level = 3

            if level.id == 4 or level.id == 5 or level == 6:
                total = record.exam_total
                if total <= 20:
                    to_level = 1
                elif total > 20 and total <= 40:
                    to_level = 2
                elif total > 40 and total <= 60:
                    to_level = 3
                elif total > 60 and total <= 100:
                    to_level = 4
                elif total > 100 and total <= 140:
                    to_level = 5
                elif total > 140 and total <= 180:
                    to_level = 6

            if level.id == 7 or level.id == 8 or level.id == 9:
                total = record.exam_total
                if total <= 20:
                    to_level = 1
                elif total > 20 and total <= 40:
                    to_level = 2
                elif total > 40 and total <= 60:
                    to_level = 3
                elif total > 60 and total <= 80:
                    to_level = 4
                elif total > 80 and total <= 100:
                    to_level = 5
                elif total > 100 and total <= 120:
                    to_level = 6
                elif total > 120 and total <= 160:
                    to_level = 7
                elif total > 160 and total <= 200:
                    to_level = 8
                elif total > 200 and total <= 240:
                    to_level = 9

            if to_level:
                print level.id, total, to_level
                record.assigned_to_level = EducationLevel.objects.get(id=to_level)
                record.save()
        except Exception as ex:
            print ex.message
            continue


@app.task
def generate_alp_report(school=0, location=0, email=None, user=None):
    from student_registration.alp.models import Outreach
    queryset = []

    if user and has_group(user, 'PARTNER'):
        queryset = Outreach.objects.filter(owner=user)
    if user and has_group(user, 'ALP_SCHOOL') and user.school_id:
        school = user.school_id
    if school:
        queryset = Outreach.objects.filter(school_id=school).order_by('id')
    if location:
        queryset = Outreach.objects.filter(school__location_id=location).order_by('id')

    data = tablib.Dataset()

    data.headers = [
        _('ALP result'),
        _('ALP round'),
        _('ALP level'),
        _('Is the child participated in an ALP program'),

        _('Education year'),
        _('Last education level'),

        _('Phone prefix'),
        _('Phone number'),
        _('Student living address'),

        _('Student ID Number'),
        _('Student ID Type'),
        _('Registered in UNHCR'),

        _('Mother nationality'),
        _('Mother fullname'),

        _('Current Section'),
        _('Current Level'),

        _('Science corrector'),
        _('Math corrector'),
        _('Foreign language corrector'),
        _('Arabic language corrector'),

        _('Assigned to level'),
        _('Total'),
        _('Science'),
        _('Math'),
        _('Foreign language'),
        _('Arabic language'),
        _('Registered in level'),

        _('Student nationality'),
        _('Student age'),
        _('Student birthday'),
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

            line.last_education_year,
            line.last_education_level.name if line.last_education_level else '',

            line.student.phone_prefix,
            line.student.phone,
            line.student.address,

            line.student.id_number,
            line.student.id_type.name if line.student.id_type else '',
            _(line.registered_in_unhcr) if line.registered_in_unhcr else '',

            line.student.mother_nationality.name if line.student.mother_nationality else '',
            line.student.mother_fullname,

            line.section.name if line.section else '',
            line.registered_in_level.name if line.registered_in_level else '',

            line.exam_corrector_science,
            line.exam_corrector_math,
            line.exam_corrector_language,
            line.exam_corrector_arabic,

            line.assigned_to_level.name if line.assigned_to_level else '',
            line.exam_total,
            line.exam_result_science,
            line.exam_result_math,
            line.exam_result_language,
            line.exam_result_arabic,
            line.level.name if line.level else '',

            line.student.nationality_name(),
            line.student.birthday,
            line.student.calc_age,
            _(line.student.sex),
            line.student.__unicode__(),

            line.school.name,
            line.school.number,
            line.school.location.name,
            line.school.location.parent.name,
        ]
        data.append(content)

    return data
