# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals


from django.contrib import admin
from django.utils.html import escape, format_html, format_html_join, html_safe
from django.utils.safestring import mark_safe

from import_export import resources, fields
from import_export import fields
from import_export.admin import ImportExportModelAdmin
from helpdesk.models import Ticket
from .models import Exporter
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
                ('alp', 'ALP'),
                )

    def queryset(self, request, queryset):
        if self.value() and self.value() == '2ndshift':
            emails = User.objects.filter(school__is_2nd_shift=True).values_list('email', flat=True)
            return queryset.filter(submitter_email__in=emails)
        if self.value() and self.value() == 'alp':
            emails = User.objects.filter(school__is_alp=True).values_list('email', flat=True)
            return queryset.filter(submitter_email__in=emails)
        return queryset


class TicketSchoolAdmin(admin.ModelAdmin):

    fields = (
        'queue',
        'title',
        'description',
        'submitter_email',
        'status',
        'created',
        'priority',
    )
    list_display = (
        'id',
        'queue',
        'title',
        'description',
        'owner',
        'school_cerd',
        'school',
        'is_2nd_shift',
        'is_alp',
        'priority',
        'submitter',
        'created',
        'status',
    )
    list_editable = ('status',)
    list_filter = (
        'queue',
        'status',
        'priority',
        SchoolFilter,
        SchoolCERDFilter,
        SchoolTypeFilter,
    )
    date_hierarchy = 'created'
    view_on_site = False

    def owner(self, obj):
        if obj.submitter_email:
            return User.objects.get(email=obj.submitter_email)
        return ''

    def submitter(self, obj):
        if self.owner(obj):
            return self.owner(obj).username
        return ''

    def school(self, obj):
        if self.owner(obj):
            return self.owner(obj).school
        return ''

    def school_cerd(self, obj):
        if self.school(obj):
            return self.school(obj).number
        return ''

    def is_2nd_shift(self, obj):
        if self.school(obj):
            return self.school(obj).is_2nd_shift
        return False

    def is_alp(self, obj):
        if self.school(obj):
            return self.school(obj).is_alp
        return False

    # def is_2nd_shift(self, obj):
    #     result = False
    #     html_icon = '<i class="{} icon"></i>'
    #     if self.school(obj):
    #         result = self.school(obj).is_2nd_shift
    #     if result:
    #         return format_html(html_icon, mark_safe('check green'))
    #     return format_html(html_icon, mark_safe('remove red'))
    #
    # def is_alp(self, obj):
    #     result = False
    #     html_icon = '<i class="{} icon"></i>'
    #     if self.school(obj):
    #         result = self.school(obj).is_alp
    #     if result:
    #         return format_html(html_icon, mark_safe('check green'))
    #     return format_html(html_icon, mark_safe('remove red'))

admin.site.register(Exporter, ExporterAdmin)
admin.site.unregister(Ticket)
admin.site.register(Ticket, TicketSchoolAdmin)
