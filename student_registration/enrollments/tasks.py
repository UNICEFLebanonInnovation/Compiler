__author__ = 'achamseddine'

import json
import os

from datetime import datetime
from django.db.models import Q
from student_registration.taskapp.celery import app


@app.task
def assign_section(section):
    from student_registration.enrollments.models import Enrollment
    from student_registration.schools.models import Section
    registrations = Enrollment.objects.exclude(deleted=True).filter(section__isnull=True)
    section = Section.objects.get(id=section)

    print len(registrations), " registration found"
    print "Start assignment"

    for registry in registrations:
        registry.section = section
        registry.save()

    print "End assignment"
