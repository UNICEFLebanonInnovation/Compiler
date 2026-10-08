# -*- coding: utf-8 -*-
"""Recording MSCC changes so they can be replicated to BMA-NFE.

A row is written inside the same transaction as the change that caused it,
and the push follows the moment that transaction commits -- so pressing Save
on an MSCC form is what sends the record, not a timer. The periodic sweep
exists only to retry what the save-time push could not deliver.

The row is written with an empty payload, which is built later, at delivery
time, from the current state of the record. That has three useful
consequences.

* A partner's save is never slowed down or rolled back by the replication.
* Several rapid edits to the same record collapse into a single push, because
  a pending event for that record is reused rather than duplicated.
* What arrives in BMA-NFE is always the record's latest state, never a stale
  snapshot taken mid-transaction.

Deletes are the exception: there is nothing left to read at delivery time, so
they carry only the resource and the id, which is all BMA-NFE needs.
"""

from __future__ import unicode_literals, absolute_import, division

import logging

from django.conf import settings
from django.db import transaction

from .constants import OPERATION_DELETE, OPERATION_UPSERT
from .models import STATUS_FAILED, STATUS_PENDING, SyncEvent

logger = logging.getLogger(__name__)


def sync_enabled():
    """Return whether outbound replication is switched on."""
    return getattr(settings, 'DATASYNC_ENABLED', False)


def enqueue(resource, source_id, operation=OPERATION_UPSERT, deliver=True):
    """Queue one change for replication.

    Args:
        resource (str): One of the ``RESOURCE_*`` constants.
        source_id: Primary key of the changed record.
        operation (str): ``upsert`` or ``delete``.
        deliver (bool): Schedule delivery as soon as the current transaction
            commits. Pass ``False`` for bulk work such as the backfill
            command, which flushes in batches of its own.

    Returns:
        SyncEvent | None: The queued event, or ``None`` when replication is
        switched off or the record has no id.
    """
    if not sync_enabled() or source_id in (None, ''):
        return None

    source_id = str(source_id)

    if operation == OPERATION_UPSERT:
        existing = SyncEvent.objects.deliverable().filter(
            resource=resource, source_id=source_id, operation=OPERATION_UPSERT,
        ).first()
        if existing is not None:
            # An undelivered push for this record is already queued; it will
            # read the record's newest state, so there is nothing to add
            # beyond clearing any retry backoff.
            if existing.status == STATUS_FAILED or existing.next_attempt:
                existing.status = STATUS_PENDING
                existing.next_attempt = None
                existing.save(update_fields=['status', 'next_attempt', 'modified'])
            if deliver:
                _schedule(existing)
            return existing

    event = SyncEvent.objects.create(
        resource=resource,
        source_id=source_id,
        operation=operation,
    )
    if deliver:
        _schedule(event)
    return event


def enqueue_instance(instance, resource=None, operation=OPERATION_UPSERT, deliver=True):
    """Queue a change for a model instance.

    Args:
        instance: The changed model instance.
        resource (str): Overrides the resource looked up from the model.
        operation (str): ``upsert`` or ``delete``.
        deliver (bool): Schedule delivery on commit.

    Returns:
        SyncEvent | None: The queued event, or ``None`` when the model is not
        replicated or replication is switched off.
    """
    from .serializers import RESOURCE_FOR_MODEL

    resource = resource or RESOURCE_FOR_MODEL.get(type(instance))
    if resource is None:
        return None
    return enqueue(resource, instance.pk, operation=operation, deliver=deliver)


def enqueue_delete(instance, resource=None):
    """Queue the removal of a record that was deleted in the Compiler."""
    return enqueue_instance(instance, resource=resource, operation=OPERATION_DELETE)


def _schedule(event):
    """Push ``event`` as soon as the save that produced it commits.

    Waiting for the commit matters: the delivery re-reads the record to build
    its payload, so it must not run until that record is actually visible.
    """
    event_pk = event.pk

    def push():
        from .dispatch import deliver_soon

        deliver_soon(event_pk)

    transaction.on_commit(push)
