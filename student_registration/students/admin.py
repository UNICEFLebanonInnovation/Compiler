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
    Location,
    LocationType,
    EducationLevel,
    ClassLevel,
    Grade,
    Section,
    ClassRoom,
    PartnerOrganization,
)


admin.site.register(Student)
admin.site.register(School)
# admin.site.register(Course)
admin.site.register(Nationality)
admin.site.register(Language)
admin.site.register(EducationLevel)
admin.site.register(ClassLevel)
admin.site.register(Grade)
admin.site.register(Section)
admin.site.register(ClassRoom)
admin.site.register(Location)
admin.site.register(LocationType)
admin.site.register(PartnerOrganization)

