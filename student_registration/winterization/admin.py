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
    )
    list_filter = (
        'assistance_type',
    )
    search_fields = (
        'id_type',
    )

    def get_queryset(self, request):
        if request.user.id == 1:
            return super(AssessmentAdmin, self).get_queryset(request)
        return Assessment.objects.none()


admin.site.register(Assessment, AssessmentAdmin)

