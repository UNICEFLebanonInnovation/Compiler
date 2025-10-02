from __future__ import absolute_import, unicode_literals

from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from import_export.fields import Field
from import_export.widgets import ForeignKeyWidget

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

    class Meta:
        model = OutreachChild
        import_id_fields = (
            'first_name',
            'birthday_year',
            'birthday_month',
            'birthday_day',
            'outreach_caregiver',
        )
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

            if not created:
                updated = False
                for key, value in caregiver_data.items():
                    if value is not None and getattr(caregiver, key) != value:
                        setattr(caregiver, key, value)
                        updated = True
                if updated:
                    caregiver.save()

            row['outreach_caregiver'] = caregiver.pk


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


admin.site.register(OutreachCaregiver, OutreachCaregiverAdmin)
admin.site.register(OutreachChild, OutreachChildAdmin)
