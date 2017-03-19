from __future__ import unicode_literals, absolute_import, division

from django.db import models
from model_utils import Choices
from model_utils.models import TimeStampedModel
from django.utils.translation import ugettext as _
from django.conf import settings
from student_registration.students.models import (
    Student,
)
from student_registration.schools.models import (
    School,
    ClassRoom,
    EducationLevel,
)


class Attendance(TimeStampedModel):

    REASON = Choices(
        ('sick', _('Sick')),
        ('no_reason', _('No reason')),
        ('no_transport', _('No transport')),
        ('other', _('Other')),
    )

    student = models.ForeignKey(
        Student,
        blank=False, null=True,
        related_name='attendances',
    )
    school = models.ForeignKey(
        School,
        blank=False, null=True,
        related_name='+',
    )
    classroom = models.ForeignKey(
        ClassRoom,
        blank=True, null=True,
        related_name='+'
    )
    classlevel = models.ForeignKey(
        EducationLevel,
        blank=True, null=True,
        related_name='+'
    )
    status = models.BooleanField(default=False)
    attendance_date = models.DateField(blank=True, null=True)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        blank=True, null=True,
        related_name='+',
    )
    validation_status = models.BooleanField(default=False)
    validation_date = models.DateField(blank=True, null=True)
    validation_owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        blank=True, null=True,
        related_name='+',
    )
    absence_reason = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        choices=REASON
    )

    @property
    def student_fullname(self):
        if self.student:
            return self.student.full_name
        return ''

    @property
    def student_gender(self):
        return self.student.sex

    def __unicode__(self):
        return self.student_fullname


class BySchoolByDay(models.Model):

    school = models.ForeignKey(
        School,
        related_name='+',
    )
    attendance_date = models.DateField()
    highest_attendance_rate = models.BooleanField(default=False)
    total_enrolled = models.IntegerField(blank=True, null=True)
    total_attended = models.IntegerField(blank=True, null=True)
    total_absences = models.IntegerField(blank=True, null=True)
    total_attended_male = models.IntegerField(blank=True, null=True)
    total_attended_female = models.IntegerField(blank=True, null=True)
    total_absent_male = models.IntegerField(blank=True, null=True)
    total_absent_female = models.IntegerField(blank=True, null=True)
    validation_date = models.DateField(blank=True, null=True)
    validation_status = models.BooleanField(default=False)


class Absentee(TimeStampedModel):

    school = models.ForeignKey(
        School,
        related_name='+',
    )
    student = models.ForeignKey(
        Student,
        related_name='absents',
    )
    last_attendance_date = models.DateField(blank=True, null=True)
    #last_absent_date = models.DateField(blank=True, null=True)
    absent_days = models.IntegerField(blank=True, null=True)
    reattend_date = models.DateField(blank=True, null=True)
    validation_status = models.BooleanField(default=False)
    dropout_status = models.BooleanField(default=False)

    def student_number(self):
        return self.student.number

