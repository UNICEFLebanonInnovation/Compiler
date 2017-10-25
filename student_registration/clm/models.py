from __future__ import unicode_literals

from django.db import models
from django.conf import settings
from django.utils.translation import ugettext as _
from django.contrib.postgres.fields import ArrayField, JSONField

from model_utils import Choices
from model_utils.models import TimeStampedModel

from student_registration.users.models import PartnerOrganization
from student_registration.students.models import Student, Labour
from student_registration.locations.models import Location
from student_registration.schools.models import (
    School,
    ClassRoom,
    EducationalLevel,
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


class RSCycle(models.Model):

    name = models.CharField(max_length=100)
    current_cycle = models.BooleanField(blank=True, default=False)

    class Meta:
        ordering = ['name']

    def __unicode__(self):
        return self.name


class Site(models.Model):

    name = models.CharField(max_length=100)
    current_cycle = models.BooleanField(blank=True, default=False)

    class Meta:
        ordering = ['name']
        verbose_name = "Program site"
        verbose_name_plural = "Program sites"

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


class Disability(models.Model):

    name = models.CharField(max_length=100)

    class Meta:
        ordering = ['name']
        verbose_name = "Disability"
        verbose_name_plural = "Disabilities"

    def __unicode__(self):
        return self.name


class CLM(TimeStampedModel):

    LANGUAGES = Choices(
        ('english_arabic', _('English/Arabic')),
        ('french_arabic', _('French/Arabic'))
    )
    STATUS = Choices(
        'enrolled',
        'pre_test',
        'post_test'
    )
    YES_NO = Choices(
        (1, _("Yes")),
        (0, _("No"))
    )
    REFERRAL = Choices(
        ('from_same_ngo', _('Referral from the same NGO')),
        ('from_other_ngo', _('Referral from an other NGO')),
        ('form_official_reference', _('Referral from an official reference (Mukhtar, Municipality, School Director, etc.)')),
        ('from_host_community', _('Referral from the host community')),
        ('from_displaced_community', _('Referral from the displaced community')),
    )
    PARTICIPATION = Choices(
        ('less_than_5days', _('Less than 5 absence days')),
        ('5_10_days', _('5 to 10 absence days')),
        ('10_15_days', _('10 to 15 absence days')),
        ('more_than_15days', _('More than 15 absence days'))
    )
    BARRIERS = Choices(
        ('seasonal_work', _('Seasonal work')),
        ('transportation', _('Transportation')),
        ('weather', _('Weather')),
        ('sickness', _('Sickness')),
        ('security', _('Security')),
        ('other', _('Other'))
    )
    HAVE_LABOUR = Choices(
        ('no', _('No')),
        ('yes_morning', _('Yes - Morning')),
        ('yes_afternoon', _('Yes - Afternoon')),
    )
    LABOURS = Choices(
        ('agriculture', _('Agriculture')),
        ('building', _('Building')),
        ('manufacturing', _('Manufacturing')),
        ('retail_store', _('Retail / Store')),
        ('begging', _('Begging')),
        ('other_many_other', _('Other (hotel, restaurant, transport, personal services such as cleaning, hair care, cooking and childcare)')),
        ('other', _('Other')),
    )
    LEARNING_RESULT = Choices(
        ('graduated_next_level', _('Graduated to the next level')),
        ('graduated_to_formal_kg', _('Graduated to formal education - KG')),
        ('graduated_to_formal_level1', _('Graduated to formal education - Level 1')),
        ('referred_to_another_program', _('Referred to another program')),
        ('dropout', _('Dropout from school'))
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
    location = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name=_('Location')
    )
    language = ArrayField(
        models.CharField(
            choices=LANGUAGES,
            max_length=50,
            blank=True,
            null=True,
        ),
        blank=True,
        null=True,
        verbose_name=_('The language supported in the program')
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
    have_labour = ArrayField(
        models.CharField(
            choices=HAVE_LABOUR,
            max_length=50,
            blank=True,
            null=True,
        ),
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
    labour_hours = models.IntegerField(
        blank=True,
        null=True,
        verbose_name=_('How many hours does this child work in a day?')
    )
    hh_educational_level = models.ForeignKey(
        EducationalLevel,
        blank=True, null=True,
        related_name='+',
        verbose_name=_('What is the educational level of a person who is valuable to the child?')
    )

    status = models.CharField(max_length=50, choices=STATUS, default=STATUS.enrolled)
    pre_test = JSONField(blank=True, null=True)
    post_test = JSONField(blank=True, null=True)

    scores = JSONField(blank=True, null=True, default=dict)

    participation = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=PARTICIPATION,
        verbose_name=_('Participation')
    )
    barriers = ArrayField(
        models.CharField(
            choices=BARRIERS,
            max_length=100,
            blank=True,
            null=True,
        ),
        blank=True,
        null=True,
        verbose_name=_('Barriers')
    )
    learning_result = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=LEARNING_RESULT,
        verbose_name=_('Learning result')
    )

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        blank=False, null=True,
        related_name='+',
    )
    deleted = models.BooleanField(blank=True, default=False)
    dropout_status = models.BooleanField(blank=True, default=False)
    moved = models.BooleanField(blank=True, default=False)
    outreach_barcode = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name=_('Outreach barcode')
    )
    new_registry = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        choices=YES_NO,
        verbose_name=_('First time registered?')
    )
    student_outreached = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        choices=YES_NO,
        verbose_name=_('Student outreached?')
    )
    have_barcode = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        choices=YES_NO,
        verbose_name=_('Have barcode with him?')
    )
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
        return '/clm/edit/%d/' % self.pk

    def __unicode__(self):
        if self.student:
            return self.student.__unicode__()
        return str(self.id)

    class Meta:
        abstract = True


