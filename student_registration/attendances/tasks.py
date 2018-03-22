# -*- coding: utf-8 -*-
__author__ = 'jcranwellward'

from datetime import date
from student_registration.taskapp.celery import app


@app.task
def find_attendances_gap(days):
    import datetime
    import tablib
    from import_export.formats import base_formats
    from student_registration.schools.models import School
    from student_registration.attendances.models import BySchoolByDay

    base = date(2016, 10, 1)
    dates = []
    weekend = [5, 6]
    for x in range(0, days):
        d = base + datetime.timedelta(days=x)
        if d.weekday() not in weekend:
            dates.append(d)

    schools = School.objects.filter(ndshift_school__isnull=False).distinct()

    content = []
    data = tablib.Dataset()
    data.headers = [
        'CERD',
        'School name',
        'District',
        'Governorate',
        'date',
    ]

    for d in dates:
        for school in schools:
            # print d, school
            try:
                attendance = BySchoolByDay.objects.get(school_id=school.id, attendance_date=d)
            except BySchoolByDay.DoesNotExist:
                content = [
                    school.number,
                    school.name,
                    school.location,
                    school.location.parent,
                    d
                ]
                data.append(content)

    file_format = base_formats.XLSX()
    file_object = open("attendances_gap.xlsx", "w")
    file_object.write(file_format.export_data(data))
    file_object.close()


@app.task
def find_attendances_gap_grouped(days):
    import datetime
    import tablib
    from import_export.formats import base_formats
    from student_registration.schools.models import School
    from student_registration.attendances.models import BySchoolByDay

    base = date(2016, 10, 1)
    dates = []
    weekend = [5, 6]
    for x in range(0, days):
        d = base + datetime.timedelta(days=x)
        if d.weekday() not in weekend:
            dates.append(d)

    schools = School.objects.filter(ndshift_school__isnull=False).distinct()

    content = []
    data = tablib.Dataset()
    data.headers = [
        'CERD',
        'School name',
        'District',
        'Governorate',
        'total'
    ]

    for school in schools:
        ctr = 0
        for d in dates:
            try:
                attendance = BySchoolByDay.objects.get(school_id=school.id, attendance_date=d)
            except BySchoolByDay.DoesNotExist:
                ctr += 1

        data.append([
                        school.number,
                        school.name,
                        school.location,
                        school.location.parent,
                        ctr
                    ])

    file_format = base_formats.XLSX()
    file_object = open("attendances_gap_grouped_by_school.xlsx", "w")
    file_object.write(file_format.export_data(data))
    file_object.close()


@app.task
def calculate_last_attendance_date():
    from .models import Absentee

    queryset = Absentee.objects.all()

    for line in queryset:
        registry = line.student.current_secondshift_registration()
        if not registry:
            continue
        registry.update(last_attendance_date=line.last_attendance_date,
                        last_absent_date=line.last_absent_date)


@app.task
def dropout_students(from_date, to_date):
    from .models import Absentee

    queryset = Absentee.objects.exclude(absent_days__lt=10)

    to_disable = queryset.filter(absent_days__gte=10, absent_days__lt=15)
    # to_dropout = queryset.filter(absent_days__gte=15)

    for line in to_disable:
        registry = line.student.current_secondshift_registration()
        if not registry:
            continue
        registry.update(disabled=True,
                        last_attendance_date=line.last_attendance_date,
                        last_absent_date=line.last_absent_date)
    #
    # for line in to_dropout:
    #     registry = line.student.last_enrollment()
    #     if not registry:
    #         continue
    #     registry.update(dropout_status=True,
    #                     last_attendance_date=line.last_attendance_date,
    #                     last_absent_date=line.last_absent_date)


@app.task
def calculate_attendances_by_student(from_date=None, to_date=None):
    from .utils import calculate_absentees
    from .models import Attendance, Absentee

    queryset = Attendance.objects.exclude(close_reason__isnull=False)\
        .exclude(students__isnull=True).order_by('attendance_date')
    # queryset = queryset.filter(school__number='340')

    if not from_date:
        Absentee.objects.all().delete()

    if from_date:
        queryset = queryset.filter(attendance_date__gte=from_date)
    if to_date:
        queryset = queryset.filter(attendance_date__lte=to_date)

    for line in queryset:
        if not line.students:
            continue
        for level_section in line.students:
            attendances = line.students[level_section]
            students = attendances['students']
            calculate_absentees(attendance=line, students=students)


@app.task
def split_attendance(school_type='2nd-shift'):
    from .models import Attendance
    from student_registration.alp.models import ALPRound
    from student_registration.schools.models import EducationYear

    queryset = Attendance.objects.all()
    if school_type == 'ALP':
        queryset = Attendance.objects.filter(school__is_alp=True)
        alp_round = ALPRound.objects.get(current_round=True)
        queryset.update(alp_round=alp_round)
    else:
        education_year = EducationYear.objects.get(current_year=True)
        queryset.update(education_year=education_year)

    queryset.update(school_type=school_type)
