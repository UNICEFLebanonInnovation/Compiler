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
        'student', 'student_age', 'school', 'registered_in_level', 'section'
    )
    list_filter = ('registered_in_level', 'school', 'location',)


admin.site.register(Outreach, OutreachAdmin)
admin.site.register(ALPRound)
