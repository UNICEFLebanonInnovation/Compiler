from __future__ import absolute_import, unicode_literals

from django.contrib import admin
from import_export import resources, fields
from import_export import fields
from import_export.admin import ImportExportModelAdmin
from .models import HouseHold, Child, OutreachYear


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
        'district',
        'partner_name',
        'interview_status'
    )

    def get_export_formats(self):
        from student_registration.users.utils import get_default_export_formats
        return get_default_export_formats()


class ChildResource(resources.ModelResource):
    class Meta:
        model = Child


class ChildAdmin(ImportExportModelAdmin):
    resource_class = Child
    list_display = (
        'form_id',
        'barcode_subset',
        'first_name',
        'father_name',
        'last_name',
        'mother_fullname',
        'birthday',
        'nationality',
    )
    search_fields = (
        'form_id',
        'barcode_subset',
    )
    list_filter = (
        'p_code',
    )

    def get_export_formats(self):
        from student_registration.users.utils import get_default_export_formats
        return get_default_export_formats()


admin.site.register(HouseHold, HouseHoldAdmin)
admin.site.register(Child, ChildAdmin)
admin.site.register(OutreachYear)
