"""Excel export of Dirasa (Bridging) students with their profile pictures.

The workbook reuses the MSCC photo export builder: one row per Bridging
registration, with the saved profile picture embedded next to the student
and registration IDs. Access follows the printable profile ID list: users
with the CLM_BRIDGING_ALL group or staff see every registration, partner
users see their partner's (and school's) registrations only.
"""

import logging
import uuid

from django.core.exceptions import PermissionDenied, ValidationError
from django.core.files.base import ContentFile
from django.urls import reverse

from student_registration.backends.models import ExportHistory
from student_registration.backends.utils import ExportStorage
from student_registration.mscc.document_exports import ExportProfile, build_children_workbook
from student_registration.mscc.tasks import _get_executor, _notify_export, _run_with_new_db_connection
from student_registration.students.models import Student
from student_registration.users.templatetags.custom_tags import has_group

from .models import Bridging

logger = logging.getLogger(__name__)

BRIDGING_PROFILE = ExportProfile(
    registration_model=Bridging, person_model=Student, person_field='student',
    person_label='Student', sheet_name='Dirasa students',
)

_INTEGER_FILTERS = (
    ('round', 'round_id'),
    ('student__nationality', 'student__nationality_id'),
    ('partner', 'partner_id'),
    ('school', 'school_id'),
    ('governorate', 'governorate_id'),
    ('district', 'district_id'),
)
_TEXT_FILTERS = (
    'student__first_name', 'student__father_name', 'student__last_name',
    'student__mother_fullname',
)
EXPORT_FILTERS = tuple(name for name, _ in _INTEGER_FILTERS) + _TEXT_FILTERS


def user_can_export_bridging(user):
    """Whether a user may export Dirasa registrations with photographs."""
    if not user or not user.is_authenticated or not user.is_active:
        return False
    if not has_group(user, 'CLM_Bridging'):
        return False
    return bool(has_group(user, 'CLM_BRIDGING_ALL') or user.is_staff or user.partner_id)


def scoped_bridging_registrations(user):
    """Return nondeleted Bridging registrations within the user's scope."""
    related = [field.name for field in Bridging._meta.fields if field.many_to_one]
    related.extend(
        'student__' + field.name for field in Student._meta.fields if field.many_to_one
    )
    queryset = Bridging.objects.filter(deleted=False).select_related(*related).order_by(
        'student__first_name', 'student__father_name', 'student__last_name', 'pk',
    )
    if not user_can_export_bridging(user):
        return queryset.none()
    if has_group(user, 'CLM_BRIDGING_ALL') or user.is_staff:
        return queryset
    if user.partner_id:
        queryset = queryset.filter(partner_id=user.partner_id)
        if getattr(user, 'school_id', None):
            queryset = queryset.filter(school_id=user.school_id)
        return queryset
    return queryset.none()


def clean_filters(filters=None):
    """Validate the list filters; a round is always required."""
    filters = filters or {}
    cleaned = {}
    for name, _ in _INTEGER_FILTERS:
        value = filters.get(name)
        if value in (None, ''):
            continue
        if not str(value).isdecimal() or int(value) <= 0:
            raise ValidationError('Invalid %s filter.' % name)
        cleaned[name] = int(value)
    if 'round' not in cleaned:
        raise ValidationError('Please select a valid round before exporting data.')
    for name in _TEXT_FILTERS:
        value = filters.get(name)
        if value:
            cleaned[name] = str(value)
    return cleaned


def filter_bridging_registrations(queryset, filters=None):
    """Apply the Dirasa list filters without widening an access scope."""
    cleaned = clean_filters(filters)
    for name, lookup in _INTEGER_FILTERS:
        if name in cleaned:
            queryset = queryset.filter(**{lookup: cleaned[name]})
    for name in _TEXT_FILTERS:
        if name in cleaned:
            queryset = queryset.filter(**{name + '__icontains': cleaned[name]})
    return queryset


def _generate_bridging_photo_export(export_id, filters=None):
    """Store an XLSX of the requester's scoped Dirasa registrations with photos."""
    try:
        export = ExportHistory.objects.select_related('created_by').get(pk=export_id)
    except ExportHistory.DoesNotExist:
        logger.error('ExportHistory with id %s does not exist', export_id)
        return
    user = export.created_by
    try:
        if not user_can_export_bridging(user):
            raise PermissionDenied('A Dirasa export role is required.')
        registrations = filter_bridging_registrations(
            scoped_bridging_registrations(user), filters,
        )
        payload = build_children_workbook(
            registrations.iterator(chunk_size=200), profile=BRIDGING_PROFILE,
        )
        file_name = ExportStorage().save(
            'bridging_photos_{}.xlsx'.format(uuid.uuid4()), ContentFile(payload),
        )
        export.file_url = reverse('mscc:export_download', args=[file_name])
        export.status = 'done'
        export.save()
    except Exception as exc:
        logger.exception('Error generating Dirasa photo export %s', export_id)
        export.status = 'failed'
        export.file_url = ''
        export.save()
        _notify_export(user, succeeded=False, reason=str(exc))
        return
    _notify_export(user, succeeded=True, file_url=export.file_url)


def queue_bridging_photo_export(export_id, filters=None):
    """Run the Dirasa photo export in the shared background export pool."""
    return _get_executor().submit(
        _run_with_new_db_connection, _generate_bridging_photo_export, export_id, filters,
    )
