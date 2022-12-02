# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import, division
import datetime

from django.db import models
from django.conf import settings
from django.utils.translation import ugettext as _
from django.contrib.postgres.fields import ArrayField, JSONField
from django.core.urlresolvers import reverse

from model_utils import Choices
from model_utils.models import TimeStampedModel

from django.db import models
from student_registration.students.models import Nationality
from student_registration.clm.models import Disability, EducationalLevel


YES_NO = Choices(
    ('Yes', _("Yes")),
    ('No', _("No"))
)


class Child(TimeStampedModel):
    # from student_registration.outreach.models import Child
    # outreach_child = models.ForeignKey(
    #     Child,
    #     blank=True, null=True,
    # )
    CURRENT_YEAR = datetime.datetime.now().year
    MONTHS = Choices(
        ('1', _('January')),
        ('2', _('February')),
        ('3', _('March')),
        ('4', _('April')),
        ('5', _('May')),
        ('6', _('June')),
        ('7', _('July')),
        ('8', _('August')),
        ('9', _('September')),
        ('10', _('October')),
        ('11', _('November')),
        ('12', _('December')),
    )
    GENDER = Choices(
        ('Male', _('Male')),
        ('Female', _('Female')),
    )
    MARITAL_STATUS = Choices(
        ('Married', _('Married')),
        ('Engaged', _('Engaged')),
        ('Divorced', _('Divorced')),
        ('Widowed', _('Widowed')),
        ('Single', _('Single')),
    )
    ID_TYPE = Choices(
        ('UNHCR Registered', _('UNHCR Registered')),
        ('UNHCR Recorded', _("UNHCR Recorded")),
        ('Syrian national ID', _("Syrian national ID")),
        ('Palestinian national ID', _("Palestinian national ID")),
        ('Lebanese national ID', _("Lebanese national ID")),
        ('Other nationality', _("Other nationality")),
        ('Child have no ID', _("Child have no ID"))
    )
    MAIN_CAREGIVER = (
        ('', '----------'),
        ('Mother', _('Mother')),
        ('Father', _('Father')),
        ('Other', _('Other')),
    )
    PHONE_OWNER = Choices(
            ('Phone Main Caregiver', _('Phone Main Caregiver')),
            ('Family Member', _('Family Member')),
            ('Neighbors', _('Neighbors')),
            ('Shawish', _('Shawish')),
        )
    first_name = models.CharField(
        max_length=64,
        db_index=True,
        blank=True, null=True,
        verbose_name=_('First name')
    )
    last_name = models.CharField(
        max_length=64,
        db_index=True,
        blank=True, null=True,
        verbose_name=_('Last name')
    )
    father_name = models.CharField(
        max_length=64,
        db_index=True,
        blank=True, null=True,
        verbose_name=_('Father name')
    )
    mother_fullname = models.CharField(
        max_length=64,
        db_index=True,
        blank=True, null=True,
        verbose_name=_('Mother fullname')
    )
    gender = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        choices=GENDER,
        verbose_name=_('Gender')
    )
    nationality = models.ForeignKey(
        Nationality,
        blank=True, null=True,
        related_name='+',
        verbose_name=_('Nationality')
    )
    nationality_other = models.TextField(
        blank=True, null=True,
        verbose_name=_('Please specify')
    )
    birthday_year = models.CharField(
        max_length=4,
        blank=True,
        null=True,
        default=0,
        choices=((str(x), x) for x in range(1990, 2050)),
        verbose_name=_('Birthday year')
    )
    birthday_month = models.CharField(
        max_length=2,
        blank=True,
        null=True,
        default=0,
        choices=MONTHS,
        verbose_name=_('Birthday month')
    )
    birthday_day = models.CharField(
        max_length=2,
        blank=True,
        null=True,
        default=0,
        choices=((str(x), x) for x in range(1, 32)),
        verbose_name=_('Birthday day')
    )
    p_code = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name=_('Insert Pcode if the child lives in Internal Settlement/Camp')
    )
    address = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('Registered child Home Address')
    )
    disability = models.ForeignKey(
        Disability,
        blank=True, null=True,
        related_name='+',
        verbose_name=_('Does the child have any disability or special need?')
    )
    marital_status = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        choices=MARITAL_STATUS,
        verbose_name=_('Child’s Marital Status')
    )
    have_children = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        choices=YES_NO,
        verbose_name=_('Does the child have children?')
    )
    children_number = models.IntegerField(
        blank=True,
        null=True,
        choices=((x, x) for x in range(0, 20)),
        verbose_name=_('If yes, how many?')
    )
    id_type = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=ID_TYPE,
        verbose_name=_('Child ID type')
    )
    case_number = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name=_('UNHCR Case number')
    )
    case_number_confirm = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name=_('UNHCR Case number confirm')
    )
    parent_individual_case_number = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name=_('Parent individual ID')
    )
    parent_individual_case_number_confirm = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name=_('Parent individual ID confirm')
    )
    individual_case_number = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name=_('Child individual ID')
    )
    individual_case_number_confirm = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name=_('Child individual ID confirm')
    )
    recorded_number = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name=_('UNHCR recorded barcode')
    )
    recorded_number_confirm = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name=_('UNHCR recorded barcode confirm')
    )
    parent_national_number = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name=_('Parent Lebanese ID number')
    )
    parent_national_number_confirm = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name=_('Parent Lebanese ID number')
    )
    national_number = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name=_('Child Lebanese ID number')
    )
    national_number_confirm = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name=_('Child Lebanese ID number')
    )
    parent_syrian_national_number = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name=_('Parent Syrian ID number ')
    )
    parent_syrian_national_number_confirm = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name=_('Parent Syrian ID number confirm')
    )
    syrian_national_number = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name=_('Child Syrian ID number')
    )
    syrian_national_number_confirm = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name=_('Child Syrian ID number confirm')
    )
    parent_sop_national_number = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name=_('Parent Palestinian ID number ')
    )
    parent_sop_national_number_confirm = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name=_('Parent Palestinian ID number')
    )
    sop_national_number = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name=_('Child Palestinian ID number')
    )
    sop_national_number_confirm = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name=_('Child Palestinian ID number confirm')
    )
    parent_other_number = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name=_('ID number of the Caregiver confirm')
    )
    parent_other_number_confirm = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name=_('ID number of the Caregiver')
    )
    other_number = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name=_('ID number of the child')
    )
    other_number_confirm = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name=_('ID number of the child confirm')
    )
    father_educational_level = models.ForeignKey(
        EducationalLevel,
        blank=True, null=True,
        related_name='+',
        verbose_name=_('What is the father\'s educational level?')
    )
    mother_educational_level = models.ForeignKey(
        EducationalLevel,
        blank=True, null=True,
        related_name='+',
        verbose_name=_('What is the father\'s educational level?')
    )
    first_phone_owner = models.CharField(
        max_length=100,
        blank=False,
        null=True,
        choices=PHONE_OWNER,
        verbose_name=_('Who will be answering the phone?')
    )
    first_phone_number = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name=_('Primary phone number')
    )
    first_phone_number_confirm = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name=_('Confirm primary phone number')
    )
    second_phone_owner = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=PHONE_OWNER,
        verbose_name=_('Who will be answering the phone')
    )
    second_phone_number = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name=_('Secondary phone number if available')
    )
    second_phone_number_confirm = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name=_('Confirm Secondary phone number if available')
    )
    main_caregiver = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=MAIN_CAREGIVER,
        verbose_name=_('who is the Child primary caregiver?')
    )
    main_caregiver_other = models.TextField(
        blank=True, null=True,
        verbose_name=_('Please specify')
    )
    caregiver_first_name = models.CharField(
        max_length=500,
        blank=False,
        null=True,
        verbose_name=_('Caregiver First Name')
    )
    caregiver_middle_name = models.CharField(
        max_length=500,
        blank=False,
        null=True,
        verbose_name=_('Caregiver Middle Name')
    )
    caregiver_last_name = models.CharField(
        max_length=500,
        blank=False,
        null=True,
        verbose_name=_('Caregiver Last Name')
    )
    caregiver_mother_name = models.CharField(
        max_length=500,
        blank=False,
        null=True,
        verbose_name=_('Caretaker Mother\'s Full Name')
    )
    def __unicode__(self):
        if not self.first_name:
            return 'No name'

        return u'{} {} {}'.format(
            self.first_name,
            self.father_name,
            self.last_name,
        )

    @property
    def full_name(self):
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

    @property
    def age(self):
        return Student.get_age(self.birthday_year, self.birthday_month, self.birthday_day)

    @staticmethod
    def get_age(birthday_year, birthday_month, birthday_day):
        if birthday_year and birthday_month and birthday_day:
            today = datetime.now()
            return today.year - int(birthday_year) - (
                    (today.month, today.day) < (int(birthday_month), int(birthday_day)))
        # if self.birthday_year:
        #     return int(self.CURRENT_YEAR)-int(self.birthday_year)
        return 0

    class Meta:
        abstract = True

    def save(self, **kwargs):
        if self.phone:
            self.std_phone = self.phone_prefix + self.phone
        """
        Generate unique IDs for every person
        :param kwargs:
        :return:
        """
        if self.pk is None:
            self.number = generate_id(
                self.first_name,
                self.father_name,
                self.last_name,
                self.mother_fullname,
                self.gender,
                self.birthday_day,
                self.birthday_month,
                self.birthday_year
            )

        super(Student, self).save(**kwargs)


