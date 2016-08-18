from __future__ import unicode_literals, absolute_import, division

from django.db import models
from model_utils import Choices
from model_utils.models import TimeStampedModel
from django.conf import settings
from student_registration.students.models import (
    Student,
)
from student_registration.schools.models import (
    School,
    ClassRoom,
    Section,
    Grade,
)


class Registration(TimeStampedModel):
    student = models.ForeignKey(
        Student,
        blank=False, null=True,
        related_name='+',
    )
    school = models.ForeignKey(
        School,
        blank=False, null=True,
        related_name='+',
    )
    section = models.ForeignKey(
        Section,
        blank=False, null=True,
        related_name='+',
    )
    grade = models.ForeignKey(
        Grade,
        blank=False, null=True,
        related_name='+',
    )
    classroom = models.ForeignKey(
        ClassRoom,
        blank=False, null=True,
        related_name='+'
    )
    year = models.CharField(
        max_length=4,
        blank=True,
        null=True,
        choices=((str(x), x) for x in range(2016, 2051))
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        blank=False, null=True,
        related_name='+',
    )

    @property
    def student_fullname(self):
        if self.student:
            return self.student.full_name
        return ''

    def __unicode__(self):
        return self.student_fullname
