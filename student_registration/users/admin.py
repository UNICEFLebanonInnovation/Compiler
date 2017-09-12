# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

<<<<<<< HEAD
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
=======
from django.contrib import admin
from django.utils.translation import gettext, gettext_lazy as _
from django.contrib.auth.admin import UserAdmin as AuthUserAdmin
from .models import User


class UserAdmin(AuthUserAdmin):

>>>>>>> 3b9073c012bcdfc49afcb1d105deb56123ab5be1
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
    actions = ('activate', 'disable',)

<<<<<<< HEAD
    def activate(self, request, queryset):
        queryset.update(is_active=True)
        # for user in queryset:
        #     user.is_active = True
        #     user.save()

    def disable(self, request, queryset):
        queryset.update(is_active=False)
        # for user in queryset:
        #     user.is_active = True
        #     user.save()

=======
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
>>>>>>> 3b9073c012bcdfc49afcb1d105deb56123ab5be1

admin.site.register(User, UserAdmin)


