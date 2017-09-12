from __future__ import unicode_literals, absolute_import, division

from django.db import models
<<<<<<< HEAD
from django.core.urlresolvers import reverse
=======
>>>>>>> 3b9073c012bcdfc49afcb1d105deb56123ab5be1
from django.utils.translation import ugettext as _
from model_utils import Choices
from model_utils.models import TimeStampedModel
from django.conf import settings
from student_registration.students.models import Student
<<<<<<< HEAD
from student_registration.registrations.models import RegisteringAdult
=======
>>>>>>> 3b9073c012bcdfc49afcb1d105deb56123ab5be1
from student_registration.schools.models import (
    School,
    EducationLevel,
    ClassLevel,
    ClassRoom,
    Section,
<<<<<<< HEAD
    Grade,
=======
>>>>>>> 3b9073c012bcdfc49afcb1d105deb56123ab5be1
    EducationYear,
)
from student_registration.locations.models import Location
from student_registration.alp.models import ALPRound


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
    EAV_TYPE = 'enrollment'

    RELATION_TYPE = Choices(
        ('child', _('Son/Daughter')),
        ('grandchild', _('Grandchild')),
        ('nibling', _('Niece/Nephew')),
        ('relative', _('Other Relative')),
        ('other', _('Other non-Relative')),
    )

    ENROLLMENT_TYPE = Choices(
        ('no', _('No')),
        ('second', _('Yes - in 2nd shift')),
        ('first', _('Yes - in 1st shift')),
        ('private', _('Yes - in private school')),
        ('other', _('Yes - in another type of school')),
    )

    RESULT = Choices(
        ('graduated', _('Graduated')),
        ('failed', _('Failed'))
    )

    EXAM_RESULT = Choices(
        ('graduated', _('Graduated')),
        ('failed', _('Failed')),
        ('uncompleted', _('Uncompleted')),
    )

    YES_NO = Choices(
        ('yes', _('Yes')),
        ('no', _('No')),
    )

    SCHOOL_TYPE = Choices(
        ('out_the_country', _('School out of the country')),
        ('public_in_country', _('Public school in the country')),
        ('private_in_country', _('Private school in the country')),
    )

    SCHOOL_SHIFT = Choices(
        ('first', _('First shift')),
        ('second', _('Second shift')),
<<<<<<< HEAD
=======
        ('alp', _('ALP')),
>>>>>>> 3b9073c012bcdfc49afcb1d105deb56123ab5be1
    )

    YEARS = ((str(x), x) for x in range(2016, 2051))

<<<<<<< HEAD
    EDUCATION_YEARS = ((str(x-1)+'/'+str(x), str(x-1)+'/'+str(x)) for x in range(2001, 2021))
=======
    EDUCATION_YEARS = list((str(x - 1) + '/' + str(x), str(x - 1) + '/' + str(x)) for x in range(2001, 2021))
    EDUCATION_YEARS.append(('n/a', 'N/A'))
>>>>>>> 3b9073c012bcdfc49afcb1d105deb56123ab5be1

    student = models.ForeignKey(
        Student,
        blank=False, null=True,
        related_name='student_enrollment',
    )
<<<<<<< HEAD

    registering_adult = models.ForeignKey(
        RegisteringAdult,
        blank=True, null=True,
        related_name='+',
    )
    relation_to_adult = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        choices=RELATION_TYPE
    )
=======
>>>>>>> 3b9073c012bcdfc49afcb1d105deb56123ab5be1
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
    )
    section = models.ForeignKey(
        Section,
        blank=True, null=True,
        related_name='+',
        verbose_name=_('Current Section')
    )
<<<<<<< HEAD
    grade = models.ForeignKey(
        Grade,
        blank=True, null=True,
        related_name='+',
    )
=======
>>>>>>> 3b9073c012bcdfc49afcb1d105deb56123ab5be1
    classroom = models.ForeignKey(
        ClassRoom,
        blank=True, null=True,
        related_name='+',
        verbose_name=_('Current Class')
    )
<<<<<<< HEAD
    year = models.CharField(
        max_length=4,
        blank=True,
        null=True,
        choices=YEARS
    )
