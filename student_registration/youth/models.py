from __future__ import unicode_literals, absolute_import, division

from django.db import models
from django.conf import settings
from django.utils.translation import ugettext as _
from django.contrib.postgres.fields import ArrayField, JSONField
from model_utils import Choices
from model_utils.models import TimeStampedModel

from student_registration.adolescent.models import Adolescent
from student_registration.locations.models import Center
from student_registration.schools.models import (
    School,
    PartnerOrganization
)

YES_NO = Choices(
    ('', '----------'),
    ('Yes', _("Yes")),
    ('No', _("No"))
)

AGREE_DISAGREE = Choices(
    ('Strongly Agree', _("Strongly Agree")),
    ('Agree', _("Agree")),
    ('Don\'t Agree', _("Don\'t Agree")),
    ('Strongly Disagree', _("Strongly Disagree"))
)


class Round(models.Model):

    name = models.CharField(max_length=45, unique=True)
    current_year = models.BooleanField(blank=True, default=False)

    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)

    class Meta:
        ordering = ['name']
        verbose_name = "Round"

    def __str__(self):
        return self.name

    def __unicode__(self):
        return self.name


class Registration(TimeStampedModel):

    YES_NO = Choices(
        ('', '----------'),
        ('Yes', _("Yes")),
        ('No', _("No"))
    )
    center = models.ForeignKey(
        Center,
        blank=True, null=True,
        related_name='+',
        verbose_name=_('Center')
    )
    adolescent = models.ForeignKey(
        Adolescent,
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
    round = models.ForeignKey(
        Round,
        blank=True, null=True,
        related_name='+',
        verbose_name=_('Round')
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
    # registration_date = models.DateField(
    #     blank=True,
    #     null=True,
    #     verbose_name=_('Registration date')
    # )

    @property
    def adolescent_fullname(self):
        if self.adolescent:
            return self.adolescent.full_name
        return ''

    @property
    def adolescent_age(self):
        if self.adolescent:
            return self.adolescent.age
        return 0

    @property
    def enrolled_programs(self):
        result = ''
        program = self.enrolled_programs.all().first()
        if program:
            result = program.education_program
        return result

    def get_absolute_url(self):
        return '/YOUTH/Child-Profile/%d/' % self.pk

    def __str__(self):
        if self.adolescent:
            return self.adolescent.__str__()
        return str(self.id)

    def __unicode__(self):
        if self.adolescent:
            return self.adolescent.__unicode__()
        return str(self.id)

    class Meta:
        ordering = ['-id']
        verbose_name = "YOUTH Registration"
        verbose_name_plural = "YOUTH Registrations"


class EnrolledPrograms(TimeStampedModel):

    EDUCATION_STATUS = Choices(
        ('', '----------'),
        ('Never registered in any formal school before', _('Never registered in any formal school before')),
        ('Was registered in formal school but didn\'t continue',
         _('Was registered in formal school but didn\'t continue')),
        ('Was registered in non formal program and was referred to MSCC',
         _('Was registered in non formal program and was referred to MSCC')),
        ('Was registered in non formal program but didn\'t continue',
         _('Was registered in non formal program but didn\'t continue')),
        ('Was enrolled in TVET Programs', _('Was enrolled in TVET Programs')),
        ('Was Registered in Formal Education but not attending',
         _('Was Registered in Formal Education but not attending')),
        ('Currently registered in Formal Education school', _('Currently registered in Formal Education school')),
        ('Currently registered in Formal Education school but not attending', _('Currently registered in Formal Education school but not attending')),
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
    PROGRAM = Choices(
        ('BLN Level 1', _('BLN Level 1')),
        ('BLN Level 2', _('BLN Level 2')),
        ('BLN Level 3', _('BLN Level 3')),
        ('ABLN Level 1', _('ABLN Level 1')),
        ('ABLN Level 2', _('ABLN Level 2')),
        ('YBLN Level 1', _('YBLN Level 1')),
        ('YBLN Level 2', _('YBLN Level 2')),
        ('YFS Level 1', _('YFS Level 1')),
        ('YFS Level 2', _('YFS Level 2')),
        ('CBECE Level 1', _('CBECE Level 1')),
        ('CBECE Level 2', _('CBECE Level 2')),
        ('CBECE Level 3', _('CBECE Level 3')),
        ('RS Grade 7', _('RS Grade 7')),
        ('RS Grade 8', _('RS Grade 8')),
        ('RS Grade 9', _('RS Grade 9')),
        ('ECD', _('ECD'))
    )
    CLASS_SECTION = Choices(
        ('', '----------'),
        ('A', _('A')),
        ('B', _('B')),
        ('C', _('C')),
        ('D', _('D')),
        ('E', _('E')),
        ('F', _('F')),
        ('G', _('G')),
        ('H', _('H')),
        ('I', _('I')),
        ('J', _('J')),
        ('K', _('K')),
        ('L', _('L')),
        ('M', _('M')),
        ('N', _('N')),
        ('O', _('O')),
        ('P', _('P')),
        ('Q', _('Q')),
        ('R', _('R')),
        ('S', _('S')),
        ('T', _('T')),
        ('U', _('U')),
        ('V', _('V')),
        ('W', _('W')),
        ('X', _('X')),
        ('Y', _('Y')),
        ('Z', _('Z')),
    )
    registration = models.ForeignKey(
        Registration,
        blank=False, null=True,
        related_name='education_service',
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
    programs = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        choices=PROGRAM,
        verbose_name=_('Education Program')
    )
    class_section = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        choices=CLASS_SECTION,
        verbose_name=_('Class Section')
    )
    # @todo not sure about this field
    registration_date = models.DateField(
        blank=True,
        null=True,
        verbose_name=_('Date of registration in the round')
    )
    completion_date = models.DateField(
        blank=True,
        null=True,
        verbose_name=_('Date of completion in the round')
    )

    round = models.ForeignKey(
        Round,
        blank=True, null=True,
        related_name='+',
        verbose_name=_('Round')
    )

    class Meta:
        ordering = ['id']
        verbose_name = "Enrolled Program"
        verbose_name_plural = "Enrolled Programs"


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
        verbose_name=_('Did the adolescent complete the YFS course?')
    )
    training_material = models.CharField(
        max_length=50,
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

