from __future__ import absolute_import, unicode_literals

from django.contrib import admin
from import_export import resources, fields
from import_export import fields
from import_export.admin import ImportExportModelAdmin
from .models import HouseHold, OutreachChild


class HouseHoldResource(resources.ModelResource):
    class Meta:
        model = HouseHold


class HouseHoldAdmin(ImportExportModelAdmin):
    resource_class = HouseHold
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


class OutreachChildAdmin(admin.ModelAdmin):
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


admin.site.register(OutreachChild, OutreachChildAdmin)
