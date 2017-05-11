from __future__ import unicode_literals, absolute_import, division

from django.db import models
from model_utils import Choices
from django.utils.translation import ugettext as _
from django.contrib.gis.db import models
from student_registration.locations.models import Location


class School(models.Model):

    # SCHOOL_TYPE = Choices(
    #     ('2ndshift', '2nd Shift'),
    #     ('alp', 'ALP')
    # )

    name = models.CharField(max_length=555L)
    number = models.CharField(max_length=45L, unique=True)
    # types = models.SelectMultipleField(blank=True, choices=SCHOOL_TYPE)
    location = models.ForeignKey(
        Location,
        blank=False, null=True,
        related_name='+',
    )
    in_use = models.BooleanField(blank=True, default=False)

    class Meta:
        ordering = ['number']

    @property
    def location_name(self):
        if self.location:
            return self.location.name
        return ''

    @property
    def location_parent_name(self):
        if self.location and self.location.parent:
            return self.location.parent.name
        return ''

    def __unicode__(self):
        # return self.name
        return u'{} - {}'.format(
            self.name,
            self.number
        )


class Course(models.Model):
    name = models.CharField(max_length=45L, unique=True)

    class Meta:
        ordering = ['name']

    def __unicode__(self):
        return self.name


class EducationLevel(models.Model):
    name = models.CharField(max_length=45L, unique=True)
    note = models.IntegerField(blank=True, null=True)

    class Meta:
        ordering = ['id']
        verbose_name = "ALP Level"

    def __unicode__(self):
        return self.name


class ClassLevel(models.Model):
    name = models.CharField(max_length=45L, unique=True)

    class Meta:
        ordering = ['id']
        verbose_name = "ALP Result"

    def __unicode__(self):
        return self.name


class Grade(models.Model):
    name = models.CharField(max_length=45L, unique=True)

    def __unicode__(self):
        return self.name


class Section(models.Model):
    name = models.CharField(max_length=45L, unique=True)

    class Meta:
        ordering = ['id']

    def __unicode__(self):
        return self.name


class ClassRoom(models.Model):
    name = models.CharField(max_length=45L, unique=True)
    school = models.ForeignKey(
        School,
        blank=True, null=True,
        related_name='+',
    )
    grade = models.ForeignKey(
        Grade,
        blank=True, null=True,
        related_name='+',
    )
    section = models.ForeignKey(
        Section,
        blank=True, null=True,
        related_name='+',
    )

    class Meta:
        ordering = ['id']
        verbose_name = "Formal Education Level"

    def __unicode__(self):
        return self.name


class PartnerOrganization(models.Model):
    name = models.CharField(max_length=100L, unique=True)

    class Meta:
        ordering = ['name']

    def __unicode__(self):
        return self.name


class ALPReferMatrix(models.Model):
    level = models.ForeignKey(
        EducationLevel,
        blank=True, null=True,
        related_name='+',
    )
    success_refer_to = models.ForeignKey(
        ClassLevel,
        blank=True, null=True,
        related_name='success_refer_to',
    )
    fail_refer_to = models.ForeignKey(
        ClassLevel,
        blank=True, null=True,
        related_name='fail_refer_to',
    )
    age = models.IntegerField(blank=True, null=True)
    success_grade = models.IntegerField(blank=True, null=True)

    class Meta:
        ordering = ['id']
        verbose_name = "ALP Refer Matrix"

    def __unicode__(self):
        return str(self.id)
