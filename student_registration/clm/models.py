from __future__ import unicode_literals

from django.db import models
from django.conf import settings
from django.utils.translation import ugettext as _
from django.contrib.postgres.fields import ArrayField, JSONField
from django.core.urlresolvers import reverse

from model_utils import Choices
from model_utils.models import TimeStampedModel

from student_registration.students.models import Student, Labour
from student_registration.locations.models import Location
from student_registration.schools.models import (
    School,
    Section,
    ClassRoom,
    CLMRound,
    EducationalLevel,
    PartnerOrganization,
)


# class CLMRound(models.Model):
#     name = models.CharField(max_length=45, unique=True)
#
#     class Meta:
#         ordering = ['name']
#         verbose_name = "CLM Round"
#
#     def __unicode__(self):
#         return self.name


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
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ['name']
        verbose_name = "Disability"
        verbose_name_plural = "Disabilities"

    def __unicode__(self):
        return self.name


class CLM(TimeStampedModel):

    LANGUAGES = Choices(
        ('arabic', _('Arabic')),
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
        ('', _('Participation')),
        ('less_than_5days', _('Less than 5 absence days')),
        ('5_10_days', _('5 to 10 absence days')),
        ('10_15_days', _('10 to 15 absence days')),
        ('more_than_15days', _('More than 15 absence days'))
    )
    BARRIERS = Choices(
        ('Full time job to support family financially', _('Full time job to support family financially')),
        ('seasonal_work', _('Seasonal work')),
        ('transportation', _('Transportation')),
        ('weather', _('Weather')),
        ('sickness', _('Sickness')),
        ('security', _('Security')),
        ('family moved', _('Family moved')),
        ('Moved back to Syria', _('Moved back to Syria')),
        ('Enrolled in formal education', _('Enrolled in formal education')),
        ('marriage engagement pregnancy', _('Marriage/Engagement/Pregnancy')),
        ('violence bullying', _('Violence/Bullying')),
        ('No interest in pursuing the programme/No value', _('No interest in pursuing the programme/No value')),
        # ('other', _('Other'))
    )
    HAVE_LABOUR = Choices(
        ('no', _('No')),
        ('yes_morning', _('Yes - Morning')),
        ('yes_afternoon', _('Yes - Afternoon')),
        ('yes_all_day', _('Yes - All day')),
    )
    LABOURS = Choices(
        ('agriculture', _('Agriculture')),
        ('building', _('Building')),
        ('manufacturing', _('Manufacturing')),
        ('retail_store', _('Retail / Store')),
        ('begging', _('Begging')),
        ('other_many_other', _('Other services (hotel, restaurant, transport, personal services such as cleaning, hair care, cooking and childcare)')),
        # ('other', _('Other')),
    )
    LEARNING_RESULT = Choices(
        ('', _('Learning result')),
        ('graduated_next_level', _('Graduated to the next level')),
        ('graduated_next_round_same_level', _('Graduated to the next round, same level')),
        ('graduated_next_round_higher_level', _('Graduated to the next round, higher level')),
        ('graduated_to_formal_kg', _('Graduated to formal education - KG')),
        ('graduated_to_formal_level1', _('Graduated to formal education - Level 1')),
        ('referred_to_another_program', _('Referred to another program')),
        # ('dropout', _('Dropout from school'))
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
    location = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name=_('Location')
    )
    language = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=LANGUAGES,
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
        verbose_name=_('What is the educational level of the mother?')
    )

    father_educational_level = models.ForeignKey(
        EducationalLevel,
        blank=True, null=True,
        related_name='+',
        verbose_name=_('What is the educational level of the father?')
    )

    status = models.CharField(max_length=50, choices=STATUS, default=STATUS.enrolled)
    pre_test = JSONField(blank=True, null=True)
    pre_test_score = models.CharField(
        max_length=45,
        blank=True,
        null=True,
        verbose_name=_('Pre-assessment')
    )
    post_test = JSONField(blank=True, null=True)
    post_test_score = models.CharField(
        max_length=45,
        blank=True,
        null=True,
        verbose_name=_('Post-assessment')
    )
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
    modified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        blank=True, null=True,
        related_name='+',
        verbose_name=_('Modified by'),
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
        choices=Choices(('yes', _("Yes")), ('no', _("No"))),
        verbose_name=_('First time registered?')
    )
    student_outreached = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        choices=Choices(('yes', _("Yes")), ('no', _("No"))),
        verbose_name=_('Student outreached?')
    )
    have_barcode = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        choices=Choices(('yes', _("Yes")), ('no', _("No"))),
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
    unsuccessful_pretest_reason = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=Choices(
            ('disability', _('Disability')),
            ('enrolled and did not do the pre-test', _("Enrolled and did not do the pre-test")),
            ('enrolled in formal', _("Enrolled in formal education")),
        ),
        verbose_name=_('unsuccessful pre test reason')
    )
    unsuccessful_posttest_reason = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=Choices(
            ('disability', _('Disability')),
            ('dropout', _("Dropout from the round")),
            ('uncompleted_participation', _("Uncompleted Participation"))
        ),
        verbose_name=_('unsuccessful post test reason')
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

    education_status = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=Choices(
            ('out of school', _('Out of school')),
            ('enrolled in formal education but did not continue', _("Enrolled in formal education but did not continue")),
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

    source_of_identification = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=Choices(
            ('Referred by CP partner', _('Referred by CP partner')),
            ('Referred by youth partner', _('Referred by youth partner')),
            ('Family walked in to NGO', _('Family walked in to NGO')),
            ('Referral from another NGO', _('Referral from another NGO')),
            ('Referral from another Municipality', _('Referral from Municipality')),
            ('Direct outreach', _('Direct outreach')),
            ('List database', _('List database'))
        ),
        verbose_name=_('Source of identification of the child')
    )

    no_child_id_confirmation = models.CharField(max_length=50, blank=True, null=True,)
    no_parent_id_confirmation = models.CharField(max_length=50, blank=True, null=True,)

    parent_id_type = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=Choices(
            ('UNHCR Registered', _('UNHCR Registered')),
            ('UNHCR Recorded', _("UNHCR Recorded")),
            ('Syrian national ID', _("Syrian national ID")),
            ('Palestinian national ID', _("Palestinian national ID")),
            ('Lebanese national ID', _("Lebanese national ID")),
            ('Parent have no ID', _("Parent have no ID"))
        ),
        verbose_name=_('Parent ID type')
    )

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

    referral_programme_type_1 = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=Choices(
            ('Formal Education', _('Formal Education')),
            ('ALP', _('ALP')),
            ('BLN', _('BLN')),
            ('CP (PSS and/or Case Management)', _('CP (PSS and/or Case Management)')),
            ('Youth', _('Youth')),
            ('Health', _('Health')),
            ('WASH', _('WASH')),
            ('Specialized Services', _('Specialized Services')),
            ('Other', _('Other')),
        ),
        verbose_name=_('Programme Type')
    )
    referral_partner_1 = models.CharField(
        max_length=500,
        blank=True,
        null=True,
        verbose_name=_('Partner')
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
            ('Formal Education', _('Formal Education')),
            ('ALP', _('ALP')),
            ('BLN', _('BLN')),
            ('CP (PSS and/or Case Management)', _('CP (PSS and/or Case Management)')),
            ('Youth', _('Youth')),
            ('Health', _('Health')),
            ('WASH', _('WASH')),
            ('Specialized Services', _('Specialized Services')),
            ('Other', _('Other')),
        ),
        verbose_name=_('Programme Type')
    )
    referral_partner_2 = models.CharField(
        max_length=500,
        blank=True,
        null=True,
        verbose_name=_('Partner')
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
            ('Formal Education', _('Formal Education')),
            ('ALP', _('ALP')),
            ('BLN', _('BLN')),
            ('CP (PSS and/or Case Management)', _('CP (PSS and/or Case Management)')),
            ('Youth', _('Youth')),
            ('Health', _('Health')),
            ('WASH', _('WASH')),
            ('Specialized Services', _('Specialized Services')),
            ('Other', _('Other')),
        ),
        verbose_name=_('Programme Type')
    )
    referral_partner_3 = models.CharField(
        max_length=500,
        blank=True,
        null=True,
        verbose_name=_('Partner')
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

    followup_call_reason_1 = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('Reason')
    )
    followup_call_result_1 = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('Results')
    )
    followup_call_date_1 = models.DateField(
        blank=True,
        null=True,
        verbose_name=_('Call date')
    )

    followup_call_reason_2 = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('Reason')
    )
    followup_call_result_2 = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('Results')
    )
    followup_call_date_2 = models.DateField(
        blank=True,
        null=True,
        verbose_name=_('Call date')
    )

    followup_visit_reason_1 = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('Reason')
    )
    followup_visit_result_1 = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('Results')
    )
    followup_visit_date_1 = models.DateField(
        blank=True,
        null=True,
        verbose_name=_('Visit date')
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

    cycle_completed = models.BooleanField(blank=True, default=False)
    enrolled_at_school = models.BooleanField(blank=True, default=False)

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

    @property
    def assessment_improvement(self):
        if self.pre_test and self.post_test:
            try:
                return '{}{}'.format(
                    round(((float(self.post_test_score) - float(self.pre_test_score)) /
                           float(self.pre_test_score)) * 100.0, 2), '%')
            except ZeroDivisionError:
                return 0.0
        return 0.0

    def get_absolute_url(self):
        return '/clm/edit/%d/' % self.pk

    def __unicode__(self):
        if self.student:
            return self.student.__unicode__()
        return str(self.id)

    def score(self, keys, stage):
        assessment = getattr(self, stage, 'pre_test')
        score = stage+'_score'
        marks = {key: float(assessment.get(key, 0)) for key in keys}
        total = sum(marks.values())
        setattr(self, score, total)

    def get_score_value(self, key, stage):
        assessment = getattr(self, stage, 'pre_test')
        if assessment:
            return float(assessment.get(key, 0))
        return 0

    class Meta:
        abstract = True


class BLN(CLM):

    LEARNING_RESULT = Choices(
        ('', _('Learning result')),
        ('graduated_to_bln_next_level', _('Graduated to the next level')),
        ('graduated_to_bln_next_round_same_level', _('Graduated to the next round, same level')),
        ('graduated_to_bln_next_round_higher_level', _('Graduated to the next round, higher level')),
        ('referred_to_alp', _('referred to ALP')),
        ('referred_public_school', _('Referred to public school')),
        ('referred_to_tvet', _('Referred to TVET')),
        ('referred_to_ybln', _('Referred to YBLN')),
        ('dropout', _('Dropout, referral not possible')),
    )

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

    learning_result = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=LEARNING_RESULT,
        verbose_name=_('Learning result')
    )

    participation = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=Choices(
            ('less_than_10days', _('Less than 10 absence days')),
            ('10_15_days', _('10 to 15 absence days')),
            ('15_20_days', _('15 to 20 absence days')),
            ('more_than_20days', _('More than 20 absence days'))
        ),
        verbose_name=_('Participation')
    )

    def calculate_score(self, stage):
        keys = [
            'BLN_ASSESSMENT/arabic',
            'BLN_ASSESSMENT/math',
            'BLN_ASSESSMENT/foreign_language',
            'BLN_ASSESSMENT/social_emotional',
            'BLN_ASSESSMENT/psychomotor',
            'BLN_ASSESSMENT/artistic',
            # 'BLN_ASSESSMENT/english',
            # 'BLN_ASSESSMENT/french'
        ]
        super(BLN, self).score(keys, stage)

    def assessment_form(self, stage, assessment_slug, callback=''):
        try:
            assessment = Assessment.objects.get(slug=assessment_slug)
            return '{form}?d[status]={status}&d[enrollment_id]={enrollment_id}&d[enrollment_model]=BLN&returnURL={callback}'.format(
                form=assessment.assessment_form,
                status=stage,
                enrollment_id=self.id,
                callback=callback
            )
        except Assessment.DoesNotExist as ex:
            return ''

    def domain_improvement(self, domain_mame):
        key = '{}/{}'.format(
            'BLN_ASSESSMENT',
            domain_mame,
        )
        try:
            if self.pre_test and self.post_test:
                return round(((float(self.post_test[key]) - float(self.pre_test[key])) /
                              20.0) * 100.0, 2)
        except Exception:
            return 0.0
        return 0.0

    def get_assessment_value(self, key, stage):
        assessment = getattr(self, stage)
        if assessment:
            key = 'BLN_ASSESSMENT/'+key
            return assessment.get(key, 0)
        return 0

    @property
    def arabic_improvement(self):
        return str(self.domain_improvement('arabic')) + '%'

    @property
    def math_improvement(self):
        return str(self.domain_improvement('math')) + '%'

    @property
    def english_improvement(self):
        return str(self.domain_improvement('english')) + '%'

    @property
    def french_improvement(self):
        return str(self.domain_improvement('french')) + '%'

    @property
    def foreign_language_improvement(self):
        french_english = self.domain_improvement('english') + self.domain_improvement('french')
        if not french_english:
            return str(self.domain_improvement('foreign_language')) + '%'
        return str(french_english) + '%'

    @property
    def social_emotional_improvement(self):
        return str(self.domain_improvement('social_emotional')) + '%'

    @property
    def psychomotor_improvement(self):
        return str(self.domain_improvement('psychomotor')) + '%'

    @property
    def artistic_improvement(self):
        return str(self.domain_improvement('artistic')) + '%'

    def pre_assessment_form(self):
        return self.assessment_form(stage='pre_test', assessment_slug='bln_pre_test')

    def post_assessment_form(self):
        return self.assessment_form(stage='post_test', assessment_slug='bln_post_test')

    class Meta:
        ordering = ['id']
        verbose_name = "BLN"
        verbose_name_plural = "BLN"


