from __future__ import unicode_literals, absolute_import, division

from django.db import models
from django.conf import settings
from django.utils.translation import ugettext as _
from django.contrib.postgres.fields import ArrayField, JSONField
from model_utils import Choices
from model_utils.models import TimeStampedModel

from student_registration.child.models import Child
from student_registration.locations.models import Center
from student_registration.schools.models import (
    School,
    PartnerOrganization
)

PACKAGE_TYPES = Choices(
    ('Core-Package', _('Core Package')),
    ('Walk-in-OOSC', _('Walk-in OOSC')),
    ('Walk-in-In-School', _('Walk-in In School')),
)

PACKAGE_CATEGORIES = Choices(
    ('Education', 'Education'),
    ('Youth', 'Youth'),
    ('Health & Nutrition', 'Health & Nutrition'),
    ('Child Protection', 'Child Protection'),
    ('Social Protection', 'Social Protection'),
)

YES_NO = Choices(
    ('', '----------'),
    ('Yes', _("Yes")),
    ('No', _("No"))
)


class Registration(TimeStampedModel):

    YES_NO = Choices(
        ('', '----------'),
        ('Yes', _("Yes")),
        ('No', _("No"))
    )

    HAVE_LABOUR = Choices(
        ('', '----------'),
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
    )
    LABOUR_INCOME = Choices(
            ('', '----------'),
            ('10,000 LBP or less', _('10,000 LBP or less')),
            ('11,000 to 25,000 LBP', _('11,000 to 25,000 LBP')),
            ('26,000 to 50,000 LBP', _('26,000 to 50,000 LBP')),
            ('More than 50,000 LBP', _('More than 50,000 LBP'))
    )
    IDENTIFICATION_SOURCE = Choices(
            ('', '----------'),
            ('Dirassa', _('Dirassa')),
            ('Awareness Session', _('Awareness Session')),
            ('Child\'s parents', _('Child\'s parents')),
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
        Child,
        blank=False, null=True,
        related_name='+',
        verbose_name=_('Child')
    )
    child_outreach = models.IntegerField(blank=True, null=True)
    student_old = models.IntegerField(blank=True, null=True)
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
    labour_type = models.CharField(
        max_length=100,
        choices=LABOURS,
        blank=True,
        null=True,
        verbose_name=_('What is the type of work?')
    )
    labour_type_specify = models.CharField(
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
    source_of_identification_specify = models.TextField(
        blank=True, null=True,
        verbose_name=_('please specify')
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
        return '/MSCC/Child-Profile/%d/' % self.pk

    def __str__(self):
        if self.child:
            return self.child.__str__()
        return str(self.id)

    def __unicode__(self):
        if self.child:
            return self.child.__unicode__()
        return str(self.id)

    class Meta:
        ordering = ['-id']
        verbose_name = "MSCC Registration"
        verbose_name_plural = "MSCC Registrations"


class EducationHistory(TimeStampedModel):

    child = models.IntegerField(blank=True, null=True)
    student_old = models.IntegerField(blank=True, null=True)
    registration_id = models.IntegerField(blank=True, null=True)

    programme_type = models.CharField(
        max_length=100,
        blank=True,
        null=True,
    )
    programme_id = models.IntegerField(blank=True, null=True)

    class Meta:
        ordering = ['-id']
        verbose_name = "Education History"
        verbose_name_plural = "Education Histories"


class ProvidedServices(models.Model):

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
    type = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name=_('Type')
    )
    category = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name=_('Category')
    )
    service_id = models.IntegerField(blank=True, null=True)
    completed = models.BooleanField(blank=True, default=False)
    required = models.BooleanField(blank=True, default=False)
    completion_date = models.DateField(
        blank=True,
        null=True,
        verbose_name=_('Completion date')
    )

    def __unicode__(self):
        return self.name

    def __str__(self):
        return self.name

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
        verbose_name=_('Category')
    )
    required = models.BooleanField(blank=True, default=False)
    age = models.IntegerField(blank=True, null=True)

    def __unicode__(self):
        return self.name

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['id']
        verbose_name = "Package"
        verbose_name_plural = "Packages"


