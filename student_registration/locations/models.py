from __future__ import unicode_literals, absolute_import, division

from django.db import models
from model_utils import Choices
from model_utils.models import TimeStampedModel
from mptt.models import MPTTModel, TreeForeignKey
from django.utils.translation import ugettext as _


class LocationType(models.Model):
    name = models.CharField(max_length=64, unique=True)
    name_en = models.CharField(max_length=145, blank=True, null=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Location Type'

    def __str__(self):
        return self.name

    def __unicode__(self):
        return self.name


class Location(MPTTModel):

    name = models.CharField(max_length=254)
    name_en = models.CharField(max_length=254, blank=True, null=True)
    type = models.ForeignKey(LocationType, verbose_name='Location Type')
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    p_code = models.CharField(max_length=32, blank=True, null=True)
    parent = TreeForeignKey('self', null=True, blank=True, related_name='children', db_index=True)

    def __str__(self):
        return self.name

    def __unicode__(self):
        # if self.type:
        #     return u'{} - {}'.format(
        #         self.name,
        #         self.type.name
        #     )
        return self.name

    class Meta:
        unique_together = ('name', 'type', 'p_code')
        ordering = ['name']


class Center(models.Model):

    name = models.CharField(max_length=100)
    governorate = models.ForeignKey(
        Location,
        blank=True, null=True,
        related_name='+',
        verbose_name=_('Governorate')
    )
    caza = models.ForeignKey(
        Location,
        blank=True, null=True,
        related_name='+',
        verbose_name=_('Caza')
    )
    cadaster = models.ForeignKey(
        Location,
        blank=True, null=True,
        related_name='+',
        verbose_name=_('Cadaster')
    )
    p_code = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name=_('P-Code')
    )
    type = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=Choices(
            ('Municipality', _('Municipality')),
            ('Collective Settlement', _('Collective Settlement')),
            ('Informal Settlement', _('Informal Settlement')),
            ('Welfare Center', _('Welfare Center')),
            ('Community Hub', _('Community Hub')),
        ),
        verbose_name=_('Type')
    )

    class Meta:
        ordering = ['name']
        verbose_name = "Center"
        verbose_name_plural = "Centers"

    def __str__(self):
        return self.name

    def __unicode__(self):
        return self.name
