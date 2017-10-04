# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from django.db import models
from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from rangefilter.filter import DateRangeFilter, DateTimeRangeFilter

from import_export.admin import ExportMixin
from import_export import resources, fields, widgets
from student_registration.alp.templatetags.util_tags import has_group
from student_registration.locations.models import Location
from .models import (
    School,
    Attendance,
    BySchoolByDay,
    Absentee,
    AttendanceSyncLog,
)


class SchoolFilter(admin.SimpleListFilter):
    # Human-readable title which will be displayed in the
    # right admin sidebar just above the filter options.
    title = 'School'

    # Parameter for the filter that will be used in the URL query.
    parameter_name = 'school'

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """
        if has_group(request.user, 'COORDINATOR'):
            return ((l.id, l.__unicode__()) for l in School.objects.filter(id__in=request.user.schools.all()))
        return ((l.id, l.__unicode__()) for l in School.objects.all())

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """
        if self.value():
            return queryset.filter(school_id=self.value())
        return queryset


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


class LocationFilter(admin.SimpleListFilter):
    # Human-readable title which will be displayed in the
    # right admin sidebar just above the filter options.
    title = 'District'

    # Parameter for the filter that will be used in the URL query.
    parameter_name = 'district'

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """
        schools = School.objects.all()
        if has_group(request.user, 'COORDINATOR'):
            schools = schools.filter(id__in=request.user.schools.all())
        return set((l.location_id, l.location.name if l.location else '') for l in schools)

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """
        if self.value():
            return queryset.filter(school__location_id=self.value())
        return queryset


class SchoolTypeFilter(admin.SimpleListFilter):
    # Human-readable title which will be displayed in the
    # right admin sidebar just above the filter options.
    title = 'School type'

    # Parameter for the filter that will be used in the URL query.
    parameter_name = 'school_type'

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """
        return (
            ('alp', 'ALP'),
            ('2ndshift', '2nd-shift')
        )

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """
        if not self.value():
            return queryset
        if self.value() == 'alp':
            return queryset.filter(school__is_alp=True)
        if self.value() == '2ndshift':
            return queryset.filter(school__is_2nd_shift=True)
        return queryset


class BySchoolResource(resources.ModelResource):
    governorate = fields.Field(
        column_name='governorate',
        attribute='school',
        widget=widgets.ForeignKeyWidget(School, 'location_parent_name')
    )
    district = fields.Field(
        column_name='district',
        attribute='school',
        widget=widgets.ForeignKeyWidget(School, 'location_name')
    )

    class Meta:
        model = BySchoolByDay
        fields = (
            'school__number',
            'school__name',
            'governorate',
            'district',
            'attendance_date',
            'total_enrolled',
            'total_attended',
            'total_attended_male',
            'total_attended_female',
            'total_absent_male',
            'total_absent_female',
            'validation_date',
        )


class BySchoolByDayAdmin(ExportMixin, admin.ModelAdmin):
    resource_class = BySchoolResource
    list_display = (
        'school',
        'district',
        'attendance_date',
        'total_enrolled',
        'total_attended',
        'total_absences',
        'highest_attendance_rate',
        'total_attended_male',
        'total_attended_female',
        'total_absent_male',
        'total_absent_female',
        'validation_date',
        'validation_status',
    )
    list_filter = (
        ('attendance_date', DateRangeFilter),
        LocationFilter,
        GovernorateFilter,
        SchoolFilter,
        SchoolTypeFilter,
        # 'attendance_date',
        'validation_date',
        'validation_status',
        'highest_attendance_rate',
    )
    date_hierarchy = 'attendance_date'
    ordering = ('-attendance_date',)

    class Media:
        css = {
            "all": ("css/admin.css",)
        }

    def district(self, obj):
        if obj.school and obj.school.location:
            return obj.school.location.name
        return ''

    def get_queryset(self, request):
        qs = super(BySchoolByDayAdmin, self).get_queryset(request)
        if has_group(request.user, 'COORDINATOR'):
            return qs.filter(school_id__in=request.user.schools.all())

        return qs

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        if has_group(request.user, 'COORDINATOR') or has_group(request.user, 'PMU'):
            return False
        return True


