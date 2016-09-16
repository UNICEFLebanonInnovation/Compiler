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
    class Meta:
        model = School
        fields = (
            'name',
            'number',
            'location',
        )
        export_order = ('name', )


class SchoolAdmin(ImportExportModelAdmin):
    resource_class = schoolResource



admin.site.register(School, SchoolAdmin)
# admin.site.register(Course)
admin.site.register(EducationLevel)
admin.site.register(ClassLevel)
admin.site.register(Grade)
admin.site.register(Section)
admin.site.register(ClassRoom)
admin.site.register(PartnerOrganization)









