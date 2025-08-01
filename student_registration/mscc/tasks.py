from __future__ import absolute_import
import io
import uuid
import csv
import zipfile
import logging
import os
import codecs
import json
import requests

from django.utils.encoding import smart_str
from django.db import connection
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from openpyxl import Workbook

from django.conf import settings
from student_registration.taskapp.celery import app

# Use a dedicated Celery queue for MSCC exports so that exports can be
# processed sequentially without exhausting worker resources.
from student_registration.backends.models import ExportHistory

logger = logging.getLogger(__name__)


def send_notification(user, file_url):
    """Send a push notification via Firebase Cloud Messaging."""
    token = getattr(user, "firebase_token", None)
    server_key = getattr(settings, "FCM_SERVER_KEY", None)
    if not token or not server_key or not file_url:
        return

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"key={server_key}",
    }
    payload = {
        "to": token,
        "data": {
            "type": "mscc_export_ready",
            "url": file_url,
        },
    }

    try:
        requests.post(
            "https://fcm.googleapis.com/fcm/send",
            headers=headers,
            data=json.dumps(payload),
            timeout=5,
        )
    except Exception:
        logger.exception("Failed to send push notification")


# Route export generation tasks to a dedicated queue so multiple requests
# are queued and processed one at a time by a low-concurrency worker.
@app.task(queue="mscc_export")
def generate_mscc_export(export_id, fields=None, file_format='csv'):
    try:
        export = ExportHistory.objects.get(id=export_id)
        user = export.created_by
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM vw_mscc_child")
        mscc_data = cursor.fetchall()
        headers = [col[0] for col in cursor.description]

        selected_headers = headers
        if fields:
            selected_headers = [h for h in headers if h in fields]

        file_ext = file_format or 'csv'

        if file_ext == 'xlsx':
            wb = Workbook()
            ws = wb.active
            ws.append(selected_headers)
            header_indices = [headers.index(h) for h in selected_headers]
            for row in mscc_data:
                ws.append([smart_str(row[i]) for i in header_indices])
            file_content_io = io.BytesIO()
            wb.save(file_content_io)
            data_bytes = file_content_io.getvalue()
        else:
            csv_output = io.StringIO()
            csv_writer = csv.writer(csv_output)
            csv_output.write(codecs.BOM_UTF8.decode('utf-8'))
            csv_writer.writerow(selected_headers)
            header_indices = [headers.index(h) for h in selected_headers]
            for row in mscc_data:
                csv_writer.writerow([smart_str(row[i]) for i in header_indices])
            data_bytes = csv_output.getvalue().encode('utf-8')
            file_ext = 'csv'

        zip_output = io.BytesIO()
        with zipfile.ZipFile(zip_output, 'w') as zf:
            zf.writestr(f'mscc_data.{file_ext}', data_bytes)

        unique_id = str(uuid.uuid4())
        file_name = f'mscc_export_{unique_id}.zip'
        file_path = os.path.join('export', file_name)
        default_storage.save(file_path, ContentFile(zip_output.getvalue()))
        file_url = default_storage.url(file_path)
        export.file_url = file_url
        export.status = 'done'
        export.save()
        if user:
            send_notification(user, file_url)
    except Exception as e:
        logger.exception('Error generating export: %s', e)
        if export:
            export.status = 'failed'
            export.save()
