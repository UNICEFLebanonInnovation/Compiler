from __future__ import unicode_literals

from django.db import models
from model_utils import Choices
from django.contrib.postgres.fields import JSONField
from django.utils.translation import ugettext as _


class HouseHold(models.Model):

    interview_status = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        choices=Choices(
            ('granted', _('Granted')),
            ('denied', _('Denied')),
            ('granted_referral', _('Granted for the referral')),
        )
    )
    interview_comment = models.CharField(max_length=200L, blank=True, null=True)
    name = models.CharField(max_length=100L, blank=True, null=True)
    phone_number = models.CharField(max_length=45L, blank=True, null=True)
    residence_type = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        choices=Choices(
            ('informal_s', _('Informal Settlement')),
            ('house_appart', _('House or Apartment')),
            ('garage_store_other', _('Garage, Store or other')),
        )
    )
    p_code = models.CharField(max_length=45L, blank=True, null=True)
    address = models.CharField(max_length=100L, blank=True, null=True)
    number_of_children = models.CharField(max_length=45L, blank=True, null=True)
    barcode_number = models.CharField(max_length=45L, blank=True, null=True)

    social_worker_name = models.CharField(max_length=200L, blank=True, null=True)
    partner_name = models.CharField(max_length=200L, blank=True, null=True)
    governorate = models.CharField(max_length=200L, blank=True, null=True)
    district = models.CharField(max_length=200L, blank=True, null=True)
    village = models.CharField(max_length=200L, blank=True, null=True)
    interview_date = models.CharField(max_length=200L, blank=True, null=True)

    children = JSONField(blank=True, null=True)

    class Meta:
        ordering = ['id']

    def __unicode__(self):
        return self.name


class Child(Person):

    class Meta:
        ordering = ['id']

    def __unicode__(self):
        return self.name
