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


class RegisteredInFilter(admin.SimpleListFilter):
    # Human-readable title which will be displayed in the
    # right admin sidebar just above the filter options.
    title = 'Registered in?'

    # Parameter for the filter that will be used in the URL query.
    parameter_name = 'registered_in'

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """
        return (
            ('pilot', 'PILOT'),
            ('alp', 'ALP'),
            ('2ndshift', '2nd-shift'),
        )

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """
        if self.value() and self.value() == 'pilot':
            return queryset.filter(student_registration__isnull=False)
        if self.value() and self.value() == 'alp':
            return queryset.exclude(alp_enrollment__deleted=True).filter(alp_enrollment__isnull=False)
        if self.value() and self.value() == '2ndshift':
            return queryset.exclude(student_enrollment__deleted=True).exclude(student_enrollment__dropout_status=True).filter(student_enrollment__isnull=False)
        return queryset


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
    list_display = (
        'first_name',
        'father_name',
        'last_name',
        'mother_fullname',
        'calc_age',
        'sex',
        'nationality',
        'mother_nationality',
    )
    list_filter = (
        'birthday_day',
        'birthday_month',
        'birthday_year',
        'sex',
        'nationality',
        'mother_nationality',
        RegisteredInFilter,
    )
    search_fields = (
        'first_name',
        'father_name',
        'last_name',
        'mother_fullname',
        'id_number',
    )


class StudentMatchingResource(resources.ModelResource):
    class Meta:
        model = StudentMatching


class StudentMatchingAdmin(ImportExportModelAdmin):
    resource_class = StudentMatching
    list_display = (
        'id',
        'pilot_id',
        'registry',
        'enrolled_id',
        'enrolment',
    )
    search_fields = (
        'registry__first_name',
        'registry__father_name',
        'registry__last_name',
        'registry__mother_fullname',
        'registry__id_number',
        'registry__number',
        'enrolment__first_name',
        'enrolment__father_name',
        'enrolment__last_name',
        'enrolment__mother_fullname',
        'enrolment__id_number',
        'enrolment__number',
    )

    def pilot_id(self, obj):
        if obj.registry:
            return obj.registry.id
        return ''

    def enrolled_id(self, obj):
        if obj.enrolment:
            return obj.enrolment.id
        return ''


admin.site.register(Student, StudentAdmin)
admin.site.register(Nationality, NationalityAdmin)
admin.site.register(Language)
admin.site.register(StudentMatching, StudentMatchingAdmin)
admin.site.register(IDType, IDTypeAdmin)
