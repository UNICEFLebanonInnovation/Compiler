# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals


from django.contrib import admin
from import_export import resources, fields
from import_export import fields
from import_export.admin import ImportExportModelAdmin

from .models import (
    School,
    Course,
    EducationLevel,
    ClassLevel,
    Grade,
    Section,
    ClassRoom,
    PartnerOrganization,
)


class schoolResource(resources.ModelResource):
    locationKazaa = fields.Field(column_name='District')
    locationGov = fields.Field(column_name='Governorate')

    class Meta:
        model = School
        fields = (
            'id',
            'name',
            'number',
            'locationGov',
            'locationKazaa'
        )
        export_order = ('id', 'name', 'number', 'locationGov', 'locationKazaa')

    def dehydrate_locationKazaa(self, school):
        return school.location.name

    def dehydrate_locationGov(self, school):
        return school.location.parent.name


class SchoolAdmin(ImportExportModelAdmin):
    resource_class = schoolResource
    list_display = ('name', 'number', 'location', )
    search_fields = ('name', 'number', )
    list_filter = ('location', )


class EducationLevelResource(resources.ModelResource):
    class Meta:
        model = EducationLevel
        fields = (
            'id',
            'name'
        )
        export_order = ('name',)


class EducationLevelAdmin(ImportExportModelAdmin):
    resource_class = EducationLevelResource


class ClassLevelResource(resources.ModelResource):
    class Meta:
        model = ClassLevel
        fields = (
            'id',
            'name'
        )
        export_order = ('name',)


class ClassLevelAdmin(ImportExportModelAdmin):
    resource_class = ClassLevelResource


class GradeResource(resources.ModelResource):
    class Meta:
        model = Grade
        fields = (
            'id',
            'name'
        )
        export_order = ('name',)


class GradeAdmin(ImportExportModelAdmin):
    resource_class = GradeResource


class SectionResource(resources.ModelResource):
    class Meta:
        model = Section
        fields = (
            'id',
            'name'
        )
        export_order = ('name',)


class SectionAdmin(ImportExportModelAdmin):
    resource_class = SectionResource


class ClassRoomResource(resources.ModelResource):
    class Meta:
        model = ClassRoom
        fields = (
            'id',
            'name',
        )
        export_order = ('id',)


class ClassRoomAdmin(ImportExportModelAdmin):
    resource_class = ClassRoomResource
    fields = (
        'name',
    )


class PartnerOrganizationResource(resources.ModelResource):
    class Meta:
        model = PartnerOrganization
        fields = (
            'id',
            'name'
        )
        export_order = ('name',)


class PartnerOrganizationAdmin(ImportExportModelAdmin):
    resource_class = PartnerOrganizationResource
    search_fields = ('name', )


admin.site.register(School, SchoolAdmin)
# admin.site.register(Course)
admin.site.register(EducationLevel, EducationLevelAdmin)
admin.site.register(ClassLevel, ClassLevelAdmin)
# admin.site.register(Grade, GradeAdmin)
admin.site.register(Section, SectionAdmin)
admin.site.register(ClassRoom, ClassRoomAdmin)
admin.site.register(PartnerOrganization, PartnerOrganizationAdmin)









