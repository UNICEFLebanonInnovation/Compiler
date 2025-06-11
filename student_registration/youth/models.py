from __future__ import unicode_literals, absolute_import, division

from django.db import models
from django.conf import settings
# from django.utils.translation import gettext as _
# from django.db.models import ArrayField, JSONField
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _
import re
from model_utils import Choices
from model_utils.models import TimeStampedModel
from datetime import datetime


from student_registration.adolescent.models import Adolescent
from student_registration.locations.models import Center, Location

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


class Partner(models.Model):

    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name=_('Full Name')
    )
    short_name = models.CharField(
        max_length=100,
        blank=True,
        unique=True,
        verbose_name=_('Short Name')
    )
    monitoring_evaluation_focal_point_name = models.CharField(
        blank=True,
        null=True,
        max_length=100,
        verbose_name=_('Monitoring and Evaluation Focal Point Name')
    )
    monitoring_evaluation_focal_point_phone = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name=_('Monitoring and Evaluation Focal Point Phone')
    )
    monitoring_evaluation_focal_point_email = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name=_('Monitoring and Evaluation Focal Point Email')
    )
    program_manager_focal_point_name = models.CharField(
        blank=True,
        null=True,
        max_length=100,
        verbose_name=_('Program Manager Focal Point Name')
    )
    program_manager_focal_point_phone = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name=_('Program Manager Focal Point Phone')
    )
    program_manager_focal_point_email = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name=_('Program Manager Focal Point Email')
    )
    active = models.BooleanField(blank=True, default=False)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    def __unicode__(self):
        return self.name


class FundedBy(models.Model):

    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name=_('Funded By')
    )
    active = models.BooleanField(blank=True, default=False)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    def __unicode__(self):
        return self.name


class ProjectStatus(models.Model):

    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name=_('Project Status')
    )

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    def __unicode__(self):
        return self.name


class FocalPoint(models.Model):

    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name=_('Name of Focal Point')
    )
    phone = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name=_('Focal Point Phone Number')
    )
    email = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name=_('Focal Point Email')
    )
    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    def __unicode__(self):
        return self.name


class Plan(models.Model):

    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name=_('Plan')
    )
    active = models.BooleanField(blank=True, default=False)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    def __unicode__(self):
        return self.name


class Sector(models.Model):

    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name=_('Sector')
    )
    default = models.BooleanField(blank=True, default=False)


    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    def __unicode__(self):
        return self.name


class ProjectType(models.Model):

    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name=_('Project Type')
    )

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    def __unicode__(self):
        return self.name


class PopulationGroups(models.Model):

    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name=_('Full Name')
    )
    short_name = models.CharField(
        max_length=100,
        blank=True, null=True,
        verbose_name=_('Short Name')
    )

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    def __unicode__(self):
        return self.name


class ProgramType(models.Model):

    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name=_('Program Type')
    )

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    def __unicode__(self):
        return self.name


class ProgramTag(models.Model):

    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name=_('Program Tag')
    )

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    def __unicode__(self):
        return self.name


class MasterProgram(TimeStampedModel):
    number = models.CharField(max_length=20, default='1')
    name = models.CharField(max_length=100)
    program_type = models.ForeignKey(
        ProgramType,
        blank=True, null=True,
        related_name='+',
        on_delete=models.SET_NULL,
        verbose_name=_('Program Type')
    )
    program_tag = models.ForeignKey(
        ProgramTag,
        blank=True, null=True,
        related_name='+',
        on_delete=models.SET_NULL,
        verbose_name=_('Program Tag')
    )
    active = models.BooleanField(blank=True, default=False)

    class Meta:
        ordering = ['name']
        verbose_name = "Master Program"

    def __str__(self):
        return self.number + ' - ' + self.name

    def __unicode__(self):
        return self.number + ' - ' + self.name

    def clean(self):
        super(MasterProgram, self).clean()

        if not self.number:
            raise ValidationError({'number': _('Number cannot be empty')})
        if not self.name:
            raise ValidationError({'name': _('Name cannot be empty')})

        # Normalize the name to ignore slight variations and equivalence of '&' and 'and'
        normalized_name = re.sub(r'\s*(?:&|and)\s*', ' ', self.name.lower().strip())

        # Extract the year from the creation date
        creation_year = self.created.year if self.created else datetime.now().year

        # Check for duplicates within the same year
        duplicates = MasterProgram.objects.exclude(id=self.id).filter(created__year=creation_year)
        for program in duplicates:
            normalized_duplicate_name = re.sub(r'\s*(?:&|and)\s*', ' ', program.name.lower().strip())
            if normalized_name == normalized_duplicate_name:
                raise ValidationError({'name': _('A Master Program with a similar name already exists in the same year: %s') % program.name})

    def creation_year(self):
        return self.created.year if self.created else 'Unknown'
    creation_year.short_description = 'Creation Year'


