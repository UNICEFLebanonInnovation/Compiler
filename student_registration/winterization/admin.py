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

        )
        export_order = fields


class BeneficiaryAdmin(ImportExportModelAdmin):
    resource_class = BeneficiaryResource
    list_display = (
        '_id',
    )
    list_filter = (
        'assistance_type',
    )
    search_fields = (
        'id_type',
    )

    def get_queryset(self, request):
        if request.user.id == 1:
            return super(BeneficiaryAdmin, self).get_queryset(request)
        return Beneficiary.objects.none()


admin.site.register(Beneficiary, BeneficiaryAdmin)

