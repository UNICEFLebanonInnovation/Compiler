from __future__ import unicode_literals, absolute_import, division
import datetime

from django.db import models
from django.conf import settings
from django.utils.translation import ugettext as _
from django.contrib.postgres.fields import ArrayField, JSONField
from django.core.urlresolvers import reverse

from model_utils import Choices
from model_utils.models import TimeStampedModel

from student_registration.students.models import Student, Labour, Nationality
from student_registration.locations.models import Location, Center
from student_registration.schools.models import (
    School,
    EducationalLevel,
    PartnerOrganization
)


class Assessment(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    overview = models.TextField(blank=True, null=True)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    capacity = models.IntegerField(blank=True, null=True)
    assessment_form = models.URLField(blank=True, null=True)

    class Meta:
        ordering = ['name']

    def __unicode__(self):
        return self.name


class Cycle(models.Model):
    name = models.CharField(max_length=100)
    current_cycle = models.BooleanField(blank=True, default=False)

    class Meta:
        ordering = ['name']
        verbose_name = "Program cycle"
        verbose_name_plural = "Program cycles"

    def __unicode__(self):
        return self.name


class Referral(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        ordering = ['name']
        verbose_name = "Referral"
        verbose_name_plural = "Referrals"

    def __unicode__(self):
        return self.name


class Registration(TimeStampedModel):
    CURRENT_YEAR = datetime.datetime.now().year

    HAVE_LABOUR = Choices(
        ('no', _('No')),
        ('yes_morning', _('Yes - Morning')),
        ('yes_afternoon', _('Yes - Afternoon')),
        ('yes_all_day', _('Yes - All day')),
    )
    LABOURS = Choices(
        ('', '----------'),
        ('agriculture', _('Agriculture')),
        ('building', _('Building')),
        ('manufacturing', _('Manufacturing')),
        ('retail_store', _('Retail / Store')),
        ('begging', _('Begging')),
        ('other_many_other', _('Other services')),
        # ('other', _('Other')),
    )
    LABOUR_INCOME = Choices(
        ('', '----------'),
        ('thousand_or_less', _('10,000 LBP or less')),
        ('eleven_thousand_to_twenty_five', _('11,000 to 25,000 LBP')),
        ('twenty_six_thousand_to_fifty', _('26,000 to 50,000 LBP')),
        ('more_than_fifty', _('More than 50,000 LBP'))
    )

    center = models.ForeignKey(
        Center,
        blank=True, null=True,
        related_name='+',
        verbose_name=_('Center')
    )
    child = models.ForeignKey(
        Student,
        blank=False, null=True,
        related_name='+',
        verbose_name=_('Child')
    )
    partner = models.ForeignKey(
        PartnerOrganization,
        blank=True, null=True,
        verbose_name=_('Partner'),
        related_name='+'
    )
    have_labour = models.CharField(
        max_length=100,
        choices=HAVE_LABOUR,
        blank=True,
        null=True,
        verbose_name=_('Does the child participate in work?')
    )
    labours = ArrayField(
        models.CharField(
            choices=LABOURS,
            max_length=50,
            blank=True,
            null=True,
        ),
        blank=True,
        null=True,
        verbose_name=_('What is the type of work ?')
    )
    labours_other_specify = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name=_(
            'Please specify (hotel, restaurant, transport, personal services such as cleaning, hair care, cooking and childcare)')
    )
    labour_hours = models.IntegerField(
        blank=True,
        null=True,
        verbose_name=_('How many hours does this child work in a day?')
    )
    labour_weekly_income = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=LABOUR_INCOME,
        verbose_name=_('What is the income of the child per week?')
    )
    source_of_identification = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=Choices(
            ('', '----------'),
            ('Dirassa', _('Dirassa')),
            ('Awarness Session', _('Awarness Session')),
            ('Child''s parents', _('Child''s parents')),
            ('From Hosted Community', _('From Hosted Community')),
            ('Sector Partners referral (CP, Education, Health, Wash, Youth, Palestenian program...) ',
             _('Sector Partners referral (CP, Education, Health, Wash, Youth, Palestenian program...) ')),
            ('From Profiling Database', _('From Profiling Database')),
            ('From Other NGO', _('From Other NGO')),
            ('From Displaced Community', _('From Displaced Community')),
            ('Referred by the municipality/Other formal sources', _('Referred by the municipality/Other formal sources')),
            ('Other Sources', _('Other Sources')),
        ),
        verbose_name=_('Source of referral of the child to MSCC')
    )

    cash_support_programmes = ArrayField(
        models.CharField(
            choices=Choices(
                ('', '----------'),
                ('Haddi', _('Haddi')),
                ('Education Cash assistance', _('Education Cash assistance')),
                ('UNHCR cash assistance', _('UNHCR cash assistance')),
                ('WFP cash assistance', _('WFP cash assistance')),
            ),
            max_length=100,
            blank=True,
            null=True,
        ),
        blank=True,
        null=True,
        verbose_name=_('Cash support programmes that child is already benefitting from')
    )

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        blank=False, null=True,
        related_name='+',
    )
    modified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        blank=True, null=True,
        related_name='+',
        verbose_name=_('Modified by'),
    )
    deleted = models.BooleanField(blank=True, default=False)
    registration_date = models.DateField(
        blank=True,
        null=True,
        verbose_name=_('Registration date')
    )

    @property
    def child_fullname(self):
        if self.child:
            return self.child.full_name
        return ''

    @property
    def child_age(self):
        if self.child:
            return self.child.age
        return 0

    def get_absolute_url(self):
        return '/mscc/edit-child/%d/' % self.pk

    def __unicode__(self):
        if self.child:
            return self.child.__unicode__()
        return str(self.id)

    class Meta:
        ordering = ['-id']
        verbose_name = "MSCC Registration"
        verbose_name_plural = "MSCC Registrations"


