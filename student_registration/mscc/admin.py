# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from django.contrib import admin
from import_export import resources, fields
from import_export import fields
from import_export.admin import ImportExportModelAdmin

from .models import *


class PackagesResource(resources.ModelResource):
    class Meta:
        model = Packages
        fields = (
            'id',
            'name',
            'type',
            'age',
            'category'
        )
        export_order = ('name', )


class PackagesAdmin(ImportExportModelAdmin):
    resource_class = PackagesResource
    list_display = (
        'id',
        'name',
        'type',
        'age',
        'category'
    )


class ProvidedServicesResource(resources.ModelResource):
    class Meta:
        model = ProvidedServices
        fields = (
            'id',
            'name',
            'type',
            'category',
            'registration',
            'completed',
            'required',
            'completion_date',
        )
        export_order = ('name', )


class ProvidedServicesAdmin(ImportExportModelAdmin):
    resource_class = ProvidedServicesResource
    list_display = (
        'id',
        'name',
        'type',
        'category',
        'registration',
        'completed',
        'required',
        'completion_date',
    )


admin.site.register(Registration)
admin.site.register(ProvidedServices, ProvidedServicesAdmin)
admin.site.register(Packages, PackagesAdmin)
admin.site.register(InclusionService)
admin.site.register(EducationHistory)
