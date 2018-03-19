# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from django.contrib import admin
from import_export import resources, fields
from import_export import fields
from import_export.admin import ImportExportModelAdmin

from .forms import BLNAdminForm, RSAdminForm, CBECEAdminForm
from .models import (
    Assessment,
    Cycle,
    Site,
    Referral,
    Disability,
    BLN,
    RS,
    CBECE
)


class BLNResource(resources.ModelResource):

    class Meta:
        fields = (
            'id',
            'new_registry',
            'student_outreached',
            'have_barcode',
            'outreach_barcode',
            'round__name',
            'governorate',
            'district',
            'location',
            'language',
            'student__id',
            'student__id_type',
            'student__id_number',
            'student__number',
            'student__first_name',
            'student__father_name',
            'student__last_name',
            'student__mother_fullname',
            'student__birthday_year',
            'student__birthday_month',
            'student__birthday_day',
            'student__nationality__name',
            'student__sex',
            'student__p_code',
            'disability',
            'internal_number',
            'comments',
            'hh_educational_level',
            'student__family_status',
            'student__have_children',
            'have_labour',
            'labours',
            'labour_hours',
            'participation',
            'barriers',
            'learning_result',
            'created',
            'modified'
        )
        model = BLN
        export_order = fields


class BLNAdmin(ImportExportModelAdmin):
    resource_class = BLNResource
    form = BLNAdminForm
    # fields = '__all__'

    list_display = (
        'student',
        'governorate',
        'district',
        'partner',
        'created',
        'modified',
    )
    list_filter = (
        'round',
        'governorate',
        'district',
        'partner',
        'language',
        'student__sex',
        'student__nationality',
        'disability',
        'hh_educational_level',
        'student__family_status',
        'student__have_children',
        'have_labour',
        'labours',
        'labour_hours',
        'participation',
        'barriers',
        'learning_result',
        'created',
        'modified',
    )
    search_fields = (
        'student__first_name',
        'student__father_name',
        'student__last_name',
        'student__mother_fullname',
    )

    def get_export_formats(self):
        from student_registration.users.utils import get_default_export_formats
        return get_default_export_formats()


class RSResource(resources.ModelResource):

    class Meta:
        model = RS
        fields = (
            'id',
            'new_registry',
            'round__name',
            'type',
            'site',
            'school',
            'governorate',
            'district',
            'location',
            'language',
            'student__id',
            'student__id_type',
            'student__id_number',
            'student__number',
            'student__first_name',
            'student__father_name',
            'student__last_name',
            'student__mother_fullname',
            'student__birthday_year',
            'student__birthday_month',
            'student__birthday_day',
            'student__nationality__name',
            'student__sex',
            'student__p_code',
            'disability',
            'internal_number',
            'comments',
            'hh_educational_level',
            'student__family_status',
            'student__have_children',
            'have_labour',
            'labours',
            'labour_hours',
            'registered_in_school',
            'shift',
            'grade',
            'section',
            'referral',
            'participation',
            'barriers',
            'learning_result',
            'created',
            'modified'
        )
        export_order = fields


class RSAdmin(ImportExportModelAdmin):
    resource_class = RSResource
    form = RSAdminForm
    # fields = '__all__'

    list_display = (
        'student',
        'governorate',
        'district',
        'partner',
        'created',
        'modified',
    )
    list_filter = (
        'round',
        'type',
        'site',
        'school',
        'governorate',
        'district',
        'partner',
        'language',
        'student__sex',
        'student__nationality',
        'disability',
        'hh_educational_level',
        'student__family_status',
        'student__have_children',
        'have_labour',
        'labours',
        'labour_hours',
        'registered_in_school',
        'shift',
        'grade',
        'section',
        'referral',
        'participation',
        'barriers',
        'learning_result',
        'created',
        'modified',
    )
    search_fields = (
        'student__first_name',
        'student__father_name',
        'student__last_name',
        'student__mother_fullname',
    )

    def get_export_formats(self):
        from student_registration.users.utils import get_default_export_formats
        return get_default_export_formats()


class CBECEResource(resources.ModelResource):

    class Meta:
        model = CBECE
        fields = (
            'id',
            'new_registry',
            'student_outreached',
            'have_barcode',
            'outreach_barcode',
            'round__name',
            'cycle',
            'site',
            'school',
            'governorate',
            'district',
            'location',
            'language',
            'referral',
            'student__id',
            'student__id_type',
            'student__id_number',
            'student__number',
            'student__first_name',
            'student__father_name',
            'student__last_name',
            'student__mother_fullname',
            'student__birthday_year',
            'student__birthday_month',
            'student__birthday_day',
            'student__nationality__name',
            'student__sex',
            'student__p_code',
            'disability',
            'internal_number',
            'comments',
            'child_muac',
            'hh_educational_level',
            'have_labour',
            'labours',
            'labour_hours',
            'participation',
            'barriers',
            'learning_result',
            'created',
            'modified'
        )
        export_order = fields


class CBECEAdmin(ImportExportModelAdmin):
    resource_class = CBECEResource
    form = CBECEAdminForm
    # fields = '__all__'

    list_display = (
        'student',
        'governorate',
        'district',
        'partner',
        'created',
        'modified',
    )
    list_filter = (
        'round',
        'cycle',
        'site',
        'school',
        'governorate',
        'district',
        'partner',
        'language',
        'student__sex',
        'student__nationality',
        'disability',
        'child_muac',
        'hh_educational_level',
        'student__family_status',
        'student__have_children',
        'have_labour',
        'labours',
        'labour_hours',
        'participation',
        'barriers',
        'learning_result',
        'created',
        'modified',
    )
    search_fields = (
        'student__first_name',
        'student__father_name',
        'student__last_name',
        'student__mother_fullname',
    )

    def get_export_formats(self):
        from student_registration.users.utils import get_default_export_formats
        return get_default_export_formats()


admin.site.register(Assessment)
admin.site.register(Cycle)
admin.site.register(Site)
admin.site.register(Referral)
admin.site.register(Disability)

admin.site.register(BLN, BLNAdmin)
admin.site.register(RS, RSAdmin)
admin.site.register(CBECE, CBECEAdmin)
