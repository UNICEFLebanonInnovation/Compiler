from __future__ import unicode_literals, absolute_import, division

from django.db import models
from django.utils.translation import ugettext as _
from model_utils import Choices
from model_utils.models import TimeStampedModel
from django.conf import settings
from student_registration.students.models import (
    Student,
    Person)
from student_registration.schools.models import (
    School,
    ClassRoom,
    Section,
    Grade,
)
from student_registration.eav.registry import Registry as eav


class RegisteringAdult(Person):

    STATUS = Choices(
        ('pending', _('Pending')),
    )

    RELATION_TYPE = Choices(
        ('head', _('Household Head')),
        ('spouse', _('Spouse')),
        ('parent', _('Farther/Mother')),
        ('relative', _('Other Relative')),
        ('other', _('Other non-Relative')),
    )

    status = models.CharField(max_length=50, blank=True, null=True, choices=STATUS)
    previously_registered = models.BooleanField(default=False)
    relation_to_child = models.CharField(max_length=50, choices=RELATION_TYPE)
    wfp_case_number = models.CharField(max_length=50, blank=True, null=True)
    csc_case_number = models.CharField(max_length=50, blank=True, null=True)
    card_issue_requested = models.BooleanField(default=False)
    child_enrolled_in_this_school = models.PositiveIntegerField()
    child_enrolled_in_other_schools = models.PositiveIntegerField()
    school = models.ForeignKey(
        School,
        blank=False, null=True,
        related_name='+',
    )


class Phone(models.Model):

    PHONE_TYPE = Choices(
        ('first', _('first')),
        ('second', _('second')),
        ('other', _('Other')),
    )

    adult = models.ForeignKey(RegisteringAdult, related_name='phones')
    prefix = models.CharField(max_length=45L, unique=True)
    number = models.CharField(max_length=45L, unique=True)
    extension = models.CharField(max_length=45L, unique=True)
    type = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        choices=PHONE_TYPE
    )


class Registration(TimeStampedModel):

    EAV_TYPE = 'registration'

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

    student = models.ForeignKey(
        Student,
        blank=False, null=True,
        related_name='+',
    )

    registering_adult = models.ForeignKey(RegisteringAdult, blank=True, null=True)
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

    school = models.ForeignKey(
        School,
        blank=False, null=True,
        related_name='+',
    )
    section = models.ForeignKey(
        Section,
        blank=False, null=True,
        related_name='+',
    )
    grade = models.ForeignKey(
        Grade,
        blank=False, null=True,
        related_name='+',
    )
    classroom = models.ForeignKey(
        ClassRoom,
        blank=False, null=True,
        related_name='+'
    )
    year = models.CharField(
        max_length=4,
        blank=True,
        null=True,
        choices=((str(x), x) for x in range(2016, 2051))
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        blank=False, null=True,
        related_name='+',
    )

    @property
    def student_fullname(self):
        if self.student:
            return self.student.full_name
        return ''

    def __unicode__(self):
        return self.student_fullname


eav.register(Registration)

