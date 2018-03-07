# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from django.contrib import admin
from django.utils.translation import ugettext as _

from import_export import resources, fields
from import_export import fields
from import_export.admin import ImportExportModelAdmin
from import_export.widgets import *
import datetime

from .models import (
    Enrollment,
    EnrollmentGrading,
    StudentMove,
    LoggingStudentMove,
    LoggingProgramMove
)
from .forms import EnrollmentAdminForm, LoggingStudentMoveForm
from student_registration.schools.models import (
    School,
)
from student_registration.locations.models import Location


class EnrollmentResource(resources.ModelResource):
    governorate = fields.Field(
        column_name='governorate',
        attribute='school',
        widget=ForeignKeyWidget(School, 'location_parent_name')
    )
    district = fields.Field(
        column_name='district',
        attribute='school',
        widget=ForeignKeyWidget(School, 'location_name')
    )
    student_age = fields.Field(column_name='Student age')

    class Meta:
        model = Enrollment
        form = EnrollmentAdminForm
        fields = (
            'id',
            'new_registry',
            'student_outreached',
            'have_barcode',
            'outreach_barcode',
            'registration_date',
            'student__id',
            'student__id_type',
            'student__id_number',
            'student__number',
            'student__first_name',
            'student__father_name',
            'student__last_name',
            'student__mother_fullname',
            'student__birthday_year',
            'student__birthday_month',
            'student__birthday_day',
            'student__place_of_birth',
            'student_age',
            'student__sex',
            'student__nationality__name',
            'student__phone_prefix',
            'student__phone',
            'student__address',
            'governorate',
            'district',
            'school__number',
            'school__name',
            'section__name',
            'classroom__name',
            'number_in_previous_school',
            'last_education_level__name',
            'last_education_year',
            'last_school_type',
            'last_school_shift',
            'last_school__name',
            'last_school__number',
            'last_year_result',
            'participated_in_alp',
            'last_informal_edu_round__name',
            'last_informal_edu_final_result__name',
            'age_min_restricted',
            'age_max_restricted',
            'last_attendance_date',
            'last_absent_date',
            'created',
            'modified',
            'moved',
            'dropout_status',
            'disabled',
        )
        export_order = fields

    def dehydrate_student_age(self, obj):
        return obj.student_age


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
            return queryset.filter(school__location__parent_id=self.value())
        return queryset


class FromAgeFilter(admin.SimpleListFilter):
    # Human-readable title which will be displayed in the
    # right admin sidebar just above the filter options.
    title = 'From Age'

    # Parameter for the filter that will be used in the URL query.
    parameter_name = 'from_age'

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """
        return ((l, l) for l in range(0, 100))

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """
        if self.value():
            now = datetime.datetime.now()
            return queryset.filter(student__birthday_year__lte=(now.year - int(self.value())))

        return queryset


class ToAgeFilter(admin.SimpleListFilter):
    # Human-readable title which will be displayed in the
    # right admin sidebar just above the filter options.
    title = 'To Age'

    # Parameter for the filter that will be used in the URL query.
    parameter_name = 'to_age'

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """
        return ((l, l) for l in range(0, 100))

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """
        if self.value():
            now = datetime.datetime.now()
            return queryset.filter(student__birthday_year__gte=(now.year - int(self.value())))
        return queryset


class TermFilter(admin.SimpleListFilter):
    title = 'Term'

    parameter_name = 'term'

    def lookups(self, request, model_admin):
        return (
            ('1', _('Term1')),
            ('2', _('Term2')),
            ('3', _('Term3')),
            ('4', _('Term4')),
        )

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(exam_term=self.value())
        return queryset


