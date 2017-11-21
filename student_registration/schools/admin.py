# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals


from django.contrib import admin
from import_export import resources, fields
from import_export import fields
from import_export.admin import ImportExportModelAdmin

from .models import (
    School,
    EducationLevel,
    ClassLevel,
    Section,
    ClassRoom,
    PartnerOrganization,
    ALPReferMatrix,
    EducationYear,
    ALPAssignmentMatrix,
    EducationalLevel,
    Holiday,
    CLMRound,
    PublicDocument
)
from student_registration.locations.models import Location
from student_registration.attendances.tasks import set_app_attendances


class SchoolResource(resources.ModelResource):
    district = fields.Field(column_name='District')
    governorate = fields.Field(column_name='Governorate')
    total_registered = fields.Field(column_name='Total registered')

    class Meta:
        model = School
        fields = (
            'id',
            'name',
            'number',
            'district',
            'governorate',
            'director_name',
            'land_phone_number',
            'fax_number',
            'director_phone_number',
            'email',
            'certified_foreign_language',
            'comments',
            'weekend',
            'it_name',
            'it_phone_number',
            'field_coordinator_name',
            'total_registered',
            'academic_year_start',
            'academic_year_end',
            'academic_year_exam_end',
            'attendance_range',
            'attendance_from_beginning',
            'is_alp',
            'number_students_alp',
            'is_2nd_shift',
            'number_students_2nd_shift',
        )
        export_order = fields

    def dehydrate_district(self, obj):
        if obj.location:
            return obj.location.name
        return ''

    def dehydrate_governorate(self, obj):
        if obj.location and obj.location.parent:
            return obj.location.parent.name
        return ''

    def dehydrate_total_registered(self, obj):
        return obj.total_registered


class GovernorateFilter(admin.SimpleListFilter):
    # Human-readable title which will be displayed in the
    # right admin sidebar just above the filter options.
    title = 'Governorate'

    # Parameter for the filter that will be used in the URL query.
    parameter_name = 'governorate'

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """
        return ((l.id, l.name) for l in Location.objects.filter(type_id=1))

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """
        if self.value():
            return queryset.filter(location__parent_id=self.value())
        return queryset


class SchoolTypeFilter(admin.SimpleListFilter):
    # Human-readable title which will be displayed in the
    # right admin sidebar just above the filter options.
    title = 'School type'

    # Parameter for the filter that will be used in the URL query.
    parameter_name = 'school_type'

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """
        return (
            ('alp', 'ALP'),
            ('2ndshift', '2nd shift'),
            ('both', 'ALP & 2nd shift'),
        )

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """
        if not self.value():
            return queryset
        if self.value() == 'alp':
            return queryset.filter(is_alp=True)
        if self.value() == '2ndshift':
            return queryset.filter(is_2nd_shift=True)
        if self.value() == 'both':
            return queryset.filter(is_alp=True, is_2nd_shift=True)


class SchoolAdmin(ImportExportModelAdmin):
    resource_class = SchoolResource

    fields = (
        'name',
        'number',
        'attendance_range',
        'attendance_from_beginning',
        'is_alp',
        'number_students_alp',
        'is_2nd_shift',
        'number_students_2nd_shift',
        'location',
        'director_name',
        'land_phone_number',
        'fax_number',
        'director_phone_number',
        'email',
        'certified_foreign_language',
        'comments',
        'weekend',
        'it_name',
        'it_phone_number',
        'field_coordinator_name',
        'academic_year_start',
        'academic_year_end',
        'academic_year_exam_end',
    )
    list_display = (
        'name',
        'number',
        'location',
        'is_2nd_shift',
        'number_students_2nd_shift',
        'is_alp',
        'number_students_alp',
        'attendance_range',
        'attendance_from_beginning',
    )
    search_fields = (
        'name',
        'number',
    )
    list_filter = (
        SchoolTypeFilter,
        GovernorateFilter,
        'location',
        'attendance_range',
        'attendance_from_beginning',
        'is_alp',
        'is_2nd_shift',
        'weekend',
    )
    date_hierarchy = 'academic_year_start'

    actions = ('push_attendances_2ndshift', 'push_attendances_2ndshift_delay',
               'push_attendances_alp', 'push_attendances_alp_delay',
               'open_attendance_90_days', 'open_attendance_60_days',
               'open_attendance_30_days', 'open_attendance_20_days',
               'open_attendance_10_days', )

    def push_attendances_2ndshift(self, request, queryset):
        for school in queryset:
            set_app_attendances(school_number=school.number)

    def push_attendances_2ndshift_delay(self, request, queryset):
        for school in queryset:
            set_app_attendances.delay(school_number=school.number)

    def push_attendances_alp(self, request, queryset):
        for school in queryset:
            set_app_attendances(school_number=school.number, school_type='alp')

    def push_attendances_alp_delay(self, request, queryset):
        for school in queryset:
            set_app_attendances.delay(school_number=school.number, school_type='alp')

    def open_attendance_90_days(self, request, queryset):
        queryset.update(attendance_range=90)

    def open_attendance_60_days(self, request, queryset):
        queryset.update(attendance_range=60)

    def open_attendance_30_days(self, request, queryset):
        queryset.update(attendance_range=30)

    def open_attendance_20_days(self, request, queryset):
        queryset.update(attendance_range=20)

    def open_attendance_10_days(self, request, queryset):
        queryset.update(attendance_range=10)

    def get_export_formats(self):
        from student_registration.users.utils import get_default_export_formats
        return get_default_export_formats()


