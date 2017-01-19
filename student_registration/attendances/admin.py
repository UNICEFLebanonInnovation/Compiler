# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from django.db import models
from django.contrib import admin

from import_export.admin import ExportMixin
from import_export import resources, fields, widgets

from .models import (
    School,
    Attendance,
    BySchoolByDay,
    Absentee
)


class BySchoolResource(resources.ModelResource):
    governorate = fields.Field(
        column_name='governorate',
        attribute='school',
        widget=widgets.ForeignKeyWidget(School, 'location_parent_name')
    )
    district = fields.Field(
        column_name='district',
        attribute='school',
        widget=widgets.ForeignKeyWidget(School, 'location_name')
    )

    class Meta:
        model = BySchoolByDay
        fields = (
            'school__number',
            'school__name',
            'governorate',
            'district',
            'attendance_date',
            'total_enrolled',
            'total_attended',
            'total_attended_male',
            'total_attended_female',
            'total_absent_male',
            'total_absent_female',
            'validation_status',
        )


class BySchoolByDayAdmin(ExportMixin, admin.ModelAdmin):
    resource_class = BySchoolResource
    list_display = (
        'school',
        'attendance_date',
        'total_enrolled',
        'total_attended',
        'total_absences',
        'highest_attendance_rate',
        'total_attended_male',
        'total_attended_female',
        'total_absent_male',
        'total_absent_female',
        'validation_status'
    )
    list_filter = (
        'school__location',
        'school',
        'attendance_date',
        'validation_status',
        'highest_attendance_rate',
    )
    date_hierarchy = 'attendance_date'
    ordering = ('-attendance_date',)

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class AttendanceAdmin(ExportMixin, admin.ModelAdmin):

    list_display = (
        'school',
        'classroom',
        'classlevel',
        'student',
        'student_gender',
        'status',
        'attendance_date',
        'validation_status',
        'validation_date'
    )
    list_filter = (
        'school__location',
        'school',
        'classroom',
        'classlevel',
        'attendance_date',
        'status',
        'validation_status',
    )
    date_hierarchy = 'attendance_date'
    ordering = ('-attendance_date',)

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class AbsenteeAdmin(admin.ModelAdmin):
    list_display = (
        'school',
        'student_number',
        'student',
        'last_attendance_date',
        'absent_days',
        'reattend_date',
    )
    list_filter = (
        'school__location',
        'school',
        'last_attendance_date',
    )
    date_hierarchy = 'last_attendance_date'
    ordering = ('-absent_days',)

    def has_add_permission(self, request):
        return False


admin.site.register(Attendance, AttendanceAdmin)
admin.site.register(BySchoolByDay, BySchoolByDayAdmin)
admin.site.register(Absentee, AbsenteeAdmin)