class EnrollmentAdmin(ImportExportModelAdmin):
    resource_class = EnrollmentResource
    form = EnrollmentAdminForm
    readonly_fields = (
        'student',
        'student_sex',
        'student_birthday',
        'student_age',
        'student_nationality',
        'student_id_type',
        'student_id_number',
        'student_mother_fullname',
        'student_mother_nationality',
        'student_phone_number',
        'student_address',
    )
    fieldsets = (
        ('Student Info', {
            'fields': (
                'student',
                'student_sex',
                'student_birthday',
                'student_age',
                'student_nationality',
                'student_id_type',
                'student_id_number',
                'student_mother_fullname',
                'student_mother_nationality',
                'student_phone_number',
                'student_address',
            )
        }),
        ('Current Situation', {
            'fields': (
                'education_year',
                'school',
                'registration_date',
                'classroom',
                'section',
            )
        }),
        ('Last formal education', {
            'classes': ('collapse',),
            'fields': (
                'last_education_level',
                'last_school_type',
                'last_school_shift',
                'last_school',
                'last_education_year',
                'last_year_result',
            ),
        }),
        ('Last informal education', {
            'classes': ('collapse',),
            'fields': ('participated_in_alp',
                       'last_informal_edu_round',
                       'last_informal_edu_final_result'
                       ),
        }),
        ('Status options', {
            'fields': ('owner',
                       'status',
                       'deleted',
                       'moved',
                       'last_moved_date',
                       'dropout_status',
                       'disabled',
                       'last_attendance_date',
                       'last_absent_date',
                       'new_registry',
                       'student_outreached',
                       'have_barcode',
                       'number_in_previous_school',
                       'age_min_restricted',
                       'age_max_restricted',
                       )
        }),
    )
    list_display = (
        'student',
        'student_age',
        'school',
        'caza',
        'governorate',
        'classroom',
        'section',
        'education_year',
        'created',
        'modified',
    )
    list_filter = (
        'education_year',
        'school__number',
        'school',
        'school__location',
        GovernorateFilter,
        'classroom',
        'section',
        'student__sex',
        'student__registered_in_unhcr',
        'student__id_type',
        'student__nationality',
        'student__mother_nationality',
        'last_education_level',
        'last_education_year',
        'last_school_type',
        'last_school_shift',
        'last_school',
        'last_year_result',
        'participated_in_alp',
        'last_informal_edu_round',
        'last_informal_edu_level',
        'last_informal_edu_final_result',
        FromAgeFilter,
        ToAgeFilter,
        'age_min_restricted',
        'age_max_restricted',
        # 'exam_result',
        'created',
        'modified',
        'dropout_status',
        'disabled',
        'moved',
        'new_registry',
        'student_outreached',
        'have_barcode',
    )
    search_fields = (
        'student__first_name',
        'student__father_name',
        'student__last_name',
        'student__mother_fullname',
        'school__name',
        'school__number',
        'student__id_number',
        'school__location__name',
        'classroom__name',
        'owner__username',
    )
    date_hierarchy = 'registration_date'

    def get_export_formats(self):
        from student_registration.users.utils import get_default_export_formats
        return get_default_export_formats()

    def caza(self, obj):
        if obj.school and obj.school.location:
            return obj.school.location.name
        return ''

    def governorate(self, obj):
        if obj.school and obj.school.location and obj.school.location.parent:
            return obj.school.location.parent.name
        return ''


class Dropout(Enrollment):
    class Meta:
        proxy = True


class DropoutAdmin(EnrollmentAdmin):

    list_display = (
        'student',
        'last_attendance_date',
        'last_absent_date',
        'school',
        'classroom',
        'section',
        'education_year',
        'caza',
        'governorate',
    )

    actions = ('cancel_dropout', )

    def get_queryset(self, request):
        return Enrollment.drop_objects.all()

    def cancel_dropout(self, request, queryset):
        queryset.update(dropout_status=False)
        queryset.update(disabled=False)


class Disabled(Enrollment):
    class Meta:
        proxy = True


