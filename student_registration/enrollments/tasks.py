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

    from student_registration.enrollments.models import Enrollment
    from student_registration.enrollments.models import StudentMove

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
