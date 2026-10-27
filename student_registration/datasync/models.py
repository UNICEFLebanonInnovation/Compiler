# -*- coding: utf-8 -*-
"""The outbox that carries MSCC changes to BMA-NFE.

Every change to a replicated model writes a :class:`SyncEvent` row inside the
same database transaction as the change itself. Delivery happens afterwards,
so a network problem can never roll back or block a partner's save -- it only
leaves a row in the outbox for the next flush to pick up.
"""

from __future__ import unicode_literals, absolute_import, division

import uuid

from django.db import models
from django.db.models import JSONField
from django.utils import timezone
from django.utils.translation import gettext as _

from model_utils.models import TimeStampedModel

from .constants import (
    OPERATIONS,
    RESOURCE_LABELS,
)
from .bulk_types import CATEGORY_LABELS, RUN_CATEGORY_CHOICES, normalize_categories
from django.conf import settings

STATUS_PENDING = 'pending'
STATUS_SENT = 'sent'
STATUS_FAILED = 'failed'
STATUS_ABANDONED = 'abandoned'

SYNC_STATUS = (
    (STATUS_PENDING, _('Pending')),
    (STATUS_SENT, _('Sent')),
    (STATUS_FAILED, _('Failed, will retry')),
    (STATUS_ABANDONED, _('Abandoned')),
)


class SourcePhotoFingerprint(models.Model):
    """Recomputable checksums of source image versions; never image bytes."""

    student_id = models.CharField(max_length=64, primary_key=True)
    storage_name = models.TextField()
    source_version = models.CharField(max_length=64)
    sha256 = models.CharField(max_length=64)
    size = models.PositiveIntegerField()


class SchoolCenterLink(TimeStampedModel):
    """Historical Dirasa school mapping; unused by Makani ProgramStaff sync."""

    school = models.OneToOneField(
        'schools.School',
        related_name='datasync_center_link',
        on_delete=models.CASCADE,
        verbose_name=_('School')
    )
    center = models.ForeignKey(
        'locations.Center',
        related_name='datasync_school_links',
        on_delete=models.CASCADE,
        verbose_name=_('Centre teachers are replicated to')
    )

    class Meta:
        ordering = ['school__name']
        verbose_name = _('School to centre link')
        verbose_name_plural = _('School to centre links')

    def __str__(self):
        return '{} -> {}'.format(self.school, self.center)


