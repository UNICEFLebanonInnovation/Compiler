__author__ = 'achamseddine'

import json
import os

from datetime import datetime
from student_registration.taskapp.celery import app


@app.task
def assign_alp_level():
    from student_registration.alp.models import Outreach, ALPRound
    from student_registration.schools.models import EducationLevel
    alp_round = ALPRound.objects.get(current_pre_test=True)

    records = Outreach.objects.filter(alp_round=alp_round)
    for record in records:
        try:
            level = record.level
            to_level = 0
            if not level:
                continue
            if level.id == 1 or level.id == 2 or level.id == 3:
                total = record.exam_total
                if total <= 40:
                    to_level = 1
                elif total > 40 and total <= 80:
                    to_level = 2
                elif total > 80 and total <= 120:
                    to_level = 3

            if level.id == 4 or level.id == 5 or level == 6:
                total = record.exam_total
                if total <= 20:
                    to_level = 1
                elif total > 20 and total <= 40:
                    to_level = 2
                elif total > 40 and total <= 60:
                    to_level = 3
                elif total > 60 and total <= 100:
                    to_level = 4
                elif total > 100 and total <= 140:
                    to_level = 5
                elif total > 140 and total <= 180:
                    to_level = 6

            if level.id == 7 or level.id == 8 or level.id == 9:
                total = record.exam_total
                if total <= 20:
                    to_level = 1
                elif total > 20 and total <= 40:
                    to_level = 2
                elif total > 40 and total <= 60:
                    to_level = 3
                elif total > 60 and total <= 80:
                    to_level = 4
                elif total > 80 and total <= 100:
                    to_level = 5
                elif total > 100 and total <= 120:
                    to_level = 6
                elif total > 120 and total <= 160:
                    to_level = 7
                elif total > 160 and total <= 200:
                    to_level = 8
                elif total > 200 and total <= 240:
                    to_level = 9

            if to_level:
                print level.id, total, to_level
                record.assigned_to_level = EducationLevel.objects.get(id=to_level)
                record.save()
        except Exception as ex:
            print ex.message
            continue


@app.task
def auto_refer_to_alp_level():
    from student_registration.alp.utils import refer_to_level
    from student_registration.alp.models import Outreach, ALPRound
    alp_round = ALPRound.objects.get(current_post_test=True)

    records = Outreach.objects.filter(alp_round=alp_round)

    for record in records:
        try:
            record.refer_to_level = refer_to_level(
                record.student.age,
                record.registered_in_level,
                record.post_exam_total
            )
            record.save()
        except Exception as ex:
            print ex.message
            continue


@app.task
def assign_section(section):
    from student_registration.alp.models import Outreach, ALPRound
    from student_registration.schools.models import Section
    alp_round = ALPRound.objects.get(current_round=True)

    registrations = Outreach.objects.exclude(deleted=True).filter(
        registered_in_level__isnull=False,
        section__isnull=True,
        alp_round=alp_round
    )
    section = Section.objects.get(id=section)

    print len(registrations), " ALP registrations found"
    print "Start assignment"

    for registry in registrations:
        registry.section = section
        registry.save()

    print "End assignment"


@app.task
def assign_round(round_id):
    from student_registration.alp.models import Outreach

    registrations = Outreach.objects.exclude(deleted=True).filter(alp_round__isnull=True).update(alp_round_id=round_id)
    print registrations

    print "End assignment"


@app.task
def assign_round_to_deleted(round_id):
    from student_registration.alp.models import Outreach

    registrations = Outreach.objects.filter(deleted=True, alp_round__isnull=True, id__lt=13724).update(alp_round_id=round_id)
    print registrations

    print "End assignment"


def fix_round_assignment(update):
    from student_registration.alp.models import Outreach

    registrations = Outreach.objects.filter(
        owner__username__contains='caritas',
        alp_round__id__exact=3,
        level__isnull=True,
        assigned_to_level__isnull=True,
        registered_in_level__isnull=True,
        id__gt=14163
    )

    print len(registrations), " records to assign"

    if update == 1:
        total = registrations.update(alp_round_id=4)
        print total, " records assigned"

    print "End assignment"
