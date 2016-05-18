# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from django.db import models
from django.contrib import admin

from .models import (
    Student,
    School,
    Course,
    Nationality,
    Language,
    Governorate,
    EducationLevel,
    ClassLevel,
    PartnerOrganization,
)


admin.site.register(Student)
admin.site.register(School)
admin.site.register(Course)
admin.site.register(Nationality)
admin.site.register(Language)
admin.site.register(Governorate)
admin.site.register(EducationLevel)
admin.site.register(ClassLevel)
admin.site.register(PartnerOrganization)
