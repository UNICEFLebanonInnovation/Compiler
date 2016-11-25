# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from django.contrib import admin
from import_export import resources, fields
from import_export import fields
from import_export.admin import ImportExportModelAdmin
from import_export.widgets import *

from .models import Enrollment
from student_registration.students.models import Student
from student_registration.schools.models import (
    School,
    ClassRoom,
    EducationLevel,
    ClassRoom,
    Section,
)


class EnrollmentResource(resources.ModelResource):
    studentFname = fields.Field(
        column_name='Student First Name',
        attribute='student',
        widget=ForeignKeyWidget(Student, 'first_name')
    )
    studentFaName = fields.Field(
        column_name='Student Father Name',
        attribute='student',
        widget=ForeignKeyWidget(Student, 'father_name')
    )
    studentLname = fields.Field(
        column_name='Student Last Name',
        attribute='student',
        widget=ForeignKeyWidget(Student, 'last_name')
    )
    section = fields.Field(
        column_name='Section',
        attribute='section',
        widget=ForeignKeyWidget(Section, 'name')
    )
    classroom = fields.Field(
        column_name='Classroom',
        attribute='classroom',
        widget=ForeignKeyWidget(ClassRoom, 'name')
    )
    year = fields.Field(
        column_name='Year',
        attribute='year'
    )
    owner = fields.Field(
        column_name='Owner',
        attribute='owner'
    )
    mother = fields.Field(
        column_name='Student Mother Name',
        attribute='student',
        widget=ForeignKeyWidget(Student, 'mother_fullname')
    )
    id_number = fields.Field(
        column_name='ID Number',
        attribute='student',
        widget=ForeignKeyWidget(Student, 'id_number')
    )

    class Meta:
        model = Enrollment
        fields = ('section', 'classroom', 'year', 'owner')
        export_order = (
            'id_number','studentFname', 'studentFaName', 'studentLname',
            'mother', 'section', 'classroom', 'year', 'owner')


class EnrollmentAdmin(ImportExportModelAdmin):
    resource_class = EnrollmentResource
    list_display = (
        'student', 'student_age', 'school', 'caza', 'governorate',
        'classroom', 'section',
    )
    list_filter = ('classroom', 'school', 'school__location', )
    search_fields = (
        'student__first_name', 'student__father_name', 'student__last_name', 'student__mother_fullname',
        'school__name', 'school__number', 'student__id_number', 'school__location__name', 'classroom__name',
        'owner__username'
    )

    def caza(self, obj):
        if obj.school and obj.school.location:
            return obj.school.location.name
        return ''

    def governorate(self, obj):
        if obj.school and obj.school.location and obj.school.location.parent:
            return obj.school.location.parent.name
        return ''


admin.site.register(Enrollment, EnrollmentAdmin)
