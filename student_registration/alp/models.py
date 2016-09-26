from __future__ import unicode_literals, absolute_import, division

from django.db import models
from model_utils import Choices
from django.utils.translation import ugettext as _
from model_utils.models import TimeStampedModel
from django.conf import settings
from django.contrib.postgres.fields import JSONField
from student_registration.students.models import (
    Person,
    Student,
    Language,
)
from student_registration.schools.models import (
    School,
    EducationLevel,
    ClassLevel,
    PartnerOrganization,
    ClassRoom,
    Section,
    Grade
)
from student_registration.locations.models import Location
from student_registration.eav.registry import Registry as eav


class Outreach(TimeStampedModel):

    EAV_TYPE = 'outreach'

    student = models.ForeignKey(
        Student,
        blank=False, null=True,
        related_name='+',
    )
    partner = models.ForeignKey(
        PartnerOrganization,
        blank=False, null=True,
        related_name='+',
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        blank=False, null=True,
        related_name='+',
    )
    school = models.ForeignKey(
        School,
        blank=False, null=True,
        related_name='+',
    )
    location = models.ForeignKey(
        Location,
        blank=False, null=True,
        related_name='+',
    )
    preferred_language = models.ForeignKey(
        Language,
        blank=True, null=True,
        related_name='+',
    )
    last_education_level = models.ForeignKey(
        EducationLevel,
        blank=False, null=True,
    )
    last_class_level = models.ForeignKey(
        ClassLevel,
        blank=False, null=True,
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
        choices=((str(x), x) for x in range(1990, 2051))
    )
    exam_month = models.CharField(
        max_length=2,
        blank=True,
        null=True,
        choices=Person.MONTHS
    )
    exam_day = models.CharField(
        max_length=2,
        blank=True,
        null=True,
        choices=((str(x), x) for x in range(1, 33))
    )
    extra_fields = JSONField(
        blank=True,
        null=True,
    )

    class Meta:
        ordering = ['id']

    @property
    def student_fullname(self):
        if self.student:
            return self.student.full_name
        return ''

    @property
    def student_mother_fullname(self):
        if self.student:
            return self.student.mother_fullname
        return ''

    def __unicode__(self):
        return self.student_fullname


class ExtraColumn(TimeStampedModel):
    name = models.CharField(max_length=64L, blank=True, null=True)
    label = models.CharField(max_length=64L, blank=True, null=True)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        blank=False, null=True,
        related_name='+',
    )

eav.register(Outreach)
