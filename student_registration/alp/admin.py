# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from django.contrib import admin
from import_export import resources, fields
from import_export import fields
from import_export.admin import ImportExportModelAdmin
from import_export.widgets import *
from .forms import OutreachForm
from .models import (
    Outreach,
    ALPRound,
)
from student_registration.schools.models import (
    School,
)
from student_registration.locations.models import Location


class OutreachResource(resources.ModelResource):
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
        model = Outreach
        fields = ('id', 'student__id', 'student__id_number', 'student__number', 'student__first_name',
                  'student__father_name', 'student__last_name', 'student__mother_fullname',
                  'student__age', 'student__sex',
                  'governorate', 'district', 'school__name', 'level__name', 'exam_total',
                  'assigned_to_level__name', 'registered_in_level__name', 'section__name',
                  'not_enrolled_in_this_school',
                  )
        export_order = ('id', 'student__id', 'student__id_number', 'student__number', 'student__first_name',
                        'student__father_name', 'student__last_name', 'student__mother_fullname',
                        'student__age', 'student__sex', 'governorate', 'district', 'school__name', 'level__name',
                        'assigned_to_level__name', 'registered_in_level__name', 'section__name',
                        'not_enrolled_in_this_school',
                        )


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


class RegisteredInLevelFilter(admin.SimpleListFilter):
    # Human-readable title which will be displayed in the
    # right admin sidebar just above the filter options.
    title = 'Registered in level'

    # Parameter for the filter that will be used in the URL query.
    parameter_name = 'registered_level'

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """
        return (
            ('yes', 'Yes'),
            ('no', 'No')
        )

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """
        if self.value() and self.value() == 'yes':
            return queryset.filter(registered_in_level__isnull=False)
        if self.value() and self.value() == 'no':
            return queryset.filter(registered_in_level__isnull=True)
        return queryset


class RegisteredInSectionFilter(admin.SimpleListFilter):
    # Human-readable title which will be displayed in the
    # right admin sidebar just above the filter options.
    title = 'Registered in section'

    # Parameter for the filter that will be used in the URL query.
    parameter_name = 'registered_section'

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """
        return (
            ('yes', 'Yes'),
            ('no', 'No')
        )

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """
        if self.value() and self.value() == 'yes':
            return queryset.filter(section__isnull=False)
        if self.value() and self.value() == 'no':
            return queryset.filter(section__isnull=True)
        return queryset


class OutreachAdmin(ImportExportModelAdmin):
    resource_class = OutreachResource
    form = OutreachForm
    list_display = (
        'student', 'student_age', 'school', 'caza', 'governorate',
        'level', 'total', 'assigned_to_level', 'registered_in_level',
        'section', 'registered_in_school', 'not_enrolled_in_this_school'
    )
    list_filter = ('school__number', 'school', 'school__location', GovernorateFilter,
                   'level', 'assigned_to_level', 'registered_in_level',
                   'section', 'student__sex', 'not_enrolled_in_this_school',
                   RegisteredInLevelFilter, RegisteredInSectionFilter, )
    search_fields = (
        'student__first_name', 'student__father_name', 'student__last_name', 'student__mother_fullname',
        'school__name', 'school__number', 'student__id_number', 'school__location__name', 'level__name',
        'owner__username'
    )

    def get_queryset(self, request):
        qs = super(OutreachAdmin, self).get_queryset(request)
        return qs.exclude(deleted=True)

    def caza(self, obj):
        if obj.school and obj.school.location:
            return obj.school.location.name
        return ''

    def governorate(self, obj):
        if obj.school and obj.school.location and obj.school.location.parent:
            return obj.school.location.parent.name
        return ''

    def total(self, obj):
        total = obj.exam_total
        if obj.level and obj.level.note:
            total = u'{}/{}'.format(
                str(total),
                str(obj.level.note)
            )
        return total

admin.site.register(Outreach, OutreachAdmin)
admin.site.register(ALPRound)
