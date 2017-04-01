from __future__ import unicode_literals, absolute_import, division

from django.db import models
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _
from model_utils import Choices
from model_utils.models import TimeStampedModel
from django.conf import settings
from student_registration.students.models import (
    Student,
)
from student_registration.registrations.models import (
    RegisteringAdult,
    Registration
)
from student_registration.users.models import User
from student_registration.schools.models import (
    School,
    ClassRoom
)


class ServiceType(models.Model):
    name = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        ordering = ['id']
        verbose_name = 'Service Type'

    def __unicode__(self):
        return self.name


class MainReason(models.Model):
    name = models.CharField(max_length=64L, unique=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Main Reason'

    def __unicode__(self):
        return self.name


class SpecificReason(models.Model):
    name = models.CharField(max_length=254L)
    main_reason = models.ForeignKey(MainReason, verbose_name='Main Reason')

    class Meta:
        ordering = ['name']
        verbose_name = 'Specific Reason'

    def __unicode__(self):
        return self.name


class HouseholdVisitTeam(models.Model):

    name = models.CharField(max_length=254L)
    first_enumerator = models.ForeignKey(
        User,
        blank=False, null=True,
        related_name='+',
    )
    second_enumerator = models.ForeignKey(
        User,
        blank=False, null=True,
        related_name='+',
    )

    class Meta:
        ordering = ['name']

    def __unicode__(self):
        return self.name

    @property
    def team_name(self):
        first_name_enumerator1 = self.first_enumerator.first_name
        last_name_enumerator1 = self.first_enumerator.last_name
        first_name_enumerator2 = self.second_enumerator.first_name
        last_name_enumerator2 = self.second_enumerator.last_name
        return "{} {} {} {} {}".format(first_name_enumerator1, last_name_enumerator1, '-', first_name_enumerator2,
                                       last_name_enumerator2)


class HouseholdVisit(TimeStampedModel):

    STATUS = Choices(
        ('pending', _('Pending')),
        ('completed', _('Completed')),
    )
    registering_adult = models.ForeignKey(
        RegisteringAdult,
        blank=True, null=True,
        related_name='+',
    )
    household_visit_team = models.ForeignKey(
        HouseholdVisitTeam,
        blank=True, null=True,
        related_name='+',
    )
    visit_status = models.CharField(max_length=50, blank=True, null=True, choices=STATUS)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        blank=False, null=True,
        related_name='+',
    )

    class Meta:
        ordering = ['id']

    def __unicode__(self):
        return self.RegisteringAdult.full_name

    @property
    def child_visit_count(self):
        return int(self.children_visits.all().count())

    @property
    def visit_attempt_count(self):
        return int(self.visit_attempt.all().count())

    @property
    def all_visit_attempt_count(self):
        total = 0
        queryset = HouseholdVisit.objects.filter(registering_adult_id=self.registering_adult_id)
        for hhv in queryset:
            total += int(HouseholdVisitAttempt.objects.filter(household_visit_id=hhv.id).count())
        return total


class HouseholdVisitAttempt(models.Model):
    household_visit = models.ForeignKey(
        HouseholdVisit,
        blank=False, null=True,
        related_name='visit_attempt',
    )
    household_not_found = models.BooleanField(blank=True, default=False)
    comment = models.CharField(max_length=255, blank=True, null=True)
    date = models.DateTimeField()

    class Meta:
        ordering = ['-id']

    def __unicode__(self):
        return self.comment


