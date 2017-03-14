__author__ = 'achamseddine'

import json
import os

from datetime import datetime
from django.db.models import Q
from student_registration.taskapp.celery import app
from student_registration.registrations.utils import get_unhcr_individuals
from student_registration.students.utils import generate_id


@app.task
def synchronize_child_age():
    from student_registration.registrations.models import RegisteringAdult
    from student_registration.students.models import Student

    adults = RegisteringAdult.objects.filter(id_type_id=1)
    for adlt in adults:
        # print adlt.id_number
        individuals = get_unhcr_individuals(adlt.id_number)
        # print individuals
        for indiv in individuals:
            try:
                child = Student.objects.get(id_number=indiv['IndividualID'])
                print indiv["DOB"]
                dob = datetime.strptime(indiv["DOB"], '%Y-%m-%dT%H:%M:%S')
                child.birthday_day = dob.day
                child.birthday_month = dob.month
                child.birthday_year = dob.year
                child.save()
                print child.id
            except Exception as ex:
                print ex.message
                continue


@app.task
def generate_adult_unique_number():
    from student_registration.registrations.models import RegisteringAdult

    adults = RegisteringAdult.objects.all()
    for adult in adults:
        try:
            adult.number = generate_id(adult.first_name, adult.father_name, adult.last_name,
                                       adult.mother_fullname, adult.sex,
                                       adult.birthday_day, adult.birthday_month, adult.birthday_year)
            print adult.number, adult.id
            adult.save()
        except Exception as ex:
            print ex.message
            continue


@app.task
def generate_child_unique_number():
    from student_registration.registrations.models import Registration

    registrations = Registration.objects.all()
    for registry in registrations:
        try:
            student = registry.student
            student.number = generate_id(student.first_name, student.father_name, student.last_name,
                                         student.mother_fullname, student.sex,
                                         student.birthday_day, student.birthday_month, student.birthday_year)

            student.number_part1 = generate_id(student.first_name, student.father_name, student.last_name,
                                               student.mother_fullname, student.sex,
                                               '', '', '')

            student.number_part2 = generate_id(student.first_name, student.father_name, student.last_name,
                                               '', '',
                                               student.birthday_day, student.birthday_month, student.birthday_year)
            print student.number, student.id
            student.save()
        except Exception as ex:
            print ex.message
            continue


@app.task
def generate_2ndshift_unique_number(offset=0):
    from student_registration.enrollments.models import Enrollment
    limit = offset + 50000
    registrations = Enrollment.objects.all()[offset:limit]
    for registry in registrations:
        student = registry.student
        try:
            student.number = generate_id(student.first_name, student.father_name, student.last_name,
                                         student.mother_fullname, student.sex,
                                         student.birthday_day, student.birthday_month, student.birthday_year)

            student.number_part1 = generate_id(student.first_name, student.father_name, student.last_name,
                                               student.mother_fullname, student.sex,
                                               '', '', '')

            student.number_part2 = generate_id(student.first_name, student.father_name, student.last_name,
                                               '', '',
                                               student.birthday_day, student.birthday_month, student.birthday_year)
            print student.number, student.id
            student.save()
        except Exception as ex:
            print ex.message
            continue


@app.task
def generate_alp_unique_number():
    from student_registration.alp.models import Outreach

    registrations = Outreach.objects.all()
    for registry in registrations:
        student = registry.student
        try:
            student.number = generate_id(student.first_name, student.father_name, student.last_name,
                                         student.mother_fullname, student.sex,
                                         student.birthday_day, student.birthday_month, student.birthday_year)

            student.number_part1 = generate_id(student.first_name, student.father_name, student.last_name,
                                               student.mother_fullname, student.sex,
                                               '', '', '')

            student.number_part2 = generate_id(student.first_name, student.father_name, student.last_name,
                                               '', '',
                                               student.birthday_day, student.birthday_month, student.birthday_year)
            print student.number, student.id
            student.save()
        except Exception as ex:
            print ex.message
            continue


@app.task
def disable_duplicate_enrolments(offset=None, school_number=None):
    from student_registration.enrollments.models import Enrollment
    registrations = []
    queryset = Enrollment.objects.exclude(deleted=True).exclude(dropout_status=True)
    if offset:
        limit = offset + 50000
        registrations = queryset.order_by('-id', 'student__number', 'school__number')[offset:limit]
    elif school_number:
        registrations = queryset.filter(school__number=school_number).order_by('-id', 'student__number', 'school__number')
    print len(registrations)

    students = {}
    students2 = {}
    duplicates = []

    print "Start find duplicates"
    for registry in registrations:
        student = registry.student
        if student.number not in students:
            students[student.number] = registry
        else:
            duplicates.append(registry)

        if student.number_part1:
            if student.number_part1 not in students2:
                students2[student.number_part1] = registry
            else:
                duplicates.append(registry)

    print "End find duplicates"

    print "duplicates: ", len(duplicates)

    print "Start disable duplicates"

    for registry in duplicates:
        registry.deleted = True
        registry.save()

    print "End disable duplicates"


