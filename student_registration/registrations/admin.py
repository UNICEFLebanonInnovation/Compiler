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
    nationality_code = fields.Field(column_name='Country Of Origin Code')

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
            'nationality_code',
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
            'nationality_code',
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

    def dehydrate_distribution_site(self, registeringadult):
        return registeringadult.wfp_distribution_site.code

    def dehydrate_nationality_code(self, registeringadult):
        return registeringadult.nationality.code


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
        u'number',
        u'id_number',
        u'first_name',
        u'father_name',
        u'last_name',
        u'primary_phone'
    )
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
        column_name='Adult First Name',
        attribute='registering_adult',
        widget=ForeignKeyWidget(RegisteringAdult, 'first_name')
    )
    registering_adult_faname = fields.Field(
        column_name='Adult Father Name',
        attribute='registering_adult',
        widget=ForeignKeyWidget(RegisteringAdult, 'father_name')
    )
    registering_adult_lname = fields.Field(
        column_name='Adult last Name',
        attribute='registering_adult',
        widget=ForeignKeyWidget(RegisteringAdult, 'last_name')
    )
    primary_phone = fields.Field(
        column_name='Primary Phone',
        attribute='registering_adult',
        widget=ForeignKeyWidget(RegisteringAdult, 'primary_phone')
    )
    secondary_phone = fields.Field(
        column_name='Secondary Phone',
        attribute='registering_adult',
        widget=ForeignKeyWidget(RegisteringAdult, 'secondary_phone')
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
    id_number = fields.Field(
        column_name='ID Number',
        attribute='student',
        widget=ForeignKeyWidget(Student, 'id_number')
    )

    class Meta:
        model = Registration
        fields = ('relation_to_adult', 'enrolled_last_year', 'enrolled_last_year_school', 'enrolled_last_year_location',
                  'section', 'grade', 'classroom', 'year', 'owner', 'status', 'out_of_school_two_years',
                  'related_to_family', 'primary_phone', 'secondary_phone')
        export_order = (
            'id_number','studentFname', 'studentFaName', 'studentLname', 'registering_adult_fname', 'registering_adult_faname',
            'registering_adult_lname', 'mother', 'relation_to_adult', 'enrolled_last_year', 'enrolled_last_year_school',
            'enrolled_last_year_location', 'section', 'grade', 'classroom', 'year', 'owner', 'status',
            'out_of_school_two_years', 'related_to_family', 'primary_phone', 'secondary_phone')


class RegistrationAdmin(ImportExportModelAdmin):
    resource_class = RegistrationResource
    list_display = (
        'student', 'registering_adult', 'relation_to_adult', 'enrolled_last_year', 'enrolled_last_year_school',
        'enrolled_last_year_location', 'school', 'section', 'grade', 'classroom', 'year', 'owner', 'status',
        'out_of_school_two_years', 'related_to_family')
    search_fields = (
        'student__first_name', 'registering_adult__first_name', 'relation_to_adult', 'enrolled_last_year',
        'enrolled_last_year_school__name', 'enrolled_last_year_location__name', 'school__name', 'section__name',
        'classroom__name', 'year', 'owner__username', 'status', 'out_of_school_two_years', 'related_to_family',
        'student__id_number',
    )
    list_filter = ('enrolled_last_year', 'status', 'school')


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
admin.site.register(Registration, RegistrationAdmin)
admin.site.register(RegisteringAdult, RegisteringAdultAdmin)
admin.site.register(WFPDistributionSite, WFPSiteAdmin)
