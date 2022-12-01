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

PACKAGE_TYPES = Choices(
    ('Core-Package', _('Core Package')),
    ('Walk-in-OOSC', _('Walk-in OOSC')),
    ('Walk-in-In-School', _('Walk-in In School')),
)

PACKAGE_CATEGORIES = Choices(
    ('Education', _('Education')),
    ('Health', _('Health')),
    ('', _('')),
    ('', _('')),
    ('', _('')),
    ('', _('')),
    ('', _('')),
)

YES_NO = Choices(
    ('Yes', _("Yes")),
    ('No', _("No"))
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

    HAVE_LABOUR = Choices(
            ('No', _('No')),
            ('Yes - Morning', _('Yes - Morning')),
            ('Yes - Afternoon', _('Yes - Afternoon')),
            ('Yes - All day', _('Yes - All day')),
    )
    LABOURS = Choices(
            ('', '----------'),
            ('Agriculture', _('Agriculture')),
            ('Building', _('Building')),
            ('Manufacturing', _('Manufacturing')),
            ('Retail / Store', _('Retail / Store')),
            ('Begging', _('Begging')),
            ('Other services', _('Other services')),
            # ('other', _('Other')),
    )
    LABOUR_INCOME = Choices(
            ('', '----------'),
            ('thousand_or_less', _('10,000 LBP or less')),
            ('eleven_thousand_to_twenty_five', _('11,000 to 25,000 LBP')),
            ('twenty_six_thousand_to_fifty', _('26,000 to 50,000 LBP')),
            ('more_than_fifty', _('More than 50,000 LBP'))
    )
    IDENTIFICATION_SOURCE = Choices(
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
    )
    CASH_SUPPORT_PROGRAMMES = Choices(
            ('', '----------'),
            ('Haddi', _('Haddi')),
            ('Education Cash assistance', _('Education Cash assistance')),
            ('UNHCR cash assistance', _('UNHCR cash assistance')),
            ('WFP cash assistance', _('WFP cash assistance')),
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
        verbose_name=_('Please specify (hotel, restaurant, transport, personal '
                       'services such as cleaning, hair care, cooking and childcare)')
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
        choices=IDENTIFICATION_SOURCE,
        verbose_name=_('Source of referral of the child to MSCC')
    )
    cash_support_programmes = ArrayField(
        models.CharField(
            choices=CASH_SUPPORT_PROGRAMMES,
            max_length=100,
            blank=True,
            null=True,
        ),
        blank=True,
        null=True,
        verbose_name=_('Cash support programmes that child is already benefitting from')
    )
    type = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name=_('Type')
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


class ProvidedServices(models.Model):

    TYPES = Choices(
            ('Core-Package', _('Core Package')),
            ('Walk-in-OOSC', _('Walk-in OOSC')),
            ('Walk-in-In-School', _('Walk-in In School')),
    )

    name = models.CharField(
        max_length=250,
        blank=False,
        null=False,
    )
    registration = models.ForeignKey(
        Registration,
        blank=False, null=True,
        related_name='+',
    )
    child = models.ForeignKey(
        Student,
        blank=False, null=True,
        related_name='+',
    )
    type = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name=_('Type')
    )
    completed = models.BooleanField(blank=True, default=False)
    required = models.BooleanField(blank=True, default=False)
    completion_date = models.DateField(
        blank=True,
        null=True,
        verbose_name=_('Completion date')
    )

    class Meta:
        ordering = ['id']
        verbose_name = "Provided Service"
        verbose_name_plural = "Provided Services"


class Packages(models.Model):

    name = models.CharField(
        max_length=250,
        blank=False,
        null=False,
    )
    type = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=PACKAGE_TYPES,
        verbose_name=_('Type')
    )
    category = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=PACKAGE_CATEGORIES,
        verbose_name=_('Type')
    )
    required = models.BooleanField(blank=True, default=False)
    age = models.IntegerField(blank=True, null=True)

    class Meta:
        ordering = ['id']
        verbose_name = "Package"
        verbose_name_plural = "Packages"


class Inclusion(TimeStampedModel):

    PARENTAL_ENGAGEMENT = Choices(
        ('Mother Only', _('Mother Only')),
        ('Father Only', _('Father Only')),
        ('Both', _('Both')),
        ('No one', _('No one')),
        ("Haven't started yet", _("Haven't started yet")),
    )

    dropout = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=YES_NO,
        verbose_name=_('Dropout')
    )
    parental_engagement = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=PARENTAL_ENGAGEMENT,
        verbose_name=_('Parental Engagement Curriculum')
    )

    class Meta:
        ordering = ['id']
        verbose_name = "Inclusion"
        verbose_name_plural = "Inclusions"


