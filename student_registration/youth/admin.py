# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from django.contrib import admin
from import_export import resources, fields
from import_export import fields
from import_export.admin import ImportExportModelAdmin
from django import forms
from .models import *


class RegistrationAdmin(admin.ModelAdmin):

    list_display = (
        'adolescent',
        'partner',
        'center',
        'created',
        'modified',
    )
    list_filter = (
        'adolescent__mother_fullname',
        'adolescent__gender',
        'adolescent__nationality',
        'partner',
        'center',
        'created',
        'modified',
    )
    search_fields = (
        'adolescent__first_name',
        'adolescent__father_name',
        'adolescent__last_name',
    )


class EducationServiceAdmin(admin.ModelAdmin):
    list_display = (
        'registration',
        'education_status',
        'dropout_date',
    )
    list_filter = (
        'education_status',

    )
    search_fields = (
        'registration__adolescent__first_name',
        'registration__adolescent__father_name',
        'registration__adolescent__last_name',
    )


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



class ProgramAdmin(admin.ModelAdmin):
    list_display = ('name', 'active')
    search_fields = ('name',)


admin.site.register(Partner)
admin.site.register(FundedBy)
admin.site.register(FocalPoint)
admin.site.register(Plan)
admin.site.register(Sector)
admin.site.register(ProjectType)
admin.site.register(PopulationGroups)

admin.site.register(Program, ProgramAdmin)
admin.site.register(SubProgram)
admin.site.register(Donor)
admin.site.register(YouthAssessment)
admin.site.register(ProgramDocument, ProgramDocumentAdmin)
admin.site.register(Registration, RegistrationAdmin)
# admin.site.register(YouthAssessment, YouthAssessmentAdmin)
