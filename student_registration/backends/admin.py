# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from django.contrib import admin
from django.urls import path
from django.db.models import Count
from django.template.response import TemplateResponse

from import_export import resources, fields
from import_export.admin import ImportExportModelAdmin
from .models import Exporter, Notification, ExportHistory, UserActivity, Metric
from student_registration.users.models import User
from student_registration.schools.models import School


class ExporterResource(resources.ModelResource):
    class Meta:
        model = Exporter


class ExporterAdmin(ImportExportModelAdmin):
    resource_class = ExporterResource
    list_display = (
        'name',
        'created',
        'file_url',
    )

    def get_export_formats(self):
        from student_registration.users.utils import get_default_export_formats
        return get_default_export_formats()


class NotificationResource(resources.ModelResource):
    class Meta:
        model = Notification
        fields = (
            'name',
            'description',
            'type',
            'status',
            # 'ticket',
            'school',
            'created',
        )
        export_order = fields


class NotificationAdmin(ImportExportModelAdmin):
    resource_class = NotificationResource
    filter_horizontal = ('schools', )
    list_display = (
        'name',
        'description',
        'type',
        'status',
        # 'ticket',
        'school',
        'created',
    )

    list_filter = (
        'type',
        'status',
        'school',
    )

    search_fields = (
        'name',
        'description',
    )

    def get_export_formats(self):
        from student_registration.users.utils import get_default_export_formats
        return get_default_export_formats()


class SchoolFilter(admin.SimpleListFilter):
    title = 'School'

    parameter_name = 'school'

    def lookups(self, request, model_admin):
        return ((l.id, l) for l in School.objects.all())

    def queryset(self, request, queryset):
        if self.value():
            emails = User.objects.filter(school_id=self.value()).values_list('email', flat=True)
            return queryset.filter(submitter_email__in=emails)
        return queryset


class SchoolCERDFilter(admin.SimpleListFilter):
    title = 'School CERD'

    parameter_name = 'school_cerd'

    def lookups(self, request, model_admin):
        return ((l.number, l.number) for l in School.objects.all())

    def queryset(self, request, queryset):
        if self.value():
            emails = User.objects.filter(school__number=self.value()).values_list('email', flat=True)
            return queryset.filter(submitter_email__in=emails)
        return queryset


class SchoolTypeFilter(admin.SimpleListFilter):
    title = 'School Type'

    parameter_name = 'school_type'

    def lookups(self, request, model_admin):
        return (('2ndshift', '2nd shift'),
                ('alp', 'ALP'))

    def queryset(self, request, queryset):
        if self.value() and self.value() == '2ndshift':
            emails = User.objects.filter(school__is_2nd_shift=True).values_list('email', flat=True)
            return queryset.filter(submitter_email__in=emails)
        if self.value() and self.value() == 'alp':
            emails = User.objects.filter(school__is_alp=True).values_list('email', flat=True)
            return queryset.filter(submitter_email__in=emails)
        return queryset


class ExportHistoryAdmin(admin.ModelAdmin):

    change_list_template = 'admin/export_history_change_list.html'

    list_display = (
        'export_type',
        'status',
        'created_by',
        'partner_name',
        'created',
        'modified',
    )
    list_filter = (
        'export_type',
        'partner_name',
    )
    search_fields = (
        'created_by__username',
    )
    list_select_related = ('created_by',)

    def get_urls(self):
        urls = super().get_urls()
        extra_urls = [
            path('dashboard/', self.admin_site.admin_view(self.dashboard_view), name='exporthistory_dashboard'),
        ]
        return extra_urls + urls

    def dashboard_view(self, request):
        queryset = ExportHistory.objects.all()

        export_stats = list(queryset.values('export_type').annotate(count=Count('id')).order_by('-count'))
        partner_stats = list(queryset.values('partner_name').annotate(count=Count('id')).order_by('-count'))

        context = dict(
            self.admin_site.each_context(request),
            title='Export History Dashboard',
            export_stats=export_stats,
            partner_stats=partner_stats,
            total=queryset.count(),
        )
        return TemplateResponse(request, 'admin/export_history_dashboard.html', context)


class UserActivityAdmin(admin.ModelAdmin):

    change_list_template = 'admin/user_activity_change_list.html'

    list_display = (
        'username',
        'path',
        'method',
        'data',
        'timestamp',
    )
    list_filter = (
        'method',
    )
    search_fields = (
        'username',
        'path'

    )

    def get_urls(self):
        urls = super().get_urls()
        extra_urls = [
            path('dashboard/', self.admin_site.admin_view(self.dashboard_view), name='useractivity_dashboard'),
        ]
        return extra_urls + urls

    def dashboard_view(self, request):
        queryset = UserActivity.objects.all()

        method_stats = list(queryset.values('method').annotate(count=Count('id')).order_by('-count'))
        top_paths = list(queryset.values('path').annotate(count=Count('id')).order_by('-count')[:10])

        context = dict(
            self.admin_site.each_context(request),
            title='User Activity Dashboard',
            method_stats=method_stats,
            top_paths=top_paths,
            total=queryset.count(),
        )
        return TemplateResponse(request, 'admin/user_activity_dashboard.html', context)


class MetricAdmin(admin.ModelAdmin):

    list_display = (
        'key',
        'label',
        'description',
        'sql_view',
        'value_column',
        'allowed_breakdowns',
        'allowed_filters',
        'default_time_column',
    )


admin.site.register(ExportHistory, ExportHistoryAdmin)
admin.site.register(UserActivity, UserActivityAdmin)
admin.site.register(Metric, MetricAdmin)