class InclusionService(TimeStampedModel):

    PARENTAL_ENGAGEMENT = Choices(
        ('', '----------'),
        ('Mother Only', _('Mother Only')),
        ('Father Only', _('Father Only')),
        ('Both', _('Both')),
        ('No one', _('No one')),
        ("Haven't started yet", _("Haven't started yet")),
    )

    registration = models.ForeignKey(
        Registration,
        blank=False, null=True,
        related_name='+',
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
        ('', '----------'),
        ('Unaccompanied or Separated Child', _('Unaccompanied or Separated Child')),
        ('Living with single parent/caregiver', _('Living with single parent/caregiver')),
        ('Living with Mother/women-headed Household ', _('Living with Mother/women-headed Household')),
        ('Child-headed Household', _('Child-headed Household')),
        ('Main caregiver is ill/disabled', _('Main caregiver is ill/disabled')),
    )

    CHILD_VULNERABILITY = Choices(
        ('', '----------'),
        ('Clear signs of neglect', _('Clear signs of neglect')),
        ('Clear signs of distress', _('Clear signs of distress')),
        ('Clear signs of physical maltreatment/damage and/or injuries',
         _('Clear signs of physical maltreatment/damage and/or injuries')),
    )

    OUT_SCHOOL_REASONS = Choices(
        ('', '----------'),
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
        verbose_name = "PSS Service"
        verbose_name_plural = "PSS Services"


class HealthNutritionService(TimeStampedModel):

    DEVELOPMENT_DELAYS = Choices(
        ('', '----------'),
        ('Mental', _('Mental')),
        ('Cognitive', _('Cognitive')),
        ('Neurological', _('Neurological')),
        ('No', _('No')),
    )
    AGE_EAT_SOLID_FOOD = Choices(
        ('', '----------'),
        ('4 months', _('4 months')),
        ('5 months', _('5 months')),
        ('6 months', _('6 months')),
        ('7 months', _('7 months')),
        ('8 months', _('8 months')),
        ('9 months', _('9 months')),
        ('10 months', _('10 months')),
        ('11 months', _('11 months')),
        ('12 months', _('12 months')),
        ('13 months', _('13 months')),
        ('14 months', _('14 months')),
        ('15 months', _('15 months')),
        ('16 months', _('16 months')),
        ('17 months', _('17 months')),
        ('18 months', _('18 months')),
        ('19 months', _('19 months')),
        ('20 months', _('20 months')),
        ('21 months', _('21 months')),
        ('22 months', _('22 months')),
        ('23 months', _('23 months')),
        ('24 months', _('24 months'))
    )
    registration = models.ForeignKey(
        Registration,
        blank=False, null=True,
        related_name='+',
    )
    # Caregivers of children 0-2
    baby_breastfed = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        choices=YES_NO,
        verbose_name=_('Is the baby being Breastfed?')
    )
    # Caregivers of children 0-2
    infant_exclusively_breastfed = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        choices=YES_NO,
        verbose_name=_('if yes, is it exclusively breastfeeding for infants between 0-6 months?')
    )
    # Caregivers of children 0-2
    eat_solid_food = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        choices=YES_NO,
        verbose_name=_('Did the child start to eat solid food?')
    )
    # Caregivers of children 0-2
    age_eat_solid_food = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        choices=AGE_EAT_SOLID_FOOD,
        verbose_name=_('If yes, at which age ?')
    )
    # Caregivers of children 0-2 - children 3-5 - children 5-18
    child_vaccinated = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        choices=YES_NO,
        verbose_name=_('Is the child being vaccinated as per the National vaccination calendar?')
    )
    # Caregivers of children 0-2 - children 3-5
    development_delays_identified = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        choices=DEVELOPMENT_DELAYS,
        verbose_name=_('Any mental , cognitive or neurological development delays is being identified?')
    )

    # Caregivers of children 3-5 - children 5-18
    eating_minimum_meals = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        choices=YES_NO,
        verbose_name=_('Is the child eating 3 minimum meals per day?')
    )
    # Caregivers of children 3-5
    positive_parenting = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        choices=YES_NO,
        verbose_name=_('positive parenting and dealing with difficult children without the use of harsh punishment?')
    )
    # Caregivers of children 5-18
    respond_stressful_events = models.TextField(
        blank=True, null=True,
        verbose_name=_('How children of different ages respond to and understand stressful and traumatic events?')
    )

    class Meta:
        ordering = ['id']
        verbose_name = "Health & Nutrition Service"
        verbose_name_plural = "Health & Nutrition Services"