class SubProgram(TimeStampedModel):

    master_program = models.ForeignKey(
        MasterProgram,
        blank=False, null=True,
        on_delete=models.SET_NULL,
        related_name='master_program',
    )
    number = models.CharField(max_length=20, default='1')
    name = models.CharField(max_length=100)

    class Meta:
        ordering = ['name']
        verbose_name = "Sub Program"

    def __str__(self):
        return self.number + ' - ' + self.name

    def __unicode__(self):
        return self.number + ' - ' + self.name

    def clean(self):
        super(SubProgram, self).clean()

        if not self.number:
            raise ValidationError({'number': _('Number cannot be empty')})
        if not self.name:
            raise ValidationError({'name': _('Name cannot be empty')})

        # Normalize the name to ignore slight variations and equivalence of '&' and 'and'
        normalized_name = re.sub(r'\s*(?:&|and)\s*', ' ', self.name.lower().strip())

        # Extract the year from the creation date
        creation_year = self.created.year if self.created else datetime.now().year

        # Check for duplicates within the same year
        duplicates = SubProgram.objects.exclude(id=self.id).filter(created__year=creation_year)
        for program in duplicates:
            normalized_duplicate_name = re.sub(r'\s*(?:&|and)\s*', ' ', program.name.lower().strip())
            if normalized_name == normalized_duplicate_name:
                raise ValidationError({'name': _('A Sub Program with a similar name already exists in the same year: %s') % program.name})

    def creation_year(self):
        return self.created.year if self.created else 'Unknown'
    creation_year.short_description = 'Creation Year'


class Donor(models.Model):

    name = models.CharField(max_length=100, unique=True)
    active = models.BooleanField(blank=True, default=False)

    class Meta:
        ordering = ['name']
        verbose_name = "Donor"

    def __str__(self):
        return self.name

    def __unicode__(self):
        return self.name