class BLN(CLM):

    cycle = models.ForeignKey(
        Cycle,
        blank=True, null=True,
        related_name='+',
        verbose_name=_('Cycle')
    )
    referral = ArrayField(
        models.CharField(
            choices=CLM.REFERRAL,
            max_length=100,
            blank=True,
            null=True,
        ),
        blank=True,
        null=True,
        verbose_name=_('Referral')
    )

    class Meta:
        ordering = ['id']
        verbose_name = "BLN"
        verbose_name_plural = "BLN"


class RS(CLM):

    SCHOOL_SHIFTS = Choices(
        ('first', _('First shift')),
        ('second', _('Second shift')),
    )
    TYPES = Choices(
        ('homework_support', _('Homework Support')),
        ('remedial_support', _('Remedial Support')),
    )
    SITES = Choices(
        ('in_school', _('Inside the school')),
        ('out_school', _('Outside the school')),
    )
    REFER_SEASON = Choices(
        ('academic', _('Academic')),
        ('absence', _('Absence'))
    )

    type = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        choices=TYPES,
        verbose_name=_('Program type')
    )
    site = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        choices=SITES,
        verbose_name=_('Program site')
    )
    school = models.ForeignKey(
        School,
        blank=False, null=True,
        related_name='+',
        verbose_name=_('Attending in school')
    )
    registered_in_school = models.ForeignKey(
        School,
        blank=False, null=True,
        related_name='+',
        verbose_name=_('Registered in school')
    )
    shift = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        choices=SCHOOL_SHIFTS,
        verbose_name=_('Shift')
    )
    grade = models.ForeignKey(
        ClassRoom,
        blank=True, null=True,
        related_name='+',
        verbose_name=_('Class')
    )
    referral = ArrayField(
        models.CharField(
            choices=CLM.REFERRAL,
            max_length=100,
            blank=True,
            null=True,
        ),
        blank=True,
        null=True,
        verbose_name=_('Reason of referral')
    )
    pre_test_arabic = models.IntegerField(
        blank=True,
        null=True,
        default=0,
        choices=((x, x) for x in range(0, 21)),
        verbose_name=_('Arabic')
    )
    pre_test_language = models.IntegerField(
        blank=True,
        null=True,
        default=0,
        choices=((x, x) for x in range(0, 21)),
        verbose_name=_('Foreign Language')
    )
    pre_test_math = models.IntegerField(
        blank=True,
        null=True,
        default=0,
        choices=((x, x) for x in range(0, 21)),
        verbose_name=_('Math')
    )
    pre_test_science = models.IntegerField(
        blank=True,
        null=True,
        default=0,
        choices=((x, x) for x in range(0, 21)),
        verbose_name=_('Science')
    )
    post_test_arabic = models.IntegerField(
        blank=True,
        null=True,
        default=0,
        choices=((x, x) for x in range(0, 21)),
        verbose_name=_('Arabic')
    )
    post_test_language = models.IntegerField(
        blank=True,
        null=True,
        default=0,
        choices=((x, x) for x in range(0, 21)),
        verbose_name=_('Foreign Language')
    )
    post_test_math = models.IntegerField(
        blank=True,
        null=True,
        default=0,
        choices=((x, x) for x in range(0, 21)),
        verbose_name=_('Math')
    )
    post_test_science = models.IntegerField(
        blank=True,
        null=True,
        default=0,
        choices=((x, x) for x in range(0, 21)),
        verbose_name=_('Science')
    )

    class Meta:
        ordering = ['id']
        verbose_name = "RS"
        verbose_name_plural = "RS"

    @property
    def pretest_total(self):
        return self.pre_test_arabic + self.pre_test_language + self.pre_test_math + self.pre_test_science

    @property
    def pretest_result(self):
        return '{}/{}'.format(
            str(self.pretest_total()),
            '80'
        )

    @property
    def posttest_total(self):
        return self.post_test_arabic+self.post_test_language+self.post_test_math+self.post_test_science

    @property
    def posttest_result(self):
        return '{}/{}'.format(
            str(self.posttest_total),
            '80'
        )


