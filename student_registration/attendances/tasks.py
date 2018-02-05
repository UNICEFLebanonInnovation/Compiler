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
def dropout_students(from_date, to_date):
    from .models import Attendance, Absentee

    queryset = Attendance.objects.exclude(total_absences=0).exclude(close_reason__isnull=False)
    # queryset = queryset.filter(
    #     attendance_date__gte=from_date,
    #     attendance_date__lte=to_date
    # )

    for line in queryset:
        if not line.students:
            continue
        for level_section in line.students:
            attendances = line.students[level_section]
            students = attendances['students']
            for student in students:
                continue


@app.task
def calculate_attendances_by_student():
    from .utils import calculate_absentees
    from .models import Attendance, Absentee

    Absentee.objects.all().delete()
    queryset = Attendance.objects.exclude(close_reason__isnull=False).exclude(students__isnull=True)
    queryset = queryset.order_by('attendance_date')

    for line in queryset:
        if not line.students:
            continue
        for level_section in line.students:
            attendances = line.students[level_section]
            students = attendances['students']
            calculate_absentees(attendance=line, students=students)


@app.task
def calculate_absentees(attendance, students):
    from .models import Absentee

    for student in students:
        try:
            absentee = Absentee.objects.get(student_id=student['student_id'])
        except Absentee.DoesNotExist:
            absentee = Absentee.objects.create(
                student_id=student['student_id'],
                school=attendance.school,
                absent_days=0,
                attended_days=0
            )

        if student['status'] == 'True':
            absentee.absent_days = 0
            absentee.attended_days += 1
            absentee.last_attendance_date = attendance.attendance_date
        elif student['status'] == 'False':
            absentee.last_absent_date = attendance.attendance_date
            absentee.absent_days += 1
            absentee.attended_days = 0

        absentee.save()


@app.task
def calculate_absentees2(attendance, students):
    from .models import Absentee

    for student in students:
        try:
            absentee = Absentee.objects.get(student_id=student['student_id'])
        except Absentee.DoesNotExist:
            absentee = Absentee.objects.create(
                student_id=student['student_id'],
                school=attendance.school,
                absent_days=0,
                attended_days=0
            )

        if student['status'] == 'True' and not attendance.attendance_date == absentee.last_attendance_date:
            if absentee.absent_days > 0:
                absentee.absent_days -= 1
            else:
                absentee.absent_days = 0
            absentee.attended_days += 1
            absentee.last_attendance_date = attendance.attendance_date
            absentee.last_absent_date = None
        elif student['status'] == 'False' and not attendance.attendance_date == absentee.last_absent_date:
            absentee.last_absent_date = attendance.attendance_date
            absentee.last_attendance_date = None
            absentee.absent_days += 1
            if absentee.attended_days > 0:
                absentee.attended_days -= 1
            else:
                absentee.attended_days = 0

        absentee.save()


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