class RS(CLM):

    LEARNING_RESULT = Choices(
        ('', _('Learning result')),
        ('repeat_level', _('Yes')),
        ('graduated_next_level', _('No'))
    )

    SCHOOL_SHIFTS = Choices(
        ('', _('Shift')),
        ('first', _('First shift')),
        ('second', _('Second shift')),
    )
    TYPES = Choices(
        ('', _('Program type')),
        ('homework_support', _('Homework Support')),
        ('remedial_support', _('Remedial Support')),
    )
    SITES = Choices(
        ('', _('Program site')),
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
            choices=REFER_SEASON,
            max_length=100,
            blank=True,
            null=True,
        ),
        blank=True,
        null=True,
        verbose_name=_('Reason of referral')
    )
    pre_test_arabic = models.FloatField(
        blank=True,
        null=True,
        default=0,
        # choices=((x, x) for x in range(0, 21)),
        verbose_name=_('Arabic')
    )
    pre_test_language = models.FloatField(
        blank=True,
        null=True,
        default=0,
        # choices=((x, x) for x in range(0, 21)),
        verbose_name=_('Foreign Language')
    )
    pre_test_math = models.FloatField(
        blank=True,
        null=True,
        default=0,
        # choices=((x, x) for x in range(0, 21)),
        verbose_name=_('Math')
    )
    pre_test_science = models.FloatField(
        blank=True,
        null=True,
        default=0,
        # choices=((x, x) for x in range(0, 21)),
        verbose_name=_('Science')
    )
    post_test_arabic = models.FloatField(
        blank=True,
        null=True,
        default=0,
        # choices=((x, x) for x in range(0, 21)),
        verbose_name=_('Arabic')
    )
    post_test_language = models.FloatField(
        blank=True,
        null=True,
        default=0,
        # choices=((x, x) for x in range(0, 21)),
        verbose_name=_('Foreign Language')
    )
    post_test_math = models.FloatField(
        blank=True,
        null=True,
        default=0,
        # choices=((x, x) for x in range(0, 21)),
        verbose_name=_('Math')
    )
    post_test_science = models.FloatField(
        blank=True,
        null=True,
        default=0,
        # choices=((x, x) for x in range(0, 21)),
        verbose_name=_('Science')
    )

    pre_reading = JSONField(blank=True, null=True)
    pre_reading_score = models.CharField(
        max_length=45,
        blank=True,
        null=True,
        verbose_name=_('Arabic reading - Pre')
    )
    post_reading = JSONField(blank=True, null=True)
    post_reading_score = models.CharField(
        max_length=45,
        blank=True,
        null=True,
        verbose_name=_('Arabic reading - Post')
    )

    pre_self_assessment = JSONField(blank=True, null=True)
    pre_self_assessment_score = models.CharField(
        max_length=45,
        blank=True,
        null=True,
        verbose_name=_('Self-assessment - Pre')
    )
    post_self_assessment = JSONField(blank=True, null=True)
    post_self_assessment_score = models.CharField(
        max_length=45,
        blank=True,
        null=True,
        verbose_name=_('Self-assessment - Post')
    )

    pre_motivation = JSONField(blank=True, null=True)
    pre_motivation_score = models.CharField(
        max_length=45,
        blank=True,
        null=True,
        verbose_name=_('Motivation - Pre')
    )
    post_motivation = JSONField(blank=True, null=True)
    post_motivation_score = models.CharField(
        max_length=45,
        blank=True,
        null=True,
        verbose_name=_('Motivation - Post')
    )

    learning_result = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=LEARNING_RESULT,
        verbose_name=_('RS Learning result')
    )
    section = models.ForeignKey(
        Section,
        blank=True, null=True,
        related_name='+',
        verbose_name=_('Section')
    )

    class Meta:
        ordering = ['id']
        verbose_name = "RS"
        verbose_name_plural = "RS"

    @property
    def pretest_total(self):
        try:
            return self.pre_test_arabic + self.pre_test_language + self.pre_test_math + self.pre_test_science
        except TypeError:
            return 0

    @property
    def pretest_result(self):
        return '{}/{}'.format(
            str(self.pretest_total),
            '80'
        )

    @property
    def posttest_total(self):
        try:
            return self.post_test_arabic+self.post_test_language+self.post_test_math+self.post_test_science
        except TypeError:
            return 0

    @property
    def posttest_result(self):
        return '{}/{}'.format(
            str(self.posttest_total),
            '80'
        )

    @property
    def academic_test_improvement(self):
        if self.pretest_total and self.posttest_total:
            try:
                return '{}{}'.format(
                    round((float(self.posttest_total) - float(self.pretest_total)) /
                          float(self.pretest_total) * 100.0, 2),
                    '%')
            except ZeroDivisionError:
                return 0.0
        return 0

    @property
    def self_assessment_improvement(self):
        if self.pre_self_assessment and self.post_self_assessment:
            try:
                return '{}{}'.format(
                    round(((float(self.post_self_assessment_score) - float(self.pre_self_assessment_score)) /
                           float(self.pre_self_assessment_score)) * 100.0, 2),
                    '%')
            except ZeroDivisionError:
                return 0.0
        return 0.0

    @property
    def motivation_improvement(self):
        if self.pre_motivation and self.post_motivation:
            try:
                return '{}{}'.format(
                    round(((float(self.post_motivation_score) - float(self.pre_motivation_score)) /
                            float(self.pre_motivation_score)) * 100.0, 2),
                    '%')
            except ZeroDivisionError:
                return 0.0
        return 0.0

    @property
    def arabic_reading_improvement(self):
        if self.pre_reading_score and self.post_reading_score:
            try:
                return self.pre_reading_score - self.post_reading_score
            except Exception:
                return 0
        return 0

    def assessment_form(self, stage, assessment_slug, callback=''):
        try:
            assessment = Assessment.objects.get(slug=assessment_slug)
            return '{form}?d[status]={status}&d[enrollment_id]={enrollment_id}&d[enrollment_model]=RS&returnURL={callback}'.format(
                form=assessment.assessment_form,
                status=stage,
                enrollment_id=self.id,
                callback=callback
            )
        except Assessment.DoesNotExist:
            return ''

    @property
    def pre_assessment_form(self):
        return self.assessment_form(stage='pre_test', assessment_slug='rs_pre_test')

    @property
    def post_assessment_form(self):
        return self.assessment_form(stage='post_test', assessment_slug='rs_post_test')

    def domain_improvement(self, domain_mame):
        pre_test = getattr(self, 'pre_test_'+domain_mame)
        post_test = getattr(self, 'post_test_'+domain_mame)
        if pre_test and post_test:
            try:
                return round(((float(post_test) - float(pre_test)) /
                              float(pre_test)) * 100.0, 2)
            except ZeroDivisionError:
                return 0.0
        return 0.0

    @property
    def arabic_improvement(self):
        return str(self.domain_improvement('arabic')) + '%'

    @property
    def math_improvement(self):
        return str(self.domain_improvement('math')) + '%'

    @property
    def language_improvement(self):
        return str(self.domain_improvement('language')) + '%'

    @property
    def science_improvement(self):
        return str(self.domain_improvement('science')) + '%'

    def get_assessment_value(self, key, stage):
        assessment = getattr(self, stage)
        if assessment:
            key = 'RS_ASSESSMENT/'+key
            return assessment.get(key, 0)
        return 0

    def calculate_score(self, stage):
        keys = []
        if stage in ['pre_test', 'post_test']:
            keys = [
                # 'RS_ASSESSMENT_0/FL0',
                'RS_ASSESSMENT/FL1',
                'RS_ASSESSMENT/FL2',
                'RS_ASSESSMENT/FL3',
                'RS_ASSESSMENT/FL4',
            ]
        elif stage in ['pre_reading', 'post_reading']:
            keys = [
                'RS_ASSESSMENT/FL1',
            ]
        elif stage in ['pre_motivation', 'post_motivation']:
            keys = [
                'RS_ASSESSMENT/FL5',
                'RS_ASSESSMENT/FL6',
                'RS_ASSESSMENT/FL7',
                'RS_ASSESSMENT/FL8',
            ]
        elif stage in ['pre_self_assessment', 'post_self_assessment']:
            keys = [
                'SELF_ASSESSMENT/assessment_1',
                'SELF_ASSESSMENT/assessment_2',
                'SELF_ASSESSMENT/assessment_3',
                'SELF_ASSESSMENT/assessment_4',
                'SELF_ASSESSMENT/assessment_5',
                'SELF_ASSESSMENT/assessment_6',
                'SELF_ASSESSMENT/assessment_7',
                'SELF_ASSESSMENT/assessment_8',
                'SELF_ASSESSMENT/assessment_9',
                'SELF_ASSESSMENT/assessment_10',
                'SELF_ASSESSMENT/assessment_11',
                'SELF_ASSESSMENT/assessment_12',
                'SELF_ASSESSMENT/assessment_13',
                'SELF_ASSESSMENT/assessment_14',
            ]
        super(RS, self).score(keys, stage)


