from __future__ import absolute_import, unicode_literals

import uuid

from django.contrib import admin, messages
from import_export import exceptions, resources
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import path, reverse
from django.utils.html import format_html
from import_export.admin import ImportExportModelAdmin
from import_export.fields import Field
from import_export.widgets import ForeignKeyWidget
from tablib import Dataset

from .models import HouseHold, OutreachCaregiver, OutreachChild


class HouseHoldResource(resources.ModelResource):
    class Meta:
        model = HouseHold


class HouseHoldAdmin(ImportExportModelAdmin):
    resource_class = HouseHoldResource
    list_display = (
        'form_id',
        'name',
        'phone_number',
        'residence_type',
        'p_code',
        'number_of_children',
        'barcode_number'
    )
    search_fields = (
        'form_id',
        'name',
        'barcode_number',
    )
    list_filter = (
        'p_code',
        'residence_type',
        'governorate',
        'district'
    )

    def get_export_formats(self):
        from student_registration.users.utils import get_default_export_formats
        return get_default_export_formats()


class OutreachCaregiverResource(resources.ModelResource):
    class Meta:
        model = OutreachCaregiver
        import_id_fields = (
            'partner_name',
            'father_name',
            'last_name',
            'primary_phone',
            'father_education_level',
            'mother_education_level',
            'number_of_children',

        )
        fields = (
            'id',
            'partner_name',
            'father_name',
            'last_name',
            'mother_full_name',
            'address',
            'father_education_level',
            'mother_education_level',
            'main_caregiver',
        )


class OutreachCaregiverAdmin(ImportExportModelAdmin):
    resource_class = OutreachCaregiverResource
    list_display = (
        'partner_name',
        'father_name',
        'last_name',
        'primary_phone',
    )
    search_fields = (
        'partner_name',
        'father_name',
        'last_name',
    )


