# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from django.contrib import admin
from import_export import resources, fields
from import_export import fields
from import_export.admin import ImportExportModelAdmin
from import_export.widgets import *

from .models import (
    HouseholdVisit,
    RegisteringAdult,
    HouseholdVisitAttempt,
    HouseholdVisitComment,
    HouseholdVisitTeam,
    MainReason ,
    SpecificReason,
    ServiceType,
    ChildVisit,
)

class HouseholdVisitResource(resources.ModelResource):
    registering_adult = fields.Field(
        column_name='registering_adult',
        attribute='registering_adult',
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




class MainReasonResource(resources.ModelResource):
    class Meta:
        model = MainReason
        fields = (
            'id',
            'name',
        )
        export_order = ('name',)

class MainReasonAdmin(ImportExportModelAdmin):
        resource_class = MainReasonResource

class SpecificReasonResource(resources.ModelResource):
    class Meta:
        model = SpecificReason
        fields = (
            'id',
            'name',
        )
        export_order = ('name',)

class SpecificReasonAdmin(ImportExportModelAdmin):
        resource_class = SpecificReasonResource

class ServiceTypeResource(resources.ModelResource):
    class Meta:
        model = ServiceType
        fields = (
            'id',
            'name',
        )
        export_order = ('name',)

class ServiceTypeAdmin(ImportExportModelAdmin):
        resource_class = ServiceTypeResource

class HouseholdVisitTeamResource(resources.ModelResource):
    class Meta:
        model = HouseholdVisitTeam
        fields = (
            'id',
            'name',
            'first_enumerator',
            'second_enumerator',
        )
        export_order = ('name',)

class HouseholdVisitTeamAdmin(ImportExportModelAdmin):
        resource_class = HouseholdVisitTeamResource


class HouseholdVisitAttemptResource(resources.ModelResource):
    class Meta:
        model = HouseholdVisitAttempt
        fields = (
            'id',
            'household_visit',
            'household_found',
            'comment',
            'date',
        )
        export_order = ('date',)

class HouseholdVisitAttemptAdmin(ImportExportModelAdmin):
        resource_class = HouseholdVisitAttemptResource

class HouseholdVisitCommentResource(resources.ModelResource):
    class Meta:
        model = HouseholdVisitComment
        fields = (
            'id',
            'household_visit',
            'household_found',
            'comment',
            'date',
        )
        export_order = ('date',)

class HouseholdVisitCommentAdmin(ImportExportModelAdmin):
        resource_class = HouseholdVisitCommentResource

admin.site.register(HouseholdVisit, HouseholdVisitAdmin)
admin.site.register(MainReason, MainReasonAdmin)
admin.site.register(SpecificReason, SpecificReasonAdmin)
admin.site.register(ServiceType, ServiceTypeAdmin)
admin.site.register(HouseholdVisitTeam, HouseholdVisitTeamAdmin)
admin.site.register(HouseholdVisitAttempt, HouseholdVisitAttemptAdmin)
admin.site.register(HouseholdVisitComment, HouseholdVisitCommentAdmin)



