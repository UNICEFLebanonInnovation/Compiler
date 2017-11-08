from django.contrib import admin

from import_export import resources, fields
from import_export import fields
from import_export.admin import ImportExportModelAdmin
from import_export.widgets import *
from .models import Assessment


class AssessmentResource(resources.ModelResource):

    location_p_code = fields.Field()
    location_p_code_name = fields.Field()
    district = fields.Field()
    cadastral = fields.Field()
    locations_type = fields.Field()

    class Meta:
        model = Assessment
        fields = (
            '_id',
            'location_p_code',
            'location_p_code_name',
            'district',
            'cadastral',
            'location_type',
            'locations_type',
            'assistance_type',
            'phone_number',
            'phone_owner',
            'latitude',
            'longitude',
            'first_name',
            'middle_name',
            'family_name',
            'mothers_name',
            'relationship_type',
            'family_count',
            'disabilities',
            'official_id',
            'gender',
            'dob',
            'marital_status',
            'creation_date',
            'completion_date',
            'partner_name',
            'moving_location',
            'new_district',
            'new_cadastral',
            '_0_to_3_months',
            '_3_to_12_months',
            '_1_year_old',
            '_2_years_old',
            '_3_years_old',
            '_4_years_old',
            '_5_years_old',
            '_6_years_old',
            '_7_years_old',
            '_8_years_old',
            '_9_years_old',
            '_10_years_old',
            '_11_years_old',
            '_12_years_old',
            '_13_years_old',
            '_14_years_old',
            'male',
            'female',
            '_3_months_kit',
            '_12_months_kit',
            '_2_years_kit',
            '_3_years_kit',
            '_5_years_kit',
            '_7_years_kit',
            '_9_years_kit',
            '_12_years_kit',
            '_14_years_kit',
            '_3_months_kit_completed',
            '_12_months_kit_completed',
            '_2_years_kit_completed',
            '_3_years_kit_completed',
            '_5_years_kit_completed',
            '_7_years_kit_completed',
            '_9_years_kit_completed',
            '_12_years_kit_completed',
            '_14_years_kit_completed',
        )
        export_order = fields

    def dehydrate_location_p_code(self, obj):
        return obj.location_p_code

    def dehydrate_location_p_code_name(self, obj):
        return obj.location_p_code_name

    def dehydrate_district(self, obj):
        return obj.district

    def dehydrate_cadastral(self, obj):
        return obj.cadastral

    def dehydrate_locations_type(self, obj):
        return obj.location_type


class AssessmentAdmin(ImportExportModelAdmin):
    resource_class = AssessmentResource
    list_display = (
        '_id',
        'location_p_code',
        'location_p_code_name',
        'district',
        'cadastral',
        'locations_type',
        'assistance_type',
        'phone_number',
        'phone_owner',
        'latitude',
        'longitude',
        'first_name',
        'middle_name',
        'family_name',
        'mothers_name',
        'relationship_type',
        'family_count',
        'disabilities',
        'official_id',
        'gender',
        'dob',
        'marital_status',
        'creation_date',
        'completion_date',
        'partner_name',
        'moving_location',
        'new_district',
        'new_cadastral',
        '_0_to_3_months',
        '_3_to_12_months',
        '_1_year_old',
        '_2_years_old',
        '_3_years_old',
        '_4_years_old',
        '_5_years_old',
        '_6_years_old',
        '_7_years_old',
        '_8_years_old',
        '_9_years_old',
        '_10_years_old',
        '_11_years_old',
        '_12_years_old',
        '_13_years_old',
        '_14_years_old',
        'male',
        'female',
        '_3_months_kit',
        '_12_months_kit',
        '_2_years_kit',
        '_3_years_kit',
        '_5_years_kit',
        '_7_years_kit',
        '_9_years_kit',
        '_12_years_kit',
        '_14_years_kit',
        '_3_months_kit_completed',
        '_12_months_kit_completed',
        '_2_years_kit_completed',
        '_3_years_kit_completed',
        '_5_years_kit_completed',
        '_7_years_kit_completed',
        '_9_years_kit_completed',
        '_12_years_kit_completed',
        '_14_years_kit_completed',
        # 'Q1',
        # 'Q2',
        # 'Q3'
    )
    list_filter = (
        'assistance_type',
        'location_type',
        'partner_name',
        'gender',
        'family_count',
        'marital_status',
    )
    search_fields = (
        'id_type',
    )
    #
    # def location_p_code(self, obj):
    #     if obj.location and obj.location['p_code']:
    #         return obj.location['p_code']
    #     return obj.p_code
    #
    # def location_p_code_name(self, obj):
    #     if obj.location and obj.location['p_code_name']:
    #         return obj.location['p_code_name']
    #     return obj.p_code_name
    #
    # def district(self, obj):
    #     if obj.location:
    #         return obj.location['district']
    #     return ''
    #
    # def cadastral(self, obj):
    #     if obj.location:
    #         return obj.location['cadastral']
    #     return ''
    #
    # def location__type(self, obj):
    #     if obj.location:
    #         return obj.location['location_type']
    #     return ''

    def get_queryset(self, request):
        if request.user.id == 1 or request.user.id == 936:
            return super(AssessmentAdmin, self).get_queryset(request)
        return Assessment.objects.none()


admin.site.register(Assessment, AssessmentAdmin)

