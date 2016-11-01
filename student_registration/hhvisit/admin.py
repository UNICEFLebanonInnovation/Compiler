# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from django.contrib import admin
from import_export import resources, fields
from import_export import fields
from import_export.admin import ImportExportModelAdmin
from import_export.widgets import *

from .models import (
    HouseholdVisit,
    RegisteringAdult
)

class HouseholdVisitResource(resources.ModelResource):
    registering_adult = fields.Field(
        column_name='school',
        attribute='school',
        widget=ForeignKeyWidget(RegisteringAdult, 'name')
    )
    owner = fields.Field(
        column_name='Owner',
        attribute='owner'
    )

    class Meta:
        model = HouseholdVisit
        fields = ('registering_adult', 'owner')


class HouseholdVisitAdmin(ImportExportModelAdmin):
    resource_class = HouseholdVisitResource
    list_display = (
        'registering_adult', 'owner')
    search_fields = (
        'registering_adult', 'owner__username')

admin.site.register(HouseholdVisit, HouseholdVisitAdmin)
