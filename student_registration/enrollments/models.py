from __future__ import unicode_literals, absolute_import, division

from django.db import models
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _
from model_utils import Choices
from model_utils.models import TimeStampedModel
from django.conf import settings
from student_registration.students.models import Student
from student_registration.registrations.models import RegisteringAdult
from student_registration.schools.models import (
    School,
    EducationLevel,
    ClassLevel,
    ClassRoom,
    Section,
    Grade,
)
from student_registration.locations.models import Location
from student_registration.alp.models import ALPRound


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
    )

    YEARS = ((str(x), x) for x in range(2016, 2051))

    EDUCATION_YEARS = ((str(x-1)+'/'+str(x), str(x-1)+'/'+str(x)) for x in range(2001, 2021))

    student = models.ForeignKey(
        Student,
        blank=False, null=True,
        related_name='student_enrollment',
    )

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
        related_name='+',
    )
    section = models.ForeignKey(
        Section,
        blank=True, null=True,
        related_name='+',
    )
    grade = models.ForeignKey(
        Grade,
        blank=True, null=True,
        related_name='+',
    )
    classroom = models.ForeignKey(
        ClassRoom,
        blank=True, null=True,
        related_name='+'
    )
    year = models.CharField(
        max_length=4,
        blank=True,
        null=True,
        choices=YEARS
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
        choices=((str(x-1)+'/'+str(x), str(x-1)+'/'+str(x)) for x in range(2001, 2021))
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
    deleted = models.BooleanField(blank=True, default=False)

    @property
    def student_fullname(self):
        if self.student:
            return self.student.full_name
        return ''

    @property
    def student_age(self):
        if self.student:
            return self.student.calc_age
        return 0

    def __unicode__(self):
        return self.student.__unicode__()


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
        verbose_name = "Student move"

    def __unicode__(self):
        return str(self.id)
