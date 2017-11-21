from __future__ import unicode_literals, absolute_import, division

import datetime

from django.db import models
from django.conf import settings
from django.utils.translation import ugettext as _

from model_utils import Choices
from model_utils.models import TimeStampedModel

from student_registration.students.models import Student
from student_registration.schools.models import (
    School,
    EducationLevel,
    ClassLevel,
    ClassRoom,
    Section,
    EducationYear,
)
from student_registration.locations.models import Location
from student_registration.alp.models import ALPRound, Outreach


class EnrollmentManager(models.Manager):
    def get_queryset(self):
        return super(EnrollmentManager, self).get_queryset().exclude(deleted=True).exclude(dropout_status=True)


class EnrollmentDropoutManager(models.Manager):
    def get_queryset(self):
        return super(EnrollmentDropoutManager, self).get_queryset().exclude(deleted=True).filter(dropout_status=True)


class Enrollment(TimeStampedModel):
    """
    Captures the details of the child in the cash pilot
    """
    ENROLLMENT_TYPE = Choices(
        ('no', _('No')),
        ('second', _('Yes - in 2nd shift')),
        ('first', _('Yes - in 1st shift')),
        ('private', _('Yes - in private school')),
        ('other', _('Yes - in another type of school')),
    )

    RESULT = Choices(
        ('na', 'n/a'),
        ('graduated', _('Graduated')),
        ('failed', _('Failed'))
    )

    EXAM_RESULT = Choices(
        ('na', _('n/a')),
        ('graduated', _('Graduated')),
        ('failed', _('Failed')),
        ('uncompleted', _('Uncompleted')),
    )

    YES_NO = Choices(
        ('yes', _('Yes')),
        ('no', _('No')),
    )

    SCHOOL_TYPE = Choices(
        ('na', 'n/a'),
        ('out_the_country', _('School out of the country')),
        ('public_in_country', _('Public school in the country')),
        ('private_in_country', _('Private school in the country')),
    )

    SCHOOL_SHIFT = Choices(
        ('na', 'n/a'),
        ('first', _('First shift')),
        ('second', _('Second shift')),
        # ('alp', _('ALP')),
    )

    CURRENT_YEAR = datetime.datetime.now().year

    YEARS = ((str(x), x) for x in range(2016, CURRENT_YEAR))

    EDUCATION_YEARS = list((str(x - 1) + '/' + str(x), str(x - 1) + '/' + str(x)) for x in range(2001, 2050))
    EDUCATION_YEARS.append(('na', 'N/A'))

    student = models.ForeignKey(
        Student,
        blank=False, null=True,
        related_name='student_enrollment',
    )
    enrolled_last_year = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        choices=ENROLLMENT_TYPE
    )

    enrolled_last_year_school = models.ForeignKey(
        School,
        blank=True, null=True,
        related_name='+',
    )
    enrolled_last_year_location = models.ForeignKey(
        Location,
        blank=True, null=True,
        related_name='+',
    )

    school = models.ForeignKey(
        School,
        blank=False, null=True,
        related_name='ndshift_school',
        verbose_name=_('School')
    )
    section = models.ForeignKey(
        Section,
        blank=True, null=True,
        related_name='+',
        verbose_name=_('Current Section')
    )
    classroom = models.ForeignKey(
        ClassRoom,
        blank=True, null=True,
        related_name='+',
        verbose_name=_('Current Class')
    )
    education_year = models.ForeignKey(
        EducationYear,
        blank=True, null=True,
        related_name='+',
        verbose_name=_('Education year')
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        blank=False, null=True,
        related_name='+',
        verbose_name=_('Created by')
    )
    status = models.BooleanField(blank=True, default=True)
    out_of_school_two_years = models.BooleanField(blank=True, default=False)
    related_to_family = models.BooleanField(blank=True, default=False)
    enrolled_in_this_school = models.BooleanField(blank=True, default=True)
    registered_in_unhcr = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        choices=YES_NO
    )

    number_in_previous_school = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name=_('Serial number in previous school')
    )

    last_education_level = models.ForeignKey(
        ClassRoom,
        blank=True, null=True,
        related_name='+',
        verbose_name=_('Last Education level')
    )
    last_education_year = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        choices=EDUCATION_YEARS,
        verbose_name=_('Last Education year')
    )
    last_year_result = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        choices=RESULT,
        verbose_name=_('Last Education result')
    )
    result = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        choices=RESULT
    )
    participated_in_alp = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        choices=Choices(
            ('na', 'n/a'),
            ('yes', _('Yes')),
            ('no', _('No')),
        ),
        verbose_name=_('Participated in ALP')
    )
    last_informal_edu_level = models.ForeignKey(
        EducationLevel,
        blank=True, null=True,
        related_name='+',
        verbose_name=_('Last informal education level')
    )
    last_informal_edu_year = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        choices=((str(x-1)+'/'+str(x), str(x-1)+'/'+str(x)) for x in range(2001, CURRENT_YEAR)),
        verbose_name=_('Last informal education year')
    )
    last_informal_edu_result = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        choices=RESULT,
        verbose_name=_('Last informal education result')
    )
    last_informal_edu_round = models.ForeignKey(
        ALPRound,
        blank=True, null=True,
        related_name='+',
        verbose_name=_('Last informal education round'),
    )
    last_informal_edu_final_result = models.ForeignKey(
        ClassLevel,
        blank=True, null=True,
        related_name='+',
        verbose_name=_('Last informal education status'),
    )
    last_school_type = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        choices=SCHOOL_TYPE,
        verbose_name=_('Last school type'),
    )
    last_school_shift = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        choices=SCHOOL_SHIFT,
        verbose_name=_('Last school shift'),
    )
    last_school = models.ForeignKey(
        School,
        blank=True, null=True,
        related_name='+',
        verbose_name=_('Last school'),
    )

    exam_result_arabic = models.CharField(
        max_length=4,
        blank=True,
        null=True,
        verbose_name=_('Arabic')
    )

    exam_result_language = models.CharField(
        max_length=4,
        blank=True,
        null=True,
        verbose_name=_('Foreign Language')
    )

    exam_result_education = models.CharField(
        max_length=4,
        blank=True,
        null=True,
        verbose_name=_('Education')
    )

    exam_result_geo = models.CharField(
        max_length=4,
        blank=True,
        null=True,
        verbose_name=_('Geography')
    )

    exam_result_history = models.CharField(
        max_length=4,
        blank=True,
        null=True,
        verbose_name=_('History')
    )

    exam_result_math = models.CharField(
        max_length=4,
        blank=True,
        null=True,
        verbose_name=_('Math')
    )

    exam_result_science = models.CharField(
        max_length=4,
        blank=True,
        null=True,
        verbose_name=_('Science')
    )

    exam_result_physic = models.CharField(
        max_length=4,
        blank=True,
        null=True,
        verbose_name=_('Physic')
    )

    exam_result_chemistry = models.CharField(
        max_length=4,
        blank=True,
        null=True,
        verbose_name=_('Chemistry')
    )

    exam_result_bio = models.CharField(
        max_length=4,
        blank=True,
        null=True,
        verbose_name=_('Biology')
    )

    exam_result_linguistic_ar = models.CharField(
        max_length=4,
        blank=True,
        null=True,
        default=None,
        verbose_name=_('Linguistic field/Arabic')
    )
    exam_result_linguistic_en = models.CharField(
        max_length=4,
        blank=True,
        null=True,
        default=None,
        verbose_name=_('Linguistic field/Foreign language')
    )

    exam_result_sociology = models.CharField(
        max_length=4,
        blank=True,
        null=True,
        default=None,
        verbose_name=_('Sociology field')
    )

    exam_result_physical = models.CharField(
        max_length=4,
        blank=True,
        null=True,
        default=None,
        verbose_name=_('Physical field')
    )

    exam_result_artistic = models.CharField(
        max_length=4,
        blank=True,
        null=True,
        default=None,
        verbose_name=_('Artistic field')
    )

    exam_result_mathematics = models.CharField(
        max_length=4,
        blank=True,
        null=True,
        default=None,
        verbose_name=_('Scientific domain/Mathematics')
    )

    exam_result_sciences = models.CharField(
        max_length=4,
        blank=True,
        null=True,
        default=None,
        verbose_name=_('Scientific domain/Sciences')
    )

    exam_total = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name=_('Final Grade')
    )

    exam_result = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        choices=EXAM_RESULT,
        verbose_name=_('Student status')
    )

    exam_result_arabic_cmplt = models.CharField(
        max_length=4,
        blank=True,
        null=True,
        default=None,
        verbose_name=_('Arabic')
    )

    exam_result_language_cmplt = models.CharField(
        max_length=4,
        blank=True,
        null=True,
        default=None,
        verbose_name=_('Foreign Language')
    )

    exam_result_math_cmplt = models.CharField(
        max_length=4,
        blank=True,
        null=True,
        default=None,
        verbose_name=_('Math')
    )

    exam_total_cmplt = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name=_('Final Grade')
    )

    exam_result_final = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        choices=EXAM_RESULT,
        verbose_name=_('Final Student status')
    )

    deleted = models.BooleanField(
        blank=True, default=False,
        verbose_name=_('deleted')
    )
    dropout_status = models.BooleanField(
        blank=True, default=False,
        verbose_name=_('Dropout status')
    )
    moved = models.BooleanField(
        blank=True, default=False,
        verbose_name=_('moved')
    )
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

    objects = EnrollmentManager()
    drop_objects = EnrollmentDropoutManager()

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

    def grading(self, term):
        if self.enrollment_gradings.count():
            return self.enrollment_gradings.get(exam_term=term).id
        return 0

    @property
    def grading_term1(self):
        return self.grading(1)

    @property
    def grading_term2(self):
        return self.grading(2)

    @property
    def final_grading(self):
        return self.grading(3)

    @property
    def last_year_grading_result(self):
        if self.enrollment_gradings.count():
            return self.enrollment_gradings.get(exam_term=3).exam_result
        return ''

    @property
    def incomplete_grading(self):
        return self.grading(4)

    @property
    def pass_to_incomplete_exam(self):
        return False

    def get_absolute_url(self):
        return '/enrollments/edit/%d/' % self.pk

    class Meta:
        ordering = ['-student__first_name']

    def __unicode__(self):
        if self.student:
            return self.student.__unicode__()
        return str(self.id)


