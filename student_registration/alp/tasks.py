__author__ = 'achamseddine'

import json
import os

from datetime import datetime
from student_registration.taskapp.celery import app


@app.task
def assign_alp_level():
    from student_registration.alp.models import Outreach, ALPRound
    alp_round = ALPRound.objects.get(current_pre_test=True)

    records = Outreach.objects.filter(alp_round=alp_round, level__isnull=False)
    print records.count()

    for record in records:
        try:
            level = record.level
            to_level = 0
            if not level:
                continue

            total = record.exam_total

            if 40 < total <= 80:
                # notes = [record.exam_result_arabic, record.exam_result_language, record.exam_result_math, record.exam_result_science]
                notes = [record.exam_result_language, record.exam_result_math, record.exam_result_science]
                if sum(i < 10 for i in notes) >= 2:
                    to_level = 12
                    print level.id, total, to_level
                    record.assigned_to_level_id = to_level
                    record.save()
                    continue

            if level.id == 1 or level.id == 2 or level.id == 3:
                if total <= 5:
                    to_level = 10
                elif 5 < total <= 20:
                    to_level = 11
                elif 20 < total <= 40:
                    to_level = 12
                elif 40 < total <= 80:
                    to_level = 2
                elif 80 < total <= 120:
                    to_level = 3

            if level.id == 4 or level.id == 5 or level == 6:
                if total <= 5:
                    to_level = 10
                elif 5 < total <= 20:
                    to_level = 11
                elif 20 < total <= 40:
                    to_level = 12
                elif 40 < total <= 80:
                    to_level = 2
                elif 80 < total <= 120:
                    to_level = 3
                elif 120 < total <= 160:
                    to_level = 4
                elif 160 < total <= 200:
                    to_level = 5
                elif 200 < total <= 240:
                    to_level = 6

            if level.id == 7 or level.id == 8 or level.id == 9:
                if total <= 5:
                    to_level = 10
                elif 5 < total <= 20:
                    to_level = 11
                elif 20 < total <= 40:
                    to_level = 12
                elif 40 < total <= 80:
                    to_level = 2
                elif 80 < total <= 120:
                    to_level = 3
                elif 120 < total <= 160:
                    to_level = 4
                elif 160 < total <= 200:
                    to_level = 5
                elif 200 < total <= 240:
                    to_level = 6
                elif 240 < total <= 280:
                    to_level = 7
                elif 280 < total <= 320:
                    to_level = 8
                elif 320 < total <= 360:
                    to_level = 9

            if to_level:
                print level.id, total, to_level
                record.assigned_to_level_id = to_level
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

    registrations = Outreach.objects.filter(
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

    registrations = Outreach.objects.filter(alp_round__isnull=True).update(alp_round_id=round_id)
    print registrations

    print "End assignment"


@app.task
def assign_round_to_deleted(round_id):
    from student_registration.alp.models import Outreach

    registrations = Outreach.objects.filter(alp_round__isnull=True, id__lt=13724).update(alp_round_id=round_id)
    print registrations

    print "End assignment"


@app.task
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


@app.task
def move_student_to_school(school_from, school_to):
    from .models import Outreach

    if not school_from or not school_to:
        return False
    print "from school: ", school_from, " to school: ", school_to
    registrations = Outreach.objects.filter(school_id=school_from)
    print registrations.count()
    registrations.update(school_id=school_to)
