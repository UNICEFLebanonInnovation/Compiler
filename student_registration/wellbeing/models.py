"""Makani child wellbeing, phase 1: rule-based flags on children who may need a follow-up, the
follow-up recorded on each flag, and monthly centre summaries.

A flag says "check on this child" and why; it is not a score or a label. Flags are worked out every
night from the data the centres already record (attendance, services, screenings, referrals, tests)
by ``rules.py``. BMA only calculates and serves them (``api.py``); NeuroDB shows them and sends the
follow-ups back, which close the flags.
"""

import datetime

from django.conf import settings
from django.db import models
from django.db.models import Q

from student_registration.child.models import Child
from student_registration.locations.models import Center
from student_registration.mscc.models import Registration, Round
from student_registration.schools.models import PartnerOrganization


def today():
    """The local date (the Compiler runs without time zones)."""
    if settings.USE_TZ:
        from django.utils import timezone
        return timezone.localdate()
    return datetime.date.today()


class FlagSettings(models.Model):
    """The thresholds of the rules (one row, edited in the admin)."""

    absence_streak = models.PositiveSmallIntegerField(
        default=3, help_text='Flag A1: class days absent in a row')
    attendance_window_days = models.PositiveSmallIntegerField(
        default=28, help_text='Flag A2: the period of the attendance rate, in calendar days')
    attendance_min_days = models.PositiveSmallIntegerField(
        default=8, help_text='Flag A2: class days recorded in that period before the rate counts')
    attendance_rate_below = models.PositiveSmallIntegerField(
        default=70, help_text='Flag A2: attendance rate under this percentage')
    drop_recent_days = models.PositiveSmallIntegerField(
        default=14, help_text='Flag A3: the recent period, in calendar days')
    drop_previous_days = models.PositiveSmallIntegerField(
        default=28, help_text='Flag A3: the period before it, in calendar days')
    drop_points = models.PositiveSmallIntegerField(
        default=30, help_text='Flag A3: drop of the attendance rate, in percentage points')
    service_weeks = models.PositiveSmallIntegerField(
        default=6, help_text='Flag S1: weeks after joining the round for the required services')
    followup_days = models.PositiveSmallIntegerField(
        default=7, help_text='Follow-up expected within this many days of a flag (centre summaries)')
    all_present_min_children = models.PositiveSmallIntegerField(
        default=5, help_text='An attendance sheet with at least this many children, all present, is '
                             'treated as not filled in: it counts neither as present nor absent')

    class Meta:
        verbose_name = 'Flag settings'
        verbose_name_plural = 'Flag settings'

    def __str__(self):
        return 'Flag settings'

    @classmethod
    def current(cls):
        return cls.objects.order_by('id').first() or cls()


