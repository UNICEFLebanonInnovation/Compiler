

def find_attendances(governorate=None, student=None, from_date=None, to_date=None):
    from student_registration.enrollments.models import Enrollment
    from student_registration.alp.models import Outreach
    from .models import Attendance

    queryset = Attendance.objects.all()

    if governorate:
        queryset = queryset.filter(school__location__parent_id=int(governorate))
    elif student:
        enrollment = Enrollment.objects.filter(
            education_year__current_year=True,
            student_id=int(student)
        ).first()
        queryset = queryset.filter(school_id=enrollment.school_id)

    if from_date and to_date:
        queryset = queryset.filter(
            attendance_date__gte=from_date,
            attendance_date__lte=to_date,
            validation_status=True
        )

    data = []
    for line in queryset:
        if not line.students or line.close_reason:
            continue
        if not isinstance(line.students, dict):
            continue
        for level_section in line.students:
            attendances = line.students[level_section]
            students = attendances['students']
            if attendances['exam_day'] == 'true':
                continue
            for student in students:
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
                }
                data.append(content)

    return data
