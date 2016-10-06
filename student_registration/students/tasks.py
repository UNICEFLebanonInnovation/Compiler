__author__ = 'achamseddine'

import json
import os

from datetime import datetime
from student_registration.taskapp.celery import app
from student_registration.registrations.utils import get_unhcr_individuals


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

