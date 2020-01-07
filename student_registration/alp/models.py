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
)
from student_registration.schools.models import (
    School,
    EducationLevel,
    ClassLevel,
    PartnerOrganization,
    ClassRoom,
    Section,
)
from student_registration.locations.models import Location
from student_registration.alp.utils import refer_to_level, assign_to_level


class ALPRound(models.Model):
    name = models.CharField(max_length=45, unique=True)
    current_round = models.BooleanField(blank=True, default=False)
    round_start_date = models.DateField(
        blank=True,
        null=True,
        verbose_name=_('Round start date')
    )
    round_end_date = models.DateField(
        blank=True,
        null=True,
        verbose_name=_('Round end date')
    )
    current_pre_test = models.BooleanField(blank=True, default=False)
    current_post_test = models.BooleanField(blank=True, default=False)

    class Meta:
        ordering = ['name']
        verbose_name = "ALP Round"

    def __unicode__(self):
        return self.name


class OutreachManager(models.Manager):
    def get_queryset(self):
        return super(OutreachManager, self).get_queryset().exclude(deleted=True).exclude(dropout_status=True)


class OutreachDropoutManager(models.Manager):
    def get_queryset(self):
        return super(OutreachDropoutManager, self).get_queryset().exclude(deleted=True).filter(dropout_status=True)


