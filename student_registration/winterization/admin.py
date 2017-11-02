from django.contrib import admin

from import_export import resources, fields
from import_export import fields
from import_export.admin import ImportExportModelAdmin
from import_export.widgets import *
from .models import Assessment


class AssessmentResource(resources.ModelResource):

    class Meta:
        model = Assessment
        fields = (

        )
        export_order = fields


class AssessmentAdmin(ImportExportModelAdmin):
    resource_class = AssessmentResource
    list_display = (
        '_id',
        'p_code',
        'p_code_name',
        'district',
        'cadastral',
        'location__type',
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
    )
    list_filter = (
        'assistance_type',
        'location_type',
    )
    search_fields = (
        'id_type',
    )

    def p_code(self, obj):
        if obj.location:
            return obj.location['p_code']
        return ''

    def p_code_name(self, obj):
        if obj.location:
            return obj.location['p_code_name']
        return ''

    def district(self, obj):
        if obj.location:
            return obj.location['district']
        return ''

    def cadastral(self, obj):
        if obj.location:
            return obj.location['cadastral']
        return ''

    def location__type(self, obj):
        if obj.location:
            return obj.location['location_type']
        return ''

    def get_queryset(self, request):
        if request.user.id == 1:
            return super(AssessmentAdmin, self).get_queryset(request)
        return Assessment.objects.none()


admin.site.register(Assessment, AssessmentAdmin)

