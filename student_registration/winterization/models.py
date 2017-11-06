from __future__ import unicode_literals

from django.db import models
from model_utils import Choices
from django.contrib.postgres.fields import JSONField,  ArrayField


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


class Assessment(models.Model):

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

    _id = models.CharField(
        max_length=45,
        unique=True,
        primary_key=True
    )
    _rev = models.CharField(
        max_length=45,
        blank=True,
        null=True,
    )
    assistance_type = JSONField(blank=True, null=True)
    barcode_num = models.CharField(
        max_length=45,
        blank=True,
        null=True,
    )
    channels = JSONField(blank=True, null=True)
    child_list = JSONField(blank=True, null=True)

    completed = models.BooleanField(default=False)
    completion_date = models.CharField(
        max_length=45,
        blank=True,
        null=True,
    )
    creation_date = models.CharField(
        max_length=45,
        blank=True,
        null=True,
    )
    criticality = models.CharField(
        max_length=45,
        blank=True,
        null=True,
    )
    disabilities = models.CharField(
        max_length=45,
        blank=True,
        null=True,
    )
    dob = models.CharField(
        max_length=45,
        blank=True,
        null=True,
    )
    family_count = models.CharField(
        max_length=45,
        blank=True,
        null=True,
    )
    family_list = JSONField(blank=True, null=True)
    family_name = models.CharField(
        max_length=100,
        blank=True,
        null=True,
    )
    first_name = models.CharField(
        max_length=100,
        blank=True,
        null=True,
    )
    gender = models.CharField(
        max_length=45,
        blank=True,
        null=True,
    )
    history = JSONField(blank=True, null=True)
    id_type = models.CharField(
        max_length=45,
        blank=True,
        null=True,
    )
    location = JSONField(blank=True, null=True)
    location_distribution = JSONField(blank=True, null=True)
    marital_status = models.CharField(
        max_length=45,
        blank=True,
        null=True,
    )
    middle_name = models.CharField(
        max_length=100,
        blank=True,
        null=True,
    )
    mothers_name = models.CharField(
        max_length=100,
        blank=True,
        null=True,
    )
    moving_location = models.CharField(
        max_length=45,
        blank=True,
        null=True,
    )
    new_cadastral = models.CharField(
        max_length=45,
        blank=True,
        null=True,
    )
    new_district = models.CharField(
        max_length=45,
        blank=True,
        null=True,
    )
    official_id = models.CharField(
        max_length=45,
        blank=True,
        null=True,
    )
    over18 = models.CharField(
        max_length=45,
        blank=True,
        null=True,
    )
    partner_name = models.CharField(
        max_length=45,
        blank=True,
        null=True,
    )
    phone_number = models.CharField(
        max_length=45,
        blank=True,
        null=True,
    )
    phone_owner = models.CharField(
        max_length=45,
        blank=True,
        null=True,
    )
    principal_applicant = models.CharField(
        max_length=45,
        blank=True,
        null=True,
    )
    relationship_type = models.CharField(
        max_length=45,
        blank=True,
        null=True,
    )
    type = models.CharField(
        max_length=45,
        blank=True,
        null=True,
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
    )
    governorate = models.CharField(
        max_length=45,
        blank=True,
        null=True,
    )
    district = models.CharField(
        max_length=45,
        blank=True,
        null=True,
    )
    cadastral = models.CharField(
        max_length=45,
        blank=True,
        null=True,
    )
    latitude = models.CharField(
        max_length=45,
        blank=True,
        null=True,
    )
    longitude = models.CharField(
        max_length=45,
        blank=True,
        null=True,
    )
    p_code = models.CharField(
        max_length=45,
        blank=True,
        null=True,
    )
    p_code_name = models.CharField(
        max_length=45,
        blank=True,
        null=True,
    )
    site_type = models.CharField(
        max_length=45,
        blank=True,
        null=True,
    )

    total_children = models.IntegerField(
        blank=True,
        null=True,
    )
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

    _0_to_3_months = models.IntegerField(
        blank=True,
        null=True,
    )
    _3_to_12_months = models.IntegerField(
        blank=True,
        null=True,
    )
    _1_year_old = models.IntegerField(
        blank=True,
        null=True,
    )
    _2_years_old = models.IntegerField(
        blank=True,
        null=True,
    )
    _3_years_old = models.IntegerField(
        blank=True,
        null=True,
    )
    _4_years_old = models.IntegerField(
        blank=True,
        null=True,
    )
    _5_years_old = models.IntegerField(
        blank=True,
        null=True,
    )
    _6_years_old = models.IntegerField(
        blank=True,
        null=True,
    )
    _7_years_old = models.IntegerField(
        blank=True,
        null=True,
    )
    _8_years_old = models.IntegerField(
        blank=True,
        null=True,
    )
    _9_years_old = models.IntegerField(
        blank=True,
        null=True,
    )
    _10_years_old = models.IntegerField(
        blank=True,
        null=True,
    )
    _11_years_old = models.IntegerField(
        blank=True,
        null=True,
    )
    _12_years_old = models.IntegerField(
        blank=True,
        null=True,
    )
    _13_years_old = models.IntegerField(
        blank=True,
        null=True,
    )
    _14_years_old = models.IntegerField(
        blank=True,
        null=True,
    )
    male = models.IntegerField(
        blank=True,
        null=True,
    )
    female = models.IntegerField(
        blank=True,
        null=True,
    )
    _3_months_kit = models.IntegerField(
        blank=True,
        null=True,
    )
    _12_months_kit = models.IntegerField(
        blank=True,
        null=True,
    )
    _2_years_kit = models.IntegerField(
        blank=True,
        null=True,
    )
    _3_years_kit = models.IntegerField(
        blank=True,
        null=True,
    )
    _5_years_kit = models.IntegerField(
        blank=True,
        null=True,
    )
    _7_years_kit = models.IntegerField(
        blank=True,
        null=True,
    )
    _9_years_kit = models.IntegerField(
        blank=True,
        null=True,
    )
    _12_years_kit = models.IntegerField(
        blank=True,
        null=True,
    )
    _14_years_kit = models.IntegerField(
        blank=True,
        null=True,
    )
    _3_months_kit_completed = models.IntegerField(
        blank=True,
        null=True,
    )
    _12_months_kit_completed = models.IntegerField(
        blank=True,
        null=True,
    )
    _2_years_kit_completed = models.IntegerField(
        blank=True,
        null=True,
    )
    _3_years_kit_completed = models.IntegerField(
        blank=True,
        null=True,
    )
    _5_years_kit_completed = models.IntegerField(
        blank=True,
        null=True,
    )
    _7_years_kit_completed = models.IntegerField(
        blank=True,
        null=True,
    )
    _9_years_kit_completed = models.IntegerField(
        blank=True,
        null=True,
    )
    _12_years_kit_completed = models.IntegerField(
        blank=True,
        null=True,
    )
    _14_years_kit_completed  = models.IntegerField(
        blank=True,
        null=True,
    )

    class Meta:
        ordering = ['id_type']
        verbose_name_plural = "Assessments"

    @property
    def amount(self):
        return 0

    def __unicode__(self):
        return self._id
