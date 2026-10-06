# -*- coding: utf-8 -*-
"""Background jobs for the Dirasa (Bridging) programme."""
from __future__ import absolute_import, unicode_literals

import logging
import uuid

from django.core.files.base import ContentFile
from django.urls import reverse

from student_registration.backends.models import ExportHistory
from student_registration.backends.utils import ExportStorage, send_push_to_web
from student_registration.mscc.tasks import _get_executor, _run_with_new_db_connection

from .models import Bridging
from .profile_id import build_profile_ids_pdf

logger = logging.getLogger(__name__)

PROFILE_IDS_EXPORT_TYPE = 'Bridging Profile IDs'
PROFILE_IDS_READY = 'bridging_profile_ids_ready'
PROFILE_IDS_FAILED = 'bridging_profile_ids_failed'


def profile_ids_registrations(registration_ids):
    """Registrations to print, in the order the Dirasa list shows them."""
    return (
        Bridging.objects.filter(id__in=registration_ids)
        .select_related('student', 'student__nationality', 'round', 'partner', 'governorate', 'disability')
        .order_by('student__first_name', 'student__father_name', 'student__last_name')
    )


def _generate_bridging_profile_ids(export_id, registration_ids):
    """Build the profile IDs PDF, store it, record it on the export and notify its owner."""
    try:
        export = ExportHistory.objects.get(id=export_id)
    except ExportHistory.DoesNotExist:
        logger.error('ExportHistory with id %s does not exist', export_id)
        return None

    user = export.created_by
    try:
        pdf_bytes = build_profile_ids_pdf(profile_ids_registrations(registration_ids))

        file_name = 'bridging_profile_ids_{}.pdf'.format(uuid.uuid4())
        ExportStorage().save(file_name, ContentFile(pdf_bytes))
        file_url = reverse('clm:bridging_profile_ids_download', args=[file_name])

        export.file_url = file_url
        export.status = ExportHistory.STATUS.done
        export.save()

        if user:
            send_push_to_web(
                user,
                'Dirasa profile IDs ready',
                'The PDF with {} profile ID card(s) is ready to download.'.format(len(registration_ids)),
                data={'type': PROFILE_IDS_READY, 'url': file_url, 'export_id': export.id},
            )
        return file_url
    except Exception as exc:
        logger.exception('Error generating Dirasa profile IDs for export %s: %s', export_id, exc)
        export.status = ExportHistory.STATUS.failed
        export.save()
        if user:
            send_push_to_web(
                user,
                'Dirasa profile IDs failed',
                str(exc),
                data={'type': PROFILE_IDS_FAILED, 'reason': str(exc), 'export_id': export.id},
            )
        return None


def queue_bridging_profile_ids(export_id, registration_ids):
    """Generate the profile IDs PDF in the background (same pool as the Makani exports)."""
    return _get_executor().submit(
        _run_with_new_db_connection,
        _generate_bridging_profile_ids,
        export_id,
        list(registration_ids),
    )
