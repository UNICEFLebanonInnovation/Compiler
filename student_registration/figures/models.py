"""Counts of beneficiaries prepared for NeuroDB, one stored snapshot per programme and year.

The counts are computed by a background task when NeuroDB asks for them (``FiguresRun``: NeuroDB
holds the schedule, BMA keeps none), never while an API request waits, so that reading them costs
the running system one small SELECT.
"""

from django.db import models


class FiguresSnapshot(models.Model):
    programme = models.CharField(max_length=32, db_index=True)  # e.g. "mscc", "bridging"
    year = models.CharField(max_length=32, help_text='the round or year the counts cover')
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    seconds = models.FloatField(default=0, help_text='how long the counting took')
    payload = models.JSONField()

    class Meta:
        ordering = ('-created_at',)
        indexes = [models.Index(fields=['programme', 'year', '-created_at'], name='figures_snapshot_lookup')]

    def __str__(self):
        return '%s %s (%s)' % (self.programme, self.year, self.created_at)


class FiguresRun(models.Model):
    """One count NeuroDB asked for: what, when, and how it went (NeuroDB polls it)."""

    QUEUED, RUNNING, SUCCEEDED, FAILED = 'queued', 'running', 'succeeded', 'failed'
    STATUSES = ((QUEUED, 'Queued'), (RUNNING, 'Running'), (SUCCEEDED, 'Succeeded'), (FAILED, 'Failed'))

    targets = models.JSONField(help_text='[[programme, year or null], ...]')
    status = models.CharField(max_length=10, choices=STATUSES, default=QUEUED, db_index=True)
    requested_by = models.CharField(max_length=150, blank=True)
    requested_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(null=True, blank=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    counted = models.JSONField(default=list, blank=True, help_text='[[programme, year, seconds], ...]')
    error = models.TextField(blank=True)

    class Meta:
        ordering = ('-requested_at',)

    def __str__(self):
        return 'figures run %s (%s)' % (self.pk, self.status)

    def as_dict(self):
        return {
            'id': self.pk,
            'status': self.status,
            'targets': self.targets,
            'requested_by': self.requested_by,
            'requested_at': self.requested_at.isoformat() if self.requested_at else None,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'finished_at': self.finished_at.isoformat() if self.finished_at else None,
            'counted': self.counted,
            'error': self.error,
        }
