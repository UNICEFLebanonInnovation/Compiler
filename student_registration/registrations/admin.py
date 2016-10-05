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
)


class WFPSiteAdmin(admin.ModelAdmin):

    filter_horizontal = ('location',)


class RegisteredChildInline(admin.TabularInline):
    model = Registration
    extra = 0


class RegisteringAdultResource(resources.ModelResource):
    """
    Export the HH registrations to the following format:
    CaseNumber
    Governorate
    District
    Village
    WFP Distribution Point
    PhoneNumber
    BeneficiaryNameAr
    DOB
    Gender
    MarriageStatus
    RegistrationDate
    FamilySize
    # of Individuals to be assisted
    OriginCountryCode
    """
    number = fields.Field(column_name='CaseNumber', attribute='case_number')
    location_gov = fields.Field(column_name='Governorate')
    location_district = fields.Field(column_name='District')
    distribution_site = fields.Field(column_name='WFP Distribution Point')
    phone = fields.Field(column_name='PhoneNumber', attribute='primary_phone')
    name = fields.Field(column_name='BeneficiaryNameAr')
    dob = fields.Field(column_name='DOB')
    sex = fields.Field(column_name='Gender', attribute='sex')
    registration_date = fields.Field(column_name='Registration Date', attribute='created')
    family_size = fields.Field(column_name='Family Size', attribute='family_size')

    class Meta:
        model = RegisteringAdult
        fields = (
            'number',
            'location_gov',
            'location_district',
            'distribution_site',
            'phone',
            'name',
            'dob',
            'sex',
            'registration_date',
            'family_size',
        )
        export_order = (
            'number',
            'location_gov',
            'location_district',
            'distribution_site',
            'phone',
            'name',
            'dob',
            'sex',
            'registration_date',
            'family_size',
        )

    def dehydrate_name(self, registeringadult):
        return '%s %s' % (registeringadult.first_name, registeringadult.last_name)

    def dehydrate_dob(self, registeringadult):
        return '%s-%s-%s' % (
            registeringadult.birthday_year, registeringadult.birthday_month, registeringadult.birthday_day)

    def dehydrate_location_district(self, registeringadult):
        return registeringadult.school.location.name if registeringadult.school else ''

    def dehydrate_location_gov(self, registeringadult):
        return registeringadult.school.location.parent.name if registeringadult.school else ''

    def dehydrate_family_size(self, registeringadult):
        return registeringadult.children.count()

    def dehydrate_distribution_list(self, registeringadult):
        return registeringadult.wfp_distribution_site.code


class RegisteringAdultAdmin(ImportExportModelAdmin):
    resource_class = RegisteringAdultResource
    list_display = (
        'case_number',
        'id_type',
        'nationality',
        'first_name',
        'father_name',
        'last_name',
        'primary_phone',
        'school',
    )
    list_filter = (
        'id_type',
        'nationality',
        'school',
    )
    search_fields = (
        'number',
        'id_number',
        'first_name',
        'father_name',
        'last_name',
        'primary_phone')
    inlines = (RegisteredChildInline,)

    def assign_distribution_site(self, request, queryset):
        for adult in queryset:
            site = WFPDistributionSite.objects.filter(location__in=[adult.school.location]).first()
            adult.wfp_distribution_site = site
            adult.save()

    assign_distribution_site.short_description = "Assign WFP Distribution site to Adult"

    actions = ('assign_distribution_site',)