class EducationService(TimeStampedModel):

    EDUCATION_STATUS = Choices(
        ('', '----------'),
        ('Never registered in any formal school before', _('Never registered in any formal school before')),
        ('Was registered in formal school but didn\'t continue',
         _('Was registered in formal school but didn\'t continue')),
        ('Was registered in non formal program and was referred to MSCC',
         _('Was registered in non formal program and was referred to MSCC')),
        ('Was registered in non formal program but didn\'t continue',
         _('Was registered in non formal program but didn\'t continue')),
        ('Was enrolled in TVET Programs', _('Was enrolled in TVET Programse')),
        ('No', _('No')),
    )
    DROPOUT_PROGRAM = Choices(
        ('', '----------'),
        ('Was registered in CBECE level 1-2', _('Was registered in CBECE level 1-2')),
        ('Was registered in BLN program', _('Was registered in BLN program')),
        ('Was registered in ALP program and didn\'t continue', _('Was registered in ALP program and didn\'t continue')),
        ('Was enrolled in Dirasa', _('Was enrolled in Dirasa')),
        ('Other', _('Other')),
    )
    EDUCATION_PROGRAM = Choices(
        ('', '----------'),
        ('BLN Level 1', _('BLN Level 1')),
        ('BLN Level 2', _('BLN Level 2')),
        ('YBLN', _('YBLN')),
        ('YFNL', _('YFNL')),
        ('CBECE Level 3', _('CBECE Level 3')),
        ('Retention Support', _('Retention Support')),
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
        verbose_name=_('Child\'s educational level when registering for the round')
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
    # @todo not sure about this field
    registration_date = models.DateField(
        blank=True,
        null=True,
        verbose_name=_('Date of registration in the round')
    )

    class Meta:
        ordering = ['id']
        verbose_name = "Education Service"
        verbose_name_plural = "Education Services"


class EducationRSService(TimeStampedModel):

    REGISTRATION_LEVEL = Choices(
        ('', '----------'),
        ('Level one', _('Level one')),
        ('Level two', _('Level two')),
        ('Level three', _('Level three')),
        ('Level four', _('Level four')),
        ('Level five', _('Level five')),
        ('Level six', _('Level six'))
    )
    SUPPORT_NEEDED = Choices(
        ('Foreign Languages', _('Foreign Languages')),
        ('Arabic', _('Arabic')),
        ('Math', _('Math')),
        ('Sciences', _('Sciences')),
    )
    SCHOOL_SHIFTS = Choices(
        ('', _('----------')),
        ('First shift', _('First shift')),
        ('Second shift', _('Second shift')),
    )
    registration = models.ForeignKey(
        Registration,
        blank=False, null=True,
        related_name='+',
    )
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
        verbose_name=_('Foreign Language\'s grade')
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
        verbose_name = "Education RS Service"
        verbose_name_plural = "Education RS Services"


class EducationAssessment(TimeStampedModel):
    MODALITY = Choices(
        ('', '----------'),
        ('Online Forms', _('Online Forms')),
        ('Phone call/WhatsApp', _('Phone call/WhatsApp')),
        ('Asking Parents', _('Asking Parents')),
        ('Offline (F2F)', _('Offline (F2F)'))
    )
    PARTICIPATION = Choices(
        ('', '----------'),
        ('No Absence', _('No Absence')),
        ('Absence for less than 5 days/equivlant remote learning sessions',
         _('Absence for less than 5 days/equivlant remote learning sessions')),
        ('Absence for 5-10 days /equivlant remote learning sessions',
         _('Absence for 5-10 days /equivlant remote learning sessions')),
        ('Absence for 10-15 days /equivlant remote learning sessions',
         _('Absence for 10-15 days /equivlant remote learning sessions')),
        ('Absence for 15-25 days /equivlant remote learning sessions',
         _('Absence for 15-25 days /equivlant remote learning sessions')),
        ('Absence for more than 25 days / equivlant remote learning sessions',
         _('Absence for more than 25 days / equivlant remote learning sessions')),
    )
    BARRIERS = Choices(
        ('', '----------'),
        ('Working Full-time to support family', _('Working Full-time to support family')),
        ('Availability of Electronic Device', _('Availability of Electronic Device')),
        ('Sickness', _('Sickness')),
        ('Family changed address in Lebanon', _('Family changed address in Lebanon')),
        ('Marriage/engagement', _('Marriage/engagement')),
        ('No barriers', _('No barriers')),
        ('Enrolled in Formal Education', _('Enrolled in Formal Education')),
        ('Seasonal Work', _('Seasonal Work')),
        ('Internet Connectivity', _('Internet Connectivity')),
        ('Security Concerns', _('Security Concerns')),
        ('Family moved back to Syria', _('Family moved back to Syria')),
        ('No Interest in pursuing programme', _('No Interest in pursuing programme')),
        ('Violence and Bullying', _('Violence and Bullying')),
        ('Other', _('Other')),
    )
    registration = models.ForeignKey(
        Registration,
        blank=False, null=True,
        related_name='+',
    )
    pre_attended_arabic = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=YES_NO,
        verbose_name=_('Did the Child Undertake Arabic Language Development Assessment')
    )
    pre_modality_arabic = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        choices=MODALITY,
        verbose_name=_('Modality')
    )
    pre_arabic_grade = models.IntegerField(
        blank=True,
        null=True,
        verbose_name=_('Grade')
    )
    pre_attended_language = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=YES_NO,
        verbose_name=_('Did the Child Undertake Foreign Language Development Assessment')
    )
    pre_modality_language = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        choices=MODALITY,
        verbose_name=_('Modality')
    )
    pre_language_grade = models.IntegerField(
        blank=True,
        null=True,
        verbose_name=_('Grade')
    )
    pre_attended_math = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=YES_NO,
        verbose_name=_('Did the Child Undertake Cognitive Development - Mathematics test')
    )
    pre_modality_math = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        choices=MODALITY,
        verbose_name=_('Modality')
    )
    pre_math_grade = models.IntegerField(
        blank=True,
        null=True,
        verbose_name=_('Grade')
    )
    participation = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=PARTICIPATION,
        verbose_name=_('Child Level of participation / Absence')
    )
    barriers = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=BARRIERS,
        verbose_name=_('The main barriers affecting the child\'s '
                       'daily attendance/participation, performance, or causing drop-out')
    )
    barriers_other = models.TextField(
        blank=True, null=True,
        verbose_name=_('Please specify')
    )
    post_test_done = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=YES_NO,
        verbose_name=_('Did the child undertake the Post tests?')
    )
    school_year_completed = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=YES_NO,
        verbose_name=_('Did the child fully complete the school year?')
    )
    post_attended_arabic = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=YES_NO,
        verbose_name=_('Did the Child Undertake Arabic Language Development Assessment')
    )
    post_modality_arabic = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        choices=MODALITY,
        verbose_name=_('Modality')
    )
    post_arabic_grade = models.IntegerField(
        blank=True,
        null=True,
        verbose_name=_('Grade')
    )
    post_attended_language = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=YES_NO,
        verbose_name=_('Did the Child Undertake Foreign Language Development Assessment')
    )
    post_modality_language = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        choices=MODALITY,
        verbose_name=_('Modality')
    )
    post_language_grade = models.IntegerField(
        blank=True,
        null=True,
        verbose_name=_('Grade')
    )
    post_attended_math = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=YES_NO,
        verbose_name=_('Did the Child Undertake Cognitive Development - Mathematics test')
    )
    post_modality_math = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        choices=MODALITY,
        verbose_name=_('Modality')
    )
    post_math_grade = models.IntegerField(
        blank=True,
        null=True,
        verbose_name=_('Grade')
    )

    @property
    def arabic_improvement(self):
        if self.pre_arabic_grade and self.post_arabic_grade:
            try:
                return '{}{}'.format(
                    round(((float(self.post_arabic_grade) - float(self.pre_arabic_grade)) /
                           float(self.pre_arabic_grade)) * 100.0, 2), '%')
            except ZeroDivisionError:
                return 0.0
        return 0.0

    @property
    def math_improvement(self):
        if self.pre_math_grade and self.post_math_grade:
            try:
                return '{}{}'.format(
                    round(((float(self.post_math_grade) - float(self.pre_math_grade)) /
                           float(self.pre_math_grade)) * 100.0, 2), '%')
            except ZeroDivisionError:
                return 0.0
        return 0.0

    @property
    def language_improvement(self):
        if self.pre_language_grade and self.post_language_grade:
            try:
                return '{}{}'.format(
                    round(((float(self.post_language_grade) - float(self.pre_language_grade)) /
                           float(self.pre_language_grade)) * 100.0, 2), '%')
            except ZeroDivisionError:
                return 0.0
        return 0.0

    class Meta:
        ordering = ['id']
        verbose_name = "Education Assessment"
        verbose_name_plural = "Education Assessments"