class AbsenteeResource(resources.ModelResource):
    governorate = fields.Field(
        column_name='governorate',
        attribute='school',
        widget=widgets.ForeignKeyWidget(School, 'location_parent_name')
    )
    district = fields.Field(
        column_name='district',
        attribute='school',
        widget=widgets.ForeignKeyWidget(School, 'location_name')
    )

    class Meta:
        model = Absentee
        fields = (
            'school__number',
            'school__name',
            'governorate',
            'district',
            'student__number',
            'student__first_name',
            'student__father_name',
            'student__last_name',
            'student__mother_fullname',
            'student__sex',
            'last_attendance_date',
            'absent_days',
            'reattend_date',
            'validation_status',
            'dropout_status',
        )
        export_order = fields


class AbsenteeAdmin(ExportMixin, admin.ModelAdmin):
    resource_class = AbsenteeResource
    list_display = (
        'school',
        'student_number',
        'district',
        'student',
        'last_attendance_date',
        'absent_days',
        'reattend_date',
        'validation_status',
        'dropout_status',
    )
    list_filter = (
        # 'school__location',
        # 'school',
        SchoolFilter,
        SchoolTypeFilter,
        LocationFilter,
        GovernorateFilter,
        'last_attendance_date',
        'validation_status',
        'dropout_status',
    )
    date_hierarchy = 'last_attendance_date'
    ordering = ('-absent_days',)

    actions = ('validate_absentees', 'dropout')

    def get_queryset(self, request):
        qs = super(AbsenteeAdmin, self).get_queryset(request)
        if has_group(request.user, 'COORDINATOR'):
            return qs.filter(school_id__in=request.user.schools.all())

        return qs

    def district(self, obj):
        if obj.school and obj.school.location:
            return obj.school.location.name
        return ''

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        if has_group(request.user, 'COORDINATOR') or has_group(request.user, 'PMU'):
            return False
        return True

    def has_validate_absentees_permission(self, request):
        if has_group(request.user, 'COORDINATOR') or has_group(request.user, 'PMU'):
            return False
        return True

    def validate_absentees(self, request, queryset):
        queryset.update(validation_status=True)

    def has_dropout_permission(self, request):
        if has_group(request.user, 'COORDINATOR') or has_group(request.user, 'PMU'):
            return False
        return True

    def dropout(self, request, queryset):
        queryset.update(dropout_status=True)
        for obj in queryset:
            student = obj.student
            enrollment = student.student_enrollment.first()
            if enrollment:
                enrollment.dropout_status = True
                enrollment.save()


class AttendanceSyncLogResource(resources.ModelResource):
    class Meta:
        model = AttendanceSyncLog
        fields = (
            'school__number',
            'school__name',
            'school_type',
            'total_records',
            'successful',
            'response_message',
            'processed_date',
            'processed_by'
        )
        export_order = fields


class AttendanceSyncLogAdmin(ImportExportModelAdmin):
    resource_class = AttendanceSyncLogResource
    list_display = (
        'school',
        'school_type',
        'total_records',
        'successful',
        'response_message',
        'processed_date',
        'processed_by'
    )
    list_filter = (
        'school',
        SchoolTypeFilter,
        'school_type',
        'successful',
    )


class AttendanceResource(resources.ModelResource):
    class Meta:
        model = Attendance
        fields = ()
        export_order = fields


class AttendanceAdmin(ImportExportModelAdmin):
    resource_class = AttendanceResource
    fields = (
        'school',
        'attendance_date',
        'validation_status',
        'validation_date',
        'validation_owner',
        'close_reason',
        'students',
        'owner',
    )
    list_display = (
        'id',
        'school',
    )
    list_filter = (
        'school',
    )

admin.site.register(Attendance, AttendanceAdmin)
# admin.site.register(BySchoolByDay, BySchoolByDayAdmin)
admin.site.register(Absentee, AbsenteeAdmin)
# admin.site.register(AttendanceSyncLog, AttendanceSyncLogAdmin)
