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
    IDType
)
from student_registration.schools.models import (
    School,
    EducationLevel,
    ClassLevel,
    ClassRoom,
    Section,
    Grade,
)
from student_registration.locations.models import Location
from student_registration.eav.registry import Registry as eav


class WFPDistributionSite(models.Model):

    code = models.IntegerField()
    name = models.CharField(max_length=30, blank=True, null=True)
    location = models.ManyToManyField(Location)

    class Meta:
        ordering = ['name']
        verbose_name = "WFP Distribution Site"

    def __unicode__(self):
        return self.name


class BeneficiaryChangedReason(models.Model):
    name = models.CharField(max_length=64L, unique=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Main Reason'

    def __unicode__(self):
        return self.name


class ComplaintCategory(models.Model):
    TYPE = Choices(
        ('distribution', _('CARD DISTRIBUTION')),
        ('card', _('CARD')),
        ('payment', _('PAYMENT')),
        ('school', _('SCHOOL-RELATED')),
        ('reinstate', _('REINSTATE BENEFICIARY')),
        ('remove', _('reinstate beneficiary')),
        ('bank', _('BANK')),
        ('other', _('OTHER'))
    )
    name = models.CharField(max_length=200, unique=True)
    complaint_type = models.CharField(max_length=50, blank=True, null=True, choices=TYPE)

    class Meta:
        ordering = ['name']
        verbose_name = 'Main Reason'

    def __unicode__(self):
        return self.name

    @property
    def complaint_count(self):
        return int(self.complaints.all().count())


class NotEligibleReason(models.Model):
    name = models.CharField(max_length=64L, unique=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Main Reason'

    def __unicode__(self):
        return self.name


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
    GENDER = Choices(
            ('Male', _('Male')),
            ('Female', _('Female')),
    )
    individual_id_number = models.CharField(max_length=45L, blank=True, null=True)
    principal_applicant_living_in_house = models.BooleanField(blank=True, default=True)
    status = models.BooleanField(blank=True, default=True)
    previously_registered = models.BooleanField(default=False)
    previously_registered_status = models.BooleanField(default=False)
    previously_registered_number = models.CharField(max_length=45L, blank=True, null=True)
    relation_to_householdhead = models.CharField(max_length=50, blank=True, null=True, choices=RELATION_TYPE)
    wfp_case_number = models.CharField(max_length=50, blank=True, null=True)
    csc_case_number = models.CharField(max_length=50, blank=True, null=True)
    card_issue_requested = models.BooleanField(default=False)
    card_number = models.CharField(max_length=50, blank=True, null=True)
    card_status = models.CharField(max_length=50, blank=True, null=True)
    card_distribution_date = models.DateField(blank=True, null=True)
    card_last_four_digits = models.CharField(max_length=4, blank=True, null=True)
    batch_number = models.IntegerField(blank=True, null=True)
    child_enrolled_in_this_school = models.PositiveIntegerField(blank=True, null=True)
    child_enrolled_in_other_schools = models.BooleanField(default=False)
    primary_phone = models.CharField(max_length=50, blank=True, null=True)
    primary_phone_answered = models.CharField(max_length=50, blank=True, null=True, choices=PHONE_ANSWEREDBY)
    secondary_phone = models.CharField(max_length=50, blank=True, null=True)
    secondary_phone_answered = models.CharField(max_length=50, blank=True, null=True, choices=PHONE_ANSWEREDBY)
    signature = models.TextField(blank=True, null=True)
    school = models.ForeignKey(
        School,
        blank=True, null=True,
        related_name='+',
    )
    wfp_distribution_site = models.ForeignKey(WFPDistributionSite, blank=True, null=True)
    old_number = models.CharField(max_length=45L, blank=True, null=True)
    beneficiary_changed_verify = models.BooleanField(default=False)
    beneficiary_changed_id_type = models.ForeignKey(
        IDType,
        blank=True, null=True,
        related_name='beneficiary_changed_id',
    )
    beneficiary_changed_id_number = models.CharField(max_length=45L, blank=True, null=True)
    beneficiary_changed_first_name = models.CharField(max_length=64L, blank=True, null=True)
    beneficiary_changed_last_name = models.CharField(max_length=64L, blank=True, null=True)
    beneficiary_changed_father_name = models.CharField(max_length=64L, blank=True, null=True)
    beneficiary_changed_mother_full_name = models.CharField(max_length=64L, blank=True, null=True)
    beneficiary_changed_birthday_year = models.CharField(
        max_length=4,
        blank=True,
        null=True,
        default=0,
        choices=((str(x), x) for x in range(1930, 2051))
    )
    beneficiary_changed_birthday_month = models.CharField(
        max_length=2,
        blank=True,
        null=True,
        default=0,
        choices=Person.MONTHS
    )
    beneficiary_changed_birthday_day = models.CharField(
        max_length=2,
        blank=True,
        null=True,
        default=0,
        choices=((str(x), x) for x in range(1, 31))
    )
    beneficiary_changed_gender = models.CharField(max_length=50,blank=True,null=True,choices= GENDER)
    beneficiary_changed_relation_to_householdhead = models.CharField(max_length=50, blank=True, null=True, choices=RELATION_TYPE)
    beneficiary_changed_phone = models.CharField(max_length=50, blank=True, null=True)
    beneficiary_changed_same_as_caller = models.BooleanField(default=False)
    beneficiary_changed_reason = models.ForeignKey(
        BeneficiaryChangedReason,
        blank=True, null=True,
        related_name='+',
    )
    beneficiary_specify_reason = models.CharField(max_length=100, blank=True, null=True)
    household_suspended = models.BooleanField(default=False)
    duplicate_card_first_card_case_number = models.CharField(max_length=50, blank=True, null=True)
    duplicate_card_first_card_last_four_digits = models.CharField(max_length=4, blank=True, null=True)
    duplicate_card_second_card_case_number = models.CharField(max_length=50, blank=True, null=True)
    duplicate_card_secondcard_last_four_digits = models.CharField(max_length=4, blank=True, null=True)
    no_logner_eligible = models.BooleanField(default=False)
    no_logner_eligible_reason = models.ForeignKey(
        NotEligibleReason,
        blank=True, null=True,
        related_name='+',
    )
    no_logner_eligible_specify = models.CharField(max_length=50, blank=True, null=True)
    no_logner_eligible_comment = models.CharField(max_length=50, blank=True, null=True)
    update_owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        blank=False, null=True,
        related_name='+',
    )

    @property
    def case_number(self):
        if self.id_type and 'UNHCR' in self.id_type.name:
            return self.id_number
        return self.number

    @property
    def adult_full_name(self):
        return self.first_name + ' ' + self.father_name + ' ' + self.last_name


class HouseholdNotFound(Person):

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
    GENDER = Choices(
        ('Male', _('Male')),
        ('Female', _('Female')),
    )

    relation_to_householdhead = models.CharField(max_length=50, blank=True, null=True, choices=RELATION_TYPE)
    primary_phone = models.CharField(max_length=50, blank=True, null=True)
    primary_phone_answered = models.CharField(max_length=50, blank=True, null=True, choices=PHONE_ANSWEREDBY)
    secondary_phone = models.CharField(max_length=50, blank=True, null=True)
    secondary_phone_answered = models.CharField(max_length=50, blank=True, null=True, choices=PHONE_ANSWEREDBY)
    number_children_five_to_nine = models.IntegerField(blank=True, null=True)
    number_children_ten_to_seventeen = models.IntegerField(blank=True, null=True)

    class Meta:
        ordering = ['id']

    def __unicode__(self):
        return self.id


class Complaint(TimeStampedModel):
    """
    Household complaints by hotline
    """

    STATUS = Choices(
            ('open', _('Open')),
            ('resolved', _('Resolved')),
    )
    complaint_adult = models.ForeignKey(
        RegisteringAdult,
        blank=True, null=True,
        related_name='complaints',
    )
    complaint_category = models.ForeignKey(
        ComplaintCategory,
        blank=True, null=True,
        related_name='complaints',
    )
    household_not_found = models.ForeignKey(
        HouseholdNotFound,
        blank=True, null=True,
        related_name='HHNotFound',
    )
    complaint_note = models.TextField(blank=True, null=True)
    complaint_status = models.CharField(max_length=20, blank=True, null=True, choices=STATUS)
    complaint_solution = models.TextField(blank=True, null=True)
    complaint_resolution_date = models.DateField(blank=True, null=True)
    complaint_bank_date_of_incident = models.DateTimeField(blank=True, null=True)
    complaint_bank_phone_used = models.CharField(max_length=50, blank=True, null=True)
    complaint_bank_service_requested = models.TextField(blank=True, null=True)
    complaint_Other_type_specify = models.TextField(blank=True, null=True)
    complaint_student_refused_entrance = models.ForeignKey(
        Student,
        blank=True, null=True,
        related_name='complaints',
    )

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        blank=False, null=True,
        related_name='+',
    )

    class Meta:
        ordering = ['id']

    def __unicode__(self):
        return self.id


