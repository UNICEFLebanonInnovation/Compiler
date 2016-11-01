# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from django.contrib import admin
from import_export import resources, fields
from import_export import fields
from import_export.admin import ImportExportModelAdmin
from import_export.widgets import *

from .models import (
    Registration,
    RegisteringAdult,
    Student,
    Location,
    School,
    WFPDistributionSite,
    WaitingList,
)

class WaitingListResource(resources.ModelResource):
    school = fields.Field(
        column_name='school',
        attribute='school',
        widget=ForeignKeyWidget(School, 'name')
    )
    location = fields.Field(
        column_name='Location',
        attribute='location',
        widget=ForeignKeyWidget(Location, 'name')
    )
    registering_adult_fname = fields.Field(
        column_name='Registering Adult First Name',
        attribute='first_name'
    )
    first_name = fields.Field(
        column_name='Adult First Name',
        attribute='first_name'
    )
    last_name = fields.Field(
        column_name='Adult Last Name',
        attribute='last_name'
    )
    father_name = fields.Field(
        column_name='Adult Father Name',
        attribute='father_name'
    )
    unhcr_id = fields.Field(
        column_name='UNHCR ID',
        attribute='unhcr_id'
    )
    phone_number = fields.Field(
        column_name='Phone Number',
        attribute='phone_number'
    )
    alternate_phone_number = fields.Field(
        column_name='Alternate phone number',
        attribute='alternate_phone_number'
    )
    village = fields.Field(
        column_name='Village',
        attribute='village'
    )
    number_of_children = fields.Field(
        column_name='Number of children',
        attribute='number_of_children'
    )
    owner = fields.Field(
        column_name='Owner',
        attribute='owner'
    )

    class Meta:
        model = WaitingList
        fields = ('school', 'first_name', 'last_name', 'father_name', 'unhcr_id', 'number_of_children',
        'phone_number', 'alternate_phone_number', 'village', 'location', 'owner')
        export_order = (
            'school', 'first_name', 'last_name', 'father_name', 'unhcr_id', 'number_of_children',
        'phone_number', 'alternate_phone_number', 'village', 'location', 'owner')


class WaitingListAdmin(ImportExportModelAdmin):
    resource_class = WaitingListResource
    list_display = (
        'school', 'first_name', 'last_name', 'father_name', 'unhcr_id', 'number_of_children',
        'phone_number', 'alternate_phone_number', 'village', 'location', 'owner')
    search_fields = (
        'school__name', 'first_name', 'last_name', 'father_name', 'unhcr_id', 'number_of_children',
        'phone_number', 'alternate_phone_number', 'village', 'location__name', 'owner__username')

admin.site.register(WaitingList, WaitingListAdmin)