class CBECE(CLM):

    MUAC = Choices(
        ('', _('MUAC')),
        ('1', _('< 11.5 CM (severe malnutrition)')),
        ('2', _('< 12.5 CM (moderate malnutrition)')),
    )
    SITES = Choices(
        ('', _('Program site')),
        ('in_school', _('Inside the school')),
        ('out_school', _('Outside the school')),
    )
    LEARNING_RESULT = Choices(
        ('', _('Learning result')),
        ('repeat_level', _('Repeat level')),
        ('graduated_next_level', _('Graduated to the next level')),
        ('graduated_to_formal_kg', _('Graduated to formal education - KG')),
        ('graduated_to_formal_education_level1', _('Graduated to formal education - Level 1')),
        ('referred_to_another_program', _('Referred to another program')),
        ('dropout', _('Dropout, referral not possible'))
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
        verbose_name=_('Where was the child referred?')
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

    learning_result = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=LEARNING_RESULT,
        verbose_name=_('Learning result')
    )
    final_grade = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        blank=True, null=True,
        # help_text='/80'
    )

    def assessment_form(self, stage, assessment_slug, callback=''):
        try:
            assessment = Assessment.objects.get(slug=assessment_slug)
            return '{form}?d[status]={status}&d[programmecycle]={programmecycle}&d[enrollment_id]={enrollment_id}&d[enrollment_model]=CBECE&returnURL={callback}'.format(
                form=assessment.assessment_form,
                status=stage,
                programmecycle=self.cycle_id,
                enrollment_id=self.id,
                callback=callback
            )
        except Assessment.DoesNotExist:
            return ''

    def domain_improvement(self, domain_mame):
        if not self.cycle_id:
            return 0.0
        if not self.pre_test or not self.post_test:
            return 0.0
        program_cycle = str(self.cycle_id)
        key = '{}/{}{}'.format(
            'CBECE_ASSESSMENT',
            domain_mame,
            program_cycle
        )
        if key in self.pre_test and key in self.post_test:
            try:
                return round(((float(self.post_test[key]) - float(self.pre_test[key])) /
                              float(self.pre_test[key])) * 100.0, 2)
            except ZeroDivisionError:
                return 0.0
        return 0.0

    def get_assessment_value(self, key, stage):
        assessment = getattr(self, stage)
        program_cycle = str(self.cycle_id)
        if assessment:
            key = 'CBECE_ASSESSMENT/{}{}'.format(key, program_cycle)
            return assessment.get(key, 0)
        return 0

    @property
    def pre_assessment_form(self):
        return self.assessment_form(stage='pre_test', assessment_slug='cbece_pre_test')

    @property
    def post_assessment_form(self):
        return self.assessment_form(stage='post_test', assessment_slug='cbece_post_test')

    @property
    def art_improvement(self):
        return str(self.domain_improvement('LanguageArtDomain')) + '%'

    @property
    def science_improvement(self):
        return str(self.domain_improvement('ScienceDomain')) + '%'

    @property
    def cognitive_improvement(self):
        return str(self.domain_improvement('CognitiveDomian')) + '%'

    @property
    def social_improvement(self):
        return str(self.domain_improvement('SocialEmotionalDomain')) + '%'

    @property
    def psycho_improvement(self):
        return str(self.domain_improvement('PsychomotorDomain')) + '%'

    @property
    def artistic_improvement(self):
        return str(self.domain_improvement('ArtisticDomain')) + '%'

    def calculate_score(self, stage):
        program_cycle = str(self.cycle_id)
        keys = [
            'CBECE_ASSESSMENT/LanguageArtDomain'+program_cycle,
            'CBECE_ASSESSMENT/CognitiveDomian'+program_cycle,
            'CBECE_ASSESSMENT/ScienceDomain'+program_cycle,
            'CBECE_ASSESSMENT/SocialEmotionalDomain'+program_cycle,
            'CBECE_ASSESSMENT/PsychomotorDomain'+program_cycle,
            'CBECE_ASSESSMENT/ArtisticDomain'+program_cycle,
        ]
        super(CBECE, self).score(keys, stage)

        self.scores = {
            'pre_LanguageArtDomain': self.get_score_value('CBECE_ASSESSMENT/LanguageArtDomain' + program_cycle,
                                                          'pre_test'),
            'pre_CognitiveDomain': self.get_score_value(
                'CBECE_ASSESSMENT/CognitiveDomian' + program_cycle,
                'pre_test'),
            'pre_ScienceDomain': self.get_score_value(
                'CBECE_ASSESSMENT/ScienceDomain' + program_cycle,
                'pre_test'),
            'pre_SocialEmotionalDomain': self.get_score_value('CBECE_ASSESSMENT/SocialEmotionalDomain' + program_cycle,
                                                              'pre_test'),
            'pre_PsychomotorDomain': self.get_score_value('CBECE_ASSESSMENT/PsychomotorDomain' + program_cycle,
                                                          'pre_test'),
            'pre_ArtisticDomain': self.get_score_value('CBECE_ASSESSMENT/ArtisticDomain' + program_cycle, 'pre_test'),


            'post_LanguageArtDomain': self.get_score_value('CBECE_ASSESSMENT/LanguageArtDomain' + program_cycle,
                                                           'post_test'),
            'post_CognitiveDomain': self.get_score_value(
                'CBECE_ASSESSMENT/CognitiveDomian' + program_cycle,
                'post_test'),
            'post_ScienceDomain': self.get_score_value(
                'CBECE_ASSESSMENT/ScienceDomain' + program_cycle,
                'pre_test'),
            'post_SocialEmotionalDomain': self.get_score_value('CBECE_ASSESSMENT/SocialEmotionalDomain' + program_cycle,
                                                               'post_test'),
            'post_PsychomotorDomain': self.get_score_value('CBECE_ASSESSMENT/PsychomotorDomain' + program_cycle,
                                                           'post_test'),
            'post_ArtisticDomain': self.get_score_value('CBECE_ASSESSMENT/ArtisticDomain' + program_cycle, 'post_test'),
        }

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