class EducationLevelResource(resources.ModelResource):
    class Meta:
        model = EducationLevel
        fields = (
            'id',
            'name',
            'note',
        )
        export_order = ('name',)


class EducationLevelAdmin(ImportExportModelAdmin):
    resource_class = EducationLevelResource

    def get_export_formats(self):
        from student_registration.users.utils import get_default_export_formats
        return get_default_export_formats()


class ClassLevelResource(resources.ModelResource):
    class Meta:
        model = ClassLevel
        fields = (
            'id',
            'name'
        )
        export_order = ('name',)


class ClassLevelAdmin(ImportExportModelAdmin):
    resource_class = ClassLevelResource
    def get_export_formats(self):
        from student_registration.users.utils import get_default_export_formats
        return get_default_export_formats()


class SectionResource(resources.ModelResource):
    class Meta:
        model = Section
        fields = (
            'id',
            'name'
        )
        export_order = ('name',)


class SectionAdmin(ImportExportModelAdmin):
    resource_class = SectionResource

    def get_export_formats(self):
        from student_registration.users.utils import get_default_export_formats
        return get_default_export_formats()


class ClassRoomResource(resources.ModelResource):
    class Meta:
        model = ClassRoom
        fields = (
            'id',
            'name',
        )
        export_order = fields


class ClassRoomAdmin(ImportExportModelAdmin):
    resource_class = ClassRoomResource
    fields = (
        'name',
    )
    list_display = fields

    def get_export_formats(self):
        from student_registration.users.utils import get_default_export_formats
        return get_default_export_formats()


class PartnerOrganizationResource(resources.ModelResource):
    class Meta:
        model = PartnerOrganization
        fields = (
            'id',
            'name'
        )
        export_order = ('name',)


class PartnerOrganizationAdmin(ImportExportModelAdmin):
    resource_class = PartnerOrganizationResource
    search_fields = ('name', )

    def get_export_formats(self):
        from student_registration.users.utils import get_default_export_formats
        return get_default_export_formats()


class ALPReferMatrixResource(resources.ModelResource):
    class Meta:
        model = ALPReferMatrix


class ALPReferMatrixAdmin(ImportExportModelAdmin):
    resource_class = ALPReferMatrixResource
    fields = (
        'level',
        'age',
        'success_refer_to',
        'fail_refer_to',
        'success_grade',
    )
    list_display = fields

    def get_export_formats(self):
        from student_registration.users.utils import get_default_export_formats
        return get_default_export_formats()


class ALPAssignmentMatrixResource(resources.ModelResource):
    class Meta:
        model = ALPAssignmentMatrix


class ALPAssignmentMatrixAdmin(ImportExportModelAdmin):
    resource_class = ALPAssignmentMatrixResource
    fields = (
        'level',
        'range_start',
        'range_end',
        'refer_to',
    )
    list_display = (
        'level',
        'range',
        'refer_to',
    )

    def get_export_formats(self):
        from student_registration.users.utils import get_default_export_formats
        return get_default_export_formats()


class PublicDocumentResource(resources.ModelResource):
    class Meta:
        model = PublicDocument


class PublicDocumentAdmin(ImportExportModelAdmin):
    resource_class = PublicDocumentResource
    list_display = (
        'name',
        'file_url',
        'created',
        'modified'
    )

    def get_export_formats(self):
        from student_registration.users.utils import get_default_export_formats
        return get_default_export_formats()


admin.site.register(School, SchoolAdmin)
admin.site.register(EducationLevel, EducationLevelAdmin)
admin.site.register(ClassLevel, ClassLevelAdmin)
admin.site.register(Section, SectionAdmin)
admin.site.register(ClassRoom, ClassRoomAdmin)
admin.site.register(PartnerOrganization, PartnerOrganizationAdmin)
admin.site.register(ALPReferMatrix, ALPReferMatrixAdmin)
admin.site.register(EducationYear)
# admin.site.register(Holiday)
admin.site.register(CLMRound)
admin.site.register(PublicDocument, PublicDocumentAdmin)
admin.site.register(EducationalLevel)
admin.site.register(ALPAssignmentMatrix, ALPAssignmentMatrixAdmin)








