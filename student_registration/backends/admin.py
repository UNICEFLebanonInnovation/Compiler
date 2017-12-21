# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from django.contrib import admin
from django.utils.html import escape, format_html, format_html_join, html_safe
from django.utils.encoding import force_text

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


class TicketSchoolResource(resources.ModelResource):
    queue_name = fields.Field(column_name='Category')
    owner_name = fields.Field(column_name='User')
    school_cerd = fields.Field(column_name='School CERD')
    school_name = fields.Field(column_name='School')
    is_2nd_shift = fields.Field(column_name='is 2nd-shift')
    is_alp = fields.Field(column_name='is ALP')
    comments = fields.Field(column_name='Comments')
    status_name = fields.Field(column_name='Status')
    priority_name = fields.Field(column_name='Priority')

    class Meta:
        model = Ticket
        fields = (
            'id',
            'school_cerd',
            'school_name',
            'owner_name',
            'submitter_email',
            'is_2nd_shift',
            'is_alp',
            'queue_name',
            'title',
            'description',
            'comments',
            'priority_name',
            'created',
            'status_name',
        )
        export_order = fields

    def dehydrate_queue_name(self, obj):
        return obj.queue.title

    def dehydrate_owner(self, obj):
        if obj.submitter_email:
            return User.objects.get(email=obj.submitter_email)
        return ''

    def dehydrate_owner_name(self, obj):
        if obj.submitter_email:
            return self.dehydrate_owner(obj).username
        return ''

    def dehydrate_school(self, obj):
        if self.dehydrate_owner(obj):
            return self.dehydrate_owner(obj).school
        return ''

    def dehydrate_school_name(self, obj):
        if self.dehydrate_school(obj):
            return self.dehydrate_school(obj).name
        return ''

    def dehydrate_school_cerd(self, obj):
        if self.dehydrate_school(obj):
            return self.dehydrate_school(obj).number
        return ''

    def dehydrate_is_2nd_shift(self, obj):
        if self.dehydrate_school(obj):
            return self.dehydrate_school(obj).is_2nd_shift
        return False

    def dehydrate_is_alp(self, obj):
        if self.dehydrate_school(obj):
            return self.dehydrate_school(obj).is_alp
        return False

    def dehydrate_comments(self, obj):
        if obj.followup_set:
            return '\r\n'.join([f.comment for f in obj.followup_set.all()])
        return ''

    def dehydrate_status_name(self, obj):
        if obj.status:
            return force_text(dict(Ticket.STATUS_CHOICES)[obj.status])
        return ''

    def dehydrate_priority_name(self, obj):
        if obj.priority:
            return force_text(dict(Ticket.PRIORITY_CHOICES)[obj.priority])
        return ''


class TicketSchoolAdmin(ImportExportModelAdmin):
    resource_class = TicketSchoolResource
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
        'id_link',
        'queue',
        'owner_link',
        'submitter_email',
        'school_cerd',
        'school_link',
        'title',
        'description',
        'comments',
        'is_2nd_shift',
        'is_alp',
        'priority',
        'created',
        'status',
        'edit_link'
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

    def owner_link(self, obj):
        if self.owner(obj):
            return '<a href="/admin/users/user/%s/change/" target="_blank">%s</a>' % \
                   (self.owner(obj).id, escape(self.owner(obj).username))
        return ''

    owner_link.allow_tags = True
    owner_link.short_description = "Submitter username"

    def id_link(self, obj):
        return '<a href="/helpdesk/tickets/%s/" target="_blank">%s</a>' % (obj.id, escape(obj.id))

    id_link.allow_tags = True
    id_link.short_description = "ID"

    def edit_link(self, obj):
        return '<a href="/helpdesk/tickets/%s/edit/" target="_blank">%s</a>' % (obj.id, escape('Edit'))

    edit_link.allow_tags = True
    edit_link.short_description = "Edit"

    def submitter(self, obj):
        if self.owner(obj):
            return self.owner(obj).username
        return ''

    def school(self, obj):
        if self.owner(obj):
            return self.owner(obj).school
        return ''

    def school_link(self, obj):
        if self.school(obj):
            return '<a href="/admin/schools/school/%s/change/" target="_blank">%s</a>' % \
                   (self.school(obj).id, escape(self.school(obj).name))
        return ''

    school_link.allow_tags = True
    school_link.short_description = "School"

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

    def comments(self, obj):
        if obj.followup_set:
            return '\r\n'.join([f.comment for f in obj.followup_set.all()])
        return ''

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
