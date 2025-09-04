from __future__ import absolute_import
import io
import uuid
import csv
import zipfile
import logging
import codecs
import os

from django.utils.encoding import smart_str
from django.db import connection
from django.core.files.base import ContentFile
from openpyxl import Workbook
from django.core.files.storage import default_storage

from student_registration.taskapp.celery import app

# Use a dedicated Celery queue for MSCC exports so that exports can be
# processed sequentially without exhausting worker resources.
from student_registration.backends.models import ExportHistory
from student_registration.backends.utils import ExportStorage, send_push_to_web
from student_registration.users.templatetags.custom_tags import has_group
from django.urls import reverse

logger = logging.getLogger(__name__)



# Route export generation tasks to a dedicated queue so multiple requests
# are queued and processed one at a time by a low-concurrency worker.
@app.task(queue="mscc_export")
def generate_mscc_export(export_id, fields=None, file_format='csv'):
    export = ExportHistory.objects.get(id=export_id)
    try:
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
        storage = ExportStorage()
        storage.save(file_name, ContentFile(zip_output.getvalue()))
        file_url = reverse('mscc:export_download', args=[file_name])
        export.file_url = file_url
        export.status = 'done'
        export.save()
        if user:
            send_push_to_web(
                user,
                "Makani export ready",
                "Your export is ready to download.",
                data={"type": "mscc_export_ready", "url": file_url},
            )
    except Exception as e:
        logger.exception('Error generating export: %s', e)
        if export:
            export.status = 'failed'
            export.save()
            if export.created_by:
                # Notify the user that the export failed and include the reason
                send_push_to_web(
                    export.created_by,
                    "Makani export failed",
                    str(e),
                    data={"type": "mscc_export_failed", "reason": str(e)},
                )


@app.task(queue="mscc_export")
def generate_filtered_mscc_export(export_id, nationality="", first_name="", last_name="",
                                  father_name="", mother_fullname="", round=""):
    """Generate an MSCC export with optional filtering and notify the user.

    Parameters are used to filter the SQL query in the same way the synchronous
    view previously did.  Results are written to a ZIP file stored in Azure
    storage.  A push notification containing the download URL is sent to the
    requesting user when done.
    """
    export = ExportHistory.objects.get(id=export_id)
    try:
        user = export.created_by
        cursor = connection.cursor()
        center_id = user.center_id
        partner_id = user.partner_id or 0

        query_params = []

        if not round:
            vw_mscc_data_str = "SELECT * FROM vw_mscc_data WHERE id = 0"
        elif round == "no_round":
            vw_mscc_data_str = "SELECT * FROM vw_mscc_data_no_round WHERE id > 0"
        else:
            vw_mscc_data_str = "SELECT * FROM vw_mscc_data WHERE round_id = %s"
            query_params.append(round)

        if has_group(user, 'MSCC_UNICEF'):
            vw_mscc_data_str += " AND id > 0"
        elif has_group(user, 'MSCC_PARTNER') and partner_id:
            vw_mscc_data_str += " AND partner_id = %s"
            query_params.append(partner_id)
        elif has_group(user, 'MSCC_CENTER') and center_id:
            vw_mscc_data_str += " AND center_id = %s"
            query_params.append(center_id)
        else:
            vw_mscc_data_str += " AND id = 0"

        cursor.execute(vw_mscc_data_str, query_params)
        mscc_data = cursor.fetchall()
        headers = [col[0] for col in cursor.description]

        zip_output = io.BytesIO()
        with zipfile.ZipFile(zip_output, 'w') as zf:
            csv_mscc_output = io.StringIO()
            csv_writer = csv.writer(csv_mscc_output)

            # Add BOM to handle Arabic text correctly
            csv_mscc_output.write(codecs.BOM_UTF8.decode('utf-8'))
            csv_writer.writerow(headers)  # Write headers

            for row in mscc_data:
                encoded_row = [smart_str(cell) for cell in row]
                csv_writer.writerow(encoded_row)

            # Add CSV to ZIP
            zf.writestr('mscc_data.csv', csv_mscc_output.getvalue())

            # Process followup_service_data
            registration_ids = [row[0] for row in mscc_data]
            if registration_ids:
                followup_service_data_str = "SELECT * FROM mscc_followupservice WHERE registration_id IN ({})".format(
                    ','.join(['%s'] * len(registration_ids)))
                cursor.execute(followup_service_data_str, registration_ids)
                followup_service_data = cursor.fetchall()
                followup_headers = [col[0] for col in cursor.description]

                # Create CSV for followup_service_data
                csv_followup_output = io.StringIO()
                csv_writer = csv.writer(csv_followup_output)

                # Add BOM to handle Arabic text correctly
                csv_followup_output.write(codecs.BOM_UTF8.decode('utf-8'))
                csv_writer.writerow(followup_headers)  # Write headers

                for row in followup_service_data:
                    encoded_row = [smart_str(cell) for cell in row]
                    csv_writer.writerow(encoded_row)

                # Add CSV to ZIP
                zf.writestr('followup_data.csv', csv_followup_output.getvalue())

        unique_id = str(uuid.uuid4())
        file_name = f"out_file_{unique_id}.zip"
        storage = ExportStorage()
        storage.save(file_name, ContentFile(zip_output.getvalue()))
        file_url = reverse('mscc:export_download', args=[file_name])
        export.file_url = file_url
        export.status = 'done'
        export.save()
        if user:
            send_push_to_web(
                user,
                "Makani export ready",
                "Your export is ready to download.",
                data={"type": "mscc_export_ready", "url": file_url},
            )
    except Exception as e:  # pragma: no cover - logged for debugging purposes
        logger.exception('Error generating export: %s', e)
        export.status = 'failed'
        export.save()
        if export.created_by:
            send_push_to_web(
                export.created_by,
                "Makani export failed",
                str(e),
                data={"type": "mscc_export_failed", "reason": str(e)},
            )
