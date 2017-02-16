from __future__ import unicode_literals, absolute_import, division

from django.db import models
from model_utils import Choices
from django.utils.translation import ugettext as _
from model_utils.models import TimeStampedModel
from django.conf import settings
from django.contrib.postgres.fields import JSONField
from student_registration.students.models import (
    Person,
    Student,
    Language,
)
from student_registration.schools.models import (
    School,
    EducationLevel,
    ClassLevel,
    PartnerOrganization,
    ClassRoom,
    Section,
    Grade
)
from student_registration.locations.models import Location
from student_registration.eav.registry import Registry as eav


class ALPRound(models.Model):
    name = models.CharField(max_length=45L, unique=True)
    current_round = models.BooleanField(blank=True, default=False)
    current_pre_test = models.BooleanField(blank=True, default=False)
    current_post_test = models.BooleanField(blank=True, default=False)

    class Meta:
        ordering = ['id']
        verbose_name = "ALP Round"

    def __unicode__(self):
        return self.name


class Outreach(TimeStampedModel):

    EAV_TYPE = 'outreach'

    RESULT = Choices(
        ('graduated', _('Graduated')),
        ('failed', _('Failed'))
    )

    YES_NO = Choices(
        ('yes', _('Yes')),
        ('no', _('No'))
    )

    student = models.ForeignKey(
        Student,
        blank=False, null=True,
        related_name='+',
    )
    partner = models.ForeignKey(
        PartnerOrganization,
        blank=True, null=True,
        related_name='+',
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        blank=False, null=True,
        related_name='+',
    )
    school = models.ForeignKey(
        School,
        blank=True, null=True,
        related_name='+',
    )
    location = models.ForeignKey(
        Location,
        blank=True, null=True,
        related_name='+',
    )
    preferred_language = models.ForeignKey(
        Language,
        blank=True, null=True,
        related_name='+',
    )
    last_class_level = models.ForeignKey(
        ClassLevel,
        blank=True, null=True,
        related_name='+',
    )
    average_distance = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        choices=Choices(
            u'<= 2.5km',
            u'> 2.5km',
            u'> 10km'
        )
    )
    exam_year = models.CharField(
        max_length=4,
        blank=True,
        null=True,
        choices=((str(x), x) for x in range(1990, 2051))
    )
    exam_month = models.CharField(
        max_length=2,
        blank=True,
        null=True,
        choices=Person.MONTHS
    )
    exam_day = models.CharField(
        max_length=2,
        blank=True,
        null=True,
        choices=((str(x), x) for x in range(1, 33))
    )
    alp_round = models.ForeignKey(
        ALPRound,
        blank=True, null=True,
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
    alp_year = models.CharField(
        max_length=20,
        blank=True,
        null=True,
    )
    status = models.BooleanField(blank=True, default=True)
    enrolled_in_this_school = models.BooleanField(blank=True, default=True)
    not_enrolled_in_this_school = models.BooleanField(blank=True, default=False)
    exam_not_exist_in_school = models.BooleanField(blank=True, default=False)
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
    exam_result_arabic = models.FloatField(
        blank=True,
        null=True,
        default=0,
    )
    exam_result_language = models.FloatField(
        blank=True,
        null=True,
        default=0,
    )
    exam_result_math = models.FloatField(
        blank=True,
        null=True,
        default=0,
    )
    exam_result_science = models.FloatField(
        blank=True,
        null=True,
        default=0,
    )
    exam_corrector_arabic = models.IntegerField(
        blank=True,
        null=True,
        default=0,
        choices=((x, x) for x in range(0, 101))
    )
    exam_corrector_language = models.IntegerField(
        blank=True,
        null=True,
        default=0,
        choices=((x, x) for x in range(0, 101))
    )
    exam_corrector_math = models.IntegerField(
        blank=True,
        null=True,
        default=0,
        choices=((x, x) for x in range(0, 101))
    )
    exam_corrector_science = models.IntegerField(
        blank=True,
        null=True,
        default=0,
        choices=((x, x) for x in range(0, 101))
    )
    registered_in_school = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        choices=YES_NO
    )
    level = models.ForeignKey(
        EducationLevel,
        blank=True, null=True,
        related_name='+',
    )
    registered_in_level = models.ForeignKey(
        EducationLevel,
        blank=True, null=True,
        related_name='+',
    )
    assigned_to_level = models.ForeignKey(
        EducationLevel,
        blank=True, null=True,
        related_name='+',
    )
    exam_school = models.ForeignKey(
        School,
        blank=True, null=True,
        related_name='+',
    )
    deleted = models.BooleanField(blank=True, default=False)

    post_exam_result_arabic = models.FloatField(
        blank=True,
        null=True,
        default=0,
    )
    post_exam_result_language = models.FloatField(
        blank=True,
        null=True,
        default=0,
    )
    post_exam_result_math = models.FloatField(
        blank=True,
        null=True,
        default=0,
    )
    post_exam_result_science = models.FloatField(
        blank=True,
        null=True,
        default=0,
    )
    post_exam_corrector_arabic = models.IntegerField(
        blank=True,
        null=True,
        default=0,
        choices=((x, x) for x in range(0, 101))
    )
    post_exam_corrector_language = models.IntegerField(
        blank=True,
        null=True,
        default=0,
        choices=((x, x) for x in range(0, 101))
    )
    post_exam_corrector_math = models.IntegerField(
        blank=True,
        null=True,
        default=0,
        choices=((x, x) for x in range(0, 101))
    )
    post_exam_corrector_science = models.IntegerField(
        blank=True,
        null=True,
        default=0,
        choices=((x, x) for x in range(0, 101))
    )
    post_exam_level = models.ForeignKey(
        ClassLevel,
        blank=True, null=True,
        related_name='+',
    )

    class Meta:
        ordering = ['id']
        verbose_name = "All ALP data"

    @property
    def student_fullname(self):
        if self.student:
            return self.student.__unicode__()
        return ''

    @property
    def student_mother_fullname(self):
        if self.student:
            return self.student.mother_fullname
        return ''

    @property
    def exam_total(self):
        total = 0
        if self.exam_result_arabic:
            total += self.exam_result_arabic
        if self.exam_result_language:
            total += self.exam_result_language
        if self.exam_result_math:
            total += self.exam_result_math
        if self.exam_result_science:
            total += self.exam_result_science
        return total

    @property
    def post_exam_total(self):
        total = 0
        if self.post_exam_result_arabic:
            total += self.post_exam_result_arabic
        if self.post_exam_result_language:
            total += self.post_exam_result_language
        if self.post_exam_result_math:
            total += self.post_exam_result_math
        if self.post_exam_result_science:
            total += self.post_exam_result_science
        return total

    @property
    def student_age(self):
        if self.student:
            return self.student.calc_age
        return 0

    @property
    def student_sex(self):
        if self.student:
            return self.student.sex
        return ''

    @property
    def student_number(self):
        if self.student:
            return self.student.number
        return ''

    @property
    def student_nationality(self):
        if self.student:
            return self.student.nationality
        return ''

    def __unicode__(self):
        if self.student:
            return self.student.__unicode__()
        return str(self.id)


class ExtraColumn(TimeStampedModel):
    name = models.CharField(max_length=64L, blank=True, null=True)
    label = models.CharField(max_length=64L, blank=True, null=True)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        blank=False, null=True,
        related_name='+',
    )

# eav.register(Outreach)