class Outreach(TimeStampedModel):

    EAV_TYPE = 'outreach'

    RESULT = Choices(
        ('graduated', _('Graduated')),
        ('failed', _('Failed'))
    )

    LANGUAGES = Choices(
        ('english', _('English')),
        ('french', _('French'))
    )

    YES_NO = Choices(
        ('na', _('n/a')),
        ('yes', _('Yes')),
        ('no', _('No'))
    )

    EDUCATION_YEARS = list((str(x - 1) + '/' + str(x), str(x - 1) + '/' + str(x)) for x in range(2001, 2050))
    EDUCATION_YEARS.append(('na', 'N/A'))

    student = models.ForeignKey(
        Student,
        blank=False, null=True,
        related_name='alp_enrollment',
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
        verbose_name=_('Created by')
    )
    modified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        blank=True, null=True,
        related_name='modifications',
        verbose_name=_('Modified by'),
    )
    school = models.ForeignKey(
        School,
        blank=True, null=True,
        related_name='alp_school',
        verbose_name=_('School')
    )
    location = models.ForeignKey(
        Location,
        blank=True, null=True,
        related_name='+',
        verbose_name=_('Location'),
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
        verbose_name=_('Current Section'),
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
    pre_test_room = models.CharField(
        max_length=45,
        blank=True,
        null=True,
        verbose_name=_('Pre test room'),
    )
    post_test_room = models.CharField(
        max_length=45,
        blank=True,
        null=True,
        verbose_name=_('Post test room'),
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
        related_name='+',
        verbose_name=_('Last Education level'),
    )
    last_education_year = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        choices=EDUCATION_YEARS,
        verbose_name=_('Last Education year'),
    )
    last_year_result = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        choices=RESULT,
        verbose_name=_('Last Education result'),
    )
    participated_in_alp = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        choices=YES_NO,
        verbose_name=_('Participated in ALP'),
    )
    last_informal_edu_level = models.ForeignKey(
        EducationLevel,
        blank=True, null=True,
        related_name='+',
        verbose_name=_('Last informal education level'),
    )
    last_informal_edu_year = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        choices=EDUCATION_YEARS,
        verbose_name=_('Last informal education year'),
    )
    last_informal_edu_result = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        choices=RESULT,
        verbose_name=_('Last informal education result'),
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
    exam_result_arabic = models.FloatField(
        blank=True,
        null=True,
        default=0,
        verbose_name=_('Arabic'),
    )
    exam_result_language = models.FloatField(
        blank=True,
        null=True,
        default=0,
        verbose_name=_('Foreign Language'),
    )
    exam_result_math = models.FloatField(
        blank=True,
        null=True,
        default=0,
        verbose_name=_('Math'),
    )
    exam_result_science = models.FloatField(
        blank=True,
        null=True,
        default=0,
        verbose_name=_('Science'),
    )
    exam_language = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        choices=LANGUAGES,
        verbose_name=_('Exam language'),
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
        verbose_name=_('Entrance Test (Pre-Test)'),
    )
    registered_in_level = models.ForeignKey(
        EducationLevel,
        blank=True, null=True,
        related_name='+',
        verbose_name=_('Current Level'),
    )
    assigned_to_level = models.ForeignKey(
        EducationLevel,
        blank=True, null=True,
        related_name='+',
        verbose_name=_('Pre-test result'),
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
        verbose_name=_('Arabic'),
    )
    post_exam_result_language = models.FloatField(
        blank=True,
        null=True,
        default=0,
        verbose_name=_('Foreign Language'),
    )
    post_exam_result_math = models.FloatField(
        blank=True,
        null=True,
        default=0,
        verbose_name=_('Math'),
    )
    post_exam_result_science = models.FloatField(
        blank=True,
        null=True,
        default=0,
        verbose_name=_('Science'),
    )
    post_exam_language = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        choices=LANGUAGES,
        verbose_name=_('Exam language'),
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
    refer_to_level = models.ForeignKey(
        ClassLevel,
        blank=True, null=True,
        related_name='+',
        verbose_name=_('Post-test result'),
    )
    dropout_status = models.BooleanField(blank=True, default=False)
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

    pre_comment = models.TextField(
        blank=True, null=True,
        verbose_name=_('Comments')
    )
    post_comment = models.TextField(
        blank=True, null=True,
        verbose_name=_('Comments')
    )

    objects = OutreachManager()
    drop_objects = OutreachDropoutManager()

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
        if self.level:
            Education_Level = EducationLevel.objects.filter(name=self.level)
            for education_level in Education_Level:
                if education_level.new_calculation:
                    if education_level.with_arabic:
                        if self.exam_result_arabic:
                            total += self.exam_result_arabic
                    if education_level.with_science:
                        if self.exam_result_science:
                            total += self.exam_result_science
                    if education_level.with_language:
                        if self.exam_result_language:
                            total += self.exam_result_language
                    if education_level.with_math:
                        if self.exam_result_math:
                            total += self.exam_result_math
                    return total
            else:
                # if self.exam_result_arabic:
                #     total += self.exam_result_arabic
                if self.exam_result_language:
                    total += self.exam_result_language
                if self.exam_result_math:
                    total += self.exam_result_math
                if self.exam_result_science:
                    total += self.exam_result_science
                return total


    @property
    def pretest_total(self):
        if self.level:
            return "{}/{}".format(self.exam_total, self.level.note)
        return 0

    @property
    def posttest_total(self):
        if self.level:
            return "{}/{}".format(self.post_exam_total, '80')
        return 0

    @property
    def next_level(self):
        if self.refer_to_level:
            return self.refer_to_level
        return ''

    @property
    def post_exam_total(self):
        total = 0.0
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
            return self.student.age
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

    @property
    def student_birthday(self):
        return self.student.birthday

    @property
    def student_id_type(self):
        return self.student.id_type

    @property
    def student_id_number(self):
        return self.student.id_number

    @property
    def student_mother_nationality(self):
        return self.student.mother_nationality

    @property
    def student_phone_number(self):
        return self.student.phone_number

    @property
    def student_address(self):
        return self.student.address

    @property
    def re_enrolled(self):
        return self.student.alp_enrollment.count()

    def calculate_pre_result(self):
        self.assigned_to_level = assign_to_level(self.level, self.exam_total)

    def calculate_post_result(self):
        self.refer_to_level = refer_to_level(self.student_age, self.registered_in_level, self.post_exam_total)

    def __unicode__(self):
        if self.student:
            return self.student.__unicode__()
        return str(self.id)
