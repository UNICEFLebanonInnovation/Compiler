# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals


from django.contrib import admin
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
        if self.owner(obj) and self.owner(obj).school:
            return self.owner(obj).school.number
        return ''


admin.site.register(Exporter, ExporterAdmin)
admin.site.unregister(Ticket)
admin.site.register(Ticket, TicketSchoolAdmin)
