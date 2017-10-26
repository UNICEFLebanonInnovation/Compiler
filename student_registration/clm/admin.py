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
        model = BLN
        fields = '__all__'
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
        'student__sex',
        'created',
        'modified',
    )
    search_fields = (
        'student__first_name',
        'student__father_name',
        'student__last_name',
        'student__mother_fullname',
    )


class RSResource(resources.ModelResource):

    class Meta:
        model = RS
        fields = '__all__'
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
        'student__sex',
        'created',
        'modified',
    )
    search_fields = (
        'student__first_name',
        'student__father_name',
        'student__last_name',
        'student__mother_fullname',
    )


class CBECEResource(resources.ModelResource):

    class Meta:
        model = CBECE
        fields = '__all__'
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
        'student__sex',
        'created',
        'modified',
    )
    search_fields = (
        'student__first_name',
        'student__father_name',
        'student__last_name',
        'student__mother_fullname',
    )


admin.site.register(Assessment)
admin.site.register(Cycle)
admin.site.register(Site)
admin.site.register(Referral)
admin.site.register(Disability)

admin.site.register(BLN, BLNAdmin)
admin.site.register(RS, RSAdmin)
admin.site.register(CBECE, CBECEAdmin)
