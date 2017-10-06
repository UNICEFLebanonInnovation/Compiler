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
    registrations = Enrollment.objects.filter(section__isnull=True)
    section = Section.objects.get(id=section)

    print(len(registrations), " registration found")
    print("Start assignment")

    for registry in registrations:
        registry.section = section
        registry.save()

    print("End assignment")


@app.task
def assign_education_year(year):
    from student_registration.enrollments.models import Enrollment, LoggingStudentMove
    registrations = Enrollment.objects.filter(education_year__isnull=True)
    logging = LoggingStudentMove.objects.filter(education_year__isnull=True)

    print(registrations.count(), " registrations found")
    print(logging.count(), " logging found")
    print("Start assignment")
    registrations.update(education_year_id=year)
    logging.update(education_year_id=year)
    print("End assignment")


@app.task
def generate_2ndshift_report(school=0, location=0, email=None, user=None):
    from student_registration.enrollments.models import Enrollment

    offset = 120000
    limit = 180000
    # queryset = Enrollment.objects.all()[offset:limit]
    queryset = Enrollment.objects.all()

    data = tablib.Dataset()
    data.headers = [

        _('Student status'),
        _('Final Grade'),

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

            line.exam_result,
            line.exam_total,

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

            line.student.age,
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

    file_format = base_formats.XLSX()
    file_object = open("enrolment_data.xlsx", "w")
    file_object.write(file_format.export_data(data))
    file_object.close()


@app.task
def track_student_moves():

    from student_registration.enrollments.models import Enrollment
    from student_registration.enrollments.models import StudentMove

    registrations = Enrollment.objects.order_by('created')

    for registry in registrations:
        student = registry.student
        match_records = Enrollment.objects.exclude(school_id=registry.school_id).filter(
            Q(student__number=student.number) |
            Q(student__number_part1=student.number_part1)
              # Q(student__number_part2=student.number_part2)
        )

        if not match_records:
            match_records = Enrollment.objects.exclude(school_id=registry.school_id).filter(
                student__first_name=student.first_name,
                student__father_name=student.father_name,
                student__last_name=student.last_name,
            )

        # match_records = Enrollment.objects.exclude(school_id=registry.school_id).exclude(deleted=True).filter(
        #     created__gt=registry.created,
        #     student__number=student.number
        # )

        if len(match_records):
            print(match_records)
            for item in match_records:
                StudentMove.objects.get_or_create(enrolment1=registry, enrolment2=item, school1=registry.school, school2=item.school)


@app.task
def migrate_gradings():
    from .models import Enrollment, EnrollmentGrading

    registrations = Enrollment.objects.all()

    for registry in registrations:
        instance = EnrollmentGrading.objects.create(
            enrollment=registry,
            exam_term=3,
            exam_result_arabic=registry.exam_result_arabic,
            exam_result_language=registry.exam_result_language,
            exam_result_education=registry.exam_result_education,
            exam_result_geo=registry.exam_result_geo,
            exam_result_history=registry.exam_result_history,
            exam_result_math=registry.exam_result_math,
            exam_result_science=registry.exam_result_science,
            exam_result_physic=registry.exam_result_physic,
            exam_result_chemistry=registry.exam_result_chemistry,
            exam_result_bio=registry.exam_result_bio,
            exam_result_linguistic_ar=registry.exam_result_linguistic_ar,
            exam_result_sociology=registry.exam_result_sociology,
            exam_result_physical=registry.exam_result_physical,
            exam_result_artistic=registry.exam_result_artistic,
            exam_result_linguistic_en=registry.exam_result_linguistic_en,
            exam_result_mathematics=registry.exam_result_mathematics,
            exam_result_sciences=registry.exam_result_sciences,
            exam_total=registry.exam_total,
            exam_result=registry.exam_result,
        )
        instance.save()
