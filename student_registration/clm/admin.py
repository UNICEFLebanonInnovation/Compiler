# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from django.contrib import admin
from import_export import resources, fields
from import_export import fields
from import_export.admin import ImportExportModelAdmin

from .forms import BLNAdminForm, RSAdminForm, CBECEAdminForm
from .models import (
    Assessment,
    Cycle,
    Site,
    Referral,
    Disability,
    BLN,
    RS,
    CBECE
)


class BLNResource(resources.ModelResource):
    arabic_improvement = fields.Field(
        column_name='arabic improvement',
        attribute='arabic_improvement',
    )
    english_improvement = fields.Field(
        column_name='english_improvement',
        attribute='english_improvement',
    )
    french_improvement = fields.Field(
        column_name='french_improvement',
        attribute='french_improvement',
    )
    math_improvement = fields.Field(
        column_name='math_improvement',
        attribute='math_improvement',
    )
    assessment_improvement = fields.Field(
        column_name='assessment_improvement',
        attribute='assessment_improvement',
    )

    class Meta:
        fields = (
            'id',
            'partner__name',
            'new_registry',
            'student_outreached',
            'have_barcode',
            'outreach_barcode',
            'round__name',
            'governorate',
            'district',
            'location',
            'language',
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
            'student__nationality__name',
            'student__sex',
            'student__p_code',
            'disability',
            'internal_number',
            'comments',
            'hh_educational_level',
            'student__family_status',
            'student__have_children',
            'have_labour',
            'labours',
            'labour_hours',
            'pre_test_score',
            'post_test_score',
            'arabic_improvement',
            'english_improvement',
            'french_improvement',
            'math_improvement',
            'assessment_improvement',
            'participation',
            'barriers',
            'learning_result',
            'created',
            'modified'
        )
        model = BLN
        export_order = fields

        # def dehydrate_arabic_improvement(self, obj):
        #     return obj.arabic_improvement


class BLNAdmin(ImportExportModelAdmin):
    resource_class = BLNResource
    form = BLNAdminForm
    # fields = '__all__'

    list_display = (
        'student',
        'governorate',
        'district',
        'partner',
        'created',
        'modified',
    )
    list_filter = (
        'round',
        'governorate',
        'district',
        'partner',
        'language',
        'student__sex',
        'student__nationality',
        'disability',
        'hh_educational_level',
        'student__family_status',
        'student__have_children',
        'have_labour',
        'labours',
        'labour_hours',
        'participation',
        'barriers',
        'learning_result',
        'created',
        'modified',
    )
    search_fields = (
        'student__first_name',
        'student__father_name',
        'student__last_name',
        'student__mother_fullname',
    )

    def get_export_formats(self):
        from student_registration.users.utils import get_default_export_formats
        return get_default_export_formats()


class RSResource(resources.ModelResource):
    arabic_reading_improvement = fields.Field(
        column_name='arabic_reading_improvement',
        attribute='arabic_reading_improvement',
    )
    pretest_result = fields.Field(
        column_name='pretest_result',
        attribute='pretest_result',
    )
    posttest_result = fields.Field(
        column_name='posttest_result',
        attribute='posttest_result',
    )
    arabic_improvement = fields.Field(
        column_name='arabic_improvement',
        attribute='arabic_improvement',
    )
    language_improvement = fields.Field(
        column_name='language_improvement',
        attribute='language_improvement',
    )
    science_improvement = fields.Field(
        column_name='science_improvement',
        attribute='science_improvement',
    )
    math_improvement = fields.Field(
        column_name='math_improvement',
        attribute='math_improvement',
    )
    academic_test_improvement = fields.Field(
        column_name='academic_test_improvement',
        attribute='academic_test_improvement',
    )
    pre_test_score = fields.Field(
        column_name='pre_test_score',
        attribute='pre_test_score',
    )
    post_test_score = fields.Field(
        column_name='post_test_score',
        attribute='post_test_score',
    )
    assessment_improvement = fields.Field(
        column_name='assessment_improvement',
        attribute='assessment_improvement',
    )
    pre_motivation_score = fields.Field(
        column_name='pre_motivation_score',
        attribute='pre_motivation_score',
    )
    post_motivation_score = fields.Field(
        column_name='post_motivation_score',
        attribute='post_motivation_score',
    )
    motivation_improvement = fields.Field(
        column_name='motivation_improvement',
        attribute='motivation_improvement',
    )
    pre_self_assessment_score = fields.Field(
        column_name='pre_self_assessment_score',
        attribute='pre_self_assessment_score',
    )
    post_self_assessment_score = fields.Field(
        column_name='post_self_assessment_score',
        attribute='post_self_assessment_score',
    )
    self_assessment_improvement = fields.Field(
        column_name='self_assessment_improvement',
        attribute='self_assessment_improvement',
    )

    class Meta:
        model = RS
        fields = (
            'id',
            'partner__name',
            'new_registry',
            'round__name',
            'type',
            'site',
            'school',
            'governorate',
            'district',
            'location',
            'language',
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
            'student__nationality__name',
            'student__sex',
            'student__p_code',
            'disability',
            'internal_number',
            'comments',
            'hh_educational_level',
            'student__family_status',
            'student__have_children',
            'have_labour',
            'labours',
            'labour_hours',
            'registered_in_school',
            'shift',
            'grade',
            'section',
            'referral',
            'pre_reading_score',
            'post_reading_score',
            'arabic_reading_improvement',
            'pretest_result',
            'posttest_result',
            'arabic_improvement',
            'language_improvement',
            'science_improvement',
            'math_improvement',
            'academic_test_improvement',
            'pre_test_score',
            'post_test_score',
            'assessment_improvement',
            'pre_motivation_score',
            'post_motivation_score',
            'motivation_improvement',
            'pre_self_assessment_score',
            'post_self_assessment_score',
            'self_assessment_improvement',
            'participation',
            'barriers',
            'learning_result',
            'created',
            'modified'
        )
        export_order = fields