class StudentMove(models.Model):

    enrolment1 = models.ForeignKey(
        Enrollment,
        blank=False, null=False,
        related_name='+',
        verbose_name='Student name',
    )
    enrolment2 = models.ForeignKey(
        Enrollment,
        blank=False, null=False,
        related_name='+',
        verbose_name='Student name',
    )
    school1 = models.ForeignKey(
        School,
        blank=False, null=False,
        related_name='+',
        verbose_name='From school',
    )
    school2 = models.ForeignKey(
        School,
        blank=False, null=False,
        related_name='+',
        verbose_name='To school',
    )

    class Meta:
        ordering = ['id']
        verbose_name = "Auto search student moves"
        verbose_name_plural = "Auto search student moves"

    def __unicode__(self):
        return str(self.id)


class EnrollmentGrading(models.Model):

    EXAM_RESULT = Choices(
        ('na', _('n/a')),
        ('graduated', _('Graduated')),
        ('failed', _('Failed')),
        ('uncompleted', _('Uncompleted')),
    )

    exam_result_arabic = models.CharField(
        max_length=4,
        blank=True,
        null=True,
        verbose_name=_('Arabic')
    )

    exam_result_language = models.CharField(
        max_length=4,
        blank=True,
        null=True,
        verbose_name=_('Foreign language')
    )

    exam_result_education = models.CharField(
        max_length=4,
        blank=True,
        null=True,
        verbose_name=_('Education')
    )

    exam_result_geo = models.CharField(
        max_length=4,
        blank=True,
        null=True,
        verbose_name=_('Geography')
    )

    exam_result_history = models.CharField(
        max_length=4,
        blank=True,
        null=True,
        verbose_name=_('History')
    )

    exam_result_math = models.CharField(
        max_length=4,
        blank=True,
        null=True,
        verbose_name=_('Math')
    )

    exam_result_science = models.CharField(
        max_length=4,
        blank=True,
        null=True,
        verbose_name=_('Science')
    )

    exam_result_physic = models.CharField(
        max_length=4,
        blank=True,
        null=True,
        verbose_name=_('Physic')
    )

    exam_result_chemistry = models.CharField(
        max_length=4,
        blank=True,
        null=True,
        verbose_name=_('Chemistry')
    )

    exam_result_bio = models.CharField(
        max_length=4,
        blank=True,
        null=True,
        verbose_name=_('Biology')
    )

    exam_result_linguistic_ar = models.CharField(
        max_length=4,
        blank=True,
        null=True,
        default=None,
        verbose_name=_('Linguistic field/Arabic')
    )
    exam_result_linguistic_en = models.CharField(
        max_length=4,
        blank=True,
        null=True,
        default=None,
        verbose_name=_('Linguistic field/Foreign language')
    )

    exam_result_sociology = models.CharField(
        max_length=4,
        blank=True,
        null=True,
        default=None,
        verbose_name=_('Sociology field')
    )

    exam_result_physical = models.CharField(
        max_length=4,
        blank=True,
        null=True,
        default=None,
        verbose_name=_('Physical field')
    )

    exam_result_artistic = models.CharField(
        max_length=4,
        blank=True,
        null=True,
        default=None,
        verbose_name=_('Artistic field')
    )

    exam_result_mathematics = models.CharField(
        max_length=4,
        blank=True,
        null=True,
        default=None,
        verbose_name=_('Scientific domain/Mathematics')
    )

    exam_result_sciences = models.CharField(
        max_length=4,
        blank=True,
        null=True,
        default=None,
        verbose_name=_('Scientific domain/Sciences')
    )

    exam_total = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name=_('Final Grade')
    )

    exam_result = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        choices=EXAM_RESULT,
        verbose_name=_('Student status')
    )

    exam_term = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name=_('Term')
    )
    enrollment = models.ForeignKey(
        Enrollment,
        blank=False, null=False,
        related_name='enrollment_gradings',
        on_delete=models.CASCADE
    )

    class Meta:
        ordering = ['id']

    def __unicode__(self):
        return str(self.id)


