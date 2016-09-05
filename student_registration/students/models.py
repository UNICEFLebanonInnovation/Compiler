from __future__ import unicode_literals, absolute_import, division

from django.contrib.gis.db import models
from django.db import models
from django.utils.translation import ugettext as _
from model_utils import Choices
from model_utils.models import TimeStampedModel
from mptt.models import MPTTModel


class Nationality(models.Model):
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


class IDType(models.Model):
    name = models.CharField(max_length=45L, unique=True)

    class Meta:
        ordering = ['name']

    def __unicode__(self):
        return self.name


class Person(TimeStampedModel):

    first_name = models.CharField(max_length=64L, blank=True, null=True)
    last_name = models.CharField(max_length=64L, blank=True, null=True)
    father_name = models.CharField(max_length=64L, blank=True, null=True)
    full_name = models.CharField(max_length=225L, blank=True, null=True)
    mother_fullname = models.CharField(max_length=64L, blank=True, null=True)
    mother_firstname = models.CharField(max_length=64L, blank=True, null=True)
    mother_lastname = models.CharField(max_length=64L, blank=True, null=True)
    sex = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        choices=Choices(
            u'Male',
            u'Female',
        )
    )
    birthday_year = models.CharField(
        max_length=4,
        blank=True,
        null=True,
        choices=((str(x), x) for x in range(1930, 2051))
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
    age = models.CharField(max_length=4L, blank=True, null=True)
    phone = models.CharField(max_length=64L, blank=True, null=True)
    id_number = models.CharField(max_length=45L, blank=True, null=True)
    id_type = models.ForeignKey(
        IDType,
        blank=True, null=True,
    )
    nationality = models.ForeignKey(
        Nationality,
        blank=True, null=True,
    )
    address = models.TextField(
        blank=True,
        null=True
    )
    number = models.CharField(max_length=45L, blank=True, null=True)

    def __unicode__(self):
        if not self.first_name:
            return self.number

        return u'{} {} {}'.format(
            self.first_name,
            self.father_name,
            self.last_name,
        )

    def nationality_name(self):
        if self.nationality:
            return self.nationality.name

        return ''

    @property
    def birthday(self):
        return u'{}/{}/{}'.format(
            self.birthday_day,
            self.birthday_month,
            self.birthday_year,
        )

    class Meta:
        abstract = True


class Student(Person):

    @property
    def attendance_list(self):
        attendances = {}
        for item in self.attendances.all():
            attendances[item.attendance_date] = item.status
        return attendances
