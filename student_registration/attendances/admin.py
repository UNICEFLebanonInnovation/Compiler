# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from django.db import models
from django.contrib import admin

from import_export.admin import ExportMixin

from .models import (
    Attendance,
    BySchoolByDay,
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
        'date',
        'total_enrolled',
        'total_attended',
        'total_absences',
        'validated'
    )
    list_filter = (
        'school',
        'date',
    )
    date_hierarchy = 'date'
    ordering = ('-date',)

    def has_add_permission(self, request):
        return False

admin.site.register(Attendance, AttendanceAdmin)
admin.site.register(BySchoolByDay, BySchoolByDayAdmin)