class DisabledAdmin(EnrollmentAdmin):

    list_display = (
        'student',
        'last_attendance_date',
        'last_absent_date',
        'school',
        'classroom',
        'section',
        'education_year',
        'caza',
        'governorate',
    )

    actions = ('dropout', 'cancel_disable')

    def get_queryset(self, request):
        return Enrollment.disabled_objects.all()

    def cancel_disable(self, request, queryset):
        queryset.update(disabled=False)

    def dropout(self, request, queryset):
        queryset.update(dropout_status=True)


class StudentMoveResource(resources.ModelResource):

    class Meta:
        model = StudentMove
        fields = (
            'enrolment1__student__first_name',
            'enrolment1__student__father_name',
            'enrolment1__student__last_name',
            'enrolment1__student__mother_fullname',
            'school1__name',
            'enrolment2__student__first_name',
            'enrolment2__student__father_name',
            'enrolment2__student__last_name',
            'enrolment2__student__mother_fullname',
            'school2__name',
        )
        export_order = fields


class StudentMoveAdmin(ImportExportModelAdmin):
    resource_class = StudentMoveResource
    fields = ()

    list_display = (
        'enrolment1',
        'school1',
        'enrolment2',
        'school2',
    )

    list_filter = (
        'school1',
        'school2',
    )

    search_fields = (
        'enrolment1__student__first_name',
        'enrolment1__student__father_name',
        'enrolment1__student__last_name',
        'enrolment1__student__mother_fullname',
        'school1__name',
        'enrolment2__student__first_name',
        'enrolment2__student__father_name',
        'enrolment2__student__last_name',
        'enrolment2__student__mother_fullname',
        'school2__name',
    )

    def get_export_formats(self):
        from student_registration.users.utils import get_default_export_formats
        return get_default_export_formats()


class LoggingStudentMoveResource(resources.ModelResource):

    class Meta:
        model = LoggingStudentMove
        fields = ()
        export_order = fields


class LoggingStudentMoveAdmin(ImportExportModelAdmin):
    resource_class = LoggingStudentMoveResource
    form = LoggingStudentMoveForm
    fields = (
    )

    list_display = (
        'education_year',
        'registered',
        'student',
        'moved_date',
        'school_from',
        'classroom',
        'section',
        'school_to',
        'registered_in_new_school',
    )

    list_filter = (
        'education_year',
        'school_from',
        'school_to',
    )

    search_fields = (

    )

    def get_export_formats(self):
        from student_registration.users.utils import get_default_export_formats
        return get_default_export_formats()

    def registered(self, obj):
        if obj.enrolment:
            return str(obj.enrolment.created)
        return ''

    def registered_in_new_school(self, obj):
        if obj.school_to:
            return str(obj.modified)
        return ''

    def classroom(self, obj):
        if obj.enrolment and obj.enrolment.classroom:
            return obj.enrolment.classroom.name
        return ''

    def section(self, obj):
        if obj.enrolment and obj.enrolment.section:
            return obj.enrolment.section.name
        return ''


class LoggingProgramMoveResource(resources.ModelResource):

    class Meta:
        model = LoggingProgramMove
        fields = (
            'education_year',
            'student__first_name',
            'student__father_name',
            'student__last_name',
            'student__sex',
            'student__mother_fullname',
            'school_from__name',
            'school_to__name',
            'eligibility',
        )
        export_order = fields


class LoggingProgramMoveAdmin(ImportExportModelAdmin):
    resource_class = LoggingProgramMoveResource
    fields = ()

    list_display = (
        'education_year',
        'student',
        'school_from',
        'school_to',
        'eligibility',
        'potential_move',
    )

    list_filter = (
        'education_year',
        'school_from',
        'school_to',
        'eligibility',
        'potential_move',
    )

    search_fields = (
        'student__first_name',
        'student__father_name',
        'student__last_name',
    )

    def get_export_formats(self):
        from student_registration.users.utils import get_default_export_formats
        return get_default_export_formats()