class RegistrationResource(resources.ModelResource):
    registering_adult_fname = fields.Field(
        column_name='Registering Adult First Name',
        attribute='registering_adult',
        widget=ForeignKeyWidget(RegisteringAdult, 'first_name')
    )
    registering_adult_faname = fields.Field(
        column_name='Registering Adult Father Name',
        attribute='registering_adult',
        widget=ForeignKeyWidget(RegisteringAdult, 'father_name')
    )
    registering_adult_lname = fields.Field(
        column_name='Registering Adult last Name',
        attribute='registering_adult',
        widget=ForeignKeyWidget(RegisteringAdult, 'last_name')
    )
    enrolled_last_year_location = fields.Field(
        column_name='Location',
        attribute='enrolled_last_year_location',
        widget=ForeignKeyWidget(Location, 'name')
    )
    enrolled_last_year_school = fields.Field(
        column_name='Last Year School',
        attribute='enrolled_last_year_school',
        widget=ForeignKeyWidget(School, 'name')
    )
    studentFname = fields.Field(
        column_name='Student First Name',
        attribute='student',
        widget=ForeignKeyWidget(Student, 'first_name')
    )
    studentFaName = fields.Field(
        column_name='Student Father Name',
        attribute='student',
        widget=ForeignKeyWidget(Student, 'father_name')
    )
    studentLname = fields.Field(
        column_name='Student Last Name',
        attribute='student',
        widget=ForeignKeyWidget(Student, 'last_name')
    )
    relation_to_adult = fields.Field(
        column_name='Relation To Adult',
        attribute='relation_to_adult'
    )
    enrolled_last_year = fields.Field(
        column_name='Enrolled Last Year',
        attribute='enrolled_last_year'
    )
    section = fields.Field(
        column_name='Section',
        attribute='section',
        widget=ForeignKeyWidget(Student, 'name')
    )
    grade = fields.Field(
        column_name='Grade',
        attribute='grade',
        widget=ForeignKeyWidget(Student, 'name')
    )
    classroom = fields.Field(
        column_name='Classroom',
        attribute='classroom',
        widget=ForeignKeyWidget(Student, 'name')
    )
    year = fields.Field(
        column_name='Year',
        attribute='year'
    )
    owner = fields.Field(
        column_name='Owner',
        attribute='owner'
    )
    status = fields.Field(
        column_name='Status',
        attribute='status'
    )
    out_of_school_two_years = fields.Field(
        column_name='Out Of School for Two Years',
        attribute='out_of_school_two_years'
    )
    related_to_family = fields.Field(
        column_name='Related To Family',
        attribute='related_to_family'
    )
    mother = fields.Field(
        column_name='Student Mother Name',
        attribute='student',
        widget=ForeignKeyWidget(Student, 'mother_fullname')
    )

    class Meta:
        model = Registration
        fields = ('relation_to_adult', 'enrolled_last_year', 'enrolled_last_year_school', 'enrolled_last_year_location',
                  'section', 'grade', 'classroom', 'year', 'owner', 'status', 'out_of_school_two_years',
                  'related_to_family')
        export_order = (
            'studentFname', 'studentFaName', 'studentLname', 'registering_adult_fname', 'registering_adult_faname',
            'registering_adult_lname', 'mother', 'relation_to_adult', 'enrolled_last_year', 'enrolled_last_year_school',
            'enrolled_last_year_location', 'section', 'grade', 'classroom', 'year', 'owner', 'status',
            'out_of_school_two_years', 'related_to_family')


class RegistrationAdmin(ImportExportModelAdmin):
    resource_class = RegistrationResource
    list_display = (
        'student', 'registering_adult', 'relation_to_adult', 'enrolled_last_year', 'enrolled_last_year_school',
        'enrolled_last_year_location', 'school', 'section', 'grade', 'classroom', 'year', 'owner', 'status',
        'out_of_school_two_years', 'related_to_family')
    search_fields = (
        'student', 'registering_adult', 'relation_to_adult', 'enrolled_last_year', 'enrolled_last_year_school',
        'enrolled_last_year_location', 'school', 'section', 'grade', 'classroom', 'year', 'owner', 'status',
        'out_of_school_two_years', 'related_to_family')
    list_filter = ('enrolled_last_year', 'status', 'school')


admin.site.register(Registration, RegistrationAdmin)
admin.site.register(RegisteringAdult, RegisteringAdultAdmin)
admin.site.register(WFPDistributionSite, WFPSiteAdmin)
