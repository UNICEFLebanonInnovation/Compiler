# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from django.contrib import admin
from import_export import resources, fields
from import_export import fields
from import_export.admin import ImportExportModelAdmin
from import_export.widgets import *

from .models import (
    Outreach,
    ALPRound,
)


class OutreachResource(resources.ModelResource):

    class Meta:
        model = Outreach


class OutreachAdmin(ImportExportModelAdmin):
    resource_class = OutreachResource
    list_display = (
        'student', 'student_age', 'school', 'caza', 'governorate',
        'level', 'total', 'assigned_to_level', 'registered_in_level', 'section',
    )
    list_filter = ('registered_in_level', 'level', 'assigned_to_level', 'school', 'school__location', )
    search_fields = (
        'student__first_name', 'student__father_name', 'student__last_name', 'student__mother_fullname',
        'school__name', 'school__number', 'student__id_number', 'school__location__name', 'level__name',
        'owner__username'
    )

    def caza(self, obj):
        if obj.school and obj.school.location:
            return obj.school.location.name
        return ''

    def governorate(self, obj):
        if obj.school and obj.school.location and obj.school.location.parent:
            return obj.school.location.parent.name
        return ''

    def total(self, obj):
        total = obj.exam_total
        if obj.level and obj.level.note:
            total = u'{}/{}'.format(
                str(total),
                str(obj.level.note)
            )
        return total

admin.site.register(Outreach, OutreachAdmin)
admin.site.register(ALPRound)
