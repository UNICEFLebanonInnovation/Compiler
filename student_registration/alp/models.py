from __future__ import unicode_literals, absolute_import, division

from django.db import models
from model_utils import Choices

from student_registration.students.models import (
    Student,
    School,
    Language,
    EducationLevel,
    ClassLevel,
    Governorate,
    PartnerOrganization,
)


class Outreach(models.Model):
    student = models.ForeignKey(
        Student,
        blank=False, null=False,
        related_name='+',
    )
    partner = models.ForeignKey(
        PartnerOrganization,
        blank=False, null=False,
        related_name='+',
    )
    school = models.ForeignKey(
        School,
        blank=False, null=False,
        related_name='+',
    )
    governorate = models.ForeignKey(
        Governorate,
        blank=False, null=False,
        related_name='+',
    )
    preferred_language = models.ForeignKey(
        Language,
        blank=True, null=True,
        related_name='+',
    )
    last_education_level = models.ForeignKey(
        EducationLevel,
        blank=False, null=False,
    )
    last_class_level = models.ForeignKey(
        ClassLevel,
        blank=False, null=False,
        related_name='+',
    )
    last_education_year = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        choices=((str(x-1)+'/'+str(x), str(x-1)+'/'+str(x)) for x in range(2001, 2021))
    )
    average_distance = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        choices=Choices(
            u'<= 2.5km',
            u'> 2.5km',
            u'> 10km'
        )
    )
    exam_year = models.CharField(
        max_length=4,
        blank=True,
        null=True,
        choices=((str(x), x) for x in range(2016, 2051))
    )
    exam_month = models.CharField(
        max_length=2,
        blank=True,
        null=True,
        choices=((str(x), x) for x in range(1, 13))
    )
    exam_day = models.CharField(
        max_length=2,
        blank=True,
        null=True,
        choices=((str(x), x) for x in range(1, 33))
    )


