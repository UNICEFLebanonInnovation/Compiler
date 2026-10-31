"""Excel export of Dirasa (Bridging) students with their profile pictures.

The workbook reuses the MSCC photo export builder: one row per Bridging
registration, with the saved profile picture embedded next to the student
and registration IDs. Access uses the same scope as the Dirasa list,
including school restrictions and exceptional partner access. The archive is
named with a dedicated prefix so the shared download endpoint can require a
completed export belonging to the requester.
"""

import io
import logging
import uuid
import zipfile

from django.core.exceptions import PermissionDenied, ValidationError
from django.core.files.base import ContentFile
from django.urls import reverse

from student_registration.backends.models import ExportHistory
from student_registration.backends.utils import ExportStorage
from student_registration.mscc.document_exports import ExportProfile, build_children_workbook
from student_registration.mscc.export_access import PHOTO_FILTER_VALUES, filter_by_photo
from student_registration.mscc.tasks import (
    _get_executor, _notify_excel_export, _run_with_new_db_connection,
)
from student_registration.students.models import Student

from .models import Bridging
from .bridging_access import scope_bridging_queryset, user_can_access_bridging

logger = logging.getLogger(__name__)

PHOTO_EXPORT_PREFIX = 'bridging_photo_export_'

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
    ('disability', 'disability_id'),
)
_TEXT_FILTERS = (
    'student__first_name', 'student__father_name', 'student__last_name',
    'student__mother_fullname', 'student__id_number', 'student__number',
    'student__unicef_id', 'internal_number', 'phone_number',
    'second_phone_number', 'owner__username',
)
EXPORT_FILTERS = tuple(name for name, _ in _INTEGER_FILTERS) + _TEXT_FILTERS + ('has_photo', 'learning_result')


def user_can_export_bridging(user):
    """Whether a user may export registrations within their list scope."""
    return user_can_access_bridging(user)


def scoped_bridging_registrations(user):
    """Return nondeleted Bridging registrations within the user's scope."""
    related = [field.name for field in Bridging._meta.fields if field.many_to_one]
    related.extend(
        'student__' + field.name for field in Student._meta.fields if field.many_to_one
    )
    queryset = Bridging.objects.filter(deleted=False, round__current_year=True).select_related(*related).order_by(
        'student__first_name', 'student__father_name', 'student__last_name', 'pk',
    )
    return scope_bridging_queryset(queryset, user)


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
    learning_result = filters.get('learning_result')
    if learning_result:
        if learning_result not in dict(Bridging.LEARNING_RESULT):
            raise ValidationError('Invalid learning result filter.')
        cleaned['learning_result'] = learning_result
    has_photo = filters.get('has_photo') or ''
    if has_photo not in PHOTO_FILTER_VALUES:
        raise ValidationError('Invalid photo filter.')
    if has_photo:
        cleaned['has_photo'] = has_photo
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
    if 'learning_result' in cleaned:
        queryset = queryset.filter(learning_result=cleaned['learning_result'])
    return filter_by_photo(queryset, cleaned.get('has_photo', ''))


def _generate_bridging_photo_export(export_id, filters=None, include_photos=True):
    """Store a ZIP holding the requester's scoped Dirasa workbook with photos."""
    try:
        export = ExportHistory.objects.select_related('created_by').get(pk=export_id)
    except ExportHistory.DoesNotExist:
        logger.error('ExportHistory with id %s does not exist', export_id)
        return
    try:
        if not user_can_export_bridging(export.created_by):
            raise PermissionDenied('A Dirasa export role is required.')
        registrations = filter_bridging_registrations(
            scoped_bridging_registrations(export.created_by), filters,
        )
        workbook = build_children_workbook(
            registrations.iterator(chunk_size=200), profile=BRIDGING_PROFILE,
            include_photos=include_photos,
        )
        output = io.BytesIO()
        with zipfile.ZipFile(output, 'w', compression=zipfile.ZIP_DEFLATED) as archive:
            archive.writestr('bridging_data.xlsx', workbook)
        file_name = ExportStorage().save(
            '{}{}.zip'.format(PHOTO_EXPORT_PREFIX, uuid.uuid4()),
            ContentFile(output.getvalue()),
        )
        export.file_url = reverse('mscc:export_download', args=[file_name])
        export.status = 'done'
        export.save(update_fields=['file_url', 'status', 'modified'])
    except Exception:
        logger.exception('Error generating Dirasa photo export %s', export_id)
        export.status = 'failed'
        export.file_url = ''
        export.save(update_fields=['status', 'file_url', 'modified'])
        _notify_excel_export(export, succeeded=False)
        return
    _notify_excel_export(export, succeeded=True)


def queue_bridging_photo_export(export_id, filters=None, include_photos=True):
    """Run the Dirasa photo export in the shared background export pool."""
    return _get_executor().submit(
        _run_with_new_db_connection, _generate_bridging_photo_export, export_id, filters, include_photos,
    )