=======
>>>>>>> 3b9073c012bcdfc49afcb1d105deb56123ab5be1
    education_year = models.ForeignKey(
        EducationYear,
        blank=True, null=True,
        related_name='+',
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        blank=False, null=True,
        related_name='+',
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
    last_education_level = models.ForeignKey(
        ClassRoom,
        blank=True, null=True,
        related_name='+'
    )
    last_education_year = models.CharField(
        max_length=10,
        blank=True,
        null=True,
<<<<<<< HEAD
        choices=((str(x-1)+'/'+str(x), str(x-1)+'/'+str(x)) for x in range(2001, 2021))
=======
        choices=EDUCATION_YEARS
>>>>>>> 3b9073c012bcdfc49afcb1d105deb56123ab5be1
    )
    last_year_result = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        choices=RESULT
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
        choices=YES_NO
    )
    last_informal_edu_level = models.ForeignKey(
        EducationLevel,
        blank=True, null=True,
        related_name='+',
    )
    last_informal_edu_year = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        choices=((str(x-1)+'/'+str(x), str(x-1)+'/'+str(x)) for x in range(2001, 2021))
    )
    last_informal_edu_result = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        choices=RESULT
    )
    last_informal_edu_round = models.ForeignKey(
        ALPRound,
        blank=True, null=True,
        related_name='+',
    )
    last_informal_edu_final_result = models.ForeignKey(
        ClassLevel,
        blank=True, null=True,
        related_name='+',
    )
    last_school_type = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        choices=SCHOOL_TYPE
    )
    last_school_shift = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        choices=SCHOOL_SHIFT
    )
    last_school = models.ForeignKey(
        School,
        blank=True, null=True,
        related_name='+',
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

<<<<<<< HEAD
    deleted = models.BooleanField(blank=True, default=False)
    dropout_status = models.BooleanField(blank=True, default=False)
    moved = models.BooleanField(blank=True, default=False)
=======
    exam_result_arabic_cmplt = models.CharField(
        max_length=4,
        blank=True,
        null=True,
        default=None,
        verbose_name=_('Arabic Term 2')
    )

    exam_result_language_cmplt = models.CharField(
        max_length=4,
        blank=True,
        null=True,
        default=None,
        verbose_name=_('Foreign language Term 2')
    )

    exam_result_math_cmplt = models.CharField(
        max_length=4,
        blank=True,
        null=True,
        default=None,
        verbose_name=_('Arabic Term 2')
    )

    exam_total_cmplt = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name=_('Final Grade Term 2')
    )

    exam_result_final = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        choices=EXAM_RESULT,
        verbose_name=_('Final Student status')
    )

    deleted = models.BooleanField(blank=True, default=False)
    dropout_status = models.BooleanField(blank=True, default=False)
    moved = models.BooleanField(blank=True, default=False)
    outreach_barcode = models.CharField(
        max_length=50,
        blank=True,
        null=True,
    )
    new_registry = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        choices=Choices((1, _("Yes")), (0, _("No")))
    )
    student_outreached = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        choices=Choices((1, _("Yes")), (0, _("No")))
    )
    have_barcode = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        choices=Choices((1, _("Yes")), (0, _("No")))
    )
    registration_date = models.DateField(
        blank=True,
        null=True,
    )
>>>>>>> 3b9073c012bcdfc49afcb1d105deb56123ab5be1

    objects = EnrollmentManager()
    drop_objects = EnrollmentDropoutManager()

<<<<<<< HEAD
=======


>>>>>>> 3b9073c012bcdfc49afcb1d105deb56123ab5be1
    @property
    def student_fullname(self):
        if self.student:
            return self.student.full_name
        return ''

    @property
    def student_age(self):
        if self.student:
<<<<<<< HEAD
            return self.student.calc_age
        return 0

    def __unicode__(self):
        return self.student.__unicode__()
=======
            return self.student.age
        return 0

    def get_absolute_url(self):
        return '/enrollments/edit/%d/' % self.pk

    def __unicode__(self):
        if self.student:
            return self.student.__unicode__()
        return str(self.id)
>>>>>>> 3b9073c012bcdfc49afcb1d105deb56123ab5be1


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


class LoggingStudentMove(TimeStampedModel):

    student = models.ForeignKey(
        Student,
        blank=False,
        null=False,
        related_name='+',
        verbose_name='Student',
    )
    enrolment = models.ForeignKey(
        Enrollment,
        blank=False,
        null=False,
        related_name='+',
        verbose_name='Enrollment',
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

    class Meta:
        ordering = ['id']
        verbose_name = "Student moves logs"
        verbose_name_plural = "Student moves logs"

    def __unicode__(self):
        return str(self.id)