class ProgramDocument(TimeStampedModel):
    YES_NO = Choices(
        ('', '----------'),
        ('Yes', _("Yes")),
        ('No', _("No"))
    )
    SUPPORT = Choices(
        ('', '----------'),
        ('No Support', _("No Support")),
        ('Support', _("Support"))
    )
    partner = models.ForeignKey(
        Partner,
        blank=True, null=True,
        related_name='+',
        on_delete=models.SET_NULL,
        verbose_name=_('Organization Name')
    )
    funded_by = models.ForeignKey(
        FundedBy,
        blank=True, null=True,
        related_name='+',
        on_delete=models.SET_NULL,
        verbose_name=_('Funded By')
    )
    project_status = models.ForeignKey(
        ProjectStatus,
        blank=True, null=True,
        related_name='+',
        on_delete=models.SET_NULL,
        verbose_name=_('Project Status')
    )
    project_code = models.CharField(
        max_length=100,
        default='project_code',
        verbose_name=_('Project Code')
    )
    project_name = models.CharField(
        max_length=250,
        default='project_name',
        verbose_name=_('Project Name')
    )
    project_description = models.CharField(
        max_length=300,
        blank=True, null=True,
        verbose_name=_('Project Description')
    )
    implementing_partners = models.CharField(
        max_length=100,
        blank=True, null=True,
        verbose_name=_('Key Implementing Partner(s)')
    )
    focal_point = models.ForeignKey(
        FocalPoint,
        blank=True, null=True,
        related_name='+',
        on_delete=models.SET_NULL,
        verbose_name=_('UNICEF Focal Point')
    )
    start_date = models.DateField(
        blank=True,
        null=True,
        verbose_name=_('Start Date')
    )
    end_date = models.DateField(
        blank=True,
        null=True,
        verbose_name=_('End Date')
    )
    comment = models.TextField(
        blank=True, null=True,
        verbose_name=_('Comment')
    )
    plan = models.ForeignKey(
        Plan,
        blank=True, null=True,
        related_name='+',
        on_delete=models.SET_NULL,
        verbose_name=_('Plan')
    )
    sectors = models.ForeignKey(
        Sector,
        blank=True, null=True,
        related_name='+',
        on_delete=models.SET_NULL,
        verbose_name=_('SELECT SECTORS TARGETED BY THIS PROJECT')
    )
    project_type = models.ForeignKey(
        ProjectType,
        blank=True, null=True,
        related_name='+',
        on_delete=models.SET_NULL,
        verbose_name=_('Type of Project')
    )
    public_institution_support = models.CharField(
        max_length=100,
        blank=True, null=True,
        choices=SUPPORT,
        verbose_name=_('Support of Public Institution')
    )
    governorates = models.ManyToManyField(Location, blank=True, related_name='+', verbose_name=_('Governorate of Coverage'))

    budget = models.FloatField(
        blank=True,
        null=True,
        verbose_name=_('Please add the Project Budget in USD')
    )
    cash_assistance = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=YES_NO,
        verbose_name=_('Does this Project have any Cash Assistance Component')
    )
    population_groups = models.ManyToManyField(PopulationGroups, blank=True, verbose_name=_('Population Groups Targeted'))

    number_targeted_syrians = models.IntegerField(
        blank=True,
        null=True,
        verbose_name=_('Number of Targeted Displaced Syrians')
    )
    number_targeted_lebanese = models.IntegerField(
        blank=True,
        null=True,
        verbose_name=_('Number of Targeted Lebanese')
    )
    number_targeted_prl = models.IntegerField(
        blank=True,
        null=True,
        verbose_name=_('Number of Targeted PRL')
    )
    number_targeted_prs = models.IntegerField(
        blank=True,
        null=True,
        verbose_name=_('Number of Targeted PRS')
    )
    master_programs = models.ManyToManyField(MasterProgram, blank=True, verbose_name=_('Master Programs'))
    donors = models.ManyToManyField(Donor, blank=True, verbose_name=_('Donors'))

    master_program1 = models.ForeignKey(
        MasterProgram,
        blank=True, null=True,
        related_name='master_program1',
        on_delete=models.SET_NULL,
        verbose_name=_('Master Program 1')
    )
    master_program2 = models.ForeignKey(
        MasterProgram,
        blank=True, null=True,
        related_name='master_program2',
        on_delete=models.SET_NULL,
        verbose_name=_('Master Program 2')
    )
    master_program3 = models.ForeignKey(
        MasterProgram,
        blank=True, null=True,
        related_name='master_program3',
        on_delete=models.SET_NULL,
        verbose_name=_('Master Program 3')
    )
    baseline1 = models.IntegerField(blank=True, null=True)
    baseline2 = models.IntegerField(blank=True, null=True)
    baseline3 = models.IntegerField(blank=True, null=True)

    target1 = models.IntegerField(blank=True, null=True)
    target2 = models.IntegerField(blank=True, null=True)
    target3 = models.IntegerField(blank=True, null=True)

    class Meta:
        ordering = ['project_name']
        verbose_name = "Program Document"

    def __str__(self):
        return self.project_name

    def __unicode__(self):
        return self.project_name

    def get_governorate_names(self):
        return ", ".join(pop.name for pop in self.governorates.all())
    # get_governorate_names.short_description = _('Governorates')

    def get_population_groups_name(self):
        return ", ".join(gov.name for gov in self.population_groups.all())

    def get_master_program_names(self):
        # Gather the names of the master programs if they exist
        programs = [
            self.master_program1.name if self.master_program1 else None,
            self.master_program2.name if self.master_program2 else None,
            self.master_program3.name if self.master_program3 else None
        ]
        # Filter out None values and join with commas
        return ", ".join(filter(None, programs))

    def get_donor_names(self):
        return ", ".join(donor.name for donor in self.donors.all())
        # return "\n".join(donor.name for donor in self.donors.all())

    def clean(self):
        super(ProgramDocument, self).clean()

        if not self.project_name:
            raise ValidationError({'project_name': _('Project Name cannot be empty')})
        if not self.project_code:
            raise ValidationError({'project_code': _('Project Code cannot be empty')})


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
        on_delete=models.SET_NULL,
        verbose_name=_('Center')
    )
    adolescent = models.ForeignKey(
        Adolescent,
        blank=False, null=True,
        related_name='+',
        on_delete=models.SET_NULL,
        verbose_name=_('adolescent')
    )
    child_outreach = models.IntegerField(blank=True, null=True)
    student_old = models.IntegerField(blank=True, null=True)
    partner = models.ForeignKey(
        Partner,
        blank=True, null=True,
        verbose_name=_('Partner'),
        related_name='+',
        on_delete=models.SET_NULL,
    )
    round = models.ForeignKey(
        Round,
        blank=True, null=True,
        related_name='+',
        on_delete=models.SET_NULL,
        verbose_name=_('Round')
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        blank=False, null=True,
        related_name='+',
        on_delete=models.SET_NULL,
    )
    modified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        blank=True, null=True,
        related_name='+',
        on_delete=models.SET_NULL,
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
        program = self.enrolled_programs.all()
        if program:
            result = program.program
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
    registration = models.ForeignKey(
        Registration,
        blank=False, null=True,
        on_delete=models.SET_NULL,
        related_name='enrolled_programs',
    )

    education_status = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        choices=EDUCATION_STATUS,
        verbose_name=_('Child\'s educational level when registering')
    )
    dropout_date = models.DateField(
        blank=True,
        null=True,
        verbose_name=_('Please Specify dropout date from school')
    )
    master_program = models.ForeignKey(
        MasterProgram,
        blank=False, null=True,
        related_name='+',
        on_delete=models.SET_NULL,
    )
    sub_program = models.ForeignKey(
        SubProgram,
        blank=False, null=True,
        related_name='+',
        on_delete=models.SET_NULL,
    )
    donor = models.ForeignKey(
        Donor,
        blank=False, null=True,
        related_name='+',
        on_delete=models.SET_NULL,
    )
    program_document = models.ForeignKey(
        ProgramDocument,
        blank=False, null=True,
        related_name='+',
        on_delete=models.SET_NULL,
    )
    registration_date = models.DateField(
        blank=True,
        null=True,
        verbose_name=_('Date of registration')
    )
    completion_date = models.DateField(
        blank=True,
        null=True,
        verbose_name=_('Date of completion')
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
        on_delete=models.SET_NULL,
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

