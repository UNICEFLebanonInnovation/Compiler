from __future__ import unicode_literals, absolute_import, division

from django.db import models
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _
from model_utils import Choices
from model_utils.models import TimeStampedModel
from django.conf import settings
from student_registration.students.models import (
    Student,
)
from student_registration.registrations.models import (
    RegisteringAdult,
)


class ServiceType(models.Model):
    name = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        ordering = ['id']
        verbose_name = 'Service Type'

    def __unicode__(self):
        return self.name


class MainReason(models.Model):
    name = models.CharField(max_length=64L, unique=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Main Reason'

    def __unicode__(self):
        return self.name


class SpecificReason(models.Model):
    name = models.CharField(max_length=254L)
    main_reason = models.ForeignKey(MainReason, verbose_name='Main Reason')

    class Meta:
        ordering = ['name']
        verbose_name = 'Specific Reason'

    def __unicode__(self):
        return self.name


class HouseholdVisit(TimeStampedModel):

    registering_adult = models.ForeignKey(
        RegisteringAdult,
        blank=True, null=True,
        related_name='+',
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        blank=False, null=True,
        related_name='+',
    )

    class Meta:
        ordering = ['id']

    def __unicode__(self):
        return self.RegisteringAdult.full_name


class HouseholdVisitStatus(models.Model):
    household_visit = models.ForeignKey(
        HouseholdVisit,
        blank=False, null=True,
        related_name='+',
    )
    household_found = models.BooleanField(blank=True, default=True)
    comment = models.CharField(max_length=255, blank=True, null=True)
    date = models.DateTimeField()

    class Meta:
        ordering = ['id']

    def __unicode__(self):
        return self.comment


class ChildVisit(TimeStampedModel):

    household_visit = models.ForeignKey(
        HouseholdVisit,
        blank=False, null=True,
        related_name='+',
    )
    student = models.ForeignKey(
        Student,
        blank=False, null=True,
        related_name='+',
    )
    main_reason = models.ForeignKey(
        MainReason,
        blank=False, null=True,
        related_name='+',
    )
    specific_reason = models.ForeignKey(
        SpecificReason,
        blank=False, null=True,
        related_name='+',
    )
    service_provider = models.CharField(max_length=255, blank=True, null=True)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        blank=False, null=True,
        related_name='+',
    )

    class Meta:
        ordering = ['id']

    def __unicode__(self):
        return self.Student.full_name


class ChildService(models.Model):

    child_visit = models.ForeignKey(
        ChildVisit,
        blank=False, null=True,
        related_name='+',
    )
    service_type = models.ForeignKey(
        ServiceType,
        blank=False, null=True,
        related_name='+',
    )

    class Meta:
        ordering = ['id']

    def __unicode__(self):
        return self.ServiceType.name

class HouseholdVisitView(models.Model):
    id = models.BigIntegerField(primary_key=True)
    full_name = models.CharField(max_length=255, blank=True, null=True)

class Meta:
    managed = False
    db_table = 'vw_HouseholdVisit'
