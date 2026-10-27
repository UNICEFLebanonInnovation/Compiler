"""Copy linked Student profile photos using Django storage, not public URLs."""

import hashlib
import io
from datetime import datetime

from django.apps import apps
from django.conf import settings

from .client import SyncTransportError
from .serializers import wire_timestamp


class PhotoSourceError(ValueError):
    """The source link needs correction before this photo can be sent."""


def photo_sync_enabled():
    return getattr(settings, 'DATASYNC_ENABLED', True)


from .makani_scope import registrations as makani_registrations


def linked_student_id(child_id):
    Registration = apps.get_model('mscc', 'Registration')
    ids = list(makani_registrations().filter(child_id=child_id).exclude(
        student_old__isnull=True).exclude(student_old=0).order_by().values_list(
            'student_old', flat=True).distinct()[:2])
    if not ids:
        return None
    if len(ids) != 1:
        raise PhotoSourceError('Child #{} has conflicting student_old links'.format(child_id))
    return ids[0]


def enqueue_child_photo(child_id, deliver=True):
    """Photo changes requeue normal registrations in the same sync pipeline."""
    if not photo_sync_enabled() or child_id is None:
        return []
    if linked_student_id(child_id) is None:
        return []
    from .outbox import enqueue
    from .constants import RESOURCE_REGISTRATION
    Registration = apps.get_model('mscc', 'Registration')
    return [enqueue(RESOURCE_REGISTRATION, pk, deliver=deliver)
            for pk in makani_registrations().filter(child_id=child_id).values_list('pk', flat=True)]


def _fingerprint_version(student):
    """Use storage metadata without downloading the Azure blob again."""
    field = student.std_image
    storage = getattr(field, 'storage', None)
    changed = None
    if storage is not None:
        try:
            changed = storage.get_modified_time(field.name)
        except (AttributeError, NotImplementedError):
            pass
        except Exception as error:
            raise SyncTransportError('Cannot read source photo metadata') from error
    if not isinstance(changed, (datetime, str, int, float)):
        changed = getattr(student, 'modified', None)
    if not isinstance(changed, (datetime, str, int, float)):
        return None
    backend = type(storage).__module__ + '.' + type(storage).__name__
    return hashlib.sha256('{}:{}:{}:{}'.format(
        backend, field.name, changed, getattr(student, 'modified', None)).encode()).hexdigest()


def prepare_photo(child_id, event, allow_reuse=False, force_read=False):
    """Return an attachment descriptor and bytes for the registration request."""
    if not photo_sync_enabled():
        return None, None
    student_id = linked_student_id(child_id)
    if student_id is None:
        return {'action': 'unavailable', 'reason': 'missing_student_link'}, None
    Student = apps.get_model('students', 'Student')
    student = Student.objects.filter(pk=student_id).first()
    if student is None:
        raise PhotoSourceError('Linked Student does not exist')
    modified = getattr(student, 'modified', None)
    modified = max(event.created, modified) if modified else event.created
    descriptor = {'source_modified': wire_timestamp(modified),
                  'action': 'put' if student.std_image else 'remove'}
    if not student.std_image:
        return descriptor, None
    limit = getattr(settings, 'DATASYNC_PHOTO_MAX_BYTES', 5 * 1024 * 1024)
    version = _fingerprint_version(student) if allow_reuse else None
    student_key = getattr(student, 'pk', None)
    cache = None
    if version and isinstance(student_key, (str, int)):
        from .models import SourcePhotoFingerprint
        cache = SourcePhotoFingerprint.objects.filter(student_id=str(student_key)).first()
    key = 'photo_' + str(event.event_id).replace('-', '')
    if (cache and not force_read and cache.storage_name == student.std_image.name
            and cache.source_version == version and 0 < cache.size <= limit):
        descriptor.update(action='verify', sha256=cache.sha256, file_key=key)
        return descriptor, None
    try:
        with student.std_image.open('rb') as source:
            data = source.read(limit + 1)
    except Exception as error:
        raise SyncTransportError('Cannot read source photo storage') from error
    if not data or len(data) > limit:
        raise PhotoSourceError('Source photo is empty or exceeds DATASYNC_PHOTO_MAX_BYTES')
    descriptor.update(sha256=hashlib.sha256(data).hexdigest(), file_key=key)
    if version and isinstance(student_key, (str, int)):
        SourcePhotoFingerprint.objects.update_or_create(student_id=str(student_key), defaults={
            'storage_name': student.std_image.name, 'source_version': version,
            'sha256': descriptor['sha256'], 'size': len(data),
        })
    if allow_reuse and not force_read and cache and cache.sha256 == descriptor['sha256']:
        descriptor['action'] = 'verify'
        return descriptor, None
    return descriptor, io.BytesIO(data)
