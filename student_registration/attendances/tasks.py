# -*- coding: utf-8 -*-
__author__ = 'jcranwellward'

from datetime import date
from student_registration.taskapp.celery import app
import requests as req


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
    from student_registration.schools.models import EducationYear

    current_year = EducationYear.objects.get(current_year=True)
    queryset = Absentee.objects.filter(education_year_id=current_year)
    #queryset = Absentee.objects.filter(school_id=123)

    for line in queryset:
        registry = line.student.current_secondshift_registration()
        if not registry:
            continue
        registry.update(last_attendance_date=line.last_attendance_date,
                        last_absent_date=line.last_absent_date)


def geo_calculate_last_attendance_date(from_school, to_school):
    from .models import Absentee
    from student_registration.schools.models import EducationYear

    #current_year = EducationYear.objects.get(current_year=True)
    queryset = Absentee.objects.all().order_by('school__number')#education_year_id=current_year
    queryset = queryset.filter(school__number__gte=from_school, school__number__lte=to_school)

    for line in queryset:
        registry = line.student.current_secondshift_registration()
        if not registry:
            continue
        registry.update(last_attendance_date=line.last_attendance_date,
                        last_absent_date=line.last_absent_date)


@app.task
def dropout_students():
    from .models import Absentee

    queryset = Absentee.objects.exclude(absent_days__lt=10)

    to_disable = queryset.filter(absent_days__gte=10, absent_days__lt=15)
    # to_dropout = queryset.filter(absent_days__gte=15)

    for line in to_disable:
        registry = line.student.current_secondshift_registration()
        if not registry:
            continue
        registry.update(disabled=True)
    #
    # for line in to_dropout:
    #     registry = line.student.last_enrollment()
    #     if not registry:
    #         continue
    #     registry.update(dropout_status=True,
    #                     last_attendance_date=line.last_attendance_date,
    #                     last_absent_date=line.last_absent_date)


@app.task
def reset_absentees():
    from .models import Absentee
    Absentee.objects.all().delete()


@app.task
def calculate_attendances_by_student(from_date=None, to_date=None):
    from .utils import calculate_absentees
    from .models import Attendance

    queryset = Attendance.objects.exclude(close_reason__isnull=False)\
        .exclude(students__isnull=True).order_by('attendance_date')
    #queryset = queryset.filter(school__id='123')

    # if not from_date:
    # Absentee.objects.all().delete()

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


def geo_calculate_attendances_per_day(from_school, to_school, from_date, to_date, txt_std):
    from .models import Attendance, Student
    from .utils import add_attendance

    queryset = Attendance.objects.exclude(close_reason__isnull=False).exclude(students__isnull=True)
    queryset = queryset.filter(attendance_date__gte=from_date, attendance_date__lte=to_date,
                               school__number__gte=from_school, school__number__lte=to_school).\
        order_by('attendance_date', 'school__number')
    std_id = list()
    if txt_std:
        std = Student.objects.filter(number=txt_std)
        for st in std:
            std_id.append(st.id)
    for line in queryset:
        if not line.students:
            continue
        for level_section in line.students:
            attendances = line.students[level_section]
            students = attendances['students']
            if std_id:
                for student_in in students:
                    for st in std_id:
                        if str(st) == str(student_in['student_id']):
                            add_attendance(attendance=line, students=students, std_id=str(st))
            else:
                add_attendance(attendance=line, students=students, std_id=txt_std)


def geo_calculate_attendances_per_day_2(from_date, to_date):
    from django.db import connection

    cursor = connection.cursor()

    cursor.execute(
        "SELECT att.id, att.school_id, "  # 0, 1
        "att.classroom_id, att.classlevel_id, "  # 2, 3
        "att.section_id, att.status, "  # 4, 5
        "att.attendance_date, "  # 6
        # "att.validation_status, att.validation_date, "  # 7, 8
        # "att.absence_reason, att.close_reason, "  # 9, 10
        "att.students "  # 7
        # "att.school_type, att.education_year_id "  # 12, 13  
        "FROM attendances_attendance att LEFT OUTER JOIN schools_school scl "
        "ON (att.school_id = scl.id) "
        "WHERE att.close_reason IS NULL "
        "AND att.education_year_id = 3 "
        # "AND att.attendance_date >= '2019-01-01' "
        # "AND att.attendance_date <= '2019-02-01' "
        "ORDER BY att.attendance_date ASC, scl.number ASC "
        "LIMIT 10000")

    rows = cursor.fetchall()
    for attendance in rows:
        for level_section, attendances in attendance[7].items():

            if 'students' not in attendances:
                continue

            students = attendances['students']
            for student in students:
                try:
                    cursor.execute("INSERT INTO public.attendances_attendancedt("
                                   "is_present, attendance_date, levelname, attendance_id, classlevel_id, "
                                   "classroom_id, school_id, section_id, student_id)"
                                   "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)", [student['status'], attendance[6],
                                                                                   student['level_name'], attendance[0],
                                                                                   student['level'], attendance[2],
                                                                                   attendance[1], student['section'],
                                                                                   student['student_id']])
                except Exception:
                    continue


def geo_calculate_attendances_by_student(from_school, to_school, from_date, to_date):
    from .utils import calculate_absentees
    from .models import Attendance
    from student_registration.schools.models import EducationYear

   # current_year = EducationYear.objects.get(current_year=True)
    queryset = Attendance.objects.exclude(close_reason__isnull=False)\
        .exclude(students__isnull=True).order_by('school__number', 'attendance_date')
   # queryset = queryset.filter(education_year_id=current_year)
    if from_date:
        queryset = queryset.filter(attendance_date__gte=from_date)
    if to_date:
        queryset = queryset.filter(attendance_date__lte=to_date)
    if from_school:
        queryset = queryset.filter(school__number__gte=from_school)
    if to_school:
        queryset = queryset.filter(school__number__lte=to_school)

    for line in queryset:
        if not line.students:
            continue
        for level_section in line.students:
            attendances = line.students[level_section]
            students = attendances['students']
            calculate_absentees(attendance=line, students=students)
