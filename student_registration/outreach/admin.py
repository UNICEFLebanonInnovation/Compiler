from __future__ import absolute_import, unicode_literals

from django.contrib import admin
from import_export import resources, fields
from import_export import fields
from django.db.models import Count
from import_export.admin import ImportExportModelAdmin
from .models import HouseHold, Child, Child2, OutreachYear
from django.utils.translation import ugettext as _


class HouseHoldResource(resources.ModelResource):
    class Meta:
        model = HouseHold


class HouseHoldAdmin(ImportExportModelAdmin):
    resource_class = HouseHold
    list_display = (
        'form_id',
        'name',
        'phone_number',
        'residence_type',
        'p_code',
        'number_of_children',
        'barcode_number'
    )
    search_fields = (
        'form_id',
        'name',
        'barcode_number',
    )
    list_filter = (
        'p_code',
        'residence_type',
        'governorate',
        'district'
    )

    def get_export_formats(self):
        from student_registration.users.utils import get_default_export_formats
        return get_default_export_formats()


class DisabilityFilter(admin.SimpleListFilter):
    # Human-readable title which will be displayed in the
    # right admin sidebar just above the filter options.
    title = 'Disability'

    # Parameter for the filter that will be used in the URL query.
    parameter_name = 'disability'

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """
        return (
            ('Walking', _('Walking')),
            ('Seeing', _('Seeing')),
            ('Hearing', _('Hearing')),
            ('Speaking', _('Speaking')),
            ('Self_Care', _('Self Care')),
            ('Learning', _('Learning')),
            ('Interacting', _('Interacting')),
            ('Other', _('Other')),
        )

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """
        if not self.value():
            return queryset
        return queryset.filter(disability_type__contains=[self.value()])


class Child2Resource(resources.ModelResource):
    class Meta:
        model = Child2
        fields = ()
        export = fields


class Child2Admin(ImportExportModelAdmin):
    resource_class = Child2Resource
    list_display = (
        'form_id',
        'formid_ind',
        'barcode_subset',
        'first_name',
        'father_name',
        'last_name',
        'mother_fullname',
        'birthday',
        'nationality',
        'disability_type',
    )
    search_fields = (
        'form_id',
        'formid_ind',
        'barcode_subset',
    )
    list_filter = (
        'p_code',
        'nationality',
        'sex',
        'disability_type',
        'household__governorate',
        DisabilityFilter,
        'last_edu_system',
        'referral_reason',
    )

    def get_export_formats(self):
        from student_registration.users.utils import get_default_export_formats
        return get_default_export_formats()


class ChildResource(resources.ModelResource):
    class Meta:
        model = Child
        fields = ()
        export = fields


class ChildAdmin(ImportExportModelAdmin):
    resource_class = ChildResource
    list_display = (
        'form_id',
        'formid_ind',
        'barcode_subset',
        'first_name',
        'father_name',
        'last_name',
        'mother_fullname',
        'birthday',
        'nationality',
        'disability_type',
    )
    search_fields = (
        'form_id',
        'formid_ind',
        'barcode_subset',
    )
    list_filter = (
        'p_code',
        'nationality',
        'sex',
        'disability_type',
        'household__governorate',
        DisabilityFilter,
        'last_edu_system',
        'referral_reason',
    )

    def get_export_formats(self):
        from student_registration.users.utils import get_default_export_formats
        return get_default_export_formats()


admin.site.register(HouseHold, HouseHoldAdmin)
admin.site.register(Child, ChildAdmin)
admin.site.register(Child2, Child2Admin)
admin.site.register(OutreachYear)