class GradingResource(resources.ModelResource):
    exam_term_name = fields.Field(column_name='Term')
    enrollment_student = fields.Field(column_name='Student fullname')
    enrollment_school_name = fields.Field(column_name='School name')
    enrollment_school_number = fields.Field(column_name='School number')
    enrollment_classroom_name = fields.Field(column_name='Class')
    enrollment_section_name = fields.Field(column_name='Section')

    class Meta:
        model = EnrollmentGrading
        fields = (
            'enrollment_student',
            'enrollment_school_name',
            'enrollment_school_number',
            'enrollment_classroom_name',
            'enrollment_section_name',
            'exam_term_name',
            'exam_result_arabic',
            'exam_result_language',
            'exam_result_education',
            'exam_result_geo',
            'exam_result_history',
            'exam_result_math',
            'exam_result_science',
            'exam_result_physic',
            'exam_result_chemistry',
            'exam_result_bio',
            'exam_result_linguistic_ar',
            'exam_result_sociology',
            'exam_result_physical',
            'exam_result_artistic',
            'exam_result_linguistic_en',
            'exam_result_mathematics',
            'exam_result_sciences',
            'exam_total',
            'exam_result',
        )
        export_order = fields

    def dehydrate_exam_term_name(self, obj):
        return obj.exam_term_name

    def dehydrate_enrollment_student(self, obj):
        return obj.enrollment_student

    def dehydrate_enrollment_school_name(self, obj):
        return obj.enrollment_school_name

    def dehydrate_enrollment_school_number(self, obj):
        return obj.enrollment_school_number

    def dehydrate_enrollment_classroom_name(self, obj):
        return obj.enrollment_classroom_name

    def dehydrate_enrollment_section_name(self, obj):
        return obj.enrollment_section_name


class GradingAdmin(ImportExportModelAdmin):
    resource_class = GradingResource
    fields = (
        'exam_term',
        'exam_result_arabic',
        'exam_result_language',
        'exam_result_education',
        'exam_result_geo',
        'exam_result_history',
        'exam_result_math',
        'exam_result_science',
        'exam_result_physic',
        'exam_result_chemistry',
        'exam_result_bio',
        'exam_result_linguistic_ar',
        'exam_result_sociology',
        'exam_result_physical',
        'exam_result_artistic',
        'exam_result_linguistic_en',
        'exam_result_mathematics',
        'exam_result_sciences',
        'exam_total',
        'exam_result',
    )

    list_display = (
        'enrollment',
        'exam_term_name',
        'exam_result_arabic',
        'exam_result_language',
        'exam_result_education',
        'exam_result_geo',
        'exam_result_history',
        'exam_result_math',
        'exam_result_science',
        'exam_result_physic',
        'exam_result_chemistry',
        'exam_result_bio',
        'exam_result_linguistic_ar',
        'exam_result_sociology',
        'exam_result_physical',
        'exam_result_artistic',
        'exam_result_linguistic_en',
        'exam_result_mathematics',
        'exam_result_sciences',
        'exam_total',
        'exam_result',
    )

    list_filter = (
        TermFilter,
        'enrollment__school',
        'enrollment__education_year'
    )

    search_fields = (
        'enrollment__student__first_name',
        'enrollment__student__father_name',
        'enrollment__student__last_name',
    )

    def get_export_formats(self):
        from student_registration.users.utils import get_default_export_formats
        return get_default_export_formats()


admin.site.register(Enrollment, EnrollmentAdmin)
admin.site.register(Dropout, DropoutAdmin)
admin.site.register(Disabled, DisabledAdmin)
# admin.site.register(StudentMove, StudentMoveAdmin)
admin.site.register(LoggingStudentMove, LoggingStudentMoveAdmin)
admin.site.register(LoggingProgramMove, LoggingProgramMoveAdmin)
admin.site.register(EnrollmentGrading, GradingAdmin)
