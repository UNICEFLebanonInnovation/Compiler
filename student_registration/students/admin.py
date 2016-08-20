# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from django.contrib import admin

from .models import (
    Student,
    Nationality,
    Language,
    IDType,
)


admin.site.register(Student)
admin.site.register(Nationality)
admin.site.register(Language)
admin.site.register(IDType)
