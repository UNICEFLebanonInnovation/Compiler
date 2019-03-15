from __future__ import unicode_literals, absolute_import, division

from django.db import models
from model_utils import Choices
from model_utils.models import TimeStampedModel

from django.utils.translation import ugettext as _
# from django.contrib.gis.db import models
from student_registration.locations.models import Location


class Coordinator(models.Model):
    name = models.CharField(max_length=200, unique=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Coordinator'

    def __unicode__(self):
            return self.name


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
    director_phone_number = models.CharField(
        max_length=100,
        blank=True, null=True,
        verbose_name=_('School director cell phone')
    )
    land_phone_number = models.CharField(
        max_length=100,
        blank=True, null=True,
        verbose_name=_('School land phone number')
    )
    fax_number = models.CharField(
        max_length=100,
        blank=True, null=True,
        verbose_name=_('School fax number')
    )
    email = models.CharField(
        max_length=100,
        blank=True, null=True,
        verbose_name=_('School email')
    )
    certified_foreign_language = models.CharField(
        max_length=100,
        blank=True, null=True,
        choices=Choices(
            ('French', _('French')),
            ('English', _('English')),
            ('French & English', _('French & English'))
        ),
        verbose_name=_('Certified foreign language')
    )
    comments = models.TextField(
        blank=True, null=True,
        verbose_name=_('Comments')
    )
    weekend = models.CharField(
        max_length=100,
        blank=True, null=True,
        choices=Choices(
            ('Friday', _('Friday')),
            ('Saturday', _('Saturday')),
        ),
        verbose_name=_('School weekends')
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
    #field_coordinator_name = models.CharField(
     #   max_length=100,
      #  blank=True, null=True,
       # verbose_name=_('Field coordinator name')
       #)
    # coordinator = models.ForeignKey(
    #     Coordinator,
    #     blank=True, null=True,
    #     verbose_name=_('coordinator'),
    #     related_name='+',
    # )
    is_2nd_shift = models.BooleanField(
        blank=True,
        default=False,
        verbose_name=_('School is 2nd shift?')
    )
    number_students_2nd_shift = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('Expected number of students in 2nd shift')
    )
    is_alp = models.BooleanField(
        blank=True,
        default=False,
        verbose_name=_('School is ALP?')
    )
    number_students_alp = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('Expected number of students in ALP')
    )
    attendance_range = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('Attendance day range')
    )
    attendance_from_beginning = models.BooleanField(
        blank=True,
        default=False,
        verbose_name=_('Start attendance from the beginning')
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

    def attendances_2ndshift(self):
        qs = self.attendances.filter(
            education_year__current_year=True,
            school_type='2nd-shift'
        )
        if self.academic_year_start:
            qs = qs.filter(
                attendance_date__gte=self.academic_year_start
            )
        return qs

    def attendances_alp(self):
        return self.attendances.filter(
            alp_round__current_round=True,
            school_type='ALP'
        )

    @property
    def total_attendances_days_2ndshift(self):
        qs = self.attendances_2ndshift()
        return qs.count()

    @property
    def total_attendances_days_2ndshift_open(self):
        qs = self.attendances_2ndshift()
        return qs.exclude(close_reason__isnull=False).count()

    @property
    def total_attendances_days_alp(self):
        return self.attendances_alp().count()

    @property
    def total_attendances_days_alp_open(self):
        qs = self.attendances_alp()
        return qs.exclude(close_reason__isnull=False).count()

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
    def total_registered(self):
        from student_registration.enrollments.models import Enrollment
        return Enrollment.objects.filter(
            education_year__current_year=True,
            school_id=self.id
        ).count()

    @property
    def total_registered_2ndshift(self):
        from student_registration.enrollments.models import Enrollment
        return Enrollment.objects.filter(
            education_year__current_year=True, moved=False,
            school_id=self.id
        ).count()

    @property
    def total_registered_2ndshift_male(self):
        from student_registration.enrollments.models import Enrollment
        return Enrollment.objects.filter(
            education_year__current_year=True,
            school_id=self.id,
            student__sex='Male'
        ).count()

    @property
    def total_registered_2ndshift_female(self):
        from student_registration.enrollments.models import Enrollment
        return Enrollment.objects.filter(
            education_year__current_year=True,
            school_id=self.id,
            student__sex='Female'
        ).count()

    @property
    def total_registered_alp(self):
        from student_registration.alp.models import Outreach
        return Outreach.objects.filter(
            alp_round__current_round=True,
            registered_in_level__isnull=False,
            school_id=self.id
        ).count()

    @property
    def total_registered_alp_male(self):
        from student_registration.alp.models import Outreach
        return Outreach.objects.filter(
            alp_round__current_round=True,
            registered_in_level__isnull=False,
            school_id=self.id,
            student__sex='Male'
        ).count()

    @property
    def total_registered_alp_female(self):
        from student_registration.alp.models import Outreach
        return Outreach.objects.filter(
            alp_round__current_round=True,
            registered_in_level__isnull=False,
            school_id=self.id,
            student__sex='Female'
        ).count()

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

    schools = models.ManyToManyField(School, blank=True)

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

    range_start = models.FloatField(blank=True, null=True)
    range_end = models.FloatField(blank=True, null=True)

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