class LoggingStudentMove(TimeStampedModel):

    student = models.ForeignKey(
        Student,
        blank=False,
        null=False,
        related_name='+',
        verbose_name=_('Student'),
    )
    enrolment = models.ForeignKey(
        Enrollment,
        blank=False,
        null=False,
        related_name='+',
        verbose_name=_('Enrollment'),
    )
    school_from = models.ForeignKey(
        School,
        blank=False,
        null=False,
        related_name='+',
        verbose_name=_('From school'),
    )
    school_to = models.ForeignKey(
        School,
        blank=True, null=True,
        related_name='+',
        verbose_name=_('To school'),
    )
    education_year = models.ForeignKey(
        EducationYear,
        blank=True, null=True,
        related_name='+',
    )

    class Meta:
        ordering = ['id']
        verbose_name = "Student moves logs"
        verbose_name_plural = "Student moves logs"

    def __unicode__(self):
        return str(self.id)


class LoggingProgramMove(TimeStampedModel):

    student = models.ForeignKey(
        Student,
        blank=False,
        null=False,
        related_name='+',
        verbose_name='Student',
    )
    registry = models.ForeignKey(
        Outreach,
        blank=True, null=True,
        related_name='+',
    )
    school_from = models.ForeignKey(
        School,
        blank=False,
        null=False,
        related_name='+',
        verbose_name='From school',
    )
    school_to = models.ForeignKey(
        School,
        blank=True, null=True,
        related_name='+',
        verbose_name='To school',
    )
    education_year = models.ForeignKey(
        EducationYear,
        blank=True, null=True,
        related_name='+',
    )
    eligibility = models.BooleanField(default=True)
    potential_move = models.BooleanField(default=False)

    class Meta:
        ordering = ['id']
        verbose_name = "Student moves from ALP"
        verbose_name_plural = "Student moves from ALP"

    def __unicode__(self):
        return str(self.id)
