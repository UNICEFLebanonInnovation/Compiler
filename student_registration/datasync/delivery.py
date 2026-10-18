"""Database-wide delivery slots and event/entity exclusion during HTTP I/O."""
from contextlib import contextmanager
import hashlib

from django.apps import apps
from django.conf import settings
from django.db import connection
from django.utils import timezone

from .client import SyncConfigurationError
from .constants import RESOURCE_CHILD_PHOTO, RESOURCE_REGISTRATION
from .models import STATUS_PENDING, STATUS_FAILED


def parallel_uploads():
    return max(1, min(int(getattr(settings, 'DATASYNC_PARALLEL_UPLOADS', 4)), 16))


def lock_key(value):
    return int.from_bytes(hashlib.sha256(('compiler-nfe:' + value).encode()).digest()[:8],
                          'big', signed=True)


def entity_key(event):
    if event.resource == RESOURCE_CHILD_PHOTO:
        return 'child:' + str(event.source_id)
    if event.resource == RESOURCE_REGISTRATION:
        Registration = apps.get_model('mscc', 'Registration')
        child = Registration.objects.filter(pk=event.source_id).values_list('child_id', flat=True).first()
        if child is not None:
            return 'child:' + str(child)
    return event.resource + ':' + str(event.source_id)


@contextmanager
def guard_events(events):
    """Session locks survive commits and release when a worker disconnects.

    No SQL transaction is held open during HTTP. All Compiler workers sharing
    this database use the same slot limit, including single-save deliveries.
    """
    if connection.vendor != 'postgresql':
        raise SyncConfigurationError('Controlled sync delivery requires PostgreSQL advisory locks')
    acquired = set()

    def take(name):
        key = lock_key(name)
        if key in acquired:
            return True
        with connection.cursor() as cursor:
            cursor.execute('SELECT pg_try_advisory_lock(%s)', [key])
            locked = cursor.fetchone()[0]
        if locked:
            acquired.add(key)
        return locked

    try:
        if not any(take('slot:' + str(slot)) for slot in range(parallel_uploads())):
            yield []
            return
        ready = []
        for event in events:
            if not take('event:' + str(event.event_id)) or not take('entity:' + entity_key(event)):
                continue
            event.refresh_from_db(fields=['status', 'attempts', 'next_attempt'])
            if event.status not in (STATUS_PENDING, STATUS_FAILED):
                continue
            if event.next_attempt and event.next_attempt > timezone.now():
                continue
            ready.append(event)
        yield ready
    finally:
        if acquired:
            try:
                with connection.cursor() as cursor:
                    for key in acquired:
                        cursor.execute('SELECT pg_advisory_unlock(%s)', [key])
            except Exception:
                # A broken connection must never retain a delivery slot.
                connection.close()

