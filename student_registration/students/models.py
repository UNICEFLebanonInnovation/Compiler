from __future__ import unicode_literals, absolute_import, division

import datetime

from django.db import models
from django.utils.translation import ugettext as _

from model_utils import Choices
from model_utils.models import TimeStampedModel
from .utils import *
from django.core.exceptions import ValidationError


def validate_file_size(value):
    filesize = value.size
    if filesize > 250000:
        raise ValidationError("The maximum file size that can be uploaded is 250K")
    else:
        return value


class Birth_DocumentType(models.Model):
    name = models.CharField(blank=True, null=True, max_length=70)

    class Meta:
        ordering = ['id']
        verbose_name = "Document Type"
        verbose_name_plural = "Documents Type"

    def __unicode__(self):
        return self.name


class StudentManager(models.Manager):
    def get_queryset(self):
        return super(StudentManager, self).get_queryset()


class Student2ndShiftManager(models.Manager):
    def get_queryset(self):
        return super(Student2ndShiftManager, self).get_queryset().filter(
            student_enrollment__isnull=False,
            student_enrollment__deleted=False,
            student_enrollment__dropout_status=False,
        )


class StudentALPManager(models.Manager):
    def get_queryset(self):
        return super(StudentALPManager, self).get_queryset().filter(
            alp_enrollment__isnull=False,
            alp_enrollment__deleted=False,
            alp_enrollment__dropout_status=False
        )


class Nationality(models.Model):
    name = models.CharField(max_length=45, unique=True)
    code = models.CharField(max_length=5, null=True)

    class Meta:
        ordering = ['id']
        verbose_name_plural = "Nationalities"

    def __unicode__(self):
        return self.name


class IDType(models.Model):
    name = models.CharField(max_length=45, unique=True)

    class Meta:
        ordering = ['id']
        verbose_name = "ID Type"
        verbose_name_plural = 'ID Types'

    def __unicode__(self):
        return self.name


class SpecialNeeds(models.Model):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        verbose_name_plural = 'Special Needs'

    def __unicode__(self):
        return self.name


class SpecialNeedsDt(models.Model):
    name = models.CharField(max_length=100, unique=True)
    specialneeds = models.ForeignKey(
        SpecialNeeds,
        blank=True,
        null=True,
        verbose_name=_('Detail Special Needs'),
    )

    class Meta:
        verbose_name_plural = 'Details Special Needs '
        verbose_name ='Detail Special Needs'

    def __unicode__(self):
        return self.name


