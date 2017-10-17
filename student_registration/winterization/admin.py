from django.contrib import admin

from import_export import resources, fields
from import_export import fields
from import_export.admin import ImportExportModelAdmin
from import_export.widgets import *
from .models import Beneficiary


class BeneficiaryResource(resources.ModelResource):

    class Meta:
        model = Beneficiary
        fields = (
            'case_number',
            'registration_status',
            'location_type',
            'governorate',
            'district',
            'cadastral',
            'phone_number',
            'total_children',
            'card_distributed',
            'card_loaded'
        )
        export_order = (
            'case_number',
            'registration_status',
            'location_type',
            'governorate',
            'district',
            'cadastral',
            'phone_number',
            'total_children',
            'card_distributed',
            'card_loaded'
        )


class BeneficiaryAdmin(ImportExportModelAdmin):
    resource_class = BeneficiaryResource
    list_display = (
        'case_number',
        'registration_status',
        'location_type',
        'governorate',
        'district',
        'cadastral',
        'phone_number',
        'total_children',
        'amount',
        'card_distributed',
        'card_loaded',
    )
    list_filter = (
        'registration_status',
        'location_type',
        'governorate',
        'district',
        'cadastral',
        'card_distributed',
        'card_loaded'
    )
    search_fields = (
        'case_number',
        'registration_status',
        'location_type',
        'governorate',
        'district',
        'cadastral',
        'phone_number',
        'total_children',
        'card_distributed',
        'card_loaded'
    )

    def get_queryset(self, request):
        if request.user.id == 1:
            return super(BeneficiaryAdmin, self).get_queryset(request)
        return Beneficiary.objects.none()


admin.site.register(Beneficiary, BeneficiaryAdmin)

