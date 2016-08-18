from __future__ import unicode_literals, absolute_import, division

from django.db import models
from model_utils import Choices
from model_utils.models import TimeStampedModel
from mptt.models import MPTTModel, TreeForeignKey
from paintstore.fields import ColorPickerField
from django.utils.translation import ugettext as _
from django.contrib.gis.db import models


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


class Student(TimeStampedModel):

    first_name = models.CharField(max_length=64L, blank=True, null=True)
    last_name = models.CharField(max_length=64L, blank=True, null=True)
    father_name = models.CharField(max_length=64L, blank=True, null=True)
    full_name = models.CharField(max_length=225L, blank=True, null=True)
    mother_fullname = models.CharField(max_length=64L, blank=True, null=True)
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
    phone = models.CharField(max_length=64L, blank=True, null=True)
    id_number = models.CharField(max_length=45L, blank=True, null=True)
    nationality = models.ForeignKey(
        Nationality,
        blank=True, null=True,
    )
    address = models.TextField(
        blank=True,
        null=True
    )

    def __unicode__(self):
        return self.full_name

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

    @property
    def attendance_list(self):
        attendances = {}
        for item in self.attendances.all():
            attendances[item.attendance_date] = item.status
        return attendances