class FinancialSupport(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __unicode__(self):
        return self.name


class Labour(models.Model):
    name = models.CharField(max_length=45, unique=True)

    class Meta:
        ordering = ['id']
        verbose_name = "Labour"

    def __unicode__(self):
        return self.name


class Person(TimeStampedModel):

    CURRENT_YEAR = datetime.datetime.now().year

    MONTHS = Choices(
        ('1', _('January')),
        ('2', _('February')),
        ('3', _('March')),
        ('4', _('April')),
        ('5', _('May')),
        ('6', _('June')),
        ('7', _('July')),
        ('8', _('August')),
        ('9', _('September')),
        ('10', _('October')),
        ('11', _('November')),
        ('12', _('December')),
    )

    GENDER = Choices(
        ('Male', _('Male')),
        ('Female', _('Female')),
    )
    FAMILY_STATUS = Choices(
        ('married', _('Married')),
        ('engaged', _('Engaged')),
        ('divorced', _('Divorced')),
        ('widower', _('Widower')),
        ('single', _('Single')),
    )

    STUDENT_INCOME= Choices(
        ('', '----------'),
        ('thousand_or_less', _('10,000 LBP or less')),
        ('eleven_thousand_to_twenty_five', _('11,000 to 25,000 LBP')),
        ('twenty_six_thousand_to_fifty', _('26,000 to 50,000 LBP')),
        ('more_than_fifty', _('More than 50,000 LBP')),
    )

    first_name = models.CharField(
        max_length=64,
        db_index=True,
        blank=True, null=True,
        verbose_name=_('First name')
    )
    last_name = models.CharField(
        max_length=64,
        db_index=True,
        blank=True, null=True,
        verbose_name=_('Last name')
    )
    father_name = models.CharField(
        max_length=64,
        db_index=True,
        blank=True, null=True,
        verbose_name=_('Father name')
    )
    mother_fullname = models.CharField(
        max_length=64,
        db_index=True,
        blank=True, null=True,
        verbose_name=_('Mother fullname')
    )
    mother_firstname = models.CharField(max_length=64, blank=True, null=True)
    mother_lastname = models.CharField(max_length=64, blank=True, null=True)
    sex = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        choices=GENDER,
        verbose_name=_('Sex')
    )
    birthday_year = models.CharField(
        max_length=4,
        blank=True,
        null=True,
        default=0,
        choices=((str(x), x) for x in range(1990, 2050)),
        verbose_name=_('Birthday year')
    )
    birthday_month = models.CharField(
        max_length=2,
        blank=True,
        null=True,
        default=0,
        choices=MONTHS,
        verbose_name=_('Birthday month')
    )
    birthday_day = models.CharField(
        max_length=2,
        blank=True,
        null=True,
        default=0,
        choices=((str(x), x) for x in range(1, 32)),
        verbose_name=_('Birthday day')
    )
    place_of_birth = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name=_('Place of birth')
    )
    family_status = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        choices=FAMILY_STATUS,
        verbose_name=_('Family status')
    )
    have_children = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        choices=Choices((1, _("Yes")), (0, _("No"))),
        verbose_name=_('Have children')
    )
    phone = models.CharField(max_length=64, blank=True, null=True, verbose_name=_('Phone number'))
    phone_prefix = models.CharField(max_length=10, blank=True, null=True, verbose_name=_('Phone prefix'))
    registered_in_unhcr = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        choices=Choices((1, _("Yes")), (0, _("No"))),
        verbose_name=_('Registered in UNHCR')
    )
    id_number = models.CharField(
        max_length=45,
        db_index=True,
        blank=True, null=True,
        verbose_name=_('ID number')
    )
    id_type = models.ForeignKey(
        IDType,
        blank=True, null=True,
        verbose_name=_('ID type')
    )
    nationality = models.ForeignKey(
        Nationality,
        blank=True, null=True,
        related_name='+',
        verbose_name=_('Nationality')
    )
    mother_nationality = models.ForeignKey(
        Nationality,
        blank=True, null=True,
        related_name='+',
        verbose_name=_('Mother nationality')
    )
    address = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('Address')
    )
    p_code = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name=_('P-code')
    )
    number = models.CharField(max_length=45, blank=True, null=True)
    number_part1 = models.CharField(max_length=45, blank=True, null=True)
    number_part2 = models.CharField(max_length=45, blank=True, null=True)
    std_phone = models.CharField(max_length=74, blank=True, null=True)
    recordnumber = models.CharField(max_length=45, blank=True, null=True, verbose_name=_('Identity record number'))

    def __unicode__(self):
        if not self.first_name:
            return 'No name'

        return u'{} {} {}'.format(
            self.first_name,
            self.father_name,
            self.last_name,
        )

    @property
    def full_name(self):
        return u'{} {} {}'.format(
            self.first_name,
            self.father_name,
            self.last_name,
        )

    def nationality_name(self):
        if self.nationality:
            return self.nationality.name

        return ''

    @property
    def birthday(self):
        return u'{}/{}/{}'.format(
            self.birthday_day,
            self.birthday_month,
            self.birthday_year,
        )

    @property
    def age(self):
        if self.birthday_year and self.birthday_month and self.birthday_day:
            today = datetime.datetime.now()
            return today.year - int(self.birthday_year) - ((today.month, today.day) < (int(self.birthday_month), int(self.birthday_day)))
        # if self.birthday_year:
        #     return int(self.CURRENT_YEAR)-int(self.birthday_year)
        return 0

    @property
    def phone_number(self):
        return '{}-{}'.format(self.phone_prefix, self.phone)

    class Meta:
        abstract = True

    def save(self, **kwargs):
        if self.phone:
            self.std_phone = self.phone_prefix+self.phone
        """
        Generate unique IDs for every person
        :param kwargs:
        :return:
        """
        if self.pk is None:
            self.number = generate_id(
                self.first_name,
                self.father_name,
                self.last_name,
                self.mother_fullname,
                self.sex,
                self.birthday_day,
                self.birthday_month,
                self.birthday_year
            )

        super(Person, self).save(**kwargs)


