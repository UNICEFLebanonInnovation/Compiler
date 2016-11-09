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

    STATUS = Choices(
        ('pending', _('Pending')),
        ('completed', _('Completed')),
    )

    registering_adult = models.ForeignKey(
        RegisteringAdult,
        blank=True, null=True,
        related_name='+',
    )

    visit_status = models.CharField(max_length=50, blank=True, null=True, choices=STATUS)

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        blank=False, null=True,
        related_name='+',
    )

    class Meta:
        ordering = ['id']

    def __unicode__(self):
        return self.RegisteringAdult.full_name

    @property
    def child_visit_count(self):
        print len(self.children_visits), " ch visit"
        print ChildVisit.objects.filter(household_visit_id=self.id)
        return len(self.children_visits)

    @property
    def visit_attempt_count(self):
        return len(self.visit_attempt)

    # @property
    # def all_visit_attempt_count(self):
    #     return HouseholdVisit.objects.filter(registering_adult_id=self.registering_adult_id).count()

    @property
    def all_visit_attempt_count(self):
        print ChildVisit.objects.filter(household_visit_id=self.id), " chhhhh"
        total = 0
        print self.registering_adult_id, " reg id"
        queryset = HouseholdVisit.objects.filter(registering_adult_id=self.registering_adult_id)
        print len(queryset), ' hhvisit'
        for hhv in queryset:
            total += HouseholdVisitAttempt.objects.filter(household_visit_id=hhv.id)
        print total
        return total


class HouseholdVisitAttempt(models.Model):
    household_visit = models.ForeignKey(
        HouseholdVisit,
        blank=False, null=True,
        related_name='visit_attempt',
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
        related_name='children_visits',
    )
    student = models.ForeignKey(
        Student,
        blank=False, null=True,
        related_name='+',
    )
    child_enrolled_in_another_school = models.BooleanField(blank=True, default=True)
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
        return self.student.first_name


class ChildService(models.Model):

    child_visit = models.ForeignKey(
        ChildVisit,
        blank=False, null=True,
        related_name='child_visit_service',
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


class HouseholdVisitComment(models.Model):
    household_visit = models.ForeignKey(
        HouseholdVisit,
        blank=False, null=True,
        related_name='visit_comment',
    )
    comment = models.CharField(max_length=255, blank=True, null=True)
    date = models.DateTimeField()

    class Meta:
        ordering = ['id']

    def __unicode__(self):
        return self.comment
