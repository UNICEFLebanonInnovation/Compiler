__author__ = 'achamseddine'

import json
import os

from datetime import datetime
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
                                       adult.mother_fullname, adult.sex)
            print adult.number, adult.id
            adult.save()
        except Exception as ex:
            print ex.message
            continue


@app.task
def generate_child_unique_number():
    from student_registration.students.models import Student

    students = Student.objects.all()
    for student in students:
        try:
            student.number = generate_id(student.first_name, student.father_name, student.last_name,
                                         student.mother_fullname, student.sex)
            print student.number, student.id
            student.save()
        except Exception as ex:
            print ex.message
            continue
