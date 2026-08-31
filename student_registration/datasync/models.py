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


class SchoolCenterLink(TimeStampedModel):
    """Which BMA-NFE centre a Compiler school's teachers belong to.

    Teachers are stored per school in the Compiler and per centre in BMA-NFE,
    and nothing in either schema connects the two. Rather than guess, the
    replication looks the centre up here; a teacher whose school is not listed
    is still replicated, just without a centre.
    """

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
