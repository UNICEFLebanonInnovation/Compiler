# -*- coding: utf-8 -*-
"""Turn queued outbox rows into HTTP pushes and record the outcome.

:func:`deliver_event` is what a save triggers; :func:`flush_outbox` is what
the periodic sweep and the backfill command use. Both funnel through
:func:`deliver_events`, which builds the payloads, posts one batch, and writes
each event's result back to the outbox.
"""

from __future__ import unicode_literals, absolute_import, division

import datetime
import logging
import threading

from concurrent.futures import ThreadPoolExecutor

from django.conf import settings
from django.db import close_old_connections
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Case, F, IntegerField, Value, When
from django.utils import timezone

from .client import SyncClient, SyncConfigurationError, SyncTransportError
from .constants import OPERATION_DELETE, RESOURCE_ORDER
from .models import (
    STATUS_ABANDONED,
    STATUS_FAILED,
    STATUS_PENDING,
    SyncEvent,
)
from .serializers import MODEL_FOR_RESOURCE, serialize

logger = logging.getLogger(__name__)

#: A rejection BMA-NFE cannot recover from is retried only a few times before
#: it is parked for an operator, rather than the full retry budget.
PERMANENT_FAILURE_ATTEMPTS = 3


def batch_size():
    """Return how many events go in one request."""
    return getattr(settings, 'DATASYNC_BATCH_SIZE', 100)


def max_attempts():
    """Return how many times an event is retried before being abandoned."""
    return getattr(settings, 'DATASYNC_MAX_ATTEMPTS', 12)


def retry_delay(attempts):
    """Return the seconds to wait before the next attempt.

    The delay doubles each time -- one minute, two, four -- and is capped by
    ``DATASYNC_MAX_RETRY_DELAY`` so a long outage still gets a regular retry.
    """
    base = getattr(settings, 'DATASYNC_RETRY_DELAY', 60)
    ceiling = getattr(settings, 'DATASYNC_MAX_RETRY_DELAY', 3600)
    return min(base * (2 ** max(attempts - 1, 0)), ceiling)


def build_wire_event(event):
    """Build the JSON event for one outbox row.

    Upserts read the record's current state, so what is sent is always the
    latest version rather than a snapshot from when the change happened.

    Args:
        event (SyncEvent): The outbox row.

    Returns:
        dict | None: The event to send, or ``None`` when the record has since
        been deleted and there is nothing left to push.
    """
    wire = {
        'event_id': str(event.event_id),
        'resource': event.resource,
        'operation': event.operation,
        'source_id': event.source_id,
        'source_modified': timezone.now().isoformat(),
    }

    if event.operation == OPERATION_DELETE:
        wire['payload'] = {}
        return wire

    model = MODEL_FOR_RESOURCE.get(event.resource)
    if model is None:
        return None
    try:
        instance = model.objects.get(pk=event.source_id)
    except (ObjectDoesNotExist, ValueError, TypeError):
        return None

    wire['payload'] = serialize(event.resource, instance)
    return wire


def _abandon_missing(event, counts):
    """Park an event whose record no longer exists in the Compiler."""
    event.status = STATUS_ABANDONED
    event.last_error = (
        'record no longer exists in the Compiler; its removal is replicated '
        'by its own delete event'
    )
    event.next_attempt = None
    event.save(update_fields=['status', 'last_error', 'next_attempt', 'modified'])
    counts['abandoned'] += 1


def _fail_one(event, error, counts, retryable=True):
    """Record a failure for one event and schedule its retry."""
    ceiling = max_attempts() if retryable else min(max_attempts(), PERMANENT_FAILURE_ATTEMPTS)

    if event.attempts >= ceiling:
        event.mark_failed(error, abandoned=True)
        counts['abandoned'] += 1
        logger.error(
            'datasync: abandoning %s#%s after %s attempt(s): %s',
            event.resource, event.source_id, event.attempts, error,
        )
        return

    retry_at = timezone.now() + datetime.timedelta(seconds=retry_delay(event.attempts))
    event.mark_failed(error, retry_at=retry_at)
    counts['failed'] += 1
    logger.warning(
        'datasync: %s#%s failed (attempt %s), retrying at %s: %s',
        event.resource, event.source_id, event.attempts, retry_at, error,
    )


