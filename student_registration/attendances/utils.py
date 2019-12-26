
import datetime


def find_absentees(governorate=None, from_date=None, to_date=None):
    from .models import Attendance

    queryset = Attendance.objects.all()
    queryset = queryset.exclude(close_reason__isnull=False).exclude(students__isnull=True)

    if governorate:
        queryset = queryset.filter(school__location__parent_id=int(governorate))

    if from_date and to_date:
        queryset = queryset.filter(
            attendance_date__gte=from_date,
            attendance_date__lte=to_date,
        )


def find_attendances(governorate=None, student_id=None, from_date=None, to_date=None, filter_by_status=None):
    from student_registration.enrollments.models import Enrollment
    from student_registration.alp.models import Outreach, ALPRound
    from .models import Attendance

    alp_round = ''
    queryset = Attendance.objects.all()
    queryset = queryset.exclude(close_reason__isnull=True).exclude(students__isnull=True)

    if governorate:
        queryset = queryset.filter(school__location__parent_id=int(governorate))
    elif student_id:
        enrollment = Enrollment.objects.filter(
            education_year__current_year=True,
            student_id=int(student_id)
        ).first()
        if not enrollment:
            alp_round = ALPRound.objects.get(current_round=True).name
            enrollment = Outreach.objects.filter(
                alp_round__current_round=True,
                registered_in_level__isnull=False,
                student_id=student_id
            ).first()

        if not enrollment:
            return []

        queryset = queryset.filter(school_id=enrollment.school_id)

    if from_date and to_date:
        queryset = queryset.filter(
            attendance_date__gte=from_date,
            attendance_date__lte=to_date,
            validation_status=True
        )

    data = []
    for line in queryset:
        # if not line.students or line.close_reason:
        #     continue
        if not isinstance(line.students, dict):
            continue
        for level_section in line.students:
            attendances = line.students[level_section]
            students = attendances['students']
            if attendances['exam_day'] == 'true':
                continue
            for student in students:
                if student_id and not student_id == student['student_id']:
                    continue
                if filter_by_status and student['status'] == "True":
                    continue
                content = {
                    'school_cerd': line.school.number,
                    'school_name': line.school.name,
                    'district': line.school.location.name,
                    'governorate': line.school.location.parent.name,

                    'attendance_date': line.attendance_date.strftime('%Y-%m-%d'),

                    'level': student['level_name'],
                    'section': student['section_name'],

                    'student_id': student['student_id'],
                    'student_fullname': student['student_fullname'],
                    'student_sex': student['student_sex'],
                    'student_age': student['student_age'],
                    'attendance_status': student['status'],
                    'absence_reason': student['absence_reason'] if 'absence_reason' in student else '',
                    'alp_round': alp_round
                }
                data.append(content)

    return data


def fill_attendancedt(attendance, students):
    from .models import AttendanceDt, EducationYear
    from student_registration.enrollments.models import Enrollment
    for student in students:
        attendance_dt = AttendanceDt.objects.filter(attendance_date=attendance.attendance_date,
                                                    student_id=student['student_id']).count()
        if attendance_dt == 0:
            attendance_dt = AttendanceDt.objects.create(
                student_id=student['student_id'],
                attendance_date=attendance.attendance_date,
                is_present=student['status'],
                school_id=attendance.school_id,
                section_id=student['section'],
                classlevel_id=student['level'],
                attendance_id=attendance.id,
                levelname=student['level_name']
            )
        if student['status'] == 'true':
            attendance_dt.is_present = 'true'
            current_year = EducationYear.objects.get(current_year=True)
            try:
                enr = Enrollment.objects.get(education_year=current_year, school_id=attendance.school_id, student_id=student['student_id'], section_id=student['section'], classroom_id=student['level'])
                if not enr.last_attendance_date:
                    enr.last_attendance_date = attendance.attendance_date
                    enr.nb_consecutiveabsences = 0
                    enr.save()
                else:
                    if attendance.attendance_date > enr.last_attendance_date:
                        enr.last_attendance_date = attendance.attendance_date
                        enr.nb_consecutiveabsences = 0
                        enr.save()
            except Enrollment.DoesNotExist:
                enr = ''
        else:
            attendance_dt.is_present = 'false'
            current_year = EducationYear.objects.get(current_year=True)
            try:
                enr = Enrollment.objects.get(education_year=current_year, school_id=attendance.school_id, student_id=student['student_id'], section_id=student['section'], classroom_id=student['level'])
                if not enr.last_absent_date:
                    enr.last_absent_date = attendance.attendance_date
                    enr.save()
                else:
                    if attendance.attendance_date > enr.last_absent_date:
                        enr.last_absent_date = attendance.attendance_date
                        if enr.nb_consecutiveabsences:
                            enr.nb_consecutiveabsences += 1
                        else:
                            enr.nb_consecutiveabsences = 1
                        enr.save()
            except Enrollment.DoesNotExist:
                enr = ''
        attendance_dt.save()


def add_attendance(attendance, students, std_id):
    from .models import AttendanceDt

    for student in students:
        if std_id != "":
            if std_id == student['student_id']:
                try:
                    AttendanceDt.objects.get(student_id=std_id, attendance_date=attendance.attendance_date)
                except AttendanceDt.DoesNotExist:
                    attendance_dt = AttendanceDt.objects.create(
                        student_id=student['student_id'],
                        attendance_date=attendance.attendance_date,
                        is_present=student['status'],
                        school_id=attendance.school_id,
                        section_id=student['section'],
                        classlevel_id=student['level'],
                        classroom_id=attendance.classroom_id,
                        attendance_id=attendance.id,
                        levelname=student['level_name'],
                        )
                    attendance_dt.save()
        else:
            try:
                AttendanceDt.objects.get(student_id=student['student_id'], attendance_date=attendance.attendance_date)
            except AttendanceDt.DoesNotExist:
                attendance_dt = AttendanceDt.objects.create(
                    student_id=student['student_id'],
                    attendance_date=attendance.attendance_date,
                    is_present=student['status'],
                    school_id=attendance.school_id,
                    section_id=student['section'],
                    classlevel_id=student['level'],
                    classroom_id=attendance.classroom_id,
                    attendance_id=attendance.id,
                    levelname=student['level_name'],
                    )
                attendance_dt.save()


def calculate_absentees(attendance, students):
    from .models import Absentee

    for student in students:

        try:
            absentee = Absentee.objects.get(student_id=student['student_id'])
        except Absentee.DoesNotExist:
            absentee = Absentee.objects.create(
                student_id=student['student_id'],
                school=attendance.school,
                education_year=attendance.education_year,
                alp_round=attendance.alp_round,
                absent_days=0,
                attended_days=0,
                total_attended_days=0,
                total_absent_days=0
            )

        absentee.level = student['level'] if 'level' in student else ''
        absentee.level_name = student['level_name'] if 'level_name' in student else ''
        absentee.section = student['section'] if 'section' in student else ''
        absentee.section_name = student['section_name'] if 'section_name' in student else ''

        absentee.last_modification_date = datetime.datetime.now()

        if student['status'] == 'True':
            absentee.absent_days = 0
            absentee.attended_days += 1
            absentee.total_attended_days += 1
            absentee.last_attendance_date = attendance.attendance_date
        elif student['status'] == 'False':
            absentee.last_absent_date = attendance.attendance_date
            absentee.absent_days += 1
            absentee.attended_days = 0
            absentee.total_absent_days += 1

        absentee.save()
