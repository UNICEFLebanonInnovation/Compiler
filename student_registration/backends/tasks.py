__author__ = 'achamseddine'

import json
import time
import tablib
from django.utils.translation import ugettext as _
from import_export.formats import base_formats
from student_registration.taskapp.celery import app
from .file import store_file
from openpyxl import load_workbook
from .utils import get_data


@app.task
def export_2ndshift(params=None, return_data=False):
    from student_registration.enrollments.models import Enrollment
    from student_registration.schools.models import EducationYear

    title = '2nd-shit-all'
    # queryset = Enrollment.objects.exclude(moved=True)
    queryset = Enrollment.objects.all()
    if 'current' in params:
        title = '2nd-shit-current'
        queryset = queryset.filter(education_year__current_year=True)
    if 'year' in params:
        queryset = queryset.filter(education_year_id=params['year'])
    if 'classroom' in params and params['classroom']:
        queryset = queryset.filter(classroom_id=params['classroom'])
    if 'school' in params:
        queryset = queryset.filter(school_id=params['school'])
    if 'section' in params and params['section']:
        queryset = queryset.filter(section_id=params['section'])

    data = tablib.Dataset()
    data.headers = [

        'created',
        'modified',
        'dropout_status',
        'disabled',
        'moved',

        'last_attendance_date',
        'last_absent_date',

        _('Last non formal education - result'),
        _('Last non formal education - round'),
        _('Is the child participated in an ALP/2016-2 program'),

        _('Last formal education - result'),
        _('Last formal education - year'),
        _('Last formal education - school shift'),
        _('Last formal education - school type'),
        _('Last formal education - school'),
        _('Last formal education - CERD'),
        _('Last formal education - level'),

        _('Serial number in previous school'),

        _('Current Section'),
        _('Current Class'),
        _('Current Cycle'),
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

            line.created,
            line.modified,
            line.dropout_status,
            line.disabled,
            line.moved,

            line.last_attendance_date,
            line.last_absent_date,

            line.last_informal_edu_final_result.name if line.last_informal_edu_final_result else '',
            line.last_informal_edu_round.name if line.last_informal_edu_round else '',
            _(line.participated_in_alp) if line.participated_in_alp else '',

            _(line.last_year_result) if line.last_year_result else '',
            line.last_education_year if line.last_education_year else '',
            _(line.last_school_type) if line.last_school_type else '',
            _(line.last_school_shift) if line.last_school_shift else '',
            line.last_school.name if line.last_school else '',
            line.last_school.number if line.last_school else '',
            line.last_education_level.name if line.last_education_level else '',

            line.number_in_previous_school,

            line.section.name if line.section else '',
            line.classroom.name if line.classroom else '',
            line.cycle,
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
    queryset = EnrollmentGrading.objects.exclude(enrollment__isnull=True).filter(enrollment__education_year=current)
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
            # alp_round__current_pre_test=True,
            level__isnull=False,
            assigned_to_level__isnull=False
        )
    if 'post_test' in params:
        title = 'alp-post-test'
        queryset = queryset.filter(
            # alp_round__current_post_test=True,
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
    if 'alp_round' in params:
        title = 'alp-round-'+params['alp_round']
        queryset = queryset.filter(
            alp_round_id=int(params['alp_round'])
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
        _('Modification date'),
        _('Re-enrolled'),

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

            student.birthday_day,
            student.birthday_month,
            student.birthday_year,
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
            line.re_enrolled,
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
    if 'from_date' in params:
        queryset = queryset.filter(attendance_date__gte=params['from_date'])
    if 'to_date' in params:
        queryset = queryset.filter(attendance_date__lte=params['to_date'])
    if 'gov' in params:
        queryset = queryset.filter(school__location__parent=int(params['gov']))
    if 'school_type' in params:
        school_type = params['school_type']
        queryset = queryset.filter(school_type=school_type)
        if school_type == 'ALP':
            queryset = queryset.filter(alp_round__current_round=True)
        if school_type == '2nd-shift':
            queryset = queryset.filter(education_year__current_year=True)

    data = tablib.Dataset()

    data.headers = [
        _('School number'),
        _('School'),
        _('School type'),
        _('Education year/ALP round'),
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
        school = line.school
        school_location = school.location
        school_location_parent = school_location.parent
        education_year = line.education_year
        alp_round = line.alp_round
        if not line.students:
            continue
        for level_section in line.students:
            attendances = line.students[level_section]
            students = attendances['students']
            for student in students:
                content = [
                    school.number,
                    school.name,
                    line.school_type,
                    education_year.name if education_year else alp_round.name,
                    school_location.name,
                    school_location_parent.name,

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
def import_attendance_by_student():
    from student_registration.attendances.models import Absentee
    wb = load_workbook(filename='attendance_by_student.xlsx', read_only=True)
    ws = wb['students']
    ctr = 0

    for row in ws.rows:
        try:
            if row[0].value == 'school_id':
                continue

            instance = Absentee.objects.create(
                school_id=row[0].value,
                student_id=row[6].value,
                education_year_id=row[1].value,
                level_name=row[2].value,
                level=row[3].value,
                section_name=row[4].value,
                section=row[5].value,
                attended_days=row[8].value,
                total_attended_days=row[9].value,
                absent_days=row[11].value,
                total_absent_days=row[12].value,
            )

            if not row[7].value == 'None':
                instance.last_attendance_date = row[7].value

            if not row[10].value == 'None':
                instance.last_absent_date = row[10].value

            if not row[13].value == 'None':
                instance.last_modification_date=row[13].value

            instance.save()

        except Exception as ex:
            print("---------------")
            ctr += 1
            print("error: ", ex)
            print("---------------")
            pass
    print(ctr)


@app.task
def export_attendance_by_student(params=None, return_data=False):
    from student_registration.attendances.models import Absentee

    queryset = Absentee.objects.all()

    data = tablib.Dataset()

    data.headers = [

        'school_id',
        'school_number',
        'school_name',
        'governorate',
        'district',
        'education_year/alp_round',
        'education_year_id',
        'alp_round_id',
        'level_name',
        'level',
        'section_name',
        'section',
        'student_id',
        'student_first_name',
        'student_father_name',
        'student_last_name',
        'student_mother_fullname',
        'student_sex',
        'student_age',
        'last_attendance_date',
        'attended_days',
        'total_attended_days',
        'last_absent_date',
        'absent_days',
        'total_absent_days',
        'last_modification_date',
    ]

    content = []
    for line in queryset:
        school = line.school
        school_location = school.location
        school_location_parent = school_location.parent
        education_year = line.education_year
        alp_round = line.alp_round

        if not education_year:
            continue

        content = [
            school.id,
            school.number,
            school.name,
            school_location_parent.name,
            school_location.name,
            education_year.name,
            education_year.id if education_year else '',
            alp_round.id if alp_round else '',
            line.level_name,
            line.level,
            line.section_name,
            line.section,
            line.student_id,
            line.student.first_name,
            line.student.father_name,
            line.student.last_name,
            line.student.mother_fullname,
            line.student.sex,
            line.student.age,
            line.last_attendance_date,
            line.attended_days,
            line.total_attended_days,
            line.last_absent_date,
            line.absent_days,
            line.total_absent_days,
            line.last_modification_date
        ]
        data.append(content)

    timestamp = '{}-{}'.format('attendance_by_student', time.time())
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



# @app.task
# def import_2ndshift_data(params=None):
#     from .models import ImportedData

    # ImportedData.objects.filter(type='2nd-shift').delete()
    # ImportedData.objects.filter(type__isnull=True).delete()

    # for i in range(36, 320):
    #     offset = 500 * i
    #     print(i)
    #     result = get_data('mdb2.azurewebsites.net', '/api/import-enrollment/?year=2&max=500&offset='+str(offset))
    #     result = json.loads(result)
    #     for item in result:
    #         ImportedData.objects.create(enrollment=item, type='2nd-shift')
    #     print('DONE')


@app.task
def import_grading_data(params=None):
    from student_registration.enrollments.models import EnrollmentGrading

    for i in range(120, 315):
        offset = 500 * i
        print(i)
        result = get_data('mdb2.azurewebsites.net', '/api/import-grading/?term=1&year=2&max=500&offset='+str(offset))
        result = json.loads(result)
        for item in result:
            try:
                instance = EnrollmentGrading.objects.get(id=item['id'])
            except Exception as ex:
                print(ex.message)
                try:
                    instance = EnrollmentGrading.objects.create(
                        id=item['id'],
                        enrollment_id=item['enrollment_id'],
                        exam_term='1',
                    )
                except Exception as ex:
                    print(ex.message)
                    continue

            instance.exam_result_arabic=item['exam_result_arabic']
            instance.exam_result_language=item['exam_result_language']
            instance.exam_result_education=item['exam_result_education']
            instance.exam_result_geo=item['exam_result_geo']
            instance.exam_result_history=item['exam_result_history']
            instance.exam_result_math=item['exam_result_math']
            instance.exam_result_science=item['exam_result_science']
            instance.exam_result_physic=item['exam_result_physic']
            instance.exam_result_chemistry=item['exam_result_chemistry']
            instance.exam_result_bio=item['exam_result_bio']
            instance.exam_result_linguistic_ar=item['exam_result_linguistic_ar']
            instance.exam_result_linguistic_en=item['exam_result_linguistic_en']
            instance.exam_result_sociology=item['exam_result_sociology']
            instance.exam_result_physical=item['exam_result_physical']
            instance.exam_result_artistic=item['exam_result_artistic']
            instance.exam_result_mathematics=item['exam_result_mathematics']
            instance.exam_result_sciences=item['exam_result_sciences']
            instance.exam_total=item['exam_total']
            instance.exam_result=item['exam_result']

            instance.save()

        print('DONE')


@app.task
def import_attendance_data(params=None):
    from student_registration.attendances.models import Attendance

    month = '5'
    year = '2018'
    max_values = 50
    from_day = 15
    to_date = 30
    for i in range(78, 200):
        offset = max_values * i
        print(i)
        result = get_data('mdb2.azurewebsites.net', '/api/export-attendances/?year=2&from_day=10&to_day=31&max=50&offset='+str(offset)+'&month='+month+'&year='+year)
        result = json.loads(result)
        for item in result:
            try:
                instance = Attendance.objects.get(id=item['id'])
            except Exception as ex:
                print(ex.message)
                try:
                    instance = Attendance.objects.create(
                        id=item['id'],
                        school_id=item['school_id'],
                        school_type=item['school_type'],
                        education_year_id=item['education_year_id'],
                        alp_round_id=item['alp_round_id'],
                        attendance_date=item['attendance_date'],

                    )
                except Exception as ex:
                    print(ex.message)
                    continue

            instance.validation_status = item['validation_status']
            instance.validation_date = item['validation_date']
            instance.validation_owner_id = item['validation_owner']
            instance.close_reason = item['close_reason']
            instance.students = item['students']

            instance.save()

        print('DONE')


# @app.task
# def import_attendance_data(params=None):
    # from .models import ImportedData
    #
    # ImportedData.objects.filter(type='attendance').delete()
    # month = '2'
    # year = '2018'
    # max_values = 50
    #
    # for i in range(0, 200):
    #     offset = max_values * i
    #     print(i)
    #     result = get_data('mdb2.azurewebsites.net', '/api/export-attendances/?year=2&max=50&offset='+str(offset)+'&month='+month+'&year='+year)
    #     result = json.loads(result)
    #     for item in result:
    #         ImportedData.objects.create(enrollment=item, type='attendance')
    #     print('DONE')


@app.task
def export_bln_list(params=None, return_data=False):

    from student_registration.clm.models import BLN

    queryset = BLN.objects.all()
    if 'partner' in params and params['partner']:
        queryset = queryset.filter(partner_id=int(params['partner']))

    data = tablib.Dataset()

    data.headers = [
        _('CLM round'),
        _('Governorate'),
        _('District'),
        _('Location'),
        _('The language supported in the program'),

        _('First name'),
        _('Father name'),
        _('Last name'),
        _('Sex'),
        _('Birthday day'),
        _('Birthday month'),
        _('Birthday year'),
        _('Birthday'),
        _('Nationality'),
        _('Mother fullname'),

        _('P-Code If a child lives in a tent / Brax in a random camp'),
        _('Does the child have any disability or special need?'),
        _('Internal number'),
        _('ID number'),
        _('Comments'),

        _('What is the educational level of a person who is valuable to the child?'),
        _('Does the child participate in work?'),
        _('What is the type of work ?'),
        _('How many hours does this child work in a day?'),

        _('What is the family status of the child?'),
        _("Does the child have children?"),

        _('Arabic - Pre'),
        _('Language - Pre'),
        _('Math - Pre'),

        _('Assessment Result - Pre'),

        _('Arabic - Post'),
        _('Language - Post'),
        _('Math - Post'),

        _('Academic Result - Post'),

        _('Arabic - Improvement'),
        _('Language - Improvement'),
        _('Math - Improvement'),
        _('Academic Result - Improvement'),

        _('How was the level of child participation in the program?'),
        _('The main barriers affecting the daily attendance and performance of the child or drop out of school?'),
        _('Based on the overall score, what is the recommended learning path?'),

        _("First time registered?"),
        _("Student outreached?"),
        _("Have barcode with him?"),

        'owner',
        'modified_by',
        'created',
        'modified',
    ]

    content = []
    for line in queryset:
        if not line.student:
            continue
        student = line.student
        content = [
            line.round.name if line.round else '',
            line.governorate.name if line.governorate else '',
            line.district.name if line.district else '',
            line.location,
            line.language,

            student.first_name,
            student.father_name,
            student.last_name,
            student.sex,
            student.birthday_day,
            student.birthday_month,
            student.birthday_year,
            student.birthday,
            student.nationality.name if student.nationality else '',
            student.mother_fullname,

            student.p_code,
            line.disability.name if line.disability else '',
            line.internal_number,
            student.id_number,
            line.comments,

            line.hh_educational_level,
            line.have_labour,
            line.labours,
            line.labour_hours,

            student.family_status,
            student.have_children,

            line.get_assessment_value('arabic', 'pre_test'),
            line.get_assessment_value('foreign_language', 'pre_test'),
            line.get_assessment_value('math', 'pre_test'),

            line.pre_test_score,

            line.get_assessment_value('arabic', 'post_test'),
            line.get_assessment_value('foreign_language', 'post_test'),
            line.get_assessment_value('math', 'post_test'),

            line.post_test_score,

            line.arabic_improvement,
            line.foreign_language_improvement,
            line.math_improvement,
            line.assessment_improvement,

            line.participation,
            line.barriers,
            line.learning_result,

            line.new_registry,
            line.student_outreached,
            line.have_barcode,

            line.owner,
            line.modified_by,
            line.created,
            line.modified,
        ]
        data.append(content)

        timestamp = '{}-{}'.format('bln_registrations_list', time.time())
        file_format = base_formats.XLSX()
        data = file_format.export_data(data)
        if return_data:
            return data
        store_file(data, timestamp, params)
        return True


@app.task
def export_cbece_list(params=None, return_data=False):

    from student_registration.clm.models import CBECE

    queryset = CBECE.objects.all()
    if 'partner' in params and params['partner']:
        queryset = queryset.filter(partner_id=int(params['partner']))

    data = tablib.Dataset()

    data.headers = [
        _('CLM round'),
        _('Cycle'),
        _('Program site'),
        _('Attending in school'),
        _('Governorate'),
        _('District'),
        _('Location'),
        _('The language supported in the program'),

        _('Where was the child referred?'),
        _('First name'),
        _('Father name'),
        _('Last name'),
        _('Sex'),
        _('Birthday day'),
        _('Birthday month'),
        _('Birthday year'),
        _('Birthday'),
        _('Nationality'),
        _('Mother fullname'),

        _('P-Code If a child lives in a tent / Brax in a random camp'),
        _('Does the child have any disability or special need?'),
        _('Internal number'),
        _('ID number'),
        _('Comments'),
        _('Child MUAC'),

        _('What is the educational level of a person who is valuable to the child?'),
        _('Does the child participate in work?'),
        _('What is the type of work ?'),
        _('How many hours does this child work in a day?'),

        _('Language Art Domain - Pre'),
        _('Cognitive Domain - Pre'),
        _('Science Domain - Pre'),
        _('Social Emotional Domain - Pre'),
        _('Psychomotor Domain - Pre'),
        _('Artistic Domain - Pre'),

        _('Academic Result - Pre'),

        _('Language Art Domain - Post'),
        _('Cognitive Domain - Post'),
        _('Science Domain - Post'),
        _('Social Emotional Domain - Post'),
        _('Psychomotor Domain - Post'),
        _('Artistic Domain - Post'),

        _('Academic Result - Post'),

        _('Language Art Domain - Improvement'),
        _('Cognitive Domain - Improvement'),
        _('Science Domain - Improvement'),
        _('Social Emotional Domain - Improvement'),
        _('Psychomotor Domain - Improvement'),
        _('Artistic Domain - Improvement'),

        _('Academic Result - Improvement'),

        _('How was the level of child participation in the program?'),
        _('The main barriers affecting the daily attendance and performance of the child or drop out of school?'),
        _('Based on the overall score, what is the recommended learning path?'),

        _("First time registered?"),
        _("Student outreached?"),
        _("Have barcode with him?"),

        'owner',
        'modified_by',
        'created',
        'modified',
    ]

    content = []
    for line in queryset:
        if not line.student:
            continue
        student = line.student
        content = [
            line.round.name if line.round else '',
            line.cycle.name if line.cycle else '',
            line.site,
            line.school.name if line.school else '',
            line.governorate.name if line.governorate else '',
            line.district.name if line.district else '',
            line.location,
            line.language,

            line.referral,
            student.first_name,
            student.father_name,
            student.last_name,
            student.sex,
            student.birthday_day,
            student.birthday_month,
            student.birthday_year,
            student.birthday,
            student.nationality.name if student.nationality else '',
            student.mother_fullname,

            student.p_code,
            line.disability.name if line.disability else '',
            line.internal_number,
            student.id_number,
            line.comments,
            line.child_muac,

            line.hh_educational_level,
            line.have_labour,
            line.labours,
            line.labour_hours,

            line.get_assessment_value('LanguageArtDomain', 'pre_test'),
            line.get_assessment_value('CognitiveDomian', 'pre_test'),
            line.get_assessment_value('ScienceDomain', 'pre_test'),
            line.get_assessment_value('SocialEmotionalDomain', 'pre_test'),
            line.get_assessment_value('PsychomotorDomain', 'pre_test'),
            line.get_assessment_value('ArtisticDomain', 'pre_test'),

            line.pre_test_score,

            line.get_assessment_value('LanguageArtDomain', 'post_test'),
            line.get_assessment_value('CognitiveDomian', 'post_test'),
            line.get_assessment_value('ScienceDomain', 'post_test'),
            line.get_assessment_value('SocialEmotionalDomain', 'post_test'),
            line.get_assessment_value('PsychomotorDomain', 'post_test'),
            line.get_assessment_value('ArtisticDomain', 'post_test'),

            line.post_test_score,

            line.art_improvement,
            line.cognitive_improvement,
            line.science_improvement,
            line.social_improvement,
            line.psycho_improvement,
            line.artistic_improvement,

            line.assessment_improvement,

            line.participation,
            line.barriers,
            line.learning_result,

            line.new_registry,
            line.student_outreached,
            line.have_barcode,

            line.owner,
            line.modified_by,
            line.created,
            line.modified,
        ]
        data.append(content)

    timestamp = '{}-{}'.format('cbece_registrations_list', time.time())
    file_format = base_formats.XLSX()
    data = file_format.export_data(data)
    if return_data:
        return data
    store_file(data, timestamp, params)
    return True


@app.task
def export_bln_list(params=None, return_data=False):

    from student_registration.clm.models import RS

    queryset = RS.objects.all()
    if 'partner' in params and params['partner']:
        queryset = queryset.filter(partner_id=int(params['partner']))

    data = tablib.Dataset()

    data.headers = [
        _('CLM round'),
        _('Program type'),
        _('Program site'),
        _('Attending in school'),
        _('Governorate'),
        _('District'),
        _('Location'),
        _('The language supported in the program'),

        _('First name'),
        _('Father name'),
        _('Last name'),
        _('Sex'),
        _('Birthday day'),
        _('Birthday month'),
        _('Birthday year'),
        _('Birthday'),
        _('Nationality'),
        _('Mother fullname'),

        _('P-Code If a child lives in a tent / Brax in a random camp'),
        _('Does the child have any disability or special need?'),
        _('Internal number'),
        _('ID number'),
        _('Comments'),

        _('What is the educational level of a person who is valuable to the child?'),
        _('Does the child participate in work?'),
        _('What is the type of work ?'),
        _('How many hours does this child work in a day?'),

        _('What is the family status of the child?'),
        _("Does the child have children?"),

        _('Registered in school'),
        _('Shift'),
        _('Class'),
        _('Reason of referral'),

        _('Arabic reading - Pre-test'),
        _('Arabic reading - Post-test'),
        _('Arabic reading - Improvement'),

        _('Arabic - Pre'),
        _('Language - Pre'),
        _('Science - Pre'),
        _('Math - Pre'),

        _('Assessment Result - Pre'),

        _('Arabic - Post'),
        _('Language - Post'),
        _('Science - Post'),
        _('Math - Post'),

        _('Assessment Result - Post'),
        _('Arabic - Improvement'),
        _('Language - Improvement'),
        _('Science - Improvement'),
        _('Math - Improvement'),
        _('Assessment Result - Improvement'),

        _('Strategy Evaluation Result - Pre'),
        _('Strategy Evaluation Result - Post'),
        _('Strategy Evaluation Result - Improvement'),

        _('Motivation - Pre'),
        _('Motivation - Post'),
        _('Motivation - Improvement'),

        _('Self Assessment - Pre'),
        _('Self Assessment - Post'),
        _('Self Assessment - Improvement'),

        _('How was the level of child participation in the program?'),
        _('The main barriers affecting the daily attendance and performance of the child or drop out of school?'),
        _('Based on the overall score, what is the recommended learning path?'),

        _("First time registered?"),

        'owner',
        'modified_by',
        'created',
        'modified',

    ]

    content = []
    for line in queryset:
        if not line.student:
            continue
        student = line.student
        content = [
            line.round.name if line.round else '',
            line.type,
            line.site,
            line.school.name if line.school else '',
            line.governorate.name if line.governorate else '',
            line.district.name if line.district else '',
            line.location,
            line.language,

            student.first_name,
            student.father_name,
            student.last_name,
            student.sex,
            student.birthday_day,
            student.birthday_month,
            student.birthday_year,
            student.birthday,
            student.nationality.name if student.nationality else '',
            student.mother_fullname,

            student.p_code,
            line.disability.name if line.disability else '',
            line.internal_number,
            student.id_number,
            line.comments,

            line.hh_educational_level,
            line.have_labour,
            line.labours,
            line.labour_hours,

            student.family_status,
            student.have_children,

            line.registered_in_school.name if line.registered_in_school else '',
            line.shift,
            line.grade.name if line.grade else '',
            line.referral,

            line.pre_reading_score,
            line.post_reading_score,
            line.arabic_reading_improvement,

            line.pre_test_arabic,
            line.pre_test_language,
            line.pre_test_math,
            line.pre_test_science,

            line.pretest_result,

            line.post_test_arabic,
            line.post_test_language,
            line.post_test_math,
            line.post_test_science,

            line.posttest_result,

            line.arabic_improvement,
            line.language_improvement,
            line.science_improvement,
            line.math_improvement,
            line.academic_test_improvement,

            line.pre_test_score,
            line.post_test_score,
            line.assessment_improvement,
            line.pre_motivation_score,
            line.post_motivation_score,
            line.motivation_improvement,
            line.pre_self_assessment_score,
            line.post_self_assessment_score,
            line.self_assessment_improvement,

            line.participation,
            line.barriers,
            line.learning_result,

            line.new_registry,

            line.owner,
            line.modified_by,
            line.created,
            line.modified,
        ]
        data.append(content)

    timestamp = '{}-{}'.format('rs_registrations_list', time.time())
    file_format = base_formats.XLSX()
    data = file_format.export_data(data)
    if return_data:
        return data
    store_file(data, timestamp, params)
    return True