class EducationProgrammeAssessment(TimeStampedModel):

    PROGRAMME_TYPE = Choices(
        ('', '----------'),
        ('BLN Level 1', _('BLN Level 1')),
        ('BLN Level 2', _('BLN Level 2')),
        ('YBLN', _('YBLN')),
        ('YFNL', _('YFNL')),
        ('CBECE Level 3', _('CBECE Level 3')),
        ('Retention Support', _('Retention Support')),
    )
    registration = models.ForeignKey(
        Registration,
        blank=False, null=True,
        related_name='+',
    )
    pre_test = JSONField(blank=True, null=True)
    post_test = JSONField(blank=True, null=True)
    programme_type = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=PROGRAMME_TYPE,
        verbose_name=_('Education Programme Type')
    )

    class Meta:
        ordering = ['id']
        verbose_name = "Education Programme Assessment"
        verbose_name_plural = "Education Programme Assessments"


class YouthKitService(TimeStampedModel):

    VOLUNTEERING = Choices(
        ('', '----------'),
        ('Outreach', _('Outreach')),
        ('Data entry', _('Data entry')),
        ('Admin work', _('Admin work')),
        ('Awareness raising sessions', _('Awareness raising sessions')),
        ('Empowerment and leadership', _('Empowerment and leadership')),
        ('Other', _('Other')),
    )
    TRAINING_MATERIAL = Choices(
        ('', '----------'),
        ('Printed workbook', _('Printed workbook')),
        ('Tablets', _('Tablets')),
        ('Access to digital content (learning Passport) ', _('Access to digital content (learning Passport)')),
        ('Other', _('Other')),
    )
    FUTURE_PATH = Choices(
        ('', '----------'),
        ('Transition to FE', _('Transition to FE')),
        ('Repeat the school year', _('Repeat the school year')),
        ('Refer to a UNICEF Youth Programme (skills training, CBT, GIL)',
         _('Refer to a UNICEF Youth Programme (skills training, CBT, GIL)')),
        ('Transition to TVET', _('Transition to TVET')),
        ('Internship or volunteering opportunity', _('Internship or volunteering opportunity')),
    )
    ATTENDANCE = Choices(
        ('', '----------'),
        ('Full attendance', _('Full attendance')),
        ('Absence for less than 5 days', _('Absence for less than 5 days')),
        ('Absence for more than 5 days', _('Absence for more than 5 days')),
        ('Dropout', _('Dropout')),
    )

    registration = models.ForeignKey(
        Registration,
        blank=False, null=True,
        related_name='+',
    )
    # For Youth
    volunteering_experience = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        choices=YES_NO,
        verbose_name=_('Does the adolescent have any volunteering experience?')
    )
    previous_community_initiative = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        choices=YES_NO,
        verbose_name=_('Was the adolescent part of any previous community based initiative?')
    )
    enrollment_reason = models.CharField(
        max_length=300,
        blank=True,
        null=True,
        verbose_name=_('What is the reason for the adolescent enrollment in the programme?')
    )
    pre_tests_administered = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        choices=YES_NO,
        verbose_name=_('Were pre-tests administered to assess adolescents level?')
    )
    # Youth Assessment
    test_diagnostic_done = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        choices=YES_NO,
        verbose_name=_('Did the adolescent undertake any Post Diagnostic tests?')
    )
    receive_passing_grade = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        choices=YES_NO,
        verbose_name=_('Did the adolescent receive a passing grade for the tests?')
    )
    life_skills_completed = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        choices=YES_NO,
        verbose_name=_('Did the adolescent complete the life skills package?')
    )
    participate_volunteering = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        choices=YES_NO,
        verbose_name=_('Did the adolescent participate in any volunteering '
                       'opportunity during the course of the program?')
    )
    volunteering_specify = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        choices=VOLUNTEERING ,
        verbose_name=_('Please specify the volunteering opportunity')
    )
    social_course = models.CharField(
            max_length=10,
            blank=True,
            null=True,
            choices=YES_NO,
            verbose_name=_('Did the adolescent benefit from any social innovation/entrepreneurship course?')
    )
    yfs_course_completed = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        choices=YES_NO,
        verbose_name=_('Did the adolescent complete the YFS course?')
    )
    training_material = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        choices=TRAINING_MATERIAL,
        verbose_name=_('What training material was provided?')
    )
    future_path = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        choices=FUTURE_PATH,
        verbose_name=_('What is the recommended future path for the adolescent?')
    )
    participate_community_initiatives = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        choices=YES_NO,
        verbose_name=_('Did the adolescent participate/come up in community based initiatives?')
    )
    community_initiatives_specify = models.TextField(
        blank=True, null=True,
        verbose_name=_('What is the initiative?')
    )
    adolescent_attendance = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        choices=ATTENDANCE,
        verbose_name=_('Adolescent attendance')
    )
    adolescent_dropout_reason = models.TextField(
        blank=True, null=True,
        verbose_name=_('Reason for dropout')
    )
    adolescent_dropout_date = models.DateField(
        blank=True,
        null=True,
        verbose_name=_('Dropout Date')
    )

    class Meta:
        ordering = ['id']
        verbose_name = "Youth Kit Service"
        verbose_name_plural = "Youth Kit Services"