class DigitalService(models.Model):

    registration = models.ForeignKey(
        Registration,
        blank=False, null=True,
        related_name='+',
    )

    using_akelius = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=YES_NO,
        verbose_name=_('Is the child using Akelius?')
    )

    using_lp = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=YES_NO,
        verbose_name=_('Is the child using Learning Passport?')
    )

    class Meta:
        ordering = ['id']
        verbose_name = "Digital"
        verbose_name_plural = "Digital"


class PSSService(models.Model):

    LIVING_ARRANGEMENT = Choices(
        ('Unaccompanied or Separated Child', _('Unaccompanied or Separated Child')),
        ('Living with single parent/caregiver', _('Living with single parent/caregiver')),
        ('Living with Mother/women-headed Household ', _('Living with Mother/women-headed Household')),
        ('Child-headed Household', _('Child-headed Household')),
        ('Main caregiver is ill/disabled', _('Main caregiver is ill/disabled')),
    )

    CHILD_VULNERABILITY = Choices(
        ('Clear signs of neglect', _('Clear signs of neglect')),
        ('Clear signs of distress', _('Clear signs of distress')),
        ('Clear signs of physical maltreatment/damage and/or injuries',
         _('Clear signs of physical maltreatment/damage and/or injuries')),
    )

    OUT_SCHOOL_REASONS = Choices(
        ('Fear of bullying, discrimination or violence at school or on the way to school',
         _('Fear of bullying, discrimination or violence at school or on the way to school')),
        ('The child needs to work', _('The child needs to work')),
        ('The child needs to stay at home to support the family with chores',
         _('The child needs to stay at home to support the family with chores')),
        ('Disability', _('Disability')),
    )

    registration = models.ForeignKey(
        Registration,
        blank=False, null=True,
        related_name='+',
    )

    child_registered = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=YES_NO,
        verbose_name=_('Is the child registered/ have birth registration?')
    )

    child_living_arrangement = models.CharField(
        max_length=250,
        blank=True,
        null=True,
        choices=LIVING_ARRANGEMENT,
        verbose_name=_("What is the child's living arrangement?")
    )

    child_vulnerability = models.CharField(
        max_length=250,
        blank=True,
        null=True,
        choices=CHILD_VULNERABILITY,
        verbose_name=_("What is the child's living arrangement?")
    )

    child_out_school_reasons = models.CharField(
        max_length=250,
        blank=True,
        null=True,
        choices=OUT_SCHOOL_REASONS,
        verbose_name=_("Reasons for a child being out of school")
    )

    caregivers_distress = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=YES_NO,
        verbose_name=_('Do you feel distressed and anxious?')
    )

    caregivers_additional_parenting = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=YES_NO,
        verbose_name=_('If yes, would you like any additional parenting or psychosocial support?')
    )

    child_distress = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=YES_NO,
        verbose_name=_('Are any of the children in your HH experiencing any '
                       'signs of distress or negative mental health symptoms ?')
    )

    child_additional_parenting = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=YES_NO,
        verbose_name=_('If yes, do you need additional support '
                       'for taking care or better dealing with your children?')
    )

    class Meta:
        ordering = ['id']
        verbose_name = "Service"
        verbose_name_plural = "Services"


class HealthNutrition(TimeStampedModel):
    DEVELOPMENT_DELAYS = Choices(
        ('Mental', _('Mental')),
        ('Cognitive', _('Cognitive')),
        ('Neurological', _('Neurological')),
        ('no', _('No')),
    )
    registration = models.ForeignKey(
        Registration,
        blank=False, null=True,
        related_name='+',
    )
    baby_breastfed = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        choices=YES_NO,
        verbose_name=_('Is the baby being Breastfed?')
    )
    infant_exclusively_breastfed = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        choices=YES_NO,
        verbose_name=_('if yes, is it exclusively breastfeeding for infants between 0-6 months?')
    )
    eat_solid_food = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        choices=YES_NO,
        verbose_name=_('Did the child start to eat solid food?')
    )
    age_eat_solid_food = models.TextField(
        blank=True, null=True,
        verbose_name=_('If yes, at which age ?')
    )
    child_vaccinated = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        choices=YES_NO,
        verbose_name=_('Is the child being vaccinated as per the National vaccination calendar?')
    )
    development_delays_identified = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        choices=DEVELOPMENT_DELAYS,
        verbose_name=_('Any mental , cognitive or neurological development delays is being identified?')
    )
    eating_minimum_meals = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        choices=YES_NO,
        verbose_name=_('Is the child eating 3 minimum meals per day?')
    )
    positive_parenting = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        choices=YES_NO,
        verbose_name=_('positive parenting and dealing with difficult children without the use of harsh punishment?')
    )
    respond_stressful_events = models.TextField(
        blank=True, null=True,
        verbose_name=_('how children of different ages respond to and understand stressful and traumatic events?')
    )

    class Meta:
        ordering = ['id']
        verbose_name = "Health"
        verbose_name_plural = "Health"