@app.task
def disable_duplicate_outreaches(school_number=None):
    from student_registration.alp.models import Outreach, ALPRound
    alp_round = ALPRound.objects.get(current_round=True)
    registrations = Outreach.objects.exclude(deleted=True).filter(alp_round=alp_round).order_by('-id')
    if school_number:
        print school_number
        registrations = registrations.filter(school__number=school_number)

    print len(registrations)

    students = {}
    students2 = {}
    duplicates = []

    print "Start find duplicates"
    for registry in registrations:

        student = registry.student
        if student.number not in students:
            students[student.number] = registry
        else:
            duplicates.append(registry)

        if student.number_part1 not in students2:
            students2[student.number_part1] = registry
        else:
            duplicates.append(registry)

    print "End find duplicates"

    print "duplicates: ", len(duplicates)

    print "Start disable duplicates"

    for registry in duplicates:
        registry.deleted = True
        registry.save()

    print "End disable duplicates"


@app.task
def find_matching():
    from student_registration.registrations.models import Registration
    from student_registration.enrollments.models import Enrollment
    from student_registration.students.models import StudentMatching

    offset = 54000
    limit = offset + 2000
    registrations = Registration.objects.all().order_by('id')[offset:limit]
    for registry in registrations:
        enrollment = None
        r_student = registry.student
        if not r_student:
            continue
        try:
            queryset = Enrollment.objects.exclude(deleted=True).exclude(dropout_status=True)
            if r_student.id_number:
                id_number_1 = r_student.id_number.replace("-", "")
                id_number_2 = id_number_1.replace("C", "c")
                id_number_3 = id_number_1.replace("c", "C")
                id_number_4 = r_student.id_number.replace("C", "c")
                id_number_5 = r_student.id_number.replace("c", "C")
                enrollment = queryset.get(
                    Q(student__number=r_student.number) |
                    Q(student__number_part1=r_student.number_part1) |
                    Q(student__id_number=r_student.id_number) |
                    Q(student__id_number=id_number_1) |
                    Q(student__id_number=id_number_2) |
                    Q(student__id_number=id_number_3) |
                    Q(student__id_number=id_number_4) |
                    Q(student__id_number=id_number_5)
                )
            else:
                enrollment = queryset.get(
                    Q(student__number=r_student.number) |
                    Q(student__number_part1=r_student.number_part1) |
                    Q(student__number_part2=r_student.number_part2)
                )
        except Exception as ex:
            # print registry.id
            continue

        if enrollment:
            e_student = enrollment.student
            StudentMatching.objects.get_or_create(registry=r_student, enrolment=e_student)


@app.task
def find_matching_2():
    from student_registration.registrations.models import Registration
    from student_registration.enrollments.models import Enrollment
    from student_registration.students.models import StudentMatching

    offset = 0
    limit = offset + 2000
    registrations = Enrollment.objects.exclude(deleted=True).exclude(dropout_status=True).filter(
        school__location__parent_id__in=[1,5]
    ).order_by('id')  #[offset:limit]

    print len(registrations)

    for registry in registrations:
        enrollment = None
        r_student = registry.student
        if not r_student:
            continue
        try:
            if r_student.id_number:
                id_number_1 = r_student.id_number.replace("-", "")
                id_number_2 = id_number_1.replace("C", "c")
                id_number_3 = id_number_1.replace("c", "C")
                id_number_4 = r_student.id_number.replace("C", "c")
                id_number_5 = r_student.id_number.replace("c", "C")
                id_number_6 = r_student.id_number.replace("ID", "")
                id_number_6 = id_number_6.replace(":", "")
                id_number_6 = id_number_6.replace("LEB", "")
                enrollment = Registration.objects.get(
                    Q(student__number=r_student.number) |
                    Q(student__number_part1=r_student.number_part1) |
                    Q(student__id_number=r_student.id_number) |
                    Q(student__id_number=id_number_1) |
                    Q(student__id_number=id_number_2) |
                    Q(student__id_number=id_number_3) |
                    Q(student__id_number=id_number_4) |
                    Q(student__id_number=id_number_5) |
                    Q(student__id_number=id_number_6)
                )
            else:
                enrollment = Registration.objects.get(
                    Q(student__number=r_student.number) |
                    Q(student__number_part1=r_student.number_part1) |
                    Q(student__number_part2=r_student.number_part2)
                )
        except Exception as ex:
            print ex.message
            # print registry.id
            continue

        if enrollment:
            e_student = enrollment.student
            StudentMatching.objects.get_or_create(registry=e_student, enrolment=r_student)