class RSAdmin(ImportExportModelAdmin):
    resource_class = RSResource
    form = RSAdminForm
    # fields = '__all__'

    list_display = (
        'student',
        'governorate',
        'district',
        'partner',
        'created',
        'modified',
    )
    list_filter = (
        'round',
        'type',
        'site',
        'school',
        'governorate',
        'district',
        'partner',
        'language',
        'student__sex',
        'student__nationality',
        'disability',
        'hh_educational_level',
        'student__family_status',
        'student__have_children',
        'have_labour',
        'labours',
        'labour_hours',
        'registered_in_school',
        'shift',
        'grade',
        'section',
        'referral',
        'participation',
        'barriers',
        'learning_result',
        'created',
        'modified',
    )
    search_fields = (
        'student__first_name',
        'student__father_name',
        'student__last_name',
        'student__mother_fullname',
    )

    def get_export_formats(self):
        from student_registration.users.utils import get_default_export_formats
        return get_default_export_formats()


class CBECEResource(resources.ModelResource):
    pre_test_score = fields.Field(
        column_name='pre_test_score',
        attribute='pre_test_score',
    )
    post_test_score = fields.Field(
        column_name='post_test_score',
        attribute='post_test_score',
    )
    art_improvement = fields.Field(
        column_name='art_improvement',
        attribute='art_improvement',
    )
    cognitive_improvement = fields.Field(
        column_name='cognitive_improvement',
        attribute='cognitive_improvement',
    )
    social_improvement = fields.Field(
        column_name='social_improvement',
        attribute='social_improvement',
    )
    psycho_improvement = fields.Field(
        column_name='psycho_improvement',
        attribute='psycho_improvement',
    )
    artistic_improvement = fields.Field(
        column_name='artistic_improvement',
        attribute='artistic_improvement',
    )
    assessment_improvement = fields.Field(
        column_name='assessment_improvement',
        attribute='assessment_improvement',
    )

    class Meta:
        model = CBECE
        fields = (
            'id',
            'partner__name',
            'new_registry',
            'student_outreached',
            'have_barcode',
            'outreach_barcode',
            'round__name',
            'cycle',
            'site',
            'school',
            'governorate__name',
            'district__name',
            'location',
            'language',
            'referral',
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
            'student__nationality__name',
            'student__sex',
            'student__p_code',
            'disability__name',
            'internal_number',
            'comments',
            'child_muac',
            'hh_educational_level',
            'have_labour',
            'labours',
            'labour_hours',
            'pre_test_score',
            'post_test_score',
            'art_improvement',
            'cognitive_improvement',
            'social_improvement',
            'psycho_improvement',
            'artistic_improvement',
            'assessment_improvement',
            'participation',
            'barriers',
            'learning_result',
            'created',
            'modified'
        )
        export_order = fields


class CBECEAdmin(ImportExportModelAdmin):
    resource_class = CBECEResource
    form = CBECEAdminForm
    # fields = '__all__'

    list_display = (
        'student',
        'governorate',
        'district',
        'partner',
        'created',
        'modified',
    )
    list_filter = (
        'round',
        'cycle',
        'site',
        'school',
        'governorate',
        'district',
        'partner',
        'language',
        'student__sex',
        'student__nationality',
        'disability',
        'child_muac',
        'hh_educational_level',
        'student__family_status',
        'student__have_children',
        'have_labour',
        'labours',
        'labour_hours',
        'participation',
        'barriers',
        'learning_result',
        'created',
        'modified',
    )
    search_fields = (
        'student__first_name',
        'student__father_name',
        'student__last_name',
        'student__mother_fullname',
    )

    def get_export_formats(self):
        from student_registration.users.utils import get_default_export_formats
        return get_default_export_formats()


class DisabilityResource(resources.ModelResource):
    class Meta:
        model = Disability
        fields = (
            'id',
            'name',
        )
        export_order = fields


class DisabilityAdmin(ImportExportModelAdmin):
    resource_class = DisabilityResource


admin.site.register(Assessment)
admin.site.register(Cycle)
admin.site.register(Site)
admin.site.register(Referral)
admin.site.register(Disability, DisabilityAdmin)

admin.site.register(BLN, BLNAdmin)
admin.site.register(RS, RSAdmin)
admin.site.register(CBECE, CBECEAdmin)
