# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from django.contrib import admin
from import_export import resources, fields
from import_export import fields
from import_export.admin import ImportExportModelAdmin
from import_export.widgets import *

from .models import Enrollment
from student_registration.students.models import Student
from student_registration.schools.models import (
    School,
    ClassRoom,
    EducationLevel,
    ClassRoom,
    Section,
)
from student_registration.locations.models import Location


class EnrollmentResource(resources.ModelResource):
    governorate = fields.Field(
        column_name='governorate',
        attribute='school',
        widget=ForeignKeyWidget(School, 'location_parent_name')
    )
    district = fields.Field(
        column_name='district',
        attribute='school',
        widget=ForeignKeyWidget(School, 'location_name')
    )

    class Meta:
        model = Enrollment
        fields = ('student__first_name', 'student__father_name', 'student__last_name', 'student__mother_fullname',
                  'student__age', 'governorate', 'district', 'school__name', 'section__name', 'classroom__name')
        export_order = ('student__first_name', 'student__father_name', 'student__last_name', 'student__mother_fullname',
                        'student__age', 'governorate', 'district', 'school__name', 'section__name', 'classroom__name')


class GovernorateFilter(admin.SimpleListFilter):
    # Human-readable title which will be displayed in the
    # right admin sidebar just above the filter options.
    title = 'Governorate'

    # Parameter for the filter that will be used in the URL query.
    parameter_name = 'governorate'

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """
        return ((l.id, l.name) for l in Location.objects.filter(type_id=1))

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """
        if self.value():
            return queryset.filter(school__location__parent_id=self.value())
        return queryset


class EnrollmentAdmin(ImportExportModelAdmin):
    resource_class = EnrollmentResource
    list_display = (
        'student', 'student_age', 'school', 'caza', 'governorate',
        'classroom', 'section',
    )
    list_filter = ('classroom', 'school', 'school__location', GovernorateFilter)
    search_fields = (
        'student__first_name', 'student__father_name', 'student__last_name', 'student__mother_fullname',
        'school__name', 'school__number', 'student__id_number', 'school__location__name', 'classroom__name',
        'owner__username'
    )

    def caza(self, obj):
        if obj.school and obj.school.location:
            return obj.school.location.name
        return ''

    def governorate(self, obj):
        if obj.school and obj.school.location and obj.school.location.parent:
            return obj.school.location.parent.name
        return ''


admin.site.register(Enrollment, EnrollmentAdmin)
