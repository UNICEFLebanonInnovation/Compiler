from __future__ import unicode_literals

from django.db import models
from model_utils import Choices


class Beneficiary(models.Model):

    REGISTRATION_STATUS = Choices(
        ('Registered', 'Registered'),
        ('Recorded', 'Recorded'),
        ('Unregistered', 'Unregistered'),
    )
    LOCATION_TYPE = Choices(
        ('CS', 'CS'),
        ('IS', 'IS'),
    )
    CARD_DISTRIBUTION_STATUS = Choices(
        ('Distributed', 'Distributed'),
        ('Not Distributed', 'Not Distributed'),
    )
    CARD_LOADED = Choices(
        ('Yes', 'Yes'),
        ('No', 'No'),
    )

    case_number = models.CharField(
        max_length=45,
        unique=True,
        primary_key=True
    )
    registration_status = models.CharField(
        max_length=45,
        blank=True,
        null=True,
        choices=REGISTRATION_STATUS
    )
    location_type = models.CharField(
        max_length=45,
        blank=True,
        null=True,
        choices=LOCATION_TYPE
    )
    governorate = models.CharField(max_length=45)
    district = models.CharField(max_length=45)
    cadastral = models.CharField(max_length=45)
    phone_number = models.CharField(max_length=45)
    total_children = models.IntegerField()
    card_distributed = models.CharField(
        max_length=45,
        blank=True,
        null=True,
        choices=CARD_DISTRIBUTION_STATUS
    )
    card_loaded = models.CharField(
        max_length=45,
        blank=True,
        null=True,
        choices=CARD_LOADED
    )

    class Meta:
        ordering = ['case_number']
        verbose_name_plural = "Beneficiaries"

    @property
    def amount(self):
        return '{} {}'.format(self.total_children * 40, 'USD')

    def __unicode__(self):
        return self.case_number