class Flag(models.Model):
    ABSENCE_STREAK = 'A1'
    LOW_ATTENDANCE = 'A2'
    ATTENDANCE_DROP = 'A3'
    SERVICE_GAP = 'S1'
    DROPOUT_NO_FOLLOWUP = 'D1'
    MALNUTRITION_NO_REFERRAL = 'H1'
    DELAY_NO_REFERRAL = 'H2'
    PROTECTION_NO_REFERRAL = 'P1'
    NO_LEARNING_GAIN = 'L1'
    KINDS = (
        (ABSENCE_STREAK, 'Absent several class days in a row'),
        (LOW_ATTENDANCE, 'Low attendance'),
        (ATTENDANCE_DROP, 'Attendance dropped'),
        (SERVICE_GAP, 'Required service not received'),
        (DROPOUT_NO_FOLLOWUP, 'Dropout without follow-up'),
        (MALNUTRITION_NO_REFERRAL, 'Malnutrition screened, not referred'),
        (DELAY_NO_REFERRAL, 'Developmental delay identified, not referred'),
        (PROTECTION_NO_REFERRAL, 'Protection concern recorded, not referred'),
        (NO_LEARNING_GAIN, 'No learning progress between tests'),
    )
    OPEN, FOLLOWED_UP, RESOLVED = 'open', 'followed_up', 'resolved'
    STATUSES = (
        (OPEN, 'Open'),
        (FOLLOWED_UP, 'Followed up'),
        (RESOLVED, 'Resolved by itself'),
    )
    RESULTS = (
        ('reached_returning', 'Child/caregiver reached: child is returning or continuing'),
        ('reached_support', 'Child/caregiver reached: extra support planned at the centre'),
        ('referred', 'Referred to a specialised service (CP, health, other)'),
        ('already_handled', 'Already handled (referral or follow-up done, not recorded)'),
        ('not_reached', 'Could not reach the child or caregiver'),
        ('dropped_out', 'Child has left the programme'),
        ('not_needed', 'Not needed: the data was wrong'),
    )

    registration = models.ForeignKey(Registration, on_delete=models.CASCADE, related_name='+')
    child = models.ForeignKey(Child, null=True, blank=True, on_delete=models.SET_NULL, related_name='+')
    center = models.ForeignKey(Center, null=True, blank=True, on_delete=models.SET_NULL, related_name='+')
    partner = models.ForeignKey(PartnerOrganization, null=True, blank=True, on_delete=models.SET_NULL,
                                related_name='+')
    round = models.ForeignKey(Round, null=True, blank=True, on_delete=models.SET_NULL, related_name='+')
    kind = models.CharField(max_length=2, choices=KINDS)
    status = models.CharField(max_length=12, choices=STATUSES, default=OPEN)
    urgent = models.BooleanField(default=False, help_text='e.g. suicidal ideation or severe malnutrition')
    priority = models.BooleanField(
        default=False, help_text='the child also works, lives without parents or has a disability')
    reason = models.TextField(help_text='why the flag was raised, in words')
    evidence = models.JSONField(default=dict, blank=True)
    as_of = models.DateField(help_text='date of the latest data behind the flag')
    opened_on = models.DateField()
    last_seen_on = models.DateField()
    followed_up_on = models.DateField(null=True, blank=True)
    followed_up_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True,
                                       on_delete=models.SET_NULL, related_name='+')
    followed_up_by_name = models.CharField(
        max_length=150, blank=True, help_text='who recorded the follow-up in NeuroDB')
    follow_up_type = models.CharField(max_length=40, blank=True)
    result = models.CharField(max_length=20, choices=RESULTS, blank=True)
    note = models.TextField(blank=True)
    resolved_on = models.DateField(null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-urgent', '-priority', 'opened_on', 'id']
        constraints = [
            models.UniqueConstraint(fields=['registration', 'kind'], condition=Q(status='open'),
                                    name='wellbeing_one_open_flag_per_kind'),
        ]
        indexes = [
            models.Index(fields=['center', 'status']),
            models.Index(fields=['partner', 'status']),
            models.Index(fields=['registration', 'kind']),
        ]

    def __str__(self):
        return '{} {} ({})'.format(self.registration_id, self.get_kind_display(), self.get_status_display())

    @property
    def days_open(self):
        end = self.followed_up_on or self.resolved_on
        if end is None:
            end = today()
        return (end - self.opened_on).days


class CenterSummary(models.Model):
    """The monthly summary of a centre, refreshed every night for the current month."""

    center = models.ForeignKey(Center, on_delete=models.CASCADE, related_name='+')
    partner = models.ForeignKey(PartnerOrganization, null=True, blank=True, on_delete=models.SET_NULL,
                                related_name='+')
    round = models.ForeignKey(Round, null=True, blank=True, on_delete=models.SET_NULL, related_name='+')
    month = models.DateField(help_text='first day of the month')
    figures = models.JSONField(default=dict)
    computed_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-month', 'center__name']
        constraints = [
            models.UniqueConstraint(fields=['center', 'round', 'month'], name='wellbeing_summary_month'),
        ]

    def __str__(self):
        return '{} {:%Y-%m}'.format(self.center, self.month)
