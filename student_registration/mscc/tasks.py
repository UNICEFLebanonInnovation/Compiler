from __future__ import absolute_import
import io
import uuid
import csv
import zipfile
import logging
import codecs
import threading

from concurrent.futures import ThreadPoolExecutor

from django.conf import settings
from django.utils.encoding import smart_str
from django.db import connection, close_old_connections
from django.core.files.base import ContentFile
from openpyxl import Workbook

from student_registration.backends.models import ExportHistory
from student_registration.backends.utils import ExportStorage, send_push_to_web
from student_registration.users.templatetags.custom_tags import has_group
from django.urls import reverse

logger = logging.getLogger(__name__)

_executor_lock = threading.Lock()
_export_executor = None


def _get_executor():
    """Return a lazily instantiated thread pool for export jobs."""
    global _export_executor
    if _export_executor is None:
        with _executor_lock:
            if _export_executor is None:
                max_workers = getattr(settings, 'MSCC_EXPORT_MAX_WORKERS', 4)
                _export_executor = ThreadPoolExecutor(
                    max_workers=max_workers,
                    thread_name_prefix='mscc-export'
                )
    return _export_executor


def _run_with_new_db_connection(fn, *args, **kwargs):
    """Execute *fn* ensuring Django DB connections are thread-safe."""
    close_old_connections()
    try:
        return fn(*args, **kwargs)
    finally:
        close_old_connections()