class Payment(models.Model):
    """
    Monthly household payment in PILOT
    """
    paid_adult = models.ForeignKey(
        RegisteringAdult,
        blank=True, null=True,
        related_name='payments',
    )
    payment_list_number = models.IntegerField(blank=True, null=True)
    payment_amount = models.IntegerField(blank=True, null=True)
    payment_month = models.IntegerField(blank=True, null=True)
    payment_year = models.IntegerField(blank=True, null=True)
    payment_date = models.DateField(blank=True, null=True)

    class Meta:
        ordering = ['id']

    def __unicode__(self):
        return self.id


class MessageType(models.Model):
    name = models.CharField(max_length=255L, unique=True)

    class Meta:
        ordering = ['name']

    def __unicode__(self):
        return self.name


class StatusLog(TimeStampedModel):
    adult = models.ForeignKey(
        RegisteringAdult,
        blank=False, null=True,
        related_name='+',
     )
    message = models.CharField(max_length=255L, blank=True, null=True)
    type = models.ForeignKey(
        MessageType,
        blank=False, null=True,
        related_name='+',
    )
    wfp_date = models.DateTimeField()

    class Meta:
        ordering = ['wfp_date']

    def __unicode__(self):
        return u'{} - {}'.format(
            self.message,
            self.type.name
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

    RESULT = Choices(
        ('graduated', _('Graduated')),
        ('failed', _('Failed'))
    )

    YES_NO = Choices(
        ('yes', _('Yes')),
        ('no', _('No'))
    )

    YEARS = ((str(x), x) for x in range(2016, 2051))

    EDUCATION_YEARS = ((str(x-1)+'/'+str(x), str(x-1)+'/'+str(x)) for x in range(2001, 2021))

    student = models.ForeignKey(
        Student,
        blank=False, null=True,
        related_name='student_registration',
    )

    registering_adult = models.ForeignKey(
        RegisteringAdult,
        blank=True, null=True,
        related_name='children',
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
    school_changed_to_verify = models.ForeignKey(
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
        related_name='last_educations'
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
        related_name='last_informal_educations',
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
    last_informal_edu_final_result = models.ForeignKey(
        ClassLevel,
        blank=True, null=True,
    )

    @property
    def student_fullname(self):
        if self.student:
            return self.student.full_name
        return ''

    def __unicode__(self):
        return self.student.__unicode__()

    @property
    def school_changed_verified(self):
        if self.school_changed_to_verify :
            return False
        return True


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

