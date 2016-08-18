from __future__ import unicode_literals, absolute_import, division

from django.db import models
from model_utils import Choices
from model_utils.models import TimeStampedModel
from mptt.models import MPTTModel, TreeForeignKey
from paintstore.fields import ColorPickerField
from django.utils.translation import ugettext as _
from django.contrib.gis.db import models
from student_registration.locations.models import Location


class School(models.Model):
    name = models.CharField(max_length=555L)
    number = models.CharField(max_length=45L, unique=True)

    location = models.ForeignKey(
        Location,
        blank=False, null=True,
        related_name='+',
    )

    class Meta:
        ordering = ['name']

    def __unicode__(self):
        return self.name


class Course(models.Model):
    name = models.CharField(max_length=45L, unique=True)

    class Meta:
        ordering = ['name']

    def __unicode__(self):
        return self.name


class EducationLevel(models.Model):
    name = models.CharField(max_length=45L, unique=True)

    def __unicode__(self):
        return self.name


class ClassLevel(models.Model):
    name = models.CharField(max_length=45L, unique=True)

    def __unicode__(self):
        return self.name


class Grade(models.Model):
    name = models.CharField(max_length=45L, unique=True)

    def __unicode__(self):
        return self.name


class Section(models.Model):
    name = models.CharField(max_length=45L, unique=True)

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

    def __unicode__(self):
        return self.name


class PartnerOrganization(models.Model):
    name = models.CharField(max_length=100L, unique=True)

    def __unicode__(self):
        return self.name
