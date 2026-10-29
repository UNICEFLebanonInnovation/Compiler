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
from concurrent.futures import ThreadPoolExecutor
from itertools import groupby

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.db import connections, close_old_connections
from django.db.models import Case, F, IntegerField, Q, Value, When
from django.utils import timezone

from .client import SyncClient, SyncConfigurationError, SyncTransportError
from .constants import OPERATION_DELETE, RESOURCE_ORDER, RESOURCE_CHILD_PHOTO, RESOURCE_REGISTRATION, RESOURCE_ATTENDANCE
from .models import (
    STATUS_ABANDONED,
    STATUS_FAILED,
    STATUS_PENDING,
    SyncEvent,
)
from .serializers import MODEL_FOR_RESOURCE, serialize, wire_timestamp
from .delivery import guard_events, parallel_uploads
from .partner_scope import PartnerScopeError, validate_bulk_delivery
from .makani_scope import MakaniScopeError, validate_delivery, registrations

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
        'source_modified': wire_timestamp(event.created),
    }

    if event.resource == 'mscc.teacher':
        raise MakaniScopeError('Legacy Dirasa teacher event blocked. Create a new ProgramStaff sync request.')
    if event.operation == OPERATION_DELETE:
        if (event.payload or {}).get('scope') != 'makani':
            raise MakaniScopeError('Legacy deletion has no Makani scope proof; review before replaying.')
        wire['payload'] = event.payload
        return wire

    model = MODEL_FOR_RESOURCE.get(event.resource)
    if model is None:
        return None
    try:
        instance = model.objects.get(pk=event.source_id)
    except (ObjectDoesNotExist, ValueError, TypeError):
        return None

    validate_delivery(event.resource, instance)
    wire['payload'] = serialize(event.resource, instance)
    validate_bulk_delivery(event, instance, wire['payload'])
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
    from .models import BulkSyncRun
    if event.bulk_run_id and BulkSyncRun.objects.filter(pk=event.bulk_run_id, preparation='cancelled').exists():
        from .bulk_jobs import STOPPED_MESSAGE
        event.mark_failed(STOPPED_MESSAGE, abandoned=True)
        counts['abandoned'] += 1
        return
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
    """Deliver dependency stages with bounded, independently pooled lanes."""
    totals = {'sent': 0, 'failed': 0, 'abandoned': 0}
    if not events or not getattr(settings, 'DATASYNC_ENABLED', True):
        return totals
    from .bulk_jobs import restrict_bulk_events
    events = restrict_bulk_events(events)
    if not events:
        return totals
    client = client or SyncClient()

    def rank(event):
        resource = RESOURCE_REGISTRATION if event.resource == RESOURCE_CHILD_PHOTO else event.resource
        return RESOURCE_ORDER.index(resource) if resource in RESOURCE_ORDER else len(RESOURCE_ORDER)

    for _rank, stage in groupby(sorted(events, key=rank), key=rank):
        stage = list(stage)
        photo_stage = stage[0].resource in (RESOURCE_REGISTRATION, RESOURCE_CHILD_PHOTO)
        if photo_stage and len(stage) > 1 and isinstance(client, SyncClient) and parallel_uploads() > 1:
            count = min(parallel_uploads(), len(stage))
            with ThreadPoolExecutor(max_workers=count) as executor:
                results = list(executor.map(lambda lane: _deliver_lane(lane, client),
                                            [stage[index::count] for index in range(count)]))
        elif photo_stage:
            results = [_locked_push([event], client) for event in stage]
        elif stage[0].resource == RESOURCE_ATTENDANCE:
            # One day contains many child rows. Keep complete days atomic but
            # avoid a metadata-sized batch monopolising the receiver.
            size = max(1, min(batch_size(), int(getattr(
                settings, 'DATASYNC_ATTENDANCE_BATCH_SIZE', 10))))
            results = [_locked_push(stage[index:index + size], client)
                       for index in range(0, len(stage), size)]
        else:
            results = [_locked_push(stage, client)]
        for result in results:
            for name in totals:
                totals[name] += result[name]
    return totals


def _deliver_lane(events, parent_client):
    close_old_connections()
    client = parent_client.worker_copy()
    totals = {'sent': 0, 'failed': 0, 'abandoned': 0}
    try:
        for event in events:
            result = _locked_push([event], client)
            for name in totals:
                totals[name] += result[name]
        return totals
    finally:
        client.close()
        connections.close_all()


def _locked_push(events, client):
    with guard_events(events) as ready:
        from .bulk_jobs import restrict_bulk_events
        return _push_events(restrict_bulk_events(ready), client)


