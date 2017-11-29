__author__ = 'achamseddine'

import time
import tablib
from django.utils.translation import ugettext as _
from import_export.formats import base_formats
from student_registration.taskapp.celery import app
from .file import store_file


@app.task
def export_2ndshift(params=None, return_data=False):
    from student_registration.enrollments.models import Enrollment
    from student_registration.schools.models import EducationYear

    queryset = Enrollment.objects.all()
    if 'current' in params:
        queryset = queryset.filter(education_year__current_year=True)
    if 'school' in params:
        queryset = queryset.filter(school_id=params['school'])

    data = tablib.Dataset()
    data.headers = [

        _('ALP result'),
        _('ALP round'),
        _('Is the child participated in an ALP/2016-2 program'),
        _('Result'),
        _('Education year'),
        _('School'),
        _('Last education level'),

        _('Serial number in previous school'),

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
        _('Place of birth'),
        _('year'),
        _('month'),
        _('day'),
        _('Sex'),
        _('Student first name'),
        _('Student father name'),
        _('Student last name'),
        _('Student fullname'),

        _('First time registered?'),
        _('Student outreached?'),
        _('Have barcode with him?'),
        _('Outreach barcode'),

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
            _(line.participated_in_alp) if line.participated_in_alp else '',

            _(line.last_year_result) if line.last_year_result else '',
            line.last_education_year if line.last_education_year else '',
            _(line.last_school_type) if line.last_school_type else '',
            line.last_education_level.name if line.last_education_level else '',

            line.number_in_previous_school,

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
            line.student.place_of_birth,
            line.student.birthday_year,
            line.student.birthday_month,
            line.student.birthday_day,
            _(line.student.sex) if line.student.sex else '',
            line.student.first_name,
            line.student.father_name,
            line.student.last_name,
            line.student.__unicode__(),

            line.new_registry,
            line.student_outreached,
            line.have_barcode,
            line.outreach_barcode,

            line.registration_date,
            line.school.name,
            line.school.number,
            line.school.location.name,
            line.school.location.parent.name,
        ]
        data.append(content)

    timestamp = time.time()
    file_format = base_formats.XLSX()
    data = file_format.export_data(data)
    if return_data:
        return data
    store_file(data, timestamp)
    return True


@app.task
def export_2ndshift_gradings(params=None, return_data=False):
    from student_registration.enrollments.models import EnrollmentGrading
    from student_registration.schools.models import EducationYear
    current = EducationYear.objects.get(current_year=True)

    queryset = EnrollmentGrading.objects.filter(enrollment__education_year=current)
    if 'school' in params:
        queryset = queryset.filter(enrollment__school_id=params['school'])

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

    timestamp = time.time()
    file_format = base_formats.XLSX()
    data = file_format.export_data(data)
    if return_data:
        return data
    store_file(data, timestamp)
    return True


@app.task
def export_alp(params=None, return_data=False):
    from student_registration.alp.models import Outreach, ALPRound

    queryset = Outreach.objects.all()

    if 'pre_test' in params:
        queryset = queryset.filter(
            alp_round__current_pre_test=True,
            level__isnull=False,
            assigned_to_level__isnull=False
        )
    if 'post_test' in params:
        queryset = queryset.filter(
            alp_round__current_post_test=True,
            registered_in_level__isnull=False,
            refer_to_level__isnull=False
        )
    if 'current' in params:
        queryset = queryset.filter(
            alp_round__current_round=True,
            registered_in_level__isnull=False,
        )
    if 'current_all' in params:
        queryset = queryset.filter(
            alp_round__current_round=True,
        )
    if 'school' in params:
        queryset = queryset.filter(school_id=params['school'])

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

    timestamp = time.time()
    file_format = base_formats.XLSX()
    data = file_format.export_data(data)
    if return_data:
        return data
    store_file(data, timestamp)
    return True