class FollowUpService(TimeStampedModel):

    FOLLOW_UP_TYPE = Choices(
        ('', _('----------')),
        ('Phone call', _('Phone call')),
        ('Home Visits', _('Home Visits')),
        ('Caregiver visited the center', _('Caregiver visited the center')),
    )
    FOLLOW_UP_RESULT = Choices(
        ('', '----------'),
        ('Child returned to program', _('Child returned to program')),
        ('Child referred to specialized services', _('Child referred to specialized services')),
        ('Child referred to CP', _('Child referred to CP')),
        ('Child referred to Health programme', _('Child referred to Health programme')),
        ('Follow-up with parents', _('Follow-up with parents')),
        ('Dropout/No Interest', _('Dropout/No Interest')),
    )
    MEETING_TYPE = Choices(
        ('', '----------'),
        ('PSS Session', _('PSS Session')),
        ('COVID health awareness session', _('COVID health awareness session')),
    )
    SESSION_MODALITY = Choices(
        ('', '----------'),
        ('Online via WhatsApp', _("Online via WhatsApp")),
        ('Phone calls', _("Phone calls")),
        ('Offline (F2F)', _("Offline (F2F)"))
    )
    CAREGIVER = Choices(
        ('', '----------'),
        ('Mother', _('Mother')),
        ('Father', _('Father')),
        ('Other', _('Other')),
    )

    registration = models.ForeignKey(
        Registration,
        blank=False, null=True,
        related_name='+',
    )
    follow_up_type = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=FOLLOW_UP_TYPE,
        verbose_name=_('In case of absence, type of Follow-up done')
    )
    phone_call_number = models.IntegerField(
        blank=True,
        null=True,
        verbose_name=_('Number of phone calls done')
    )
    house_visit_number = models.IntegerField(
        blank=True,
        null=True,
        verbose_name=_('Number of home visits done')
    )
    caregiver_visit_number = models.IntegerField(
        blank=True,
        null=True,
        verbose_name=_('Number of caregiver visits to center')
    )
    follow_up_result = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=FOLLOW_UP_RESULT,
        verbose_name=_('Result of follow up')
    )
    dropout_reason = models.TextField(
        blank=True, null=True,
        verbose_name=_('Reason for dropout')
    )
    dropout_date = models.DateField(
        blank=True,
        null=True,
        verbose_name=_('Dropout Date')
    )
    parent_attended_meeting = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        choices=YES_NO,
        verbose_name=_('Did the child\'s caregiver attend parent meeting/engagment sessions')
    )
    meeting_type = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        choices=MEETING_TYPE,
        verbose_name=_('Please indicate the types of meeting')
    )
    meeting_number = models.IntegerField(
        blank=True,
        null=True,
        verbose_name=_('Number of sessions attended')
    )
    meeting_modality = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        choices=SESSION_MODALITY,
        verbose_name=_('Please the modality used per each session')
    )
    caregiver_attended = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=CAREGIVER,
        verbose_name=_('Who attended the meetings')
    )
    caregiver_attended_other = models.TextField(
        blank=True, null=True,
        verbose_name=_('Please specify')
    )

    class Meta:
        ordering = ['id']
        verbose_name = "Follow Up Service"
        verbose_name_plural = "Follow Up Services"


