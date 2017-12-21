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

    title = '2nd-shit-all'
    queryset = Enrollment.objects.all()
    if 'current' in params:
        title = '2nd-shit-current'
        queryset = queryset.filter(education_year__current_year=True)
    if 'school' in params:
        queryset = queryset.filter(school_id=params['school'])
    if 'section' in params and params['section']:
        queryset = queryset.filter(section_id=params['section'])

    data = tablib.Dataset()
    data.headers = [

        _('Last non formal education - result'),
        _('Last non formal education - round'),
        _('Is the child participated in an ALP/2016-2 program'),

        _('Last formal education - result'),
        _('Last formal education - year'),
        _('Last formal education - school'),
        _('Last formal education - level'),

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

    timestamp = '{}-{}'.format(title, time.time())
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

    title = '2nd-shift-grading-current'
    queryset = EnrollmentGrading.objects.filter(enrollment__education_year=current)
    if 'school' in params:
        queryset = queryset.filter(enrollment__school_id=params['school'])
    if 'classroom' in params and params['classroom']:
        queryset = queryset.filter(enrollment__classroom_id=params['classroom'])
    if 'section' in params and params['section']:
        queryset = queryset.filter(enrollment__section_id=params['section'])
    if 'year' in params and params['year']:
        title = '2nd-shift-grading-year-'+params['year']
        queryset = queryset.filter(enrollment__education_year_id=params['year'])
    if 'term' in params and params['term']:
        queryset = queryset.filter(exam_term=params['term'])

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
            line.exam_term_name,

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

    timestamp = '{}-{}'.format(title, time.time())
    file_format = base_formats.XLSX()
    data = file_format.export_data(data)
    if return_data:
        return data
    store_file(data, timestamp)
    return True


@app.task
def export_alp(params=None, return_data=False):
    from student_registration.alp.models import Outreach, ALPRound

    title = 'alp-all'
    queryset = Outreach.objects.all()

    if 'pre_test' in params:
        title = 'alp-pre-test'
        queryset = queryset.filter(
            alp_round__current_pre_test=True,
            level__isnull=False,
            assigned_to_level__isnull=False
        )
    if 'post_test' in params:
        title = 'alp-post-test'
        queryset = queryset.filter(
            alp_round__current_post_test=True,
            registered_in_level__isnull=False,
            refer_to_level__isnull=False
        )
    if 'current' in params:
        title = 'alp-current'
        queryset = queryset.filter(
            alp_round__current_round=True,
            registered_in_level__isnull=False,
        )
    if 'current_all' in params:
        title = 'alp-current-all'
        queryset = queryset.filter(
            alp_round__current_round=True,
        )
    if 'school' in params:
        queryset = queryset.filter(school_id=params['school'])

    data = tablib.Dataset()

    data.headers = [

        _('ALP round'),
        _('Governorate'),
        _('District'),
        _('School number'),
        _('School'),
        _('First name'),

        _('Father name'),
        _('Last name'),
        _('Mother fullname'),
        _('Birthday day'),
        _('Birthday month'),

        _('Birthday year'),
        _('Student age'),
        _('Student sex'),
        _('Student nationality'),
        _('Mother nationality'),

        _('Registered in UNHCR'),
        _('Student ID Type'),
        _('Student ID Number'),
        _('Phone prefix'),
        _('Phone number'),

        _('Student living address'),
        _('Pre-test level'),
        _('Pre-test room'),
        _('Arabic'),
        _('Exam language'),
        _('Foreign language'),

        _('Math'),
        _('Science'),
        _('Pre-test total'),
        _('Comments'),
        _('Assigned to level'),

        _('Current Section'),
        _('Registered in Level'),
        _('Arabic'),
        _('Exam language'),

        _('Foreign language'),
        _('Math'),
        _('Science'),
        _('Post-test room'),
        _('Post-test total'),
        _('Post-test result'),

        _('Comments'),

        _('Last formal education - level'),
        _('Last formal education - year'),
        _('Is the child participated in an ALP program'),
        _('Last non formal education - level'),
        _('Last non formal education - round'),

        _('Last non formal education - result'),
        _('Created by'),
        _('Modified by'),
        _('Creation date'),
        _('Modification date')

    ]

    content = []
    for line in queryset:
        if not line.student or not line.school:
            continue
        student = line.student
        content = [

            line.alp_round.name if line.alp_round else '',
            line.school.location.parent.name,
            line.school.location.name,
            line.school.number,
            line.school.name,
            student.first_name,

            student.father_name,
            student.last_name,
            student.mother_fullname,
            student.birthday_year,
            student.birthday_month,

            student.birthday_day,
            student.age,
            student.sex,
            student.nationality.name if student.nationality else '',
            student.mother_nationality.name if student.mother_nationality else '',

            student.registered_in_unhcr,
            student.id_type.name if student.id_type else '',
            student.id_number,
            student.phone_prefix,
            student.phone,

            student.address,
            line.level.name if line.level else '',
            line.pre_test_room,
            line.exam_result_arabic,
            line.exam_language,
            line.exam_result_language,

            line.exam_result_math,
            line.exam_result_science,
            line.exam_total,
            line.pre_comment,
            line.assigned_to_level.name if line.assigned_to_level else '',

            line.section.name if line.section else '',
            line.registered_in_level.name if line.registered_in_level else '',

            line.post_exam_result_arabic,
            line.post_exam_language,

            line.post_exam_result_language,
            line.post_exam_result_math,
            line.post_exam_result_science,
            line.post_test_room,
            line.post_exam_total,
            line.refer_to_level,
            line.post_comment,

            line.last_education_level.name if line.last_education_level else '',
            line.last_education_year,
            _(line.participated_in_alp) if line.participated_in_alp else '',
            line.last_informal_edu_level.name if line.last_informal_edu_level else '',
            line.last_informal_edu_round.name if line.last_informal_edu_round else '',

            line.last_informal_edu_final_result.name if line.last_informal_edu_final_result else '',
            line.owner.username if line.owner else '',
            line.modified_by.username if line.modified_by else '',
            line.created,
            line.modified,
        ]
        data.append(content)

    timestamp = '{}-{}'.format(title, time.time())
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

    timestamp = '{}-{}'.format('attendance', time.time())
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
            line.get_id(),
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
            line.get_0_to_3_months(),
            line.get_3_to_12_months(),
            line.get_1_year_old(),
            line.get_2_years_old(),
            line.get_3_years_old(),
            line.get_4_years_old(),
            line.get_5_years_old(),
            line.get_6_years_old(),
            line.get_7_years_old(),
            line.get_8_years_old(),
            line.get_9_years_old(),
            line.get_10_years_old(),
            line.get_11_years_old(),
            line.get_12_years_old(),
            line.get_13_years_old(),
            line.get_14_years_old(),
            line.male,
            line.female,
            line.get_3_months_kit(),
            line.get_12_months_kit(),
            line.get_2_years_kit(),
            line.get_3_years_kit(),
            line.get_5_years_kit(),
            line.get_7_years_kit(),
            line.get_9_years_kit(),
            line.get_12_years_kit(),
            line.get_14_years_kit(),
            line.get_3_months_kit_completed(),
            line.get_12_months_kit_completed(),
            line.get_2_years_kit_completed(),
            line.get_3_years_kit_completed(),
            line.get_5_years_kit_completed(),
            line.get_7_years_kit_completed(),
            line.get_9_years_kit_completed(),
            line.get_12_years_kit_completed(),
            line.get_14_years_kit_completed(),
        ]

        data.append(content)

    timestamp = '{}-{}'.format('winter', time.time())
    file_format = base_formats.XLSX()
    data = file_format.export_data(data)
    if return_data:
        return data
    store_file(data, timestamp)
    return True