def deliver_events(events, client=None):
    """Push ``events`` in one request and record what BMA-NFE reported.

    Args:
        events (list): ``SyncEvent`` rows to deliver.
        client (SyncClient): Injected in tests; a default client otherwise.

    Returns:
        dict: ``{"sent": n, "failed": n, "abandoned": n}``.
    """
    counts = {'sent': 0, 'failed': 0, 'abandoned': 0}
    if not events:
        return counts

    client = client or SyncClient()
    payloads = []
    by_event_id = {}

    for event in events:
        wire = build_wire_event(event)
        if wire is None:
            _abandon_missing(event, counts)
            continue
        payloads.append(wire)
        by_event_id[wire['event_id']] = event

    if not payloads:
        return counts

    # Count the attempt before calling out, so a worker that dies mid-request
    # cannot leave an event retrying forever.
    SyncEvent.objects.filter(pk__in=[e.pk for e in by_event_id.values()]).update(
        attempts=F('attempts') + 1
    )
    for event in by_event_id.values():
        event.attempts += 1

    try:
        response = client.push(payloads)
    except (SyncTransportError, SyncConfigurationError) as error:
        for event in by_event_id.values():
            _fail_one(event, error, counts, retryable=True)
        return counts

    reported = {
        str(result.get('event_id')): result
        for result in (response.get('results') or [])
    }

    for event_id, event in by_event_id.items():
        result = reported.get(event_id)
        if result is None:
            _fail_one(event, 'BMA-NFE did not report this event', counts)
            continue

        if result.get('status') in ('applied', 'skipped'):
            event.mark_sent(
                remote_id=result.get('local_id'),
                detail=result.get('detail') or result.get('status'),
                conflict=bool(result.get('conflict')),
                ignored_fields=result.get('ignored_fields') or [],
            )
            counts['sent'] += 1
        else:
            _fail_one(
                event,
                result.get('detail') or 'rejected by BMA-NFE',
                counts,
                retryable=bool(result.get('retryable')),
            )

    return counts


def deliver_event(event_pk, client=None):
    """Deliver a single outbox row.

    Args:
        event_pk: Primary key of the ``SyncEvent`` to deliver.
        client (SyncClient): Injected in tests.

    Returns:
        dict: The counts returned by :func:`deliver_events`.
    """
    event = SyncEvent.objects.filter(pk=event_pk).first()
    if event is None or event.status not in (STATUS_PENDING, STATUS_FAILED):
        return {'sent': 0, 'failed': 0, 'abandoned': 0}
    return deliver_events([event], client=client)


# --------------------------------------------------------------------------
# How a save-time delivery is actually invoked
# --------------------------------------------------------------------------

_executor_lock = threading.Lock()
_executor = None

#: Delivery strategies for the push that follows a save.
MODE_THREAD = 'thread'
MODE_INLINE = 'inline'
MODE_CELERY = 'celery'
DELIVERY_MODES = (MODE_THREAD, MODE_INLINE, MODE_CELERY)


def delivery_mode():
    """Return how a saved record is pushed to BMA-NFE.

    ``thread`` (the default) pushes from the web process itself, on a small
    background pool, the moment the save commits. ``inline`` pushes before the
    response is returned. ``celery`` hands the push to a worker.

    An unrecognised value falls back to ``thread`` rather than silently
    disabling the real-time push.
    """
    mode = getattr(settings, 'DATASYNC_DELIVERY_MODE', MODE_THREAD)
    if mode not in DELIVERY_MODES:
        logger.warning(
            'datasync: unknown DATASYNC_DELIVERY_MODE %r, using %r',
            mode, MODE_THREAD,
        )
        return MODE_THREAD
    return mode


