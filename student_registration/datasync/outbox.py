# -*- coding: utf-8 -*-
"""Recording MSCC changes so they can be replicated to BMA-NFE.

Enqueueing is deliberately cheap: a row is written inside the same
transaction as the change that caused it, but the payload is left empty and
built later, at delivery time, from the current state of the record. That has
three useful consequences.

* A partner's save is never slowed down or rolled back by the replication.
* Every committed edit keeps a distinct event ID so edits made while a push
  is in flight cannot be lost. The receiver ignores out-of-order old events.
* What arrives in BMA-NFE is always the record's latest state, never a stale
  snapshot taken mid-transaction.

Deletes are the exception: there is nothing left to read at delivery time, so
they carry only the resource and the id, which is all BMA-NFE needs.
"""

from __future__ import unicode_literals, absolute_import, division

import logging

from django.conf import settings
from django.db import transaction

from .constants import OPERATION_DELETE, OPERATION_UPSERT, RESOURCE_CHILD_PHOTO, RESOURCE_REGISTRATION
from .models import STATUS_FAILED, STATUS_PENDING, SyncEvent

logger = logging.getLogger(__name__)


def sync_enabled():
    """Return whether outbound replication is switched on."""
    return getattr(settings, 'DATASYNC_ENABLED', True)


def enqueue(resource, source_id, operation=OPERATION_UPSERT, deliver=True, payload=None):
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

    # Never reuse an in-flight event: a save that happens during HTTP delivery
    # must have its own durable event, otherwise its update can be lost.
    # The dispatcher reads the latest committed model state for every event.

    event = SyncEvent.objects.create(
        resource=resource,
        source_id=source_id,
        operation=operation,
        payload=payload or {},
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
    """Ask for ``event`` to be delivered once the transaction commits."""
    event_pk = event.pk
    if event.resource in (RESOURCE_CHILD_PHOTO, RESOURCE_REGISTRATION) and sync_enabled():
        transaction.on_commit(lambda: _deliver_now(event_pk, allow_inline=False))
    else:
        transaction.on_commit(lambda: _deliver_now(event_pk))


def _deliver_now(event_pk, allow_inline=True):
    """Hand one event to a worker, falling back to an in-process send.

    Delivery normally runs in Celery so the request finishes immediately. When
    the broker cannot be reached the event is sent inline instead: partners
    expect the record to be in BMA-NFE as soon as they press save, and an
    event left sitting in the outbox would only surface on the next sweep.
    """
    from .tasks import deliver_sync_event

    try:
        deliver_sync_event.delay(event_pk)
        return
    except Exception as error:  # noqa: BLE001 - broker down must not break the save
        logger.warning(
            'datasync: could not queue delivery of event %s (%s); event remains pending',
            event_pk, type(error).__name__,
        )

    if not allow_inline or not getattr(settings, 'DATASYNC_INLINE_FALLBACK', True):
        return

    from .dispatch import deliver_event

    try:
        deliver_event(event_pk)
    except Exception:  # noqa: BLE001 - the sweep will retry
        logger.exception('datasync: inline delivery of event %s failed', event_pk)