class CBECE(CLM):

    MUAC = Choices(
        ('1', _('< 11.5 CM (severe malnutrition)')),
        ('2', _('< 12.5 CM (moderate malnutrition)')),
    )
    REFER_SEASON = Choices(
        ('academic', _('Academic')),
        ('absence', _('Absence'))
    )
    SITES = Choices(
        ('in_school', _('Inside the school')),
        ('out_school', _('Outside the school')),
    )

    cycle = models.ForeignKey(
        Cycle,
        blank=True, null=True,
        related_name='+',
        verbose_name=_('Cycle')
    )
    site = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        choices=SITES,
        verbose_name=_('Program site')
    )
    school = models.ForeignKey(
        School,
        blank=False, null=True,
        related_name='+',
        verbose_name=_('Attending in school')
    )
    referral = ArrayField(
        models.CharField(
            choices=CLM.REFERRAL,
            max_length=100,
            blank=True,
            null=True,
        ),
        blank=True,
        null=True,
        verbose_name=_('Reason of referral')
    )
    child_muac = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        choices=MUAC,
        verbose_name=_('Child MUAC')
    )
    pre_test_arabic = models.IntegerField(
        blank=True,
        null=True,
        choices=((x, x) for x in range(0, 21)),
        verbose_name=_('Arabic')
    )
    pre_test_language = models.FloatField(
        blank=True,
        null=True,
        choices=((x, x) for x in range(0, 21)),
        verbose_name=_('Foreign Language')
    )
    pre_test_math = models.FloatField(
        blank=True,
        null=True,
        choices=((x, x) for x in range(0, 21)),
        verbose_name=_('Math')
    )
    pre_test_science = models.FloatField(
        blank=True,
        null=True,
        choices=((x, x) for x in range(0, 21)),
        verbose_name=_('Science')
    )

    class Meta:
        ordering = ['id']
        verbose_name = "CB-ECE"
        verbose_name_plural = "CB-ECE"


class SelfPerceptionGrades(models.Model):

    enrollment = models.ForeignKey(
        RS,
        blank=True, null=True,
        related_name='+',
        verbose_name=_('Enrollment')
    )
    assessment_type = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name=_('Assessment type')
    )
    assessment_date = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name=_('Assessment date')
    )
    answers = JSONField(
        blank=True,
        null=True,
        default={},
        verbose_name=_('Assessment answers')
    )

    class Meta:
        ordering = ['id']
        verbose_name = "Child perception grade"
        verbose_name_plural = "Child perception grades"

    def __unicode__(self):
        return self.enrollment
