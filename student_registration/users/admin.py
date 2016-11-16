# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as AuthUserAdmin
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from import_export import resources, fields
from import_export import fields
from import_export.admin import ImportExportModelAdmin


from .models import (
    User,
)


class UserResource(resources.ModelResource):
    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'first_name',
            'last_name',
            'email',
            'is_active',
            'phone_number',
            'school',
            'location',
            'password',
            'groups',
        )
        export_order = ('first_name', 'last_name')


class UserAdmin(ImportExportModelAdmin):
    resource_class = UserResource
    filter_horizontal = ('groups', 'user_permissions', 'locations', 'schools')
    list_display = ('username', 'first_name', 'last_name', 'email', 'school', 'location', 'phone_number',)
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
    )
    # fieldsets = (
    #     ('School', {
    #         'classes': ('collapse',),
    #         'fields': ('school', 'schools'),
    #     }),
    #     ('Location', {
    #         'classes': ('collapse',),
    #         'fields': ('location', 'locations'),
    #     }),
    # )


admin.site.register(User, UserAdmin)


