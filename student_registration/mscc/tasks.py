import csv
import io
import os
import uuid
import zipfile
import codecs
from django.contrib.auth import get_user_model
from django.utils.encoding import smart_str
from django.db import connection
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

from student_registration.taskapp.celery import app
from student_registration.mscc.views import has_group  # reuse existing function
from student_registration.backends.models import ExportHistory, Notification
from student_registration.utility.firebase import send_push

@app.task
def export_mscc_data_async(user_id, round_id):
    cursor = connection.cursor()
    User = get_user_model()
    user = User.objects.get(id=user_id)
    center_id = user.center_id
    partner_id = user.partner_id or 0
    partner_name = user.partner.name if user.partner_id else ''

    query_params = []
    if round_id == 'no_round':
        vw_mscc_data_str = "SELECT * FROM vw_mscc_data_no_round WHERE id > 0 "
    else:
        vw_mscc_data_str = "SELECT * FROM vw_mscc_data WHERE round_id = %s"
        query_params = [round_id]

    if has_group(user, 'MSCC_UNICEF'):
        vw_mscc_data_str += " AND id > 0 "
    elif has_group(user, 'MSCC_PARTNER') and partner_id:
        vw_mscc_data_str += " AND partner_id = %s"
        query_params.append(partner_id)
    elif has_group(user, 'MSCC_CENTER') and center_id:
        vw_mscc_data_str += " AND center_id = %s"
        query_params.append(center_id)
    else:
        vw_mscc_data_str += " AND id = 0 "

    cursor.execute(vw_mscc_data_str, query_params)
    mscc_data = cursor.fetchall()
    headers = [col[0] for col in cursor.description]

    zip_output = io.BytesIO()
    with zipfile.ZipFile(zip_output, 'w') as zf:
        csv_mscc_output = io.StringIO()
        csv_writer = csv.writer(csv_mscc_output)
        csv_mscc_output.write(codecs.BOM_UTF8.decode('utf-8'))
        csv_writer.writerow(headers)
        for row in mscc_data:
            encoded_row = [smart_str(cell) for cell in row]
            csv_writer.writerow(encoded_row)
        zf.writestr('mscc_data.csv', csv_mscc_output.getvalue())

        registration_ids = [row[0] for row in mscc_data]
        if registration_ids:
            followup_service_data_str = (
                "SELECT * FROM mscc_followupservice WHERE registration_id IN ({})".format(
                    ','.join(['%s'] * len(registration_ids)))
            )
            cursor.execute(followup_service_data_str, registration_ids)
            followup_service_data = cursor.fetchall()
            followup_headers = [col[0] for col in cursor.description]
            csv_followup_output = io.StringIO()
            csv_writer = csv.writer(csv_followup_output)
            csv_followup_output.write(codecs.BOM_UTF8.decode('utf-8'))
            csv_writer.writerow(followup_headers)
            for row in followup_service_data:
                encoded_row = [smart_str(cell) for cell in row]
                csv_writer.writerow(encoded_row)
            zf.writestr('followup_data.csv', csv_followup_output.getvalue())

    unique_id = str(uuid.uuid4())
    file_name = f"mscc_export_{unique_id}.zip"
    file_path = os.path.join('export', file_name)
    default_storage.save(file_path, ContentFile(zip_output.getvalue()))

    ExportHistory.objects.create(
        export_type='Makani List',
        created_by=user,
        partner_name=partner_name,
    )

    notification = Notification.objects.create(
        name='MSCC export ready',
        type='general',
        description=f'MSCC export file {file_name} is ready for download.',
    )
    if user.school_id:
        notification.schools.add(user.school_id)

    if user.fcm_token:
        send_push(user.fcm_token, 'MSCC export ready', 'Your export file is ready.')

    return file_name
