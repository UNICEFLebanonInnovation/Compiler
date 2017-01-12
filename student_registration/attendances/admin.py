# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from django.db import models
from django.contrib import admin

from import_export.admin import ExportMixin

from .models import (
    Attendance,
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
        'validation_date'
    )
    list_filter = (
        'school',
        'classroom',
        'classlevel',
        'attendance_date',
        'status',
    )
    date_hierarchy = 'attendance_date'
    ordering = ('-attendance_date',)


admin.site.register(Attendance, AttendanceAdmin)