class ChildVisit(TimeStampedModel):
    STATUS = Choices(
        ('pending', _('Pending')),
        ('completed', _('Completed')),
    )
    ABSENCE_DURATION = Choices(
        ('first', _('5-10')),
        ('second', _('10-20')),
        ('third', _('20++')),
        ('never', _('Never Attended')),
        ('frequent', _('Frequently Absent')),
    )
    household_visit = models.ForeignKey(
        HouseholdVisit,
        blank=False, null=True,
        related_name='children_visits',
    )
    student = models.ForeignKey(
        Student,
        blank=False, null=True,
        related_name='+',
    )
    child_enrolled_in_another_school = models.BooleanField(default=False)
    child_no_longer_living_in_the_pilot_area = models.BooleanField(default=False)

    main_reason = models.ForeignKey(
        MainReason,
        blank=True, null=True,
        related_name='+',
    )
    specific_reason = models.ForeignKey(
        SpecificReason,
        blank=True, null=True,
        related_name='+',
    )
    specific_reason_other_specify = models.CharField(max_length=255, blank=True, null=True)
    last_attendance_date = models.DateField(blank=True, null=True)
    child_status = models.CharField(max_length=50, blank=True, null=True, choices=STATUS)
    child_absence_period = models.CharField(max_length=50, blank=True, null=True, choices=ABSENCE_DURATION)

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        blank=False, null=True,
        related_name='+',
    )

    class Meta:
        ordering = ['id']

    def __unicode__(self):
        return self.student.first_name


    @property
    def child_school(self):

        studentRecordRecord = Registration.objects.filter(student_id=self.student_id).values('school_id').first()

        schoolid = None

        if studentRecordRecord is not None:
            schoolid = studentRecordRecord['school_id']

        if not (schoolid is None):
            classRoomRecord = School.objects.filter(id=schoolid).values('name').first()

            classRoomName = '';

            if classRoomRecord is not None:
                classRoomName = classRoomRecord['name']

            return classRoomName
        else:
            return ''
        return

    @property
    def child_classroom(self):

        studentRecordRecord = Registration.objects.filter(student_id=self.student_id).values('classroom_id').first()
        classroomid = None

        if studentRecordRecord is not None:
            classroomid = studentRecordRecord['classroom_id']


        if not (classroomid is None):

            classRoomRecord = ClassRoom.objects.filter(id=classroomid).values('name').first()

            classRoomName = ''

            if classRoomRecord is not None:
                classRoomName = classRoomRecord['name']

            return classRoomName
        else:
            return ''


class ChildService(models.Model):

    child_visit = models.ForeignKey(
        ChildVisit,
        blank=False, null=True,
        related_name='child_visit_service',
    )
    service_type = models.ForeignKey(
        ServiceType,
        blank=False, null=True,
        related_name='+',
    )
    service_provider = models.CharField(max_length=255, blank=True, null=True)

    service_provider_followup = models.BooleanField(blank=True, default=False)

    class Meta:
        ordering = ['id']

    def __unicode__(self):
        return self.ServiceType.name


class ChildReason(models.Model):

    child_visit = models.ForeignKey(
        ChildVisit,
        blank=False, null=True,
        related_name='child_visit_reason',
    )
    main_reason = models.ForeignKey(
        MainReason,
        blank=True, null=True,
        related_name='+',
    )
    specific_reason = models.ForeignKey(
        SpecificReason,
        blank=True, null=True,
        related_name='+',
    )
    specific_reason_other_specify = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        ordering = ['id']

    def __unicode__(self):
        return self.ServiceType.name


class ChildAttendanceMonitoring(models.Model):
    child_visit = models.ForeignKey(
        ChildVisit,
        blank=False, null=True,
        related_name='+',
    )
    visit_attempt = models.ForeignKey(
        HouseholdVisitAttempt,
        blank=False, null=True,
        related_name='+',
    )
    student = models.ForeignKey(
        Student,
        blank=False, null=False,
        related_name='+',
    )
    is_first_visit = models.BooleanField()
    date_from = models.DateField(blank=False, null=True)
    date_to = models.DateField(blank=False, null=True)

    class Meta:
        ordering = ['-id']

    def __unicode__(self):
        return self.comment


class AttendanceMonitoringDate(models.Model):

    date_monitoring = models.DateField()

    class Meta:
        ordering = ['-id']

    def __unicode__(self):
        return self.comment


class HouseholdVisitComment(models.Model):
    household_visit = models.ForeignKey(
        HouseholdVisit,
        blank=False, null=True,
        related_name='visit_comment',
    )
    comment = models.CharField(max_length=255, blank=True, null=True)
    date = models.DateTimeField()

    class Meta:
        ordering = ['-id']

    def __unicode__(self):
        return self.comment


# class StudentAbsence(models.Model):
#     student = models.ForeignKey(
#         Student,
#         blank=False, null=False,
#         related_name='+',
#     )
#     date_from = models.DateField(blank=False, null=True)
#     date_to = models.DateField(blank=False, null=True)
#     date_entry = models.DateField(blank=False, null=True)
#
#     class Meta:
#         ordering = ['id']
#
#     def __unicode__(self):
#         return self.id


