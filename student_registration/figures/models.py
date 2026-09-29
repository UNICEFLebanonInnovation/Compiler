"""Counts of beneficiaries prepared for NeuroDB, one stored snapshot per programme and year.

The counts are computed by a background task (at night, or when a snapshot is too old), never while
an API request waits, so that reading them costs the running system one small SELECT.
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
