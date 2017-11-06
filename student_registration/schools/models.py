from __future__ import unicode_literals, absolute_import, division

from django.db import models
from model_utils import Choices
from model_utils.models import TimeStampedModel

from django.utils.translation import ugettext as _
from django.contrib.gis.db import models
from student_registration.locations.models import Location


class School(models.Model):

    name = models.CharField(
        max_length=255,
        verbose_name=_('School name')
    )
    number = models.CharField(
        max_length=45,
        unique=True,
        verbose_name=_('CERD')
    )
    director_name = models.CharField(
        max_length=100,
        blank=True, null=True,
        verbose_name=_('School director name')
    )
    land_phone_number = models.CharField(
        max_length=100,
        blank=True, null=True,
        verbose_name=_('School land phone number')
    )
    director_phone_number = models.CharField(
        max_length=100,
        blank=True, null=True,
        verbose_name=_('School director cell phone')
    )
    it_name = models.CharField(
        max_length=100,
        blank=True, null=True,
        verbose_name=_('School IT name')
    )
    it_phone_number = models.CharField(
        max_length=100,
        blank=True, null=True,
        verbose_name=_('School IT phone number')
    )
    field_coordinator_name = models.CharField(
        max_length=100,
        blank=True, null=True,
        verbose_name=_('Field coordinator name')
    )
    is_2nd_shift = models.BooleanField(
        blank=True,
        default=False,
        verbose_name=_('School is 2nd shift?')
    )
    number_students_2nd_shift = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('Number of students in 2nd shift')
    )
    is_alp = models.BooleanField(
        blank=True,
        default=False,
        verbose_name=_('School is ALP?')
    )
    number_students_alp = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('Number of students in ALP')
    )
    attendance_range = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('Attendance day range')
    )
    academic_year_start = models.DateField(
        blank=True,
        null=True,
        verbose_name=_('School year start date')
    )
    academic_year_end = models.DateField(
        blank=True,
        null=True,
        verbose_name=_('School year end date')
    )
    academic_year_exam_end = models.DateField(
        blank=True,
        null=True,
        verbose_name=_('Exam end date')
    )
    location = models.ForeignKey(
        Location,
        blank=False, null=True,
        verbose_name=_('School location'),
        related_name='+',
    )

    class Meta:
        ordering = ['number']

    @property
    def location_name(self):
        if self.location:
            return self.location.name
        return ''

    @property
    def location_parent_name(self):
        if self.location and self.location.parent:
            return self.location.parent.name
        return ''

    @property
    def have_academic_year_dates(self):
        if not self.academic_year_start \
           or not self.academic_year_end \
           or not self.academic_year_exam_end:
            return False
        return True

    def __unicode__(self):
        return u'{} - {}'.format(
            self.name,
            self.number
        )


class EducationLevel(models.Model):
    name = models.CharField(max_length=45, unique=True)
    note = models.IntegerField(blank=True, null=True)

    class Meta:
        ordering = ['id']
        verbose_name = "ALP Level"

    def __unicode__(self):
        return self.name


class ClassLevel(models.Model):
    name = models.CharField(max_length=45, unique=True)

    class Meta:
        ordering = ['id']
        verbose_name = "ALP Result"

    def __unicode__(self):
        return self.name


class Section(models.Model):
    name = models.CharField(max_length=45, unique=True)

    class Meta:
        ordering = ['id']

    def __unicode__(self):
        return self.name


class ClassRoom(models.Model):
    name = models.CharField(max_length=45, unique=True)

    class Meta:
        ordering = ['id']
        verbose_name = "Formal Education Level"

    def __unicode__(self):
        return self.name


class CLMRound(models.Model):
    name = models.CharField(max_length=45, unique=True)

    class Meta:
        ordering = ['name']
        verbose_name = "CLM Round"

    def __unicode__(self):
        return self.name


class PartnerOrganization(models.Model):

    name = models.CharField(max_length=100, unique=True)

    bln_round = models.ForeignKey(
        CLMRound,
        blank=True, null=True,
        related_name='+',
        verbose_name=_('BLN current round')
    )
    rs_round = models.ForeignKey(
        CLMRound,
        blank=True, null=True,
        related_name='+',
        verbose_name=_('RS current round')
    )
    cbece_round = models.ForeignKey(
        CLMRound,
        blank=True, null=True,
        related_name='+',
        verbose_name=_('CB-ECE current round')
    )

    class Meta:
        ordering = ['name']

    def __unicode__(self):
        return self.name


class ALPReferMatrix(models.Model):
    level = models.ForeignKey(
        EducationLevel,
        blank=True, null=True,
        related_name='+',
    )
    success_refer_to = models.ForeignKey(
        ClassLevel,
        blank=True, null=True,
        related_name='success_refer_to',
    )
    fail_refer_to = models.ForeignKey(
        ClassLevel,
        blank=True, null=True,
        related_name='fail_refer_to',
    )
    age = models.IntegerField(blank=True, null=True)
    success_grade = models.IntegerField(blank=True, null=True)

    class Meta:
        ordering = ['id']
        verbose_name = "ALP Post-test Refer Matrix"

    def __unicode__(self):
        return str(self.id)


class EducationYear(models.Model):
    name = models.CharField(max_length=100, unique=True)
    current_year = models.BooleanField(blank=True, default=False)

    class Meta:
        ordering = ['name']
        verbose_name = "Education Year"

    def __unicode__(self):
        return self.name


class ALPAssignmentMatrix(models.Model):
    level = models.ForeignKey(
        EducationLevel,
        blank=True, null=True,
        related_name='+',
    )
    refer_to = models.ForeignKey(
        EducationLevel,
        blank=True, null=True,
        related_name='refer_to',
    )
    range_start = models.IntegerField(blank=True, null=True)
    range_end = models.IntegerField(blank=True, null=True)

    @property
    def range(self):
        return "{}-{}".format(self.range_start, self.range_end)

    class Meta:
        ordering = ['id']
        verbose_name = "ALP Pre-test Refer Matrix"

    def __unicode__(self):
        return str(self.id)


class EducationalLevel(models.Model):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        ordering = ['id']

    def __unicode__(self):
        return self.name


class Holiday(models.Model):
    name = models.CharField(max_length=100, unique=True)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)

    class Meta:
        ordering = ['id']

    def __unicode__(self):
        return self.name


class PublicDocument(TimeStampedModel):

    name = models.CharField(max_length=100)
    overview = models.TextField(blank=True, null=True)
    file_url = models.URLField(blank=True, null=True)

    class Meta:
        ordering = ['created']

    def __unicode__(self):
        return self.name