class Student(Person):
    from student_registration.outreach.models import Child

    status = models.BooleanField(default=True)
    hh_barcode = models.CharField(max_length=45, blank=True, null=True)

    outreach_child = models.ForeignKey(
        Child,
        blank=True, null=True,
    )
    std_image = models.ImageField(
        upload_to="profiles",
        null=True,
        blank=True,
        help_text=_('Profile Picture'),
        verbose_name=_('Profile Picture'),
        validators=[validate_file_size]
    )

    objects = StudentManager()
    second_shift = Student2ndShiftManager()
    alp = StudentALPManager()
    is_specialneeds = models.BooleanField(default=False)
    birth_documenttype = models.ForeignKey(
        Birth_DocumentType,
        blank=True,
        null=True,
        verbose_name=_('Document Type'),
        related_name='documenttype'
    )
    specialneeds = models.ForeignKey(
        SpecialNeeds,
        blank=True,
        null=True,
        verbose_name=_('Types Special Needs'),
        related_name='specialneeds'
    )
    specialneedsdt = models.ForeignKey(
        SpecialNeedsDt,
        blank=True,
        null=True,
        verbose_name=_('Details Special Needs')
    )
    id_image = models.ImageField(
        upload_to='profiles/ids',
        blank=True,
        null=True,
        help_text=_('Identification picture'),
        validators=[validate_file_size]
    )
    unhcr_image = models.ImageField(
        upload_to='profiles/unhcr',
        blank=True,
        null=True,
        help_text=_('UNHCR picture'),
        validators=[validate_file_size]
    )
    birthdoc_image = models.ImageField(
        upload_to='profiles/birthdoc',
        blank=True,
        null=True,
        help_text=_('Birth Document'),
        validators=[validate_file_size]
    )
    unhcr_family = models.CharField(
        max_length=150,
        blank=True,
        null=True,
        verbose_name=_('UNHCR Family Number')
    )
    unhcr_personal = models.CharField(
        max_length=150,
        blank=True,
        null=True,
        db_index=True,
        verbose_name=_('UNHCR Personal Number')
    )
    is_financialsupport = models.BooleanField(default=False)
    Financialsupport_number = models.CharField(
        max_length=64,
        blank=True,
        null=True,
        verbose_name=_('Financial Support Number'),
    )
    financialsupport = models.ForeignKey(
        FinancialSupport,
        blank=True,
        null=True,
        verbose_name=_('Financial Support Program'),
        related_name='financialsupport'
    )
   # @property
    #def image_url(self):
     #   if self.std_image and hasattr(self.std_image, 'url'):
      #      return self.std_image.url

    @property
    def last_enrollment(self):
        return self.student_enrollment.all().order_by('pk').last

    @property
    def secondshift_registrations(self):
        return self.student_enrollment.all()

    def current_secondshift_registration(self):
        from student_registration.schools.models import EducationYear

        education_year = EducationYear.objects.get(current_year=True)
        return self.student_enrollment.filter(education_year=education_year)

    @property
    def alp_registrations(self):
        return self.alp_enrollment.all()

    def current_alp_registration(self):
        from student_registration.alp.models import ALPRound

        alp_round = ALPRound.objects.get(current_round=True)
        return self.alp_enrollment.filter(alp_round=alp_round)

    @property
    def last_alp_registration(self):
        return self.alp_enrollment.all().order_by('pk').last

    @property
    def last_alp_round(self):
        registry = self.last_alp_registration()
        if registry:
            return registry.alp_round.name
        return None

    @property
    def last_alp_level(self):
        registry = self.last_alp_registration()
        if registry:
            return registry.registered_to_level.name
        return None

    @property
    def last_alp_section(self):
        registry = self.last_alp_registration()
        if registry:
            return registry.section.name
        return None

    @property
    def last_alp_referral_level(self):
        registry = self.last_alp_registration()
        if registry:
            return registry.refer_to_level.name
        return None

    @property
    def attendance_list(self):
        attendances = {}
        for item in self.attendances.all():
            attendances[item.attendance_date] = item.status
        return attendances

    @property
    def enrollment_school(self):
        last_enrollment = self.last_enrollment()
        if last_enrollment:
            return last_enrollment.school.name
        return ''

    @property
    def enrollment_education_year(self):
        last_enrollment = self.last_enrollment()
        if last_enrollment:
            return last_enrollment.education_year.name
        return ''

class StudentMatching(models.Model):

    registry = models.ForeignKey(
        Student,
        blank=False, null=False,
        related_name='+',
    )
    enrolment = models.ForeignKey(
        Student,
        blank=False, null=False,
        related_name='+',
    )
