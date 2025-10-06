import codecs
import csv
import datetime
import io
import logging
import uuid

from django.core.files.base import ContentFile
from django.db import connection
from django.urls import reverse
from django.utils.encoding import smart_str

from student_registration.backends.models import ExportHistory
from student_registration.backends.utils import ExportStorage, send_push_to_web
from student_registration.taskapp.celery import app
from student_registration.users.templatetags.custom_tags import has_group


logger = logging.getLogger(__name__)


def _build_bridging_query(user, round_id=None, school_id=None):
    query = "SELECT * FROM vw_bridging_data WHERE id > 0"
    params = []

    if round_id:
        query += " AND round_id = %s"
        params.append(round_id)

    if school_id:
        query += " AND school_id = %s"
        params.append(school_id)

    clm_bridging_all = has_group(user, 'CLM_BRIDGING_ALL') if user else False
    is_staff = getattr(user, 'is_staff', False)

    if user and not clm_bridging_all and not is_staff:
        if user.partner_id:
            query += " AND partner_id = %s"
            params.append(user.partner_id)
            if user.school_id:
                query += " AND school_id = %s"
                params.append(user.school_id)
        else:
            # Users without partner access should not receive any data.
            query += " AND id = 0"

    query += " ORDER BY student_first_name, student_fathername, last_name"
    return query, params


def _write_csv(headers, rows):
    csv_output = io.StringIO()
    csv_output.write(codecs.BOM_UTF8.decode('utf-8'))
    writer = csv.writer(csv_output)
    writer.writerow(headers)
    for row in rows:
        formatted_row = []
        for cell in row:
            if isinstance(cell, (datetime.date, datetime.datetime)):
                formatted_row.append(cell.strftime('%Y-%m-%d'))
            else:
                formatted_row.append(smart_str(cell))
        writer.writerow(formatted_row)
    return csv_output.getvalue().encode('utf-8')


def _finalize_export(export, file_name, file_bytes, success_message, notification_type):
    storage = ExportStorage()
    storage.save(file_name, ContentFile(file_bytes))
    file_url = reverse('mscc:export_download_csv', args=[file_name])
    export.file_url = file_url
    export.status = ExportHistory.STATUS.done
    export.save()
    if export.created_by:
        send_push_to_web(
            export.created_by,
            "Bridging export ready",
            success_message,
            data={"type": notification_type, "url": file_url},
        )


def _mark_export_failed(export, error, notification_type):
    export.status = ExportHistory.STATUS.failed
    export.save()
    if export.created_by:
        send_push_to_web(
            export.created_by,
            "Bridging export failed",
            str(error),
            data={"type": notification_type, "reason": str(error)},
        )


@app.task(queue="mscc_export")
def generate_bridging_export(export_id, round_id=None, school_id=None):
    export = ExportHistory.objects.get(id=export_id)
    try:
        user = export.created_by
        cursor = connection.cursor()
        query, params = _build_bridging_query(user, round_id=round_id, school_id=school_id)
        cursor.execute(query, params)
        rows = cursor.fetchall()
        headers = [col[0] for col in cursor.description]
        file_bytes = _write_csv(headers, rows)
        prefix = 'bridging_school' if school_id else 'bridging'
        file_name = f"{prefix}_{uuid.uuid4().hex}.csv"
        _finalize_export(
            export,
            file_name,
            file_bytes,
            "Your bridging export is ready to download.",
            "clm_bridging_export_ready",
        )
    except Exception as exc:  # pragma: no cover - logging for debugging
        logger.exception('Error generating bridging export: %s', exc)
        _mark_export_failed(export, exc, "clm_bridging_export_failed")


@app.task(queue="mscc_export")
def generate_bridging_extract_export(export_id):
    export = ExportHistory.objects.get(id=export_id)
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM vw_bridging_extract WHERE id > 0")
        rows = cursor.fetchall()
        headers = [col[0] for col in cursor.description]
        file_bytes = _write_csv(headers, rows)
        file_name = f"bridging_{uuid.uuid4().hex}.csv"
        _finalize_export(
            export,
            file_name,
            file_bytes,
            "Your bridging export is ready to download.",
            "clm_bridging_export_ready",
        )
    except Exception as exc:  # pragma: no cover - logging for debugging
        logger.exception('Error generating bridging extract export: %s', exc)
        _mark_export_failed(export, exc, "clm_bridging_export_failed")
