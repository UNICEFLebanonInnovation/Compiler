__author__ = 'achamseddine'

from django.db.models import Q
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
def track_student_moves():

    from student_registration.enrollments.models import Enrollment, StudentMove

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
def track_student_program_moves():

    from student_registration.alp.models import Outreach
    from student_registration.enrollments.models import Enrollment, LoggingProgramMove

    LoggingProgramMove.objects.all().delete()

    registrations = Outreach.objects.filter(alp_round__id__lte=6, registered_in_level__isnull=False).order_by('-alp_round')
    print(registrations.count())
    enrollments = Enrollment.objects.filter(education_year__id=2)
    print(enrollments.count())

    for registry in registrations:
        refer_to_level = registry.refer_to_level_id
        eligibility = True if refer_to_level in [1, 10, 11, 12, 13, 14, 15, 16, 17] else False
        student = registry.student
        matched1 = enrollments.filter(
            Q(student__number=student.number)
        ).first()
        if matched1:
            try:
                LoggingProgramMove.objects.get(student=matched1.student)
            except Exception:
                LoggingProgramMove.objects.create(
                    student=matched1.student,
                    enrollment=matched1,
                    registry=registry,
                    school_from=registry.school,
                    school_to=matched1.school,
                    eligibility=eligibility
                )

            continue

        matched2 = enrollments.filter(
            student__first_name=student.first_name,
            student__father_name=student.father_name,
            student__last_name=student.last_name,
            student__birthday_year=student.birthday_year,
            student__sex=student.sex
        ).first()
        if matched2:
            try:
                LoggingProgramMove.objects.get(student=matched2.student)
            except Exception:
                LoggingProgramMove.objects.create(
                    student=matched2.student,
                    enrollment=matched2,
                    registry=registry,
                    school_from=registry.school,
                    school_to=matched2.school,
                    eligibility=eligibility
                )

            continue

        matched3 = enrollments.filter(
            student__first_name=student.first_name,
            student__last_name=student.father_name,
            student__mother_fullname=student.mother_fullname,
            student__birthday_year=student.birthday_year,
            student__sex=student.sex
        ).first()
        if matched3:
            try:
                LoggingProgramMove.objects.get(student=matched3.student)
            except Exception:
                LoggingProgramMove.objects.create(
                    student=matched3.student,
                    enrollment=matched3,
                    registry=registry,
                    school_from=registry.school,
                    school_to=matched3.school,
                    eligibility=eligibility
                )

            continue


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


def export_student_program_moves(params=None, return_data=False):
    import tablib
    from import_export.formats import base_formats
    from student_registration.enrollments.models import LoggingProgramMove

    queryset = LoggingProgramMove.objects.all().order_by('-registry__alp_round')
    queryset2 = LoggingProgramMove.objects.all()

    data = tablib.Dataset()
    data.headers = [
        'alp_round',
        'student_first_name',
        'student_father_name',
        'student_last_name',
        'student_sex',
        'birthday',
        'nationality',
        'student_mother_fullname',
        'from school',
        'governorate',
        'district',
        'refer_to_level',
        'registered_in_level',
        'class level',
        'to school',
        'governorate',
        'district',
        'is_eligibility',
    ]

    content = []
    for line in queryset:
        # if LoggingProgramMove.objects.exclude(id=line.id).filter(student_id=line.student_id):
        #     continue
        content = [
            line.registry.alp_round.name,
            line.student.first_name,
            line.student.father_name,
            line.student.last_name,
            line.student.sex,
            line.student.birthday,
            line.student.mother_fullname,
            line.student.nationality.name,
            line.school_from,
            line.school_from.location.parent.name if line.school_from and line.school_from.location else '',
            line.school_from.location.name if line.school_from and line.school_from.location else '',
            line.registry.refer_to_level,
            line.registry.registered_in_level.name,
            line.enrollment.classroom.name,
            line.school_to,
            line.school_to.location.parent.name if line.school_to and line.school_to.location else '',
            line.school_to.location.name if line.school_to and line.school_to.location else '',
            line.eligibility
        ]
        data.append(content)

    file_format = base_formats.XLSX()
    data = file_format.export_data(data)
    return data