def _generate_mscc_export(export_id, fields=None, file_format='csv'):
    try:
        export = ExportHistory.objects.get(id=export_id)
    except ExportHistory.DoesNotExist:
        logger.error("ExportHistory with id %s does not exist", export_id)
        return
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
def _generate_filtered_mscc_export(export_id, nationality="", first_name="", last_name="",
                                   father_name="", mother_fullname="", round=""):
    """Generate an MSCC export with optional filtering and notify the user.

    Parameters are used to filter the SQL query in the same way the synchronous
    view previously did.  Results are written to a ZIP file stored in Azure
    storage.  A push notification containing the download URL is sent to the
    requesting user when done.
    """
    print('[MSCC EXPORT DEBUG] _generate_filtered_mscc_export: started export_id={} nationality={!r} first_name={!r} last_name={!r} father_name={!r} mother_fullname={!r} round={!r}'.format(export_id, nationality, first_name, last_name, father_name, mother_fullname, round), flush=True)
    export = ExportHistory.objects.get(id=export_id)
    print('[MSCC EXPORT DEBUG] _generate_filtered_mscc_export: loaded ExportHistory id={} status={}'.format(export.id, export.status), flush=True)
    try:
        user = export.created_by
        print('[MSCC EXPORT DEBUG] _generate_filtered_mscc_export: user_id={} username={}'.format(getattr(user, 'id', None), getattr(user, 'username', None)), flush=True)
        cursor = connection.cursor()
        print('[MSCC EXPORT DEBUG] _generate_filtered_mscc_export: database cursor opened', flush=True)
        statement_timeout_ms = getattr(settings, 'MSCC_EXPORT_STATEMENT_TIMEOUT_MS', 300000)
        cursor.execute("SET statement_timeout = %s", [statement_timeout_ms])
        print('[MSCC EXPORT DEBUG] _generate_filtered_mscc_export: statement_timeout set to {}ms'.format(statement_timeout_ms), flush=True)
        center_id = user.center_id
        partner_id = user.partner_id or 0
        is_world_learning = bool(user.partner and user.partner.is_world_learning)
        print('[MSCC EXPORT DEBUG] _generate_filtered_mscc_export: user scope center_id={} partner_id={} is_world_learning={}'.format(center_id, partner_id, is_world_learning), flush=True)

        query_params = []

        if not round:
            vw_mscc_data_str = "SELECT * FROM vw_mscc_data WHERE id = 0"

        elif round == "no_round":
            if is_world_learning:
                vw_mscc_data_str = "SELECT * FROM vw_mscc_wl_data_no_round WHERE id > 0"
            else:
                vw_mscc_data_str = "SELECT * FROM vw_mscc_data_no_round WHERE id > 0"

        else:
            if is_world_learning:
                vw_mscc_data_str = "SELECT * FROM vw_mscc_wl_data WHERE round_id = %s"
            else:
                vw_mscc_data_str = "SELECT * FROM vw_mscc_data WHERE round_id = %s"

            query_params.append(round)

        if has_group(user, 'MSCC_UNICEF') or is_world_learning:
            vw_mscc_data_str += " AND id > 0"
            print('[MSCC EXPORT DEBUG] _generate_filtered_mscc_export: applying unrestricted UNICEF/WL scope to match MSCC list access', flush=True)
        elif has_group(user, 'MSCC_PARTNER') and partner_id:
            vw_mscc_data_str += " AND partner_id = %s"
            query_params.append(partner_id)
            print('[MSCC EXPORT DEBUG] _generate_filtered_mscc_export: applying MSCC_PARTNER scope partner_id={}'.format(partner_id), flush=True)
        elif has_group(user, 'MSCC_CENTER') and center_id:
            vw_mscc_data_str += " AND center_id = %s"
            query_params.append(center_id)
            print('[MSCC EXPORT DEBUG] _generate_filtered_mscc_export: applying MSCC_CENTER scope center_id={}'.format(center_id), flush=True)
        else:
            vw_mscc_data_str += " AND id = 0"
            print('[MSCC EXPORT DEBUG] _generate_filtered_mscc_export: no matching export scope, forcing empty result', flush=True)

        print('[MSCC EXPORT DEBUG] _generate_filtered_mscc_export: executing main query sql={!r} params={}'.format(vw_mscc_data_str, query_params), flush=True)
        cursor.execute(vw_mscc_data_str, query_params)
        mscc_data = cursor.fetchall()
        headers = [col[0] for col in cursor.description]
        print('[MSCC EXPORT DEBUG] _generate_filtered_mscc_export: main query returned rows={} headers={}'.format(len(mscc_data), headers), flush=True)
        if not mscc_data and "center_id = %s" in vw_mscc_data_str and partner_id:
            fallback_query = vw_mscc_data_str.replace("center_id = %s", "partner_id = %s", 1)
            fallback_params = list(query_params)
            fallback_params[-1] = partner_id
            print('[MSCC EXPORT DEBUG] _generate_filtered_mscc_export: center scope returned 0 rows; retrying with partner fallback sql={!r} params={}'.format(fallback_query, fallback_params), flush=True)
            cursor.execute(fallback_query, fallback_params)
            mscc_data = cursor.fetchall()
            headers = [col[0] for col in cursor.description]
            vw_mscc_data_str = fallback_query
            query_params = fallback_params
            print('[MSCC EXPORT DEBUG] _generate_filtered_mscc_export: partner fallback returned rows={} headers={}'.format(len(mscc_data), headers), flush=True)

        zip_output = io.BytesIO()
        with zipfile.ZipFile(zip_output, 'w') as zf:
            print('[MSCC EXPORT DEBUG] _generate_filtered_mscc_export: writing mscc_data.csv to zip', flush=True)
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
            print('[MSCC EXPORT DEBUG] _generate_filtered_mscc_export: registration_ids count={}'.format(len(registration_ids)), flush=True)
            if registration_ids:
                followup_service_data_str = "SELECT * FROM mscc_followupservice WHERE registration_id IN ({})".format(
                    ','.join(['%s'] * len(registration_ids)))
                print('[MSCC EXPORT DEBUG] _generate_filtered_mscc_export: executing followup query rows={} sql={!r}'.format(len(registration_ids), followup_service_data_str), flush=True)
                cursor.execute(followup_service_data_str, registration_ids)
                followup_service_data = cursor.fetchall()
                followup_headers = [col[0] for col in cursor.description]
                print('[MSCC EXPORT DEBUG] _generate_filtered_mscc_export: followup query returned rows={} headers={}'.format(len(followup_service_data), followup_headers), flush=True)

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
            else:
                print('[MSCC EXPORT DEBUG] _generate_filtered_mscc_export: no registration ids; writing empty followup_data.csv with headers only', flush=True)
                cursor.execute("SELECT * FROM mscc_followupservice WHERE 1 = 0")
                followup_headers = [col[0] for col in cursor.description]
                csv_followup_output = io.StringIO()
                csv_writer = csv.writer(csv_followup_output)
                csv_followup_output.write(codecs.BOM_UTF8.decode('utf-8'))
                csv_writer.writerow(followup_headers)
                zf.writestr('followup_data.csv', csv_followup_output.getvalue())

        unique_id = str(uuid.uuid4())
        file_name = f"out_file_{unique_id}.zip"
        print('[MSCC EXPORT DEBUG] _generate_filtered_mscc_export: saving zip file_name={} bytes={}'.format(file_name, len(zip_output.getvalue())), flush=True)
        storage = ExportStorage()
        storage.save(file_name, ContentFile(zip_output.getvalue()))
        file_url = reverse('mscc:export_download', args=[file_name])
        print('[MSCC EXPORT DEBUG] _generate_filtered_mscc_export: file saved file_url={}'.format(file_url), flush=True)
        export.file_url = file_url
        export.status = 'done'
        export.save()
        print('[MSCC EXPORT DEBUG] _generate_filtered_mscc_export: ExportHistory marked done id={}'.format(export.id), flush=True)
        if user:
            print('[MSCC EXPORT DEBUG] _generate_filtered_mscc_export: sending success push notification', flush=True)
            send_push_to_web(
                user,
                "Makani export ready",
                "Your export is ready to download.",
                data={"type": "mscc_export_ready", "url": file_url},
            )
    except Exception as e:  # pragma: no cover - logged for debugging purposes
        print('[MSCC EXPORT DEBUG] _generate_filtered_mscc_export: exception={!r}'.format(e), flush=True)
        logger.exception('Error generating export: %s', e)
        export.status = 'failed'
        export.save()
        print('[MSCC EXPORT DEBUG] _generate_filtered_mscc_export: ExportHistory marked failed id={}'.format(export.id), flush=True)
        if export.created_by:
            print('[MSCC EXPORT DEBUG] _generate_filtered_mscc_export: sending failure push notification', flush=True)
            send_push_to_web(
                export.created_by,
                "Makani export failed",
                str(e),
                data={"type": "mscc_export_failed", "reason": str(e)},
            )


def queue_mscc_export(export_id, fields=None, file_format='csv'):
    """Run the MSCC export in a background thread."""
    executor = _get_executor()
    return executor.submit(
        _run_with_new_db_connection,
        _generate_mscc_export,
        export_id,
        fields,
        file_format,
    )


def queue_filtered_mscc_export(export_id, nationality="", first_name="", last_name="",
                               father_name="", mother_fullname="", round=""):
    """Run the filtered MSCC export in a background thread."""
    print('[MSCC EXPORT DEBUG] queue_filtered_mscc_export: submitting export_id={}'.format(export_id), flush=True)
    executor = _get_executor()
    future = executor.submit(
        _run_with_new_db_connection,
        _generate_filtered_mscc_export,
        export_id,
        nationality,
        first_name,
        last_name,
        father_name,
        mother_fullname,
        round,
    )
    print('[MSCC EXPORT DEBUG] queue_filtered_mscc_export: submitted export_id={} future={}'.format(export_id, future), flush=True)
    return future
