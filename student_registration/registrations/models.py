from __future__ import unicode_literals, absolute_import, division

from django.db import models
from django.core.urlresolvers import reverse
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
    """
    Captures the details of the adult who
    is registering the child in the pilot
    """
    STATUS = Choices(
        ('pending', _('Pending')),
    )

    RELATION_TYPE = Choices(
        ('head', _('I am the household head')),
        ('spouse', _('Spouse')),
        ('parent', _('Father/Mother')),
        ('relative', _('Other Relative')),
        ('other', _('Other non-Relative')),
    )

    PHONE_ANSWEREDBY = Choices(
        ('me', _('Me personally')),
        ('relay', _('Someone who always relays the message to me')),
        ('notrelay', _('Someone who may not relay the message to me')),
    )

    status = models.BooleanField(blank=True, default=False)
    previously_registered = models.BooleanField(default=False)
    relation_to_householdhead = models.CharField(max_length=50, blank=True, null=True, choices=RELATION_TYPE)
    wfp_case_number = models.CharField(max_length=50, blank=True, null=True)
    csc_case_number = models.CharField(max_length=50, blank=True, null=True)
    card_issue_requested = models.BooleanField(default=False)
    child_enrolled_in_this_school = models.PositiveIntegerField(blank=True, null=True)
    child_enrolled_in_other_schools = models.BooleanField(default=False)
    primary_phone = models.CharField(max_length=50, blank=True, null=True)
    # primary_phone_answered = models.CharField(max_length=50, blank=True, null=True)
    primary_phone_answered = models.CharField(max_length=50, blank=True, null=True, choices=PHONE_ANSWEREDBY)
    secondary_phone = models.CharField(max_length=50, blank=True, null=True)
    # secondary_phone_answered = models.CharField(max_length=50, blank=True, null=True)
    secondary_phone_answered = models.CharField(max_length=50, blank=True, null=True, choices=PHONE_ANSWEREDBY)
    signature = models.TextField(blank=True, null=True)
    school = models.ForeignKey(
        School,
        blank=True, null=True,
        related_name='+',
    )

    def get_absolute_url(self):
        return reverse('registrations:registering_child', kwargs={'pk': self.pk})


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
    """
    Captures the details of the child in the cash pilot
    """
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

    registering_adult = models.ForeignKey(
        RegisteringAdult,
        blank=True, null=True
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
        return 'none'
        # return self.student_fullname


eav.register(Registration)