class Inclusion(TimeStampedModel):
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
    YES_NO = Choices(
        ('', '----------'),
        ('yes', _("Yes")),
        ('no', _("No")),
    )
    PARTICIPATION = Choices(
        ('', '----------'),
        ('no_absence', _('No Absence')),
        ('less_than_3days', _('Less than 3 absence days')),
        ('3_7_days', _('3 to 7 absence days')),
        ('7_12_days', _('7 to 12 absence days')),
        ('more_than_12days', _('More than 12 absence days')),
    )
    BARRIERS = Choices(
        ('', '----------'),
        ('Full time job to support family financially', _('Full time job to support family financially')),
        ('seasonal_work', _('Seasonal work')),
        ('cold_weather', _('Cold Weather')),
        ('sickness', _('Sickness')),
        ('security', _('Security')),
        ('family moved', _('Family moved')),
        ('Moved back to Syria', _('Moved back to Syria')),
        ('Enrolled in formal education', _('Enrolled in formal education')),
        ('marriage engagement pregnancy', _('Marriage/Engagement/Pregnancy')),
        ('violence bullying', _('Violence/Bullying')),
        ('No interest in pursuing the programme/No value', _('No interest in pursuing the programme/No value')),
    )
    HAVE_LABOUR = Choices(
        ('no', _('No')),
        ('yes_morning', _('Yes - Morning')),
        ('yes_afternoon', _('Yes - Afternoon')),
        ('yes_all_day', _('Yes - All day')),
    )
    LABOURS = Choices(
        ('', '----------'),
        ('agriculture', _('Agriculture')),
        ('building', _('Building')),
        ('manufacturing', _('Manufacturing')),
        ('retail_store', _('Retail / Store')),
        ('begging', _('Begging')),
        ('other_many_other', _(
            'Other services (hotel, restaurant, transport, personal services such as cleaning, hair care, cooking and childcare)')),
        # ('other', _('Other')),
    )
    LEARNING_RESULT = Choices(
        ('graduated_to_abln_next_round_same_level', _('Graduated to the next round, same level')),
        ('graduated_to_abln_next_round_higher_level', _('Graduated to the next round, higher level')),
        ('referred_to_bln', _('Referred to BLN')),
        ('referred_to_ybln', _('Referred to YBLN')),
        # ('referred_to_alp', _('Referred to ALP')),
        ('referred_to_cbt', _('Referred to CBT')),
        ('other', _('Other')),
    )
    MAIN_CAREGIVER = (
        ('', '----------'),
        ('mother', _('Mother')),
        ('father', _('Father')),
        ('other', _('Other')),
    )

    source_of_identification = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=Choices(
            ('Direct outreach', _('Direct outreach')),
            ('List database', _('List database')),
            ('Referral from another NGO', _('Referral from another NGO')),
            ('Referred by CP partner', _('Referred by CP partner')),
            ('Referred by youth partner', _('Referred by youth partner')),
            ('Referral from another Municipality', _('Referral from Municipality')),
            ('Family walked in to NGO', _('Family walked in to NGO')),
            ('from abln', _('FROM ABLN')),
            ('from bln', _('FROM BLN')),
            ('from cbece', _('FROM CBECE')),
            ('ocha', _('OCHA')),
            ('non unicef', _('Non - UNICEF')),
            ('RIMS', _('RIMS')),
        ),
        verbose_name=_('Source of identification of the child')
    )
    rims_case_number = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name=_('RIMS Case Number')
    )
    first_attendance_date = models.DateField(
        blank=True,
        null=True,
        verbose_name=_('First attendance date')
    )
    round = models.ForeignKey(
        CLMRound,
        blank=True, null=True,
        related_name='+',
        verbose_name=_('Round')
    )
    governorate = models.ForeignKey(
        Location,
        blank=True, null=True,
        related_name='+',
        verbose_name=_('Governorate')
    )
    district = models.ForeignKey(
        Location,
        blank=True, null=True,
        related_name='+',
        verbose_name=_('District')
    )
    cadaster = models.ForeignKey(
        Location,
        blank=True, null=True,
        related_name='+',
        verbose_name=_('Cadaster')
    )
    location = models.CharField(
        max_length=250,
        blank=True,
        null=True,
        verbose_name=_('Location')
    )
    student = models.ForeignKey(
        Student,
        blank=False, null=True,
        related_name='+',
        verbose_name=_('Student')
    )
    disability = models.ForeignKey(
        Disability,
        blank=True, null=True,
        related_name='+',
        verbose_name=_('Disability')
    )
    have_labour = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=HAVE_LABOUR,
        verbose_name=_('Does the child participate in work?')
    )
    labour_type = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=LABOURS,
        verbose_name=_('What is the type of work ?')
    )
    participation = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=PARTICIPATION,
        verbose_name=_('Participation')
    )
    learning_result = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=LEARNING_RESULT,
        verbose_name=_('Learning result')
    )
    barriers = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=BARRIERS,
        verbose_name=_('The main barriers affecting the daily attendance and performance')
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        blank=False, null=True,
        related_name='+',
    )
    modified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        blank=True, null=True,
        related_name='+',
        verbose_name=_('Modified by'),
    )
    deleted = models.BooleanField(blank=True, default=False)
    registration_date = models.DateField(
        blank=True,
        null=True,
        verbose_name=_('Registration date')
    )
    partner = models.ForeignKey(
        PartnerOrganization,
        blank=True, null=True,
        verbose_name=_('Partner'),
        related_name='+'
    )
    internal_number = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name=_('Internal number')
    )
    comments = models.TextField(
        blank=True, null=True,
        verbose_name=_('Comments')
    )
    phone_number = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name=_('Phone number')
    )
    phone_number_confirm = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name=_('Phone number confirm')
    )

    phone_owner = models.CharField(
        max_length=100,
        blank=False,
        null=True,
        choices=Choices(
            ('main_caregiver', _('Phone Main Caregiver')),
            ('family member', _('Family Member')),
            ('neighbors', _('Neighbors')),
            ('shawish', _('Shawish')),
        ),
        verbose_name=_('Phone Owner')
    )
    second_phone_owner = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=Choices(
            ('main_caregiver', _('Phone Main Caregiver')),
            ('family member', _('Family Member')),
            ('neighbors', _('Neighbors')),
            ('shawish', _('Shawish')),
        ),
        verbose_name=_('Second Phone Owner')
    )
    second_phone_number = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name=_('Second Phone number')
    )
    second_phone_number_confirm = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name=_('Second Phone number confirm')
    )

    education_status = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=Choices(
            ('out of school', _('Out of school')),
            ('enrolled in formal education but did not continue',
             _("Enrolled in formal education but did not continue")),
            ('enrolled in ABLN', _("Enrolled in ABLN")),
        ),
        verbose_name=_('Education status')
    )

    id_type = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=Choices(
            ('UNHCR Registered', _('UNHCR Registered')),
            ('UNHCR Recorded', _("UNHCR Recorded")),
            ('Syrian national ID', _("Syrian national ID")),
            ('Palestinian national ID', _("Palestinian national ID")),
            ('Lebanese national ID', _("Lebanese national ID")),
            ('Other nationality', _("Other nationality")),
            ('Child have no ID', _("Child have no ID"))
        ),
        verbose_name=_('Child ID type')
    )

    case_number = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name=_('Case number')
    )
    case_number_confirm = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name=_('Case number confirm')
    )

    individual_case_number = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name=_('Individual Case number')
    )
    individual_case_number_confirm = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name=_('Individual Case number confirm')
    )

    recorded_number = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name=_('Recorded number')
    )
    recorded_number_confirm = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name=_('Recorded number confirm')
    )

    other_nationality = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name=_('Specify the nationality')
    )

    national_number = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name=_('Lebanese ID number ')
    )
    national_number_confirm = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name=_('Lebanese ID number confirm')
    )
    syrian_national_number = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name=_('Syrian ID number ')
    )
    syrian_national_number_confirm = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name=_('Syrian ID number confirm')
    )
    sop_national_number = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name=_('Palestinian ID number ')
    )
    sop_national_number_confirm = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name=_('Palestinian ID number confirm')
    )
    no_child_id_confirmation = models.CharField(max_length=50, blank=True, null=True, )
    no_parent_id_confirmation = models.CharField(max_length=50, blank=True, null=True, )

    parent_case_number = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name=_('Case number')
    )
    parent_case_number_confirm = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name=_('Case number confirm')
    )

    parent_individual_case_number = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name=_('Individual Case number')
    )
    parent_individual_case_number_confirm = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name=_('Individual Case number confirm')
    )

    parent_national_number = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name=_('Lebanese ID number ')
    )
    parent_national_number_confirm = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name=_('Lebanese ID number confirm')
    )
    parent_syrian_national_number = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name=_('Syrian ID number ')
    )
    parent_syrian_national_number_confirm = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name=_('Syrian ID number confirm')
    )
    parent_sop_national_number = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name=_('Palestinian ID number ')
    )
    parent_sop_national_number_confirm = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name=_('Palestinian ID number confirm')
    )
    parent_other_number = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name=_('ID number ')
    )
    parent_other_number_confirm = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name=_('ID number confirm')
    )
    other_number = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name=_('Child ID number ')
    )
    other_number_confirm = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name=_('Child ID number confirm')
    )
    main_caregiver = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=MAIN_CAREGIVER,
        verbose_name=_('Main Caregiver')
    )

    main_caregiver_nationality = models.ForeignKey(
        Nationality,
        blank=False, null=True,
        related_name='+',
        verbose_name=_('Main Caregiver Nationality')
    )

    other_caregiver_relationship = models.CharField(
        max_length=500,
        blank=True,
        null=True,
        verbose_name=_('Other Caregiver Relationship')
    )

    caretaker_first_name = models.CharField(
        max_length=500,
        blank=False,
        null=True,
        verbose_name=_('Caretaker First Name')
    )
    caretaker_middle_name = models.CharField(
        max_length=500,
        blank=False,
        null=True,
        verbose_name=_('Caretaker Middle Name')
    )
    caretaker_last_name = models.CharField(
        max_length=500,
        blank=False,
        null=True,
        verbose_name=_('Caretaker Last Name')
    )
    caretaker_mother_name = models.CharField(
        max_length=500,
        blank=False,
        null=True,
        verbose_name=_('Caretaker Mother Name')
    )
    caretaker_birthday_year = models.CharField(
        max_length=4,
        blank=True,
        null=True,
        default=0,
        choices=((str(x), x) for x in range(1940, CURRENT_YEAR - 18)),
        verbose_name=_('Caretaker birthday year')
    )
    caretaker_birthday_month = models.CharField(
        max_length=2,
        blank=True,
        null=True,
        default=0,
        choices=MONTHS,
        verbose_name=_('Caretaker birthday month')
    )
    caretaker_birthday_day = models.CharField(
        max_length=2,
        blank=True,
        null=True,
        default=0,
        choices=((str(x), x) for x in range(1, 32)),
        verbose_name=_('Caretaker birthday day')
    )

    referral_programme_type_1 = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=Choices(
            ('CP (PSS and/or Case Management)', _('CP (PSS and/or Case Management)')),
            ('Health', _('Health')),
            ('WASH', _('WASH')),
            ('Specialized Services', _('Specialized Services')),
            ('Other', _('Other')),
            ('No need', _('No need')),
        ),
        verbose_name=_('Programme Type')
    )
    referral_partner_1 = models.CharField(
        max_length=500,
        blank=True,
        null=True,
        verbose_name=_('School / Center')
    )
    referral_date_1 = models.DateField(
        blank=True,
        null=True,
        verbose_name=_('Referral date')
    )
    confirmation_date_1 = models.DateField(
        blank=True,
        null=True,
        verbose_name=_('Date when the receiving organization confirms accepting the child (or child receiving service)')
    )

    referral_programme_type_2 = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=Choices(
            ('CP (PSS and/or Case Management)', _('CP (PSS and/or Case Management)')),
            ('Health', _('Health')),
            ('WASH', _('WASH')),
            ('Specialized Services', _('Specialized Services')),
            ('Other', _('Other')),
            ('No need', _('No need')),
        ),
        verbose_name=_('Programme Type')
    )
    referral_partner_2 = models.CharField(
        max_length=500,
        blank=True,
        null=True,
        verbose_name=_('School / Center')
    )
    referral_date_2 = models.DateField(
        blank=True,
        null=True,
        verbose_name=_('Referral date')
    )
    confirmation_date_2 = models.DateField(
        blank=True,
        null=True,
        verbose_name=_('Date when the receiving organization confirms accepting the child (or child receiving service)')
    )

    referral_programme_type_3 = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=Choices(
            ('CP (PSS and/or Case Management)', _('CP (PSS and/or Case Management)')),
            ('Health', _('Health')),
            ('WASH', _('WASH')),
            ('Specialized Services', _('Specialized Services')),
            ('Other', _('Other')),
            ('No need', _('No need')),
        ),
        verbose_name=_('Programme Type')
    )
    referral_partner_3 = models.CharField(
        max_length=500,
        blank=True,
        null=True,
        verbose_name=_('School / Center')
    )
    referral_date_3 = models.DateField(
        blank=True,
        null=True,
        verbose_name=_('Referral date')
    )
    confirmation_date_3 = models.DateField(
        blank=True,
        null=True,
        verbose_name=_('Date when the receiving organization confirms accepting the child (or child receiving service)')
    )
    additional_comments = models.TextField(
        blank=True, null=True,
        verbose_name=_('Comments')
    )
    child_dropout = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        choices=YES_NO,
        verbose_name=_('Has the child dropped out of the program?')
    )

    child_dropout_specify = models.TextField(
        blank=True, null=True,
        verbose_name=_('Please specify')
    )

    caregiver_trained_parental_engagement = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=Choices(
            ('', '----------'),
            ('Mother Only', _('Mother Only')),
            ('Father Only', _('Father Only')),
            ('Both Mother and Father', _('Both Mother and Father')),
            ('None', _('None')),
            ('Other', _('Other')),
            ('Not begun yet', _('Not begun yet')),
        ),
        verbose_name=_('Have the Caregivers been trained on the Parental Engagement Curriculum? ')
    )
    @property
    def student_fullname(self):
        if self.student:
            return self.student.full_name
        return ''

    @property
    def student_age(self):
        if self.student:
            return self.student.age
        return 0

    def get_absolute_url(self):
        return '/inclusion/edit/%d/' % self.pk

    def __unicode__(self):
        if self.student:
            return self.student.__unicode__()
        return str(self.id)

    class Meta:
        ordering = ['id']
        verbose_name = "Disability specialized"
        verbose_name_plural = "Disability specialized"
