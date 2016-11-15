# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from django.contrib import admin
from import_export import resources, fields
from import_export import fields
from import_export.admin import ImportExportModelAdmin

from .models import (
    Student,
    Hashing,
    Nationality,
    Language,
    IDType,
)


class HashingResource(resources.ModelResource):
    class Meta:
        model = Hashing
        fields = (
            'id',
            'id_number',
            'first_name',
            'father_name',
            'last_name',
            'mother_fullname',
            'sex',
            'birthday',
            'number',
        )
        export_order = ('id', )


class HashingAdmin(ImportExportModelAdmin):
    resource_class = HashingResource


class NationalityResource(resources.ModelResource):
    class Meta:
        model = Nationality
        fields = (
            'id',
            'name',
        )
        export_order = ('name', )


class NationalityAdmin(ImportExportModelAdmin):
    resource_class = NationalityResource


class IDTypeResource(resources.ModelResource):
    class Meta:
        model = IDType
        fields = (
            'id',
            'name'
        )
        export_order = ('name', )


class IDTypeAdmin(ImportExportModelAdmin):
        resource_class = IDTypeResource


admin.site.register(Student)
admin.site.register(Hashing, HashingAdmin)
admin.site.register(Nationality, NationalityAdmin)
admin.site.register(Language)
admin.site.register(IDType, IDTypeAdmin)