class Education(TimeStampedModel):
    EDUCATION_STATUS = Choices(
        ('', '----------'),
        ('never registered', _('never registered in any formal school before')),
        ('Was registered in formal school but didnt continue',
         _('Was registered in formal school but didn’t continue')),
        ('Was registered in non formal program and was referred to MSCC',
         _('Was registered in non formal program and was referred to MSCC')),
        ('Was registered in non formal program but did not continue',
         _('Was registered in non formal program but did not continue')),
        ('Was enrolled in TVET Programs', _('Was enrolled in TVET Programse')),
        ('no', _('No')),
    )
    DROPOUT_PROGRAM = Choices(
        ('', '----------'),
        ('Was registered in CBECE level 1-2', _('Was registered in CBECE level 1-2')),
        ('Was registered in BLN program', _('Was registered in BLN program')),
        ('Was registered in ALP program and didnt continue', _('Was registered in ALP program and didnt continue')),
        ('Was enrolled in Dirasa', _('Was enrolled in Dirasa')),
        ('other', _('Other')),
    )
    EDUCATION_PROGRAM = Choices(
        ('', '----------'),
        ('BLN Level 1', _('BLN Level 1')),
        ('BLN Level 2', _('BLN Level 2')),
        ('YBLN', _('YBLN')),
        ('YFNL', _('YFNL')),
        ('CBECE Level 3', _('CBECE Level 3')),
        ('Retention Support', _('Retention Support')),
    ),
    SCHOOL_SHIFTS = Choices(
        ('', _('----------')),
        ('first', _('First shift')),
        ('second', _('Second shift')),
    )
    REGISTRATION_LEVEL = (
        ('', '----------'),
        ('level_one', _('Level one')),
        ('level_two', _('Level two')),
        ('level_three', _('Level three')),
        ('level_four', _('Level four')),
        ('level_five', _('Level five')),
        ('level_six', _('Level six'))
    )
    SUPPORT_NEEDED = Choices(
        ('', _('----------')),
        ('foreign languages', _('Foreign Languages')),
        ('arabic', _('Arabic')),
        ('math', _('Math')),
        ('sciences', _('Sciences')),
    )
    registration = models.ForeignKey(
        Registration,
        blank=False, null=True,
        related_name='+',
    )
    education_status = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        choices=EDUCATION_STATUS,
        verbose_name=_('Child’s educational level when registering for the round')
    )
    dropout_date = models.DateField(
        blank=True,
        null=True,
        verbose_name=_('Please Specify dropout date from school')
    )
    dropout_program = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        choices=DROPOUT_PROGRAM,
        verbose_name=_('Dropout Program')
    )
    dropout_program_specify = models.TextField(
        blank=True, null=True,
        verbose_name=_('please specify')
    )
    education_program = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        choices=EDUCATION_PROGRAM,
        verbose_name=_('Education Program')
    )
    registration_date = models.DateField(
        blank=True,
        null=True,
        verbose_name=_('Date of registration in the round')
    )
    # RS fields
    school = models.ForeignKey(
        School,
        blank=False, null=True,
        related_name='+',
        verbose_name=_('Name of public School')
    )
    foreign_language_grade = models.IntegerField(
        blank=True,
        null=True,
        choices=((x, x) for x in range(0, 100)),
        verbose_name=_('Foreign Languages grade')
    )
    arabic_grade = models.IntegerField(
        blank=True,
        null=True,
        choices=((x, x) for x in range(0, 100)),
        verbose_name=_('Arabic grade')
    )
    math_grade = models.IntegerField(
        blank=True,
        null=True,
        choices=((x, x) for x in range(0, 100)),
        verbose_name=_('Math grade')
    )
    sciences_grade = models.IntegerField(
        blank=True,
        null=True,
        choices=((x, x) for x in range(0, 100)),
        verbose_name=_('Sciences grade')
    )
    shift = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        choices=SCHOOL_SHIFTS,
        verbose_name=_('First or Second shift schools')
    )
    grade_level = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=REGISTRATION_LEVEL,
        verbose_name=_('Grade level')
    )
    support_needed = ArrayField(
        models.CharField(
            choices=SUPPORT_NEEDED,
            max_length=100,
            blank=True,
            null=True,
        ),
        blank=True,
        null=True,
        verbose_name=_('Needed support')
    )

    class Meta:
        ordering = ['id']
        verbose_name = "Education"
        verbose_name_plural = "Education"
