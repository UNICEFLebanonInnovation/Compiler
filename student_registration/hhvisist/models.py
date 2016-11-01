from __future__ import unicode_literals, absolute_import, division

from django.db import models
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _
from model_utils import Choices
from model_utils.models import TimeStampedModel
from django.conf import settings
from student_registration.students.models import (
    Person,
    Student,
    Person,
)
from student_registration.schools.models import (
    School,
)
from student_registration.locations.models import Location


class WaitingList(TimeStampedModel):

    location = models.ForeignKey(
        Location,
        blank=True, null=True,
        related_name='+',
    )
    school = models.ForeignKey(
        School,
        blank=True, null=True,
        related_name='+',
    )
    first_name = models.CharField(max_length=64L, blank=True, null=True)
    last_name = models.CharField(max_length=64L, blank=True, null=True)
    father_name = models.CharField(max_length=64L, blank=True, null=True)
    unhcr_id = models.CharField(max_length=15L, blank=True, null=True)
    number_of_children = models.IntegerField(blank=True, null=True)
    phone_number = models.CharField(max_length=15L, blank=True, null=True)
    alternate_phone_number = models.CharField(max_length=15L, blank=True, null=True)
    village = models.CharField(max_length=50L, blank=True, null=True)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        blank=False, null=True,
        related_name='+',
    )

eav.register(Registration)