class Referral(TimeStampedModel):

    REFERRED_SERVICE = Choices(
        ('', '----------'),
        ('No', _('No')),
        ('CP', _('CP')),
        ('Wash', _('Wash')),
        ('Health', _('Health')),
        ('Youth', _('Youth')),
        ('Other', _('Other')),
    )
    LEARNING_PATH = Choices(
        ('', '----------'),
        ('Transition to Dirasa', _('Transition to Dirasa')),
        ('Repeat same level in next  school year', _('Repeat same level in next  school year')),
        ('Progress to FE', _('Progress to FE')),
        ('Referred to Specialized Education', _('Referred to Specialized Education')),
        ('Referred to TVET', _('Referred to TVET')),
        ('Drop out', _('Drop out')),
        ('Referred to YBLN', _('Referred to YBLN')),
    )

    registration = models.ForeignKey(
        Registration,
        blank=False, null=True,
        related_name='+',
    )
    referred_formal_education = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        choices=YES_NO,
        verbose_name=_('Was the child referred to formal education (Grade 1)?')
    )
    referred_school = models.ForeignKey(
        School,
        blank=False, null=True,
        related_name='+',
        verbose_name=_('Name of the School referred to')
    )
    receive_needed_material = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        choices=YES_NO,
        verbose_name=_('Did the child receive all needed materials and resources (Stationery, Books, Learning bundle)?')
    )
    referred_service = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=REFERRED_SERVICE,
        verbose_name=_('Was the child referred to a service?')
    )
    referred_service_other = models.TextField(
        blank=True, null=True,
        verbose_name=_('Please specify')
    )
    recommended_learning_path = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=LEARNING_PATH,
        verbose_name=_('Based on the overall score, what is the recommended learning path/outcome?')
    )

    class Meta:
        ordering = ['id']
        verbose_name = "Referral"
        verbose_name_plural = "Referrals"


