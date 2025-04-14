# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

from .models import Adolescent


class AdolescentAdmin(admin.ModelAdmin):

    list_display = (
        'full_name',
        'nationality',
        'birthday_year',
        'unicef_id',
        'created',
        'modified',
    )
    list_filter = (
        'nationality',
        'birthday_year',
        'number',
        'created',
        'modified',
    )
    search_fields = (
        'first_name',
        'father_name',
        'last_name',
    )


admin.site.register(Adolescent, AdolescentAdmin)
