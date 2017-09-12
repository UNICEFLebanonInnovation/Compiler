from __future__ import unicode_literals, absolute_import, division

from django.db import models
from model_utils import Choices
from model_utils.models import TimeStampedModel
from mptt.models import MPTTModel, TreeForeignKey
<<<<<<< HEAD
from paintstore.fields import ColorPickerField
=======
>>>>>>> 3b9073c012bcdfc49afcb1d105deb56123ab5be1
from django.utils.translation import ugettext as _
from django.contrib.gis.db import models


class LocationType(models.Model):
<<<<<<< HEAD
    name = models.CharField(max_length=64L, unique=True)
=======
    name = models.CharField(max_length=64, unique=True)
>>>>>>> 3b9073c012bcdfc49afcb1d105deb56123ab5be1

    class Meta:
        ordering = ['name']
        verbose_name = 'Location Type'

    def __unicode__(self):
        return self.name


class Location(MPTTModel):

<<<<<<< HEAD
    name = models.CharField(max_length=254L)
    type = models.ForeignKey(LocationType, verbose_name='Location Type')
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    p_code = models.CharField(max_length=32L, blank=True, null=True)

    parent = TreeForeignKey('self', null=True, blank=True, related_name='children', db_index=True)
    pilot_in_use = models.BooleanField(blank=True, default=False)
    # geom = models.MultiPolygonField(null=True, blank=True)
    # point = models.PointField(null=True, blank=True)
    # objects = models.GeoManager()

    def __unicode__(self):
        #TODO: Make generic
        return u'{} - {}'.format(
            self.name,
            self.type.name
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
=======
    name = models.CharField(max_length=254)
    type = models.ForeignKey(LocationType, verbose_name='Location Type')
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    p_code = models.CharField(max_length=32, blank=True, null=True)

    parent = TreeForeignKey('self', null=True, blank=True, related_name='children', db_index=True)

    def __unicode__(self):
        return u'{}'.format(
            self.name
        )
>>>>>>> 3b9073c012bcdfc49afcb1d105deb56123ab5be1

    class Meta:
        unique_together = ('name', 'type', 'p_code')
        ordering = ['name']
