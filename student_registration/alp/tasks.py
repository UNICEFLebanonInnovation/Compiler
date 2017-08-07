__author__ = 'achamseddine'

import json
import os
from django.db.models import Q
from datetime import datetime
from student_registration.taskapp.celery import app


@app.task
def auto_assign_to_alp_level():
    from student_registration.alp.utils import assign_to_level
    from student_registration.alp.models import Outreach, ALPRound
    alp_round = ALPRound.objects.get(current_pre_test=True)

    registrations = Outreach.objects.filter(alp_round=alp_round, level__isnull=False)

    print registrations.count()

    for registry in registrations:
        try:
            registry.assigned_to_level = assign_to_level(registry.level, registry.exam_total)
            registry.save()
        except Exception as ex:
            print ex.message
            continue


@app.task
def assign_alp_level():
    from student_registration.alp.models import Outreach, ALPRound
    alp_round = ALPRound.objects.get(current_pre_test=True)

    records = Outreach.objects.filter(alp_round=alp_round, level__isnull=False)
    print records.count()

    for record in records:
        try:
            level = record.level
            to_level = 0
            if not level:
                continue

            total = record.exam_total

            if level.id == 1 or level.id == 2 or level.id == 3:
                if total <= 5:
                    to_level = 10
                elif 5 < total <= 15:
                    to_level = 11
                elif 15 < total <= 30:
                    to_level = 12
                elif 30 < total <= 60:
                    to_level = 2
                elif 60 < total <= 90:
                    to_level = 3

            if level.id == 4 or level.id == 5 or level == 6:
                if total <= 30:
                    to_level = 10
                elif 30 < total <= 35:
                    to_level = 10
                elif 35 < total <= 45:
                    to_level = 11
                elif 45 < total <= 60:
                    to_level = 12
                elif 60 < total <= 90:
                    to_level = 2
                elif 90 < total <= 120:
                    to_level = 3
                elif 120 < total <= 150:
                    to_level = 4
                elif 150 < total <= 180:
                    to_level = 5
                elif 180 < total <= 210:
                    to_level = 6

            if level.id == 7 or level.id == 8 or level.id == 9:
                if total <= 30:
                    to_level = 10
                elif 30 < total <= 35:
                    to_level = 10
                elif 35 < total <= 45:
                    to_level = 11
                elif 45 < total <= 60:
                    to_level = 12
                elif 60 < total <= 90:
                    to_level = 2
                elif 90 < total <= 120:
                    to_level = 3
                elif 120 < total <= 150:
                    to_level = 4
                elif 150 < total <= 180:
                    to_level = 5
                elif 180 < total <= 210:
                    to_level = 6
                elif 210 < total <= 240:
                    to_level = 7
                elif 240 < total <= 270:
                    to_level = 8
                elif 270 < total <= 300:
                    to_level = 9

            if to_level:
                print level.id, total, to_level
                record.assigned_to_level_id = to_level
                record.save()
        except Exception as ex:
            print ex.message
            continue


@app.task
def auto_refer_to_alp_level():
    from student_registration.alp.utils import refer_to_level
    from student_registration.alp.models import Outreach, ALPRound
    alp_round = ALPRound.objects.get(current_post_test=True)

    records = Outreach.objects.filter(alp_round=alp_round)

    for record in records:
        try:
            record.refer_to_level = refer_to_level(
                record.student.age,
                record.registered_in_level,
                record.post_exam_total
            )
            record.save()
        except Exception as ex:
            print ex.message
            continue


@app.task
def assign_section(section):
    from student_registration.alp.models import Outreach, ALPRound
    from student_registration.schools.models import Section
    alp_round = ALPRound.objects.get(current_round=True)

    registrations = Outreach.objects.filter(
        registered_in_level__isnull=False,
        section__isnull=True,
        alp_round=alp_round
    )
    section = Section.objects.get(id=section)

    print len(registrations), " ALP registrations found"
    print "Start assignment"

    for registry in registrations:
        registry.section = section
        registry.save()

    print "End assignment"


@app.task
def assign_round(round_id):
    from student_registration.alp.models import Outreach

    registrations = Outreach.objects.filter(alp_round__isnull=True).update(alp_round_id=round_id)
    print registrations

    print "End assignment"


@app.task
def assign_round_to_deleted(round_id):
    from student_registration.alp.models import Outreach

    registrations = Outreach.objects.filter(alp_round__isnull=True, id__lt=13724).update(alp_round_id=round_id)
    print registrations

    print "End assignment"


@app.task
def fix_round_assignment(update):
    from student_registration.alp.models import Outreach

    registrations = Outreach.objects.filter(
        owner__username__contains='caritas',
        alp_round__id__exact=3,
        level__isnull=True,
        assigned_to_level__isnull=True,
        registered_in_level__isnull=True,
        id__gt=14163
    )

    print len(registrations), " records to assign"

    if update == 1:
        total = registrations.update(alp_round_id=4)
        print total, " records assigned"

    print "End assignment"


@app.task
def move_student_to_school(school_from, school_to):
    from .models import Outreach

    if not school_from or not school_to:
        return False
    print "from school: ", school_from, " to school: ", school_to
    registrations = Outreach.objects.filter(school_id=school_from)
    print registrations.count()
    registrations.update(school_id=school_to)


