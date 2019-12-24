from __future__ import unicode_literals
from model_utils.models import TimeStampedModel
from django.db import models

import datetime
from django.db import models
from django.conf import settings
from django.utils.translation import ugettext as _
from model_utils import Choices
from student_registration.staffs.models import Staffs
from student_registration.schools.models import (
    School,
    ClassRoom,
    Section,
    EducationYear,
)
from student_registration.students.models import Student
# Create your models here.


class Jobs(models.Model):
    name = models.CharField(max_length=45, unique=True, verbose_name=_('Job description'), null=False, default=' ')
    hourrate = models.IntegerField(
        blank=True,
        null=True,
        verbose_name=_('Hour Rate')
    )
    maxhoursperweek = models.IntegerField(blank=True, null=True, verbose_name=_('Max.Hours per week'), )

    class Meta:
        ordering = ['id']
        verbose_name_plural = 'Jobs'

    def __unicode__(self):
        return self.name


class Subjects(models.Model):
    name = models.CharField(max_length=45, unique=True)

    class Meta:
        ordering = ['id']
        verbose_name_plural = 'Subjects'

    def __unicode__(self):
        return self.name


class StaffEnroll(TimeStampedModel):
    EDUCATION_YEARS = list((str(x - 1) + '/' + str(x), str(x - 1) + '/' + str(x)) for x in range(2001, 2050))
    EDUCATION_YEARS.append(('na', 'N/A'))
    SCHOOL_SHIFT = Choices(
        ('na', 'n/a'),
        ('first', _('First shift')),
        ('second', _('Second shift')),
        ('alp', _('ALP')),
    )
    SHIFT = Choices(
        ('D', _('Day')),
        ('N', _('Night')),
    )
    CURRENT_YEAR = datetime.datetime.now().year
    YEARS = ((str(x), x) for x in range(2016, CURRENT_YEAR))
    staff = models.ForeignKey(
        Staffs,
        blank=False, null=True,
        related_name='staff_enrollment',
    )
    job = models.ForeignKey(
        Jobs,
        blank=True, null=True,
        verbose_name=_('Jobs')
    )
    joineddate = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        choices=EDUCATION_YEARS
    )
    school = models.ForeignKey(
        School,
        blank=False, null=True,
        related_name='school',
        verbose_name=_('School')
     )
    section = models.ForeignKey(
        Section,
        blank=True, null=True,
        related_name='+',
        verbose_name=_('Current Section')
    )
    classroom = models.ForeignKey(
        ClassRoom,
        blank=True, null=True,
        related_name='+',
        verbose_name=_('Current Class')
    )
    subject = models.ForeignKey(
        Subjects,
        blank=True, null=True,
        related_name='+',
        verbose_name=_('Subjects')
    )
    education_year = models.ForeignKey(
        EducationYear,
        blank=True, null=True,
        related_name='+',
        verbose_name=_('Education year')
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        blank=False, null=True,
        related_name='+',
        verbose_name=_('Created by')
    )
    deleted = models.BooleanField(
         blank=True, default=False,
         verbose_name=_('deleted')
    )
    weeklyhours = models.IntegerField(
        default=0,
        verbose_name=_('Weekly Nb of hours'),
    )
    current_hourrate = models.IntegerField(
        blank=True,
        null=True,
        verbose_name=_('Hour Rate')
    )
    shift = models.CharField(
        max_length=1,
        blank=True,
        null=True,
        choices=SHIFT
    )
    school_ispublic = models.BooleanField(
        blank=True, default=False,
        verbose_name=_('is public')
    )
    work = models.CharField(
        blank=True, max_length=150, verbose_name=_('main work')
    )
    @property
    def cycle(self):
        if self.classroom_id in [2, 3, 4]:
            return 'Cycle 1'
        if self.classroom_id in [5, 6, 7]:
            return 'Cycle 2'
        if self.classroom_id in [8, 9, 10]:
            return 'Cycle 3'
        if self.classroom_id == 1:
            return 'KG'
        return ''

    class Meta:
        ordering = ['-student__first_name']

    def __unicode__(self):
        if self.student:
            return self.student.__unicode__()
        return str(self.id)
