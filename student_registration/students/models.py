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
    name = models.CharField(max_length=45L, unique=True)

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
    phone = models.CharField(max_length=64L, blank=True)
    id_number = models.CharField(max_length=45L, unique=True)

    def __unicode__(self):
        return u'{} {} ({})'.format(
            self.first_name,
            self.father_name,
            self.last_name,
        )
