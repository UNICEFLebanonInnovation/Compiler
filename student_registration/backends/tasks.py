__author__ = 'achamseddine'

import json
import os
import tablib
from datetime import datetime
from django.db.models import Q
from django.utils.translation import ugettext as _
from import_export.formats import base_formats
from student_registration.taskapp.celery import app
from .file import store_file


@app.task
def export_2ndshift(params=None):
    from student_registration.enrollments.models import Enrollment
    from student_registration.schools.models import EducationYear
    current = EducationYear.objects.get(current_year=True)

    queryset = Enrollment.objects.all()
    if 'current' in params:
        queryset = queryset.filter(education_year=current)

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
        _('Education year'),

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

        _('Registration date'),
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
            line.education_year.name if line.education_year else '',

            line.student.phone_prefix,
            line.student.phone,
            line.student.address,

            line.student.id_number,
            line.student.id_type.name if line.student.id_type else '',
            line.registered_in_unhcr,

            line.student.mother_nationality.name if line.student.mother_nationality else '',
            line.student.mother_fullname,
            line.student.nationality_name(),

            line.student.age,
            line.student.birthday,
            line.student.birthday_year,
            line.student.birthday_month,
            line.student.birthday_day,
            _(line.student.sex) if line.student.sex else '',
            line.student.__unicode__(),

            line.registration_date,
            line.school.name,
            line.school.number,
            line.school.location.name,
            line.school.location.parent.name,
        ]
        data.append(content)

    file_format = base_formats.XLSX()
    content = file_format.export_data(data)
    store_file(content, '2ndshift_extraction.xlsx')


@app.task
def export_2ndshift_gradings(params=None):
    from student_registration.enrollments.models import EnrollmentGrading
    from student_registration.schools.models import EducationYear
    current = EducationYear.objects.get(current_year=True)

    queryset = EnrollmentGrading.objects.filter(enrollment__education_year=current)

    data = tablib.Dataset()
    data.headers = [
        _('Student status'),
        _('Final Grade'),
        _('Term'),

        _('Linguistic field/Arabic'),
        _('Sociology field'),
        _('Physical field'),
        _('Artistic field'),
        _('Linguistic field/Foreign language'),
        _('Scientific domain/Mathematics'),
        _('Scientific domain/Sciences'),

        _('Biology'),
        _('Chemistry'),
        _('Physic'),
        _('Science'),
        _('Math'),
        _('History'),
        _('Geography'),
        _('Education'),
        _('Foreign language'),
        _('Arabic'),

        _('Current Section'),
        _('Current Class'),

        _('Mother fullname'),
        _('Student nationality'),
        _('Sex'),
        _('Student fullname'),

        _('Registration date'),
        _('School'),
        _('School number'),
        _('District'),
        _('Governorate'),
    ]

    content = []
    for line in queryset:
        enrollment = line.enrollment
        if not enrollment.student or not enrollment.school:
            continue
        content = [

            line.exam_result,
            line.exam_total,
            line.exam_term,

            line.exam_result_linguistic_ar,
            line.exam_result_sociology,
            line.exam_result_physical,
            line.exam_result_artistic,
            line.exam_result_linguistic_en,
            line.exam_result_mathematics,
            line.exam_result_sciences,

            line.exam_result_bio,
            line.exam_result_chemistry,
            line.exam_result_physic,
            line.exam_result_science,
            line.exam_result_math,
            line.exam_result_history,
            line.exam_result_geo,
            line.exam_result_education,
            line.exam_result_language,
            line.exam_result_arabic,

            enrollment.section.name if enrollment.section else '',
            enrollment.classroom.name if enrollment.classroom else '',

            enrollment.student.mother_fullname,
            enrollment.student.nationality_name(),

            _(enrollment.student.sex) if enrollment.student.sex else '',
            enrollment.student.__unicode__(),

            enrollment.registration_date,
            enrollment.school.name,
            enrollment.school.number,
            enrollment.school.location.name,
            enrollment.school.location.parent.name,
        ]
        data.append(content)

    file_format = base_formats.XLSX()
    content = file_format.export_data(data)
    store_file(content, '2ndshift_gradings_extraction.xlsx')


@app.task
def export_alp(params=None):
    from student_registration.alp.models import Outreach, ALPRound

    queryset = Outreach.objects.all()

    if 'pre_test' in params:
        alp_round = ALPRound.objects.get(current_pre_test=True)
        queryset = queryset.filter(
            alp_round__current_pre_test=True,
            level__isnull=False,
            assigned_to_level__isnull=False
        )
    if 'post_test' in params:
        alp_round = ALPRound.objects.get(current_post_test=True)
        queryset = queryset.filter(
            alp_round__current_post_test=True,
            registered_in_level__isnull=False,
            refer_to_level__isnull=False
        )
    if 'current' in params:
        alp_round = ALPRound.objects.get(current_round=True)
        queryset = queryset.filter(
            alp_round__current_round=True,
            registered_in_level__isnull=False,
        )

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

        _('Post-test result'),
        _('Assigned to level'),
        _('Pre-test result'),

        _('Student nationality'),
        _('Student age'),
        _('Student birthday'),
        _('Sex'),
        _('Student fullname'),

        _('School'),
        _('School number'),
        _('District'),
        _('Governorate'),
    ]

    # 'id',
    # 'student__id',
    # 'student__id_type',
    # 'student__id_number',
    # 'student__number',
    # 'student__first_name',
    # 'student__father_name',
    # 'student__last_name',
    # 'student__mother_fullname',
    # 'student__birthday_year',
    # 'student__birthday_month',
    # 'student__birthday_day',
    # 'student_age',
    # 'student__sex',
    # 'student__nationality__name',
    # 'student__phone_prefix',
    # 'student__phone',
    # 'student__address',
    # 'governorate',
    # 'district',
    # 'school__number',
    # 'school__name',
    # 'level__name',
    # 'exam_result_arabic',
    # 'exam_language',
    # 'exam_result_language',
    # 'exam_result_math',
    # 'exam_result_science',
    # 'exam_total',
    # 'passed_pre',
    # 'assigned_to_level__name',
    # 'registered_in_level__name',
    # 'section__name',
    # 'post_exam_result_arabic',
    # 'post_exam_language',
    # 'post_exam_result_language',
    # 'post_exam_result_math',
    # 'post_exam_result_science',
    # 'post_exam_total',
    # 'referred_to',
    # 're_enrolled',
    # 'passed_post',
    # 'owner__username',
    # 'modified_by__username',
    # 'created',
    # 'modified',

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

            line.post_exam_total,
            line.assigned_to_level.name if line.assigned_to_level else '',
            line.exam_total,

            line.student.nationality_name(),
            line.student.age,
            line.student.birthday,
            _(line.student.sex),
            line.student.__unicode__(),

            line.school.name,
            line.school.number,
            line.school.location.name,
            line.school.location.parent.name,
        ]
        data.append(content)

    file_format = base_formats.XLS()
    content = file_format.export_data(data)
    store_file(content, 'alp_extraction.xlsx')