class BulkSyncRun(TimeStampedModel):
    """A durable partner selection, optionally filtered by a round."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    partner = models.ForeignKey(
        'schools.PartnerOrganization', null=True, blank=True, on_delete=models.PROTECT,
        verbose_name=_('Partner'),
    )
    round = models.ForeignKey('mscc.Round', null=True, blank=True, on_delete=models.PROTECT)
    category = models.CharField(max_length=100, choices=RUN_CATEGORY_CHOICES)
    categories = models.JSONField(default=list, blank=True, verbose_name=_('Selected categories'))
    requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL,
    )
    preparation = models.CharField(max_length=12, default='waiting', choices=(
        ('waiting', 'Waiting to queue'), ('ready', 'Queued'), ('failed', 'Queueing failed'),
    ))
    queued_counts = models.JSONField(default=dict)
    last_error = models.TextField(blank=True)

    class Meta:
        ordering = ['-created']
        verbose_name = _('Bulk sync')
        verbose_name_plural = _('Bulk sync')

    def __str__(self):
        return '{} / {}'.format(self.scope_label, self.get_category_display())

    @property
    def scope_label(self):
        scope = str(self.round) if self.round_id else 'All rounds (centres and teachers)'
        return '{} · {}'.format(self.partner if self.partner_id else 'All partners (legacy)', scope)

    @property
    def selected_categories(self):
        # Requests saved before multiple selection retain their original scope.
        raw = self.categories or [self.category]
        if 'mscc.teacher' in raw:
            return raw  # Historical IDs must never be reinterpreted as ProgramStaff.
        return normalize_categories(raw)

    def get_category_display(self):
        try:
            return ', '.join(CATEGORY_LABELS.get(key, 'Legacy Dirasa teacher (disabled)') for key in self.selected_categories)
        except ValueError:
            return 'Invalid category selection'


class SyncEventQuerySet(models.QuerySet):
    """Queries used by the delivery tasks."""

    def deliverable(self):
        """Return events still waiting to reach BMA-NFE, oldest first."""
        return self.filter(status__in=(STATUS_PENDING, STATUS_FAILED))

    def due(self, now=None):
        """Return deliverable events whose retry backoff has elapsed."""
        now = now or timezone.now()
        return self.deliverable().filter(
            models.Q(next_attempt__isnull=True) | models.Q(next_attempt__lte=now)
        )


class SyncEvent(TimeStampedModel):
    """One create, update or delete waiting to be replicated to BMA-NFE."""

    event_id = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False,
        verbose_name=_('Event id')
    )
    bulk_run = models.ForeignKey(
        BulkSyncRun, null=True, blank=True, on_delete=models.PROTECT,
        related_name='events', verbose_name=_('Bulk sync run'),
    )
    resource = models.CharField(
        max_length=100,
        choices=RESOURCE_LABELS,
        db_index=True,
        verbose_name=_('Resource')
    )
    operation = models.CharField(
        max_length=20,
        choices=OPERATIONS,
        verbose_name=_('Operation')
    )
    source_id = models.CharField(
        max_length=64,
        db_index=True,
        verbose_name=_('Record id')
    )
    payload = JSONField(
        default=dict, blank=True,
        verbose_name=_('Payload')
    )
    status = models.CharField(
        max_length=20,
        choices=SYNC_STATUS,
        default=STATUS_PENDING,
        db_index=True,
        verbose_name=_('Status')
    )
    attempts = models.PositiveIntegerField(
        default=0,
        verbose_name=_('Delivery attempts')
    )
    next_attempt = models.DateTimeField(
        blank=True, null=True,
        db_index=True,
        verbose_name=_('Not before')
    )
    last_error = models.TextField(
        blank=True, null=True,
        verbose_name=_('Last error')
    )
    remote_detail = models.TextField(
        blank=True, null=True,
        verbose_name=_('Reply from BMA-NFE')
    )
    remote_id = models.CharField(
        max_length=64,
        blank=True, null=True,
        verbose_name=_('Id in BMA-NFE')
    )
    conflict = models.BooleanField(
        default=False,
        verbose_name=_('Overwrote a local edit in BMA-NFE')
    )
    ignored_fields = JSONField(
        default=list, blank=True,
        verbose_name=_('Fields BMA-NFE does not store')
    )
    sent_at = models.DateTimeField(
        blank=True, null=True,
        verbose_name=_('Delivered at')
    )

    objects = SyncEventQuerySet.as_manager()

    class Meta:
        ordering = ['created', 'id']
        indexes = [
            models.Index(fields=['status', 'next_attempt']),
            models.Index(fields=['resource', 'source_id']),
        ]
        verbose_name = _('Sync event')
        verbose_name_plural = _('Sync events')

    def __str__(self):
        return '{} {}#{} ({})'.format(
            self.operation, self.resource, self.source_id, self.status
        )

    def mark_sent(self, remote_id=None, detail='', conflict=False, ignored_fields=None):
        """Record a successful delivery."""
        self.status = STATUS_SENT
        self.sent_at = timezone.now()
        self.remote_id = str(remote_id) if remote_id is not None else None
        self.remote_detail = detail or ''
        self.conflict = bool(conflict)
        self.ignored_fields = ignored_fields or []
        self.last_error = ''
        self.next_attempt = None
        self.save(update_fields=[
            'status', 'sent_at', 'remote_id', 'remote_detail', 'conflict',
            'ignored_fields', 'last_error', 'next_attempt', 'modified',
        ])

    def mark_failed(self, error, retry_at=None, abandoned=False):
        """Record a failed delivery and when to try again.

        ``attempts`` is incremented by the dispatcher before it calls out, so
        the count is right even if the process dies mid-request.
        """
        self.status = STATUS_ABANDONED if abandoned else STATUS_FAILED
        self.last_error = str(error)[:4000]
        self.next_attempt = None if abandoned else retry_at
        self.save(update_fields=[
            'status', 'last_error', 'next_attempt', 'modified',
        ])