class ABLN(CLM):

    LEARNING_RESULT = Choices(
        ('', _('Learning result')),
        ('graduated_to_abln_next_level', _('Graduated to the ABLN next level')),
        ('graduated_to_abln_next_round_same_level', _('Graduated to the next round, same level')),
        ('graduated_to_abln_next_round_higher_level', _('Graduated to the next round, higher level')),
        ('referred_to_bln', _('Referred to BLN')),
        ('referred_to_ybln', _('Referred to YBLN')),
        ('referred_to_alp', _('Referred to ALP')),
        ('referred_to_cbt', _('Referred to CBT')),
        ('dropout', _('Dropout, referral not possible')),
    )

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

    learning_result = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=LEARNING_RESULT,
        verbose_name=_('Learning result')
    )

    participation = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=Choices(
            ('less_than_3days', _('Less than 3 absence days')),
            ('3_7_days', _('3 to 7 absence days')),
            ('7_12_days', _('7 to 12 absence days')),
            ('more_than_12days', _('More than 12 absence days'))
        ),
        verbose_name=_('Participation')
    )

    def calculate_score(self, stage):
        keys = [
            'ABLN_ASSESSMENT/arabic',
            'ABLN_ASSESSMENT/math',
            'ABLN_ASSESSMENT/social_emotional',
            'ABLN_ASSESSMENT/psychomotor',
            'ABLN_ASSESSMENT/artistic',
        ]
        super(ABLN, self).score(keys, stage)

    def assessment_form(self, stage, assessment_slug, callback=''):
        try:
            assessment = Assessment.objects.get(slug=assessment_slug)
            return '{form}?d[status]={status}&d[enrollment_id]={enrollment_id}&d[enrollment_model]=ABLN&returnURL={callback}'.format(
                form=assessment.assessment_form,
                status=stage,
                enrollment_id=self.id,
                callback=callback
            )
        except Assessment.DoesNotExist as ex:
            return ''

    def domain_improvement(self, domain_mame):
        key = '{}/{}'.format(
            'ABLN_ASSESSMENT',
            domain_mame,
        )
        try:
            if self.pre_test and self.post_test:
                return round(((float(self.post_test[key]) - float(self.pre_test[key])) /
                              20.0) * 100.0, 2)
        except Exception:
            return 0.0
        return 0.0

    def get_assessment_value(self, key, stage):
        assessment = getattr(self, stage)
        if assessment:
            key = 'ABLN_ASSESSMENT/'+key
            return assessment.get(key, 0)
        return 0

    @property
    def arabic_improvement(self):
        return str(self.domain_improvement('arabic')) + '%'

    @property
    def math_improvement(self):
        return str(self.domain_improvement('math')) + '%'

    @property
    def english_improvement(self):
        return str(self.domain_improvement('english')) + '%'

    @property
    def french_improvement(self):
        return str(self.domain_improvement('french')) + '%'

    @property
    def social_emotional_improvement(self):
        return str(self.domain_improvement('social_emotional')) + '%'

    @property
    def psychomotor_improvement(self):
        return str(self.domain_improvement('psychomotor')) + '%'

    @property
    def artistic_improvement(self):
        return str(self.domain_improvement('artistic')) + '%'

    def pre_assessment_form(self):
        return self.assessment_form(stage='pre_test', assessment_slug='bln_pre_test')

    def post_assessment_form(self):
        return self.assessment_form(stage='post_test', assessment_slug='bln_post_test')

    class Meta:
        ordering = ['id']
        verbose_name = "ABLN"
        verbose_name_plural = "ABLN"
