from __future__ import unicode_literals

from django.db import models
from django.contrib.postgres.fields import JSONField
from django.utils.translation import ugettext as _

from model_utils import Choices

from student_registration.students.models import Person


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
    interview_comment = models.CharField(max_length=200, blank=True, null=True)
    name = models.CharField(max_length=100, blank=True, null=True)
    phone_number = models.CharField(max_length=45, blank=True, null=True)
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
    p_code = models.CharField(max_length=45, blank=True, null=True)
    address = models.CharField(max_length=100, blank=True, null=True)
    number_of_children = models.CharField(max_length=45, blank=True, null=True)
    barcode_number = models.CharField(max_length=45, blank=True, null=True)

    social_worker_name = models.CharField(max_length=200, blank=True, null=True)
    partner_name = models.CharField(max_length=200, blank=True, null=True)
    governorate = models.CharField(max_length=200, blank=True, null=True)
    district = models.CharField(max_length=200, blank=True, null=True)
    village = models.CharField(max_length=200, blank=True, null=True)
    interview_date = models.CharField(max_length=200, blank=True, null=True)

    children = JSONField(blank=True, null=True)

    class Meta:
        ordering = ['id']

    def __unicode__(self):
        return self.name


class Child(Person):

    household = models.ForeignKey(
        HouseHold,
        blank=True, null=True,
        related_name='+'
    )
    barcode_subset = models.CharField(max_length=45, blank=True, null=True)
