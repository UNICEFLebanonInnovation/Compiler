"""One unfinished bulk job across all operators; automatic edits keep flowing."""
from contextlib import contextmanager

from django.core.exceptions import PermissionDenied
from django.db import connection, transaction
from django.db.models import Exists, OuterRef, Q
from django.utils import timezone

from .models import BulkSyncRun, SyncEvent

MUTEX = 1112359251
STOPPED_MESSAGE = 'Stopped by the operator. Records already received by BMA-NFE are preserved.'


class BulkBusy(Exception):
    pass


@contextmanager
def admission_lock():
    with transaction.atomic():
        with connection.cursor() as cursor:
            cursor.execute('SELECT pg_try_advisory_xact_lock(%s)', [MUTEX])
            if not cursor.fetchone()[0]:
                raise BulkBusy('Another sync is starting. Refresh and try again.')
        yield


def unfinished_runs():
    outstanding = SyncEvent.objects.filter(bulk_run_id=OuterRef('pk'), status__in=('pending', 'failed'))
    return BulkSyncRun.objects.alias(_outstanding=Exists(outstanding)).filter(
        Q(preparation='waiting') | Q(preparation__in=('ready', 'cancelled'), _outstanding=True),
    ).order_by('created', 'pk')


def current_run():
    return unfinished_runs().select_related('partner', 'round', 'requested_by').first()


def required_resources(categories):
    from .bulk_types import ALL_CATEGORIES, GLOBAL_CATEGORIES
    from .constants import RESOURCE_ORDER, RESOURCE_CENTER, RESOURCE_REGISTRATION, RESOURCE_ROUND, RESOURCE_TEACHER
    selected = set(RESOURCE_ORDER if categories == [ALL_CATEGORIES] else categories)
    required = set(selected)
    if RESOURCE_TEACHER in selected:
        required.add(RESOURCE_CENTER)
    if selected - GLOBAL_CATEGORIES - {RESOURCE_ROUND}:
        required.update((RESOURCE_ROUND, RESOURCE_CENTER, RESOURCE_REGISTRATION))
    return required


def submit_run(user, partner, round_object, categories, request_id):
    from .bulk_types import selection_kind
    with admission_lock():
        existing = BulkSyncRun.objects.filter(pk=request_id).first()
        if existing:
            if (existing.requested_by_id, existing.partner_id, existing.round_id, existing.selected_categories) != (
                    user.pk, partner.pk, round_object.pk if round_object else None, categories):
                raise PermissionDenied
            return existing, False
        if unfinished_runs().exists():
            raise BulkBusy('A sync is already in progress. Finish or stop it before starting another.')
        run = BulkSyncRun.objects.create(pk=request_id, requested_by=user, partner=partner,
            round=round_object, category=selection_kind(categories), categories=categories)
        return run, True


def retire_stopped_events():
    """Skip in-flight rows; a later sweep finishes cleanup if a worker dies."""
    while True:
        with transaction.atomic():
            rows = list(SyncEvent.objects.filter(bulk_run__preparation='cancelled',
                status__in=('pending', 'failed')).order_by('pk').select_for_update(skip_locked=True)
                .values_list('pk', 'event_id')[:1000])
            if not rows:
                return
            # Delivery owns session-level event locks while HTTP is in flight;
            # it deliberately holds no row lock or SQL transaction during I/O.
            from .delivery import lock_key
            with connection.cursor() as cursor:
                cursor.execute("SELECT classid::bigint, objid::bigint FROM pg_locks "
                               "WHERE locktype='advisory' AND granted AND objsubid=1")
                held = {(high << 32) | low for high, low in cursor.fetchall()}
            ids = [pk for pk, event_id in rows
                   if lock_key('event:' + str(event_id)) % (1 << 64) not in held]
            if not ids:
                return
            SyncEvent.objects.filter(pk__in=ids).update(status='abandoned', last_error=STOPPED_MESSAGE,
                                                        next_attempt=None, modified=timezone.now())


def stop_run(run_id):
    with transaction.atomic():
        run = BulkSyncRun.objects.select_for_update(skip_locked=True).filter(pk=run_id).first()
        if run is None:
            raise BulkBusy('The sync is finishing a preparation step. Refresh and try Stop again.')
        if run.preparation not in ('waiting', 'cancelled') and not run.events.filter(
                status__in=('pending', 'failed')).exists():
            return False
        run.preparation = 'cancelled'
        run.last_error = STOPPED_MESSAGE
        run.save(update_fields=['preparation', 'last_error', 'modified'])
    retire_stopped_events()
    return True


def retry_run(run_id):
    with admission_lock():
        active = current_run()
        if active and active.pk != run_id:
            raise BulkBusy('Another sync is in progress. Finish or stop it first.')
        run = BulkSyncRun.objects.select_for_update(skip_locked=True).filter(pk=run_id).first()
        if run is None:
            raise BulkBusy('The sync is preparing records. Refresh and try Retry again.')
        if run.preparation == 'cancelled':
            raise BulkBusy('This sync was stopped. Select the records and start a new sync.')
        if run.preparation == 'failed':
            run.preparation = 'waiting'
        run.last_error = ''
        run.save(update_fields=['preparation', 'last_error', 'modified'])
        run.events.filter(status__in=('pending', 'failed')).update(next_attempt=None)
        return run


def restrict_bulk_events(events):
    if not any(event.bulk_run_id for event in events):
        return events
    run = current_run()
    active_id = run.pk if run and run.preparation == 'ready' else None
    return [event for event in events if not event.bulk_run_id or event.bulk_run_id == active_id]