class YouthAssessment(TimeStampedModel):
    VOLUNTEERING_OPPORTUNITY = Choices(
        ('', '----------'),
        ('Outreach', _('Outreach')),
        ('Data entry', _('Data entry')),
        ('Admin work', _('Admin work')),
        ('Awareness raising sessions', _('Awareness raising sessions')),
        ('Empowerment and leadership', _('Empowerment and leadership')),
        ('Other', _('Other')),
    )
    TRAINING_MATERIAL = Choices(
        ('', '----------'),
        ('Printed workbook', _('Printed workbook')),
        ('Tablets', _('Tablets')),
        ('Access to digital content (learning Passport)', _('Access to digital content (learning Passport)')),
        ('Other', _('Other')),
    )
    FUTURE_PATH = Choices(
        ('', '----------'),
        ('Transition to FE', _('Transition to FE')),
        ('Repeat the school year', _('Repeat the school year')),
        ('Refer to a UNICEF Youth Programme (skills tranining, CBT, GIL...)', _('Refer to a UNICEF Youth Programme (skills tranining, CBT, GIL...)')),
        ('Transition to TVET', _('Transition to TVET')),
        ('Internship or volunteering opportunity', _('Internship or volunteering opportunity')),
    )
    ATTENDANCE = Choices(
        ('', '----------'),
        ('Full attendance', _('Full attendance')),
        ('Absence for less than 5 days', _('Absence for less than 5 days')),
        ('Absence for more than 5 days', _('Absence for more than 5 days')),
        ('Dropout', _('Dropout')),
    )
    registration = models.ForeignKey(
        Registration,
        blank=False, null=True,
        related_name='+',
    )
    undertake_post_diagnostic = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=YES_NO,
        verbose_name=_('Did the adolescent undertake any Post Diagnotic tests?')
    )
    receive_passing_grade = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=YES_NO,
        verbose_name=_('Did the adolescent receive a passing grade for the tests?')
    )
    complete_life_skills = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=YES_NO,
        verbose_name=_('Did the adolescent complete the life skills package?')
    )
    participate_volunteering = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=YES_NO,
        verbose_name=_('Did the adolescent participate in any volunteering opportunity during the course of the program?')
    )
    volunteering_opportunity = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        choices=VOLUNTEERING_OPPORTUNITY,
        verbose_name=_('Is yes, please specify the volunteering opportunity')
    )
    benefit_innovation_course = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=YES_NO,
        verbose_name=_('Did the adolescent benefit from any social innovation/entrepreneurship course?')
    )
    compelete_yfs_course = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=YES_NO,
        verbose_name=_('Did the adolescent compelete the YFS course?')
    )
    training_material = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        choices=TRAINING_MATERIAL,
        verbose_name=_('What training material was provided?')
    )
    future_path = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        choices=FUTURE_PATH,
        verbose_name=_('What is the recommended future path for the adolescent?')
    )
    participate_community_initiatives = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=YES_NO,
        verbose_name=_('Did the adolescent participate/come up in community based initiatives?')
    )
    attendance = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        choices=ATTENDANCE,
        verbose_name=_('Adolescent attendance')
    )
    class Meta:
        ordering = ['id']
        verbose_name = "Youth Assessment"
        verbose_name_plural = "Youth Assessments"

