# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from django.contrib import admin
from import_export import resources, fields
from import_export import fields
from import_export.admin import ImportExportModelAdmin

from .models import (
    Student,
    StudentMatching,
    Nationality,
    Language,
    IDType,
)


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


class StudentResource(resources.ModelResource):
    class Meta:
        model = Student
        fields = (
            'first_name',
            'father_name',
            'last_name',
            'mother_fullname',
            'age',
            'birthday_day',
            'birthday_month',
            'birthday_year',
            'sex',
            'nationality',
            'mother_nationality',
            'id_type',
            'id_number',
            'number',
            'address',
            'phone',
            'phone_prefix',
        )
        export_order = (
            'first_name',
            'father_name',
            'last_name',
            'mother_fullname',
            'age',
            'birthday_day',
            'birthday_month',
            'birthday_year',
            'sex',
            'nationality',
            'mother_nationality',
            'id_type',
            'id_number',
            'number',
            'address',
            'phone',
            'phone_prefix',
        )


class StudentAdmin(ImportExportModelAdmin):
    resource_class = StudentResource
    list_display = ('first_name', 'father_name', 'last_name', 'mother_fullname',
                    'calc_age', 'sex', 'nationality', 'mother_nationality',
                    )
    list_filter = ('birthday_day', 'birthday_month', 'birthday_year',
                   'sex', 'nationality', 'mother_nationality',
                   )
    search_fields = ('first_name', 'father_name', 'last_name', 'mother_fullname',
                     'id_number',
                )


admin.site.register(Student, StudentAdmin)
admin.site.register(Nationality, NationalityAdmin)
admin.site.register(Language)
admin.site.register(StudentMatching)
admin.site.register(IDType, IDTypeAdmin)
