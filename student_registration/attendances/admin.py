# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from django.db import models
from django.contrib import admin

from import_export.admin import ExportMixin

from .models import (
    Attendance,
    BySchoolByDay,
    Absentee
)

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


class BySchoolByDayAdmin(admin.ModelAdmin):
    list_display = (
        'school',
        'attendance_date',
        'total_enrolled',
        'total_attended',
        'total_absences',
        'validated'
    )
    list_filter = (
        'school__location',
        'school',
        'attendance_date',
    )
    date_hierarchy = 'attendance_date'
    ordering = ('-attendance_date',)

    def has_add_permission(self, request):
        return False


class AbsenteeAdmin(admin.ModelAdmin):
    list_display = (
        'school',
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


admin.site.register(Attendance, AttendanceAdmin)
admin.site.register(BySchoolByDay, BySchoolByDayAdmin)
admin.site.register(Absentee, AbsenteeAdmin)
