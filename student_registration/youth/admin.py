# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from import_export import resources, fields
from import_export import fields
from import_export.admin import ImportExportModelAdmin
from django import forms
from .models import *


class RegistrationAdmin(admin.ModelAdmin):

    list_display = (
        'adolescent',
        'get_unicef_id',
        'partner',
        'center',
        'deleted',
        'created',
        'modified',
    )
    list_filter = (
        'adolescent__mother_fullname',
        'adolescent__gender',
        'adolescent__nationality',
        'partner',
        'center',
        'deleted',
        'created',
        'modified',
    )
    search_fields = (
        'adolescent__first_name',
        'adolescent__father_name',
        'adolescent__last_name',
        'adolescent__unicef_id',
    )

    def get_unicef_id(self, obj):
        return obj.adolescent.unicef_id
    get_unicef_id.short_description = 'Unicef ID'


class YouthAssessmentAdmin(admin.ModelAdmin):
    list_display = (
        'registration',
        'undertake_post_diagnostic',
        'receive_passing_grade',
        'complete_life_skills',
        'participate_volunteering',
        'volunteering_opportunity',
        'benefit_innovation_course',
        'compelete_yfs_course',
        'training_material',
        'future_path',
        'participate_community_initiatives',
        'attendance'
    )

    search_fields = (
        'registration__adolescent__first_name',
        'registration__adolescent__father_name',
        'registration__adolescent__last_name',
    )


class ProgramDocumentAdminForm(forms.ModelForm):
    class Meta:
        model = ProgramDocument
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(ProgramDocumentAdminForm, self).__init__(*args, **kwargs)
        self.fields['governorates'].queryset = Location.objects.filter(parent__isnull=True)


class ProgramDocumentAdmin(admin.ModelAdmin):
    form = ProgramDocumentAdminForm
    list_display = (
        'project_code',
        'project_name',
        'project_description',
        'partner',
        'funded_by',
        'project_status',
    )
    list_filter = (
        'partner',
        'funded_by',
        'project_status',
    )
    search_fields = (
        'project_code',
        'project_name',
        'project_description',
    )


class ProgramTypeAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']


class ProgramTagAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']


class CreationYearFilter(admin.SimpleListFilter):
    title = _('creation year')
    parameter_name = 'creation_year'

    def lookups(self, request, model_admin):
        years = set([obj.created.year for obj in model_admin.model.objects.all()])
        return [(year, year) for year in years]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(created__year=self.value())
        return queryset


class MasterProgramAdmin(admin.ModelAdmin):
    list_display = ('number', 'name', 'program_type', 'program_tag', 'active', 'creation_year')
    search_fields = ('number', 'name')
    list_filter = (CreationYearFilter, 'program_type', 'program_tag', 'active')


class SubProgramAdmin(admin.ModelAdmin):
    list_display = ('number', 'name', 'master_program', 'creation_year')
    search_fields = ('number', 'name', 'master_program', 'active')
    list_filter = (CreationYearFilter,)


class PartnerAdmin(admin.ModelAdmin):
    list_display = ('name', 'short_name', 'active')
    search_fields = ('name', 'short_name', 'active')


class FundedByAdmin(admin.ModelAdmin):
    list_display = ('name', 'active')
    search_fields = ('name', 'active')


class FocalPointAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'email')
    search_fields = ['name']


class PlanAdmin(admin.ModelAdmin):
    list_display = ('name', 'active')
    search_fields = ('name', 'active')


class SectorAdmin(admin.ModelAdmin):
    list_display = ('name', 'default')
    search_fields = ('name', 'default')


class ProjectTypeAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']


class ProjectStatusAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']


class PopulationGroupsAdmin(admin.ModelAdmin):
    list_display = ('name', 'short_name')
    search_fields = ('name', 'short_name')


class DonorAdmin(admin.ModelAdmin):
    list_display = ('name', 'active')
    search_fields = ('name', 'active')


class EnrolledProgramAdmin(admin.ModelAdmin):
    list_display = (
        'registration',
        'education_status',
        'dropout_date',
        'master_program',
        'sub_program',
        'donor',
        'program_document',
        'registration_date',
        'completion_date'
    )
    list_filter = (
        'education_status',
        'master_program',
        'donor',
    )


admin.site.register(Partner, PartnerAdmin)
admin.site.register(FundedBy, FundedByAdmin)
admin.site.register(FocalPoint, FocalPointAdmin)
admin.site.register(Plan, PlanAdmin)
admin.site.register(Sector, SectorAdmin)
admin.site.register(ProjectType, ProjectTypeAdmin)
admin.site.register(ProjectStatus, ProjectStatusAdmin)
admin.site.register(PopulationGroups, PopulationGroupsAdmin)
admin.site.register(ProgramType, ProgramTypeAdmin)
admin.site.register(ProgramTag, ProgramTagAdmin)
admin.site.register(MasterProgram, MasterProgramAdmin)
admin.site.register(SubProgram, SubProgramAdmin)
admin.site.register(Donor,DonorAdmin)
admin.site.register(YouthAssessment)
admin.site.register(ProgramDocument, ProgramDocumentAdmin)
admin.site.register(Registration, RegistrationAdmin)
# admin.site.register(EnrolledPrograms, EnrolledProgramAdmin)
# admin.site.register(YouthAssessment, YouthAssessmentAdmin)
