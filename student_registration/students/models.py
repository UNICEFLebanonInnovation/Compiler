from __future__ import unicode_literals, absolute_import, division

from django.db import models
from model_utils import Choices
from mptt.models import MPTTModel, TreeForeignKey
from paintstore.fields import ColorPickerField
from django.contrib.gis.db import models


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


class LocationType(models.Model):
    name = models.CharField(max_length=64L, unique=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Location Type'

    def __unicode__(self):
        return self.name


class Location(MPTTModel):

    name = models.CharField(max_length=254L)
    gateway = models.ForeignKey(LocationType, verbose_name='Location Type')
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    p_code = models.CharField(max_length=32L, blank=True, null=True)

    parent = TreeForeignKey('self', null=True, blank=True, related_name='children', db_index=True)
    # geom = models.MultiPolygonField(null=True, blank=True)
    # point = models.PointField(null=True, blank=True)
    # objects = models.GeoManager()

    def __unicode__(self):
        #TODO: Make generic
        return u'{} - {}'.format(
            self.name,
            self.gateway.name
        )
    #
    # @property
    # def geo_point(self):
    #     return self.point if self.point else self.geom.point_on_surface


    # @property
    # def point_lat_long(self):
    #     return "Lat: {}, Long: {}".format(
    #         self.point.y,
    #         self.point.x
    #     )

    class Meta:
        unique_together = ('name', 'gateway', 'p_code')
        ordering = ['name']


class PartnerOrganization(models.Model):
    name = models.CharField(max_length=100L, unique=True)

    def __unicode__(self):
        return self.name


class Student(models.Model):

    first_name = models.CharField(max_length=64L)
    last_name = models.CharField(max_length=64L)
    father_name = models.CharField(max_length=64L)
    full_name = models.CharField(max_length=225L)
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
        return u'{} {} {}'.format(
            self.first_name,
            self.father_name,
            self.last_name,
        )

    def nationality_name(self):
        if self.nationality:
            return self.nationality.name

        return ''

    def birthday(self):
        return u'{}/{}/{}'.format(
            self.birthday_day,
            self.birthday_month,
            self.birthday_year,
        )
