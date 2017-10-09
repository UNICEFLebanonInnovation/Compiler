from __future__ import unicode_literals, absolute_import, division

from django.db import models
from django.conf import settings
from django.utils.translation import ugettext as _
from django.contrib.postgres.fields import JSONField, ArrayField

from model_utils import Choices
from model_utils.models import TimeStampedModel

from student_registration.students.models import (
    Student,
)
from student_registration.schools.models import (
    School,
    Section,
    ClassRoom,
    EducationLevel,
)


class Attendance(TimeStampedModel):

    ABSENCE_REASON = Choices(
        ('sick', _('Sick')),
        ('no_reason', _('No reason')),
        ('no_transport', _('No transport')),
        ('other', _('Other')),
    )

    CLOSE_REASON = Choices(
        ('public_holiday', _('Public Holiday')),
        ('school_holiday', _('School Holiday')),
        ('strike', _('Strike')),
        ('weekly_holiday', _('Weekly Holiday')),
    )

    DEFAULT_ATTENDANCE_RANGE = 10

    student = models.ForeignKey(
        Student,
        blank=True, null=True,
        related_name='attendances',
    )
    school = models.ForeignKey(
        School,
        blank=False, null=True,
        related_name='+',
    )
    classroom = models.ForeignKey(
        ClassRoom,
        blank=True, null=True,
        related_name='+'
    )
    classlevel = models.ForeignKey(
        EducationLevel,
        blank=True, null=True,
        related_name='+'
    )
    section = models.ForeignKey(
        Section,
        blank=True, null=True,
        related_name='+'
    )
    status = models.BooleanField(default=False)
    attendance_date = models.DateField(blank=True, null=True)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        blank=True, null=True,
        related_name='+',
    )
    validation_status = models.BooleanField(default=False)
    validation_date = models.DateField(blank=True, null=True)
    validation_owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        blank=True, null=True,
        related_name='+',
    )
    absence_reason = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        choices=ABSENCE_REASON
    )
    close_reason = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        choices=CLOSE_REASON
    )

    students = JSONField(blank=True, null=True)

    total_enrolled = models.IntegerField(blank=True, null=True)
    total_attended = models.IntegerField(blank=True, null=True)
    total_absences = models.IntegerField(blank=True, null=True)
    total_attended_male = models.IntegerField(blank=True, null=True)
    total_attended_female = models.IntegerField(blank=True, null=True)
    total_absent_male = models.IntegerField(blank=True, null=True)
    total_absent_female = models.IntegerField(blank=True, null=True)

    @property
    def student_fullname(self):
        if self.student:
            return self.student.full_name
        return ''

    @property
    def student_gender(self):
        return self.student.sex

    def __unicode__(self):
        return self.school.__unicode__()

    def save(self, **kwargs):
        """
        """
        if self.students:
            self.total_attended = 0
            self.total_absences = 0
            self.total_attended_male = 0
            self.total_attended_female = 0
            self.total_absent_male = 0
            self.total_absent_female = 0
            for level_section in self.students:
                self.total_attended += self.students[level_section]['total_attended']
                self.total_absences += self.students[level_section]['total_absences']
                self.total_attended_male += self.students[level_section]['total_attended_male']
                self.total_attended_female += self.students[level_section]['total_attended_female']
                self.total_absent_male += self.students[level_section]['total_absent_male']
                self.total_absent_female += self.students[level_section]['total_absent_female']

        super(Attendance, self).save(**kwargs)


class BySchoolByDay(models.Model):

    school = models.ForeignKey(
        School,
        related_name='+',
    )
    attendance_date = models.DateField()
    highest_attendance_rate = models.BooleanField(default=False)
    total_enrolled = models.IntegerField(blank=True, null=True)
    total_attended = models.IntegerField(blank=True, null=True)
    total_absences = models.IntegerField(blank=True, null=True)
    total_attended_male = models.IntegerField(blank=True, null=True)
    total_attended_female = models.IntegerField(blank=True, null=True)
    total_absent_male = models.IntegerField(blank=True, null=True)
    total_absent_female = models.IntegerField(blank=True, null=True)
    validation_date = models.DateField(blank=True, null=True)
    validation_status = models.BooleanField(default=False)


class Absentee(TimeStampedModel):

    school = models.ForeignKey(
        School,
        related_name='+',
    )
    student = models.ForeignKey(
        Student,
        related_name='absents',
    )
    last_attendance_date = models.DateField(blank=True, null=True)
    last_absent_date = models.DateField(blank=True, null=True)
    absent_days = models.IntegerField(blank=True, null=True)
    reattend_date = models.DateField(blank=True, null=True)
    validation_status = models.BooleanField(default=False)
    dropout_status = models.NullBooleanField(default=False)

    def student_number(self):
        return self.student.number


class AttendanceSyncLog(models.Model):

    school = models.ForeignKey(School)
    school_type = models.CharField(
        max_length=50,
        blank=True,
        null=True,
    )
    total_records = models.IntegerField(default=0)
    total_processed = models.IntegerField(default=0)
    successful = models.BooleanField(default=False)
    exception_message = models.TextField(blank=True, null=True)
    response_message = models.TextField(blank=True, null=True)
    processed_date = models.DateTimeField(auto_now=True)
    processed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        blank=True, null=True,
        related_name='+',
    )

    def __unicode__(self):
        return str(self.processed_date)

    class Meta:
        ordering = ['processed_date']
