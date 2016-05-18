from __future__ import unicode_literals, absolute_import, division

from django.db import models
from model_utils import Choices


class Nationality(models.Model):
    name = models.CharField(max_length=45L, unique=True)

    class Meta:
        ordering = ['name']

    def __unicode__(self):
        return self.name


class School(models.Model):
    name = models.CharField(max_length=555L)
    number = models.CharField(max_length=45L, unique=True)

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


class Language(models.Model):
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


class Governorate(models.Model):
    name = models.CharField(max_length=45L)
    p_code = models.CharField(max_length=32L, blank=True, null=True)

    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ['name']


class PartnerOrganization(models.Model):
    name = models.CharField(max_length=100L, unique=True)

    def __unicode__(self):
        return self.name


class Student(models.Model):

    first_name = models.CharField(max_length=64L)
    last_name = models.CharField(max_length=64L)
    father_name = models.CharField(max_length=64L)
    mother_fullname = models.CharField(max_length=64L)
    sex = models.CharField(
        max_length=50,
        choices=Choices(
            u'Male',
            u'Female',
        )
    )
    birthday_year = models.CharField(
        max_length=4,
        blank=True,
        null=True,
        choices=((str(x), x) for x in range(1990, 2051))
    )
    birthday_month = models.CharField(
        max_length=2,
        blank=True,
        null=True,
        choices=((str(x), x) for x in range(1, 13))
    )
    birthday_day = models.CharField(
        max_length=2,
        blank=True,
        null=True,
        choices=((str(x), x) for x in range(1, 33))
    )
    phone = models.CharField(max_length=64L, blank=True)
    id_number = models.CharField(max_length=45L, unique=True)
    nationality = models.ForeignKey(
        Nationality,
        blank=True, null=True,
    )
    address = models.TextField(
        blank=True,
        null=True
    )

    def __unicode__(self):
        return u'{} {} ({})'.format(
            self.first_name,
            self.father_name,
            self.last_name,
        )
