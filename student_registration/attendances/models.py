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
        blank=False, null=True,
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

    def __unicode__(self):
        return self.student_fullname