@app.task
def matching_pretest_2ndshift_enrollments():
    import tablib
    from import_export.formats import base_formats
    from .models import Outreach, ALPRound
    from student_registration.enrollments.models import Enrollment, EducationYear

    alp_round = ALPRound.objects.get(current_pre_test=True)
    registrations = Outreach.objects.filter(alp_round=alp_round)

    print registrations.count()

    content = []
    data = tablib.Dataset()
    data.headers = [
        'CERD (pre-test)',
        'School name ( pre-test)',
        'Student (pre-test)',
        'Student mother fullname (pre-test)',
        'CERD (enrollment)',
        'School (enrollment)',
        'Student (enrollment)',
        'Student mother fullname (enrollment)',
        'Level',
    ]

    queryset = Enrollment.objects.all()

    for registry in registrations:
        enrollment = None
        r_student = registry.student
        if not r_student or not registry.school:
            continue
        try:
            if r_student.id_type_id == 1 and r_student.id_number or '-' in r_student.id_number:
                id_number_1 = r_student.id_number.replace("-", "")
                id_number_2 = id_number_1.replace("C", "c")
                id_number_3 = id_number_1.replace("c", "C")
                id_number_4 = r_student.id_number.replace("C", "c")
                id_number_5 = r_student.id_number.replace("c", "C")
                enrollment = queryset.filter(
                    Q(student__id_number=r_student.id_number) |
                    Q(student__id_number=id_number_1) |
                    Q(student__id_number=id_number_2) |
                    Q(student__id_number=id_number_3) |
                    Q(student__id_number=id_number_4) |
                    Q(student__id_number=id_number_5) |
                    Q(Q(student__first_name=r_student.first_name) &
                      Q(student__father_name=r_student.father_name) &
                      Q(student__last_name=r_student.last_name) &
                      Q(student__mother_fullname=r_student.mother_fullname)
                      )
                )
            else:
                enrollment = queryset.filter(
                    student__first_name=r_student.first_name,
                    student__father_name=r_student.father_name,
                    student__last_name=r_student.last_name,
                    student__mother_fullname=r_student.mother_fullname
                )
        except Exception as ex:
            print registry.id, ex.message
            continue

        if enrollment and not enrollment.count() > 2:
            for row in enrollment:
                data.append([
                    registry.school.number,
                    registry.school,
                    registry.student,
                    registry.student.mother_fullname,
                    row.school.number,
                    row.school,
                    row.student,
                    row.student.mother_fullname,
                    row.classroom
                ])

    file_format = base_formats.XLSX()
    file_object = open("pre_test_matching_enrollment.xlsx", "w")
    file_object.write(file_format.export_data(data))
    file_object.close()


@app.task
def matching_pretest_alp_rounds():
    import tablib
    from import_export.formats import base_formats
    from .models import Outreach, ALPRound

    alp_round = ALPRound.objects.get(current_pre_test=True)
    registrations = Outreach.objects.filter(alp_round=alp_round)

    print registrations.count()

    content = []
    data = tablib.Dataset()
    data.headers = [
        'CERD (pre-test)',
        'School name ( pre-test)',
        'Student (pre-test)',
        'Student mother fullname (pre-test)',
        'CERD (enrollment)',
        'School (enrollment)',
        'Student (enrollment)',
        'Student mother fullname (enrollment)',
        'Level',
    ]

    queryset = Outreach.objects.filter(registered_in_level__isnull=False, alp_round_id__lt=alp_round.id)

    for registry in registrations:
        enrollment = None
        r_student = registry.student
        if not r_student or not registry.school:
            continue
        try:
            # if r_student.id_type_id == 1 and r_student.id_number or '-' in r_student.id_number:
            if not r_student.id_type_id == 6:
                id_number_1 = r_student.id_number.replace("-", "")
                id_number_2 = id_number_1.replace("C", "c")
                id_number_3 = id_number_1.replace("c", "C")
                id_number_4 = r_student.id_number.replace("C", "c")
                id_number_5 = r_student.id_number.replace("c", "C")
                enrollment = queryset.filter(
                    Q(student__id_number=r_student.id_number) |
                    Q(student__id_number=id_number_1) |
                    Q(student__id_number=id_number_2) |
                    Q(student__id_number=id_number_3) |
                    Q(student__id_number=id_number_4) |
                    Q(student__id_number=id_number_5) |
                    Q(Q(student__first_name=r_student.first_name) &
                      Q(student__father_name=r_student.father_name) &
                      Q(student__last_name=r_student.last_name) &
                      Q(student__mother_fullname=r_student.mother_fullname)
                      )
                )
            else:
                enrollment = queryset.filter(
                    student__first_name=r_student.first_name,
                    student__father_name=r_student.father_name,
                    student__last_name=r_student.last_name,
                    student__mother_fullname=r_student.mother_fullname
                )
        except Exception as ex:
            print registry.id, ex.message
            continue

        if enrollment and not enrollment.count() > 2:
            for row in enrollment:
                data.append([
                    registry.school.number,
                    registry.school,
                    registry.student,
                    registry.student.mother_fullname,
                    row.school.number,
                    row.school,
                    row.student,
                    row.student.mother_fullname,
                    row.registered_in_level
                ])

    file_format = base_formats.XLSX()
    file_object = open("pre_test_matching_rounds.xlsx", "w")
    file_object.write(file_format.export_data(data))
    file_object.close()