def _push_events(events, client):
    """Push ``events`` in one request and record what BMA-NFE reported.

    Args:
        events (list): ``SyncEvent`` rows to deliver.
        client (SyncClient): Injected in tests; a default client otherwise.

    Returns:
        dict: ``{"sent": n, "failed": n, "abandoned": n}``.
    """
    counts = {'sent': 0, 'failed': 0, 'abandoned': 0}
    if not events or not getattr(settings, 'DATASYNC_ENABLED', True):
        return counts

    client = client or SyncClient()
    from .photos import photo_sync_enabled, prepare_photo, PhotoSourceError
    payloads = []
    attachments = {}
    by_event_id = {}

    for event in events:
        event.attempts += 1
        SyncEvent.objects.filter(pk=event.pk).update(attempts=F('attempts') + 1)
        try:
            if isinstance(client, SyncClient):
                client._check()
            if event.resource == RESOURCE_CHILD_PHOTO:
                # Migrate pending jobs from the former photo-only pipeline.
                from django.apps import apps
                Registration = apps.get_model('mscc', 'Registration')
                registration = registrations().filter(child_id=event.source_id).order_by('pk').first()
                if registration is None:
                    _abandon_missing(event, counts)
                    continue
                validate_delivery(RESOURCE_REGISTRATION, registration)
                wire = {'event_id': str(event.event_id), 'resource': RESOURCE_REGISTRATION,
                        'operation': 'upsert', 'source_id': str(registration.pk),
                        'source_modified': event.created.isoformat(),
                        'payload': serialize(RESOURCE_REGISTRATION, registration)}
            else:
                wire = build_wire_event(event)
            if wire is None:
                _abandon_missing(event, counts)
                continue
            if wire['resource'] == RESOURCE_REGISTRATION and wire['operation'] != OPERATION_DELETE:
                child = wire['payload'].get('child')
                if child:
                    reuse = isinstance(client, SyncClient) and getattr(
                        settings, 'DATASYNC_PHOTO_REUSE_ENABLED', True)
                    descriptor, stream = prepare_photo(child['source_id'], event, allow_reuse=reuse)
                    if descriptor and descriptor.get('action') == 'verify' and not client.photo_reuse_supported():
                        descriptor, stream = prepare_photo(child['source_id'], event,
                                                           allow_reuse=True, force_read=True)
                    if descriptor is not None:
                        child['photo_sync'] = descriptor
                    if stream is not None:
                        attachments[descriptor['file_key']] = stream
        except (PhotoSourceError, PartnerScopeError, MakaniScopeError) as error:
            _fail_one(event, error, counts, retryable=False)
            continue
        except (SyncTransportError, SyncConfigurationError) as error:
            _fail_one(event, error, counts, retryable=True)
            continue
        payloads.append(wire)
        by_event_id[wire['event_id']] = event

    if not payloads:
        return counts

    try:
        response = client.push(payloads, attachments=attachments) if attachments else client.push(payloads)
        # A verification request commits metadata only when NFE proves its
        # current image matches. Missing/edited files request bytes and roll
        # back; continue the same event immediately, without another attempt.
        if len(payloads) == 1 and any(result.get('photo_upload_required')
                                      for result in response.get('results', [])):
            wire = payloads[0]
            child = wire['payload'].get('child', {})
            if child.get('photo_sync', {}).get('action') == 'verify':
                descriptor, stream = prepare_photo(child['source_id'], by_event_id[wire['event_id']],
                                                   allow_reuse=True, force_read=True)
                child['photo_sync'] = descriptor
                try:
                    files = {descriptor['file_key']: stream} if stream else None
                    response = client.push([wire], attachments=files) if files else client.push([wire])
                finally:
                    if stream:
                        stream.close()
    except PhotoSourceError as error:
        for event in by_event_id.values():
            _fail_one(event, error, counts, retryable=False)
        return counts
    except (SyncTransportError, SyncConfigurationError) as error:
        for event in by_event_id.values():
            _fail_one(event, error, counts, retryable=True)
        return counts
    finally:
        for stream in attachments.values():
            stream.close()

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


def due_events(limit=None):
    """Return the events ready to be sent, in dependency order.

    Rounds and centres go before the registrations that point at them, and
    registrations before the services, gradings, referrals and attendance
    rows that hang off them. Ordering in SQL rather than in Python keeps the
    oldest work at the front even when the outbox is long.
    """
    from .bulk_jobs import current_run, retire_stopped_events
    retire_stopped_events()
    run = current_run()
    active_id = run.pk if run and run.preparation == 'ready' else None
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
        .filter(Q(bulk_run__isnull=True) | Q(bulk_run_id=active_id, bulk_run__preparation='ready'))
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