class OutreachChildResource(resources.ModelResource):
    outreach_caregiver = Field(
        column_name='outreach_caregiver',
        attribute='outreach_caregiver',
        widget=ForeignKeyWidget(OutreachCaregiver, 'id'),
    )

    CAREGIVER_COLUMNS = (
        'partner_name',
        'father_name',
        'last_name',
        'mother_full_name',
        'address',
        'father_education_level',
        'mother_education_level',
        'main_caregiver',
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._not_imported_headers = None
        self._not_imported_rows = []

    class Meta:
        model = OutreachChild
        import_id_fields = ()
        fields = (
            'id',
            'outreach_caregiver',
            'first_name',
            'birthday_year',
            'birthday_month',
            'birthday_day',
            'gender',
            'nationality',
            'nationality_other',
            'disability',
            'disability_other',
            'working_status',
        )

    def before_import_row(self, row, **kwargs):
        caregiver_data = {
            column: (row.get(column) or None)
            for column in self.CAREGIVER_COLUMNS
        }

        if any(caregiver_data.values()):
            lookup = {
                'partner_name': caregiver_data.get('partner_name') or '',
                'father_name': caregiver_data.get('father_name') or '',
                'last_name': caregiver_data.get('last_name') or '',
            }
            caregiver, created = OutreachCaregiver.objects.get_or_create(
                **lookup,
                defaults={k: v for k, v in caregiver_data.items() if v is not None},
            )

            row['outreach_caregiver'] = caregiver.pk

    def get_or_init_instance(self, instance_loader, row):
        try:
            return super().get_or_init_instance(instance_loader, row)
        except OutreachChild.MultipleObjectsReturned:
            # Allow duplicate imports by creating a fresh instance when multiple
            # matches exist instead of skipping the row altogether.
            instance = self.init_instance(row)
            return instance, True

    def _store_not_imported_row(self, row, error_messages):
        if self._not_imported_headers is None:
            try:
                keys = list(row.keys())
            except AttributeError:
                keys = list(row)
            self._not_imported_headers = keys + ['error']

        serialized_row = []
        for key in self._not_imported_headers[:-1]:
            if hasattr(row, 'get'):
                value = row.get(key)
            else:
                try:
                    value = row[key]
                except Exception:
                    value = None
            serialized_row.append(value)
        serialized_row.append('; '.join(error_messages))
        self._not_imported_rows.append(serialized_row)

    def import_row(self, row, instance_loader, **kwargs):
        row_result = super().import_row(row, instance_loader, **kwargs)

        import_type = getattr(row_result, 'import_type', None)
        error_constant = getattr(row_result, 'IMPORT_TYPE_ERROR', 'error')
        skip_constant = getattr(row_result, 'IMPORT_TYPE_SKIP', 'skip')

        if import_type in {error_constant, skip_constant}:
            messages_list = []
            for error in getattr(row_result, 'errors', []) or []:
                message = getattr(error, 'error', error)
                messages_list.append(str(message))

            if hasattr(row, 'get'):
                extra_message = row.get('_import_error')
                if extra_message and extra_message not in messages_list:
                    messages_list.append(extra_message)

            validation_error = getattr(row_result, 'validation_error', None)
            if validation_error:
                messages_list.append(str(validation_error))

            if not messages_list:
                messages_list.append('Row was skipped during import')

            self._store_not_imported_row(row, messages_list)

        return row_result

    def after_import(self, dataset, result, using_transactions, dry_run, **kwargs):
        try:
            super().after_import(
                dataset,
                result,
                using_transactions=using_transactions,
                dry_run=dry_run,
                **kwargs,
            )
        except TypeError as exc:
            message = str(exc)
            if 'unexpected keyword argument' in message or 'positional arguments' in message:
                super().after_import(dataset, result, **kwargs)
            else:
                raise
        if self._not_imported_rows and not dry_run:
            not_imported = Dataset()
            not_imported.headers = self._not_imported_headers
            for row in self._not_imported_rows:
                not_imported.append(row)
            result.not_imported_dataset = not_imported
        else:
            result.not_imported_dataset = None

        self._not_imported_rows = []
        self._not_imported_headers = None


class OutreachChildAdmin(ImportExportModelAdmin):
    resource_class = OutreachChildResource
    list_display = (
        'full_name',
        'date_of_birth',
        'nationality',
    )
    list_filter = (
        'outreach_caregiver__form_id',
    )
    search_fields = (
        'first_name',
        'outreach_caregiver__father_name',
        'outreach_caregiver__last_name',
    )

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                'download-not-imported/<str:storage_id>/',
                self.admin_site.admin_view(self.download_not_imported_records),
                name='outreach_outreachchild_download_not_imported',
            ),
        ]
        return custom_urls + urls

    def process_result(self, result, request):
        response = super().process_result(result, request)

        dataset = getattr(result, 'not_imported_dataset', None)
        if dataset and len(dataset):
            storage_id = str(uuid.uuid4())
            session_key = self._build_session_key(storage_id)
            request.session[session_key] = dataset.export('csv')

            download_url = reverse(
                'admin:outreach_outreachchild_download_not_imported',
                args=[storage_id],
            )
            message = format_html(
                'Some rows were not imported. <a href="{}">Download the skipped rows</a>.',
                download_url,
            )
            self.message_user(request, message, level=messages.WARNING)

        return response

    def _build_session_key(self, storage_id):
        return f'outreach_child_not_imported_{storage_id}'

    def download_not_imported_records(self, request, storage_id):
        session_key = self._build_session_key(storage_id)
        data = request.session.pop(session_key, None)

        if data is None:
            self.message_user(
                request,
                'The file with skipped rows is no longer available. Please run the import again.',
                level=messages.ERROR,
            )
            changelist_url = reverse(
                f'admin:{self.model._meta.app_label}_{self.model._meta.model_name}_changelist'
            )
            return HttpResponseRedirect(changelist_url)

        response = HttpResponse(data, content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="outreachchild_not_imported.csv"'
        return response


admin.site.register(OutreachCaregiver, OutreachCaregiverAdmin)
admin.site.register(OutreachChild, OutreachChildAdmin)
