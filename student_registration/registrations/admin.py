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
    School
)


class RegisteringAdultResource(resources.ModelResource):
    number = fields.Field(column_name='CaseNumber', attribute='number')
    name = fields.Field(column_name='BeneficiaryNameAr')
    phone = fields.Field(column_name='PhoneNumber', attribute='phone')
    dob = fields.Field(column_name='DOB')
    sex = fields.Field(column_name='Gender', attribute='sex')
    registrationdate = fields.Field(column_name='Registration Date', attribute='created')
    locationKazaa = fields.Field(column_name='District')
    locationGov = fields.Field(column_name='Governorate')
    family_size = fields.Field(column_name='Family Size',  attribute='family_size')
    distributionlist = fields.Field(column_name='WFP Distribution List')


    class Meta:
        model = RegisteringAdult
        fields = ('number','name', 'phone', 'dob','sex', 'registrationdate', 'locationKazaa', 'locationGov', 'family_size','distributionlist')
        export_order = ('number', 'locationGov', 'locationKazaa', 'phone', 'name',  'dob', 'sex', 'registrationdate', 'family_size','distributionlist')

    def dehydrate_name(self, registeringadult):
        return '%s %s' % (registeringadult.first_name, registeringadult.last_name)

    def dehydrate_dob(self, registeringadult):
        return '%s-%s-%s' % (registeringadult.birthday_year, registeringadult.birthday_month, registeringadult.birthday_day)

    def dehydrate_locationKazaa(self, registeringadult):
        return registeringadult.school.location.name

    def dehydrate_locationGov(self, registeringadult):
        return registeringadult.school.location.parent.name

    def dehydrate_family_size(self, registeringadult):
        return len(registeringadult.children.all())

    def dehydrate_distributionlist(self, registeringadult):
        return registeringadult.school.location.distribution_list


class RegisteringAdultAdmin(ImportExportModelAdmin):
    resource_class = RegisteringAdultResource
    list_display = ('first_name', 'father_name', 'last_name','phone')
    search_fields = ('first_name', 'father_name', 'last_name','phone')


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
            fields = ('relation_to_adult', 'enrolled_last_year', 'enrolled_last_year_school', 'enrolled_last_year_location','section','grade','classroom','year','owner','status','out_of_school_two_years','related_to_family')
            export_order = ('studentFname','studentFaName','studentLname', 'registering_adult_fname', 'registering_adult_faname', 'registering_adult_lname', 'mother', 'relation_to_adult', 'enrolled_last_year', 'enrolled_last_year_school', 'enrolled_last_year_location', 'section', 'grade', 'classroom', 'year', 'owner', 'status','out_of_school_two_years', 'related_to_family')


class RegistrationAdmin(ImportExportModelAdmin):
    resource_class = RegistrationResource
    list_display = ('student', 'registering_adult', 'relation_to_adult', 'enrolled_last_year', 'enrolled_last_year_school','enrolled_last_year_location', 'school','section','grade','classroom','year','owner','status','out_of_school_two_years','related_to_family')


admin.site.register(Registration, RegistrationAdmin)
admin.site.register(RegisteringAdult, RegisteringAdultAdmin)