def _get_executor():
    """Return the lazily created pool used for save-time pushes.

    Bounded on purpose: a burst of saves queues up behind a few workers rather
    than opening a socket per save. Anything that has to wait is already
    durable in the outbox, and the sweep is behind it either way. Size it with
    ``DATASYNC_MAX_WORKERS``.
    """
    global _executor
    if _executor is None:
        with _executor_lock:
            if _executor is None:
                _executor = ThreadPoolExecutor(
                    max_workers=getattr(settings, 'DATASYNC_MAX_WORKERS', 4),
                    thread_name_prefix='datasync',
                )
    return _executor


def _deliver_in_thread(event_pk):
    """Deliver one event on a pool thread, with its own DB connection.

    Django connections are not shared across threads, so this opens and closes
    its own. Nothing is allowed to escape: the caller is a request that has
    already committed, and the sweep retries whatever fails here.
    """
    close_old_connections()
    try:
        deliver_event(event_pk)
    except Exception:  # noqa: BLE001 - the sweep will retry
        logger.exception('datasync: background delivery of event %s failed', event_pk)
    finally:
        close_old_connections()


def deliver_soon(event_pk):
    """Push one event as soon as the save that produced it has committed.

    This is the real-time path: by the time a partner's browser has the
    response, the record is either already in BMA-NFE or sitting in the outbox
    with a retry scheduled. It never raises -- a replication problem must not
    turn into a failed save.

    Args:
        event_pk: Primary key of the ``SyncEvent`` to deliver.
    """
    mode = delivery_mode()

    if mode == MODE_CELERY:
        from .tasks import deliver_sync_event

        try:
            deliver_sync_event.delay(event_pk)
            return
        except Exception as error:  # noqa: BLE001 - broker down must not break the save
            logger.warning(
                'datasync: could not queue event %s (%s), delivering in process',
                event_pk, error,
            )

    if mode == MODE_INLINE:
        try:
            deliver_event(event_pk)
        except Exception:  # noqa: BLE001 - the sweep will retry
            logger.exception('datasync: inline delivery of event %s failed', event_pk)
        return

    try:
        _get_executor().submit(_deliver_in_thread, event_pk)
    except Exception:  # noqa: BLE001 - fall back rather than lose the push
        logger.exception(
            'datasync: could not start background delivery of event %s', event_pk
        )


def due_events(limit=None):
    """Return the events ready to be sent, in dependency order.

    Rounds and centres go before the registrations that point at them, and
    registrations before the services, gradings, referrals and attendance
    rows that hang off them. Ordering in SQL rather than in Python keeps the
    oldest work at the front even when the outbox is long.
    """
    rank = Case(
        *[
            When(resource=resource, then=Value(index))
            for index, resource in enumerate(RESOURCE_ORDER)
        ],
        default=Value(len(RESOURCE_ORDER)),
        output_field=IntegerField(),
    )
    return list(
        SyncEvent.objects.due()
        .annotate(dependency_rank=rank)
        .order_by('dependency_rank', 'created', 'id')[:limit or batch_size()]
    )


def flush_outbox(limit=None, client=None):
    """Send everything currently due, one batch at a time.

    Args:
        limit (int): Maximum events per batch.
        client (SyncClient): Injected in tests.

    Returns:
        dict: Totals across the batches that ran.
    """
    totals = {'sent': 0, 'failed': 0, 'abandoned': 0, 'batches': 0}
    client = client or SyncClient()

    while True:
        events = due_events(limit=limit)
        if not events:
            break
        counts = deliver_events(events, client=client)
        totals['sent'] += counts['sent']
        totals['failed'] += counts['failed']
        totals['abandoned'] += counts['abandoned']
        totals['batches'] += 1
        if not counts['sent'] and not counts['abandoned']:
            # Nothing moved -- BMA-NFE is down, or every event in the batch
            # was deferred. Stop rather than spin; the next sweep resumes.
            break
    return totals
