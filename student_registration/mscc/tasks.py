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
from .models import MSCCExportRequest

logger = logging.getLogger(__name__)


def send_notification(instance):
    """Send a push notification via Firebase Cloud Messaging."""
    token = getattr(instance.user, "firebase_token", None)
    server_key = getattr(settings, "FCM_SERVER_KEY", None)
    if not token or not server_key or not instance.file_url:
        return

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"key={server_key}",
    }
    payload = {
        "to": token,
        "data": {
            "type": "mscc_export_ready",
            "url": instance.file_url,
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


@app.task
def generate_mscc_export(request_id):
    try:
        req = MSCCExportRequest.objects.get(id=request_id)
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM vw_mscc_child")
        mscc_data = cursor.fetchall()
        headers = [col[0] for col in cursor.description]

        selected_headers = headers
        if req.fields:
            selected_headers = [h for h in headers if h in req.fields]

        file_ext = req.file_format or 'csv'

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
        req.file_url = default_storage.url(file_path)
        req.status = 'done'
        req.save()
        send_notification(req)
    except Exception as e:
        logger.exception('Error generating export: %s', e)
        if req:
            req.status = 'failed'
            req.save()