@app.task
def export_attendance(params=None, return_data=False):
    from student_registration.attendances.models import Attendance

    queryset = Attendance.objects.all()
    if 'school' in params:
        queryset = queryset.filter(school_id=params['school'])
    if 'date' in params:
        queryset = queryset.filter(attendance_date=params['date'])

    data = tablib.Dataset()

    data.headers = [
        _('School number'),
        _('School'),
        _('District'),
        _('Governorate'),

        _('Attendance date'),
        _('Validation status'),
        _('Validation date'),
        _('Validated by'),
        _('Close reason'),
        _('Exam day'),

        _('Level'),
        _('Section'),

        _('Student fullname'),
        _('Sex'),
        _('Age'),
        _('Attendance status'),
        _('Absence reason'),
        _('Dropout')
    ]

    content = []
    for line in queryset:
        if not line.students:
            continue
        for level_section in line.students:
            attendances = line.students[level_section]
            students = attendances['students']
            for student in students:
                content = [
                    line.school.number,
                    line.school.name,
                    line.school.location.name,
                    line.school.location.parent.name,

                    line.attendance_date,
                    line.validation_date,
                    line.validation_status,
                    line.validation_owner.username if line.validation_owner else '',
                    line.close_reason,
                    attendances['exam_day'],

                    student['level_name'],
                    student['section_name'],

                    student['student_fullname'],
                    student['student_sex'],
                    student['student_age'],
                    student['status'],
                    student['absence_reason'] if 'absence_reason' in student else '',
                    student['dropout'] if 'dropout' in student else '',
                ]
                data.append(content)

    timestamp = time.time()
    file_format = base_formats.XLSX()
    data = file_format.export_data(data)
    if return_data:
        return data
    store_file(data, timestamp)
    return True


@app.task
def export_winterization(return_data=False):
    from student_registration.winterization.models import Assessment

    queryset = Assessment.objects.all()

    data = tablib.Dataset()
    data.headers = [
        '_id',
        'p_code',
        'p_code_name',
        'district',
        'cadastral',
        'location_type',
        'assistance_type',
        'phone_number',
        'phone_owner',
        'latitude',
        'longitude',
        'first_name',
        'middle_name',
        'last_name',
        'mothers_name',
        'relationship_type',
        'family_count',
        'disabilities',
        'official_id',
        'gender',
        'dob',
        'marital_status',
        'creation_date',
        'completion_date',
        'partner_name',
        'moving_location',
        'new_district',
        'new_cadastral',
        '0 to 3 months',
        '3 to 12 months',
        '1 year old',
        '2 years old',
        '3 years old',
        '4 years old',
        '5 years old',
        '6 years old',
        '7 years old',
        '8 years old',
        '9 years old',
        '10 years old',
        '11 years old',
        '12 years old',
        '13 years old',
        '14 years old',
        'male',
        'female',
        '3 months kit',
        '12 months kit',
        '2 years kit',
        '3 years kit',
        '5 years kit',
        '7 years kit',
        '9 years kit',
        '12 years kit',
        '14 years kit',
        '3 months kit Completed',
        '12 months kit Completed',
        '2 years kit Completed',
        '3 years kit Completed',
        '5 years kit Completed',
        '7 years kit Completed',
        '9 years kit Completed',
        '12 years kit Completed',
        '14 years kit Completed',
    ]

    content = []
    for line in queryset:
        content = [
            line._id,
            line.location_p_code,
            line.location_p_code_name,
            line.district,
            line.cadastral,
            line.location_type,
            line.locations_type,
            line.assistance_type,
            line.phone_number,
            line.phone_owner,
            line.latitude,
            line.longitude,
            line.first_name,
            line.middle_name,
            line.last_name,
            line.mothers_name,
            line.relationship_type,
            line.family_count,
            line.disabilities,
            line.official_id,
            line.gender,
            line.dob,
            line.marital_status,
            line.creation_date,
            line.completion_date,
            line.partner_name,
            line.moving_location,
            line.new_district,
            line.new_cadastral,
            line._0_to_3_months,
            line._3_to_12_months,
            line._1_year_old,
            line._2_years_old,
            line._3_years_old,
            line._4_years_old,
            line._5_years_old,
            line._6_years_old,
            line._7_years_old,
            line._8_years_old,
            line._9_years_old,
            line._10_years_old,
            line._11_years_old,
            line._12_years_old,
            line._13_years_old,
            line._14_years_old,
            line.male,
            line.female,
            line._3_months_kit,
            line._12_months_kit,
            line._2_years_kit,
            line._3_years_kit,
            line._5_years_kit,
            line._7_years_kit,
            line._9_years_kit,
            line._12_years_kit,
            line._14_years_kit,
            line._3_months_kit_completed,
            line._12_months_kit_completed,
            line._2_years_kit_completed,
            line._3_years_kit_completed,
            line._5_years_kit_completed,
            line._7_years_kit_completed,
            line._9_years_kit_completed,
            line._12_years_kit_completed,
            line._14_years_kit_completed,
        ]

        data.append(content)

    timestamp = time.time()
    file_format = base_formats.XLSX()
    data = file_format.export_data(data)
    if return_data:
        return data
    store_file(data, timestamp)
    return True
