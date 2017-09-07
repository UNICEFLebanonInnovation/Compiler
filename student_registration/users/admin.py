# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from django.contrib import admin
from django.utils.translation import gettext, gettext_lazy as _
from django.contrib.auth.admin import UserAdmin as AuthUserAdmin
from django.contrib.auth.models import Group
from .models import User


class UserAdmin(AuthUserAdmin):

    filter_horizontal = ('groups', 'user_permissions', 'locations', 'schools')
    list_display = (
        'username',
        'first_name',
        'last_name',
        'is_active',
        'email',
        'school',
        'location',
        'phone_number',
    )
    search_fields = (
        u'username',
        u'school__name',
        u'location__name',
        u'first_name',
        u'last_name',
    )
    list_filter = (
        'groups',
        'school',
        'location',
        'is_active',
    )
    actions = (
        'activate',
        'disable',
        'allow_enroll_create',
        'allow_enroll_edit',
        'allow_enroll_grading',
        'allow_attendance',
        'deny_enroll_create',
        'deny_enroll_edit',
        'deny_enroll_grading',
        'deny_attendance',
    )

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser',
                                       'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
        (None, {'fields': ('partner', 'location', 'school', 'locations', 'schools')})
    )

    add_fieldsets = (
        (None, {'fields': ('username', 'password1', 'password2')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser',
                                       'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
        (None, {'fields': ('partner', 'location', 'school', 'locations', 'schools')})
    )

    def activate(self, request, queryset):
        queryset.update(is_active=True)

    def disable(self, request, queryset):
        queryset.update(is_active=False)
        return False

    def allow_enroll_create(self, request, queryset):
        group = Group.objects.get(name='ENROL_CREATE')
        for user in queryset:
            user.groups.add(group)

    def allow_enroll_edit(self, request, queryset):
        group = Group.objects.get(name='ENROL_EDIT')
        for user in queryset:
            user.groups.add(group)

    def allow_enroll_grading(self, request, queryset):
        group = Group.objects.get(name='ENROL_GRADING')
        for user in queryset:
            user.groups.add(group)

    def allow_attendance(self, request, queryset):
        group = Group.objects.get(name='ATTENDANCE')
        for user in queryset:
            user.groups.add(group)

    def deny_enroll_create(self, request, queryset):
        group = Group.objects.get(name='ENROL_CREATE')
        for user in queryset:
            user.groups.remove(group)

    def deny_enroll_edit(self, request, queryset):
        group = Group.objects.get(name='ENROL_EDIT')
        for user in queryset:
            user.groups.remove(group)

    def deny_enroll_grading(self, request, queryset):
        group = Group.objects.get(name='ENROL_GRADING')
        for user in queryset:
            user.groups.remove(group)

    def deny_attendance(self, request, queryset):
        group = Group.objects.get(name='ATTENDANCE')
        for user in queryset:
            user.groups.remove(group)

admin.site.register(User, UserAdmin)


