from django.utils.translation import gettext_lazy as _
from django import forms
from django_filters import (
    FilterSet,
    ModelChoiceFilter,
    ChoiceFilter,
    CharFilter
)
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, ButtonHolder, Submit, HTML
from model_utils import Choices
from .models import (
    Center,
    Location
)
from student_registration.filter_labels import label_filter_fields

class PlaceholderFilterSet(FilterSet):
    """Base FilterSet with the shared toolbar (Filter, Export) and a visible label on every control."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.form.helper = FormHelper(self.form)
        self.form.helper.form_method = "get"     # django-filter expects GET
        self.form.helper.form_class = "form-inline"
        self.form.helper.form_tag = True
        # self.form.helper.add_input(Submit("submit", "Filter"))
        # self.form.helper.add_input(Rest("Rest", "Cancel"))
        all_fields = list(self.form.fields)  # -> ['type', 'partner', 'round', ...]
        self.form.helper.layout = Layout(
            *all_fields,
            ButtonHolder(
                Submit("submit", "Filter", css_class="btn btn-primary"),
                HTML(
                    '<a href="#" title="Download" class="btn btn-success download-center-report">'
                    'Export'
                    '</a>'
                ),
                css_class="d-flex gap-2"  # optional: layout/spacing
            ),
        )
        # Visible labels for every control; see student_registration/filter_labels.py.
        label_filter_fields(self.form)


class CenterFilter(PlaceholderFilterSet):
    TRUE_FALSE = Choices(
        ('True', _("Yes")),
        ('False', _("No")),
    )
    YES_NO = Choices(
        ('Yes', _("Yes")),
        ('No', _("No")),
    )
    name = CharFilter(lookup_expr='icontains' )
    governorate = ModelChoiceFilter(queryset=Location.objects.filter(parent__isnull=True), empty_label=_('Governorate'))
    is_active = ChoiceFilter(
        choices=TRUE_FALSE,
        empty_label=_('Center is active'),
        label=_('Is Active'),
        method='filter_is_active'
    )
    type = ChoiceFilter(
        choices=Center.TYPE,
        empty_label=_('Type'),
        label=_('Type'),
    )
    is_tarl = ChoiceFilter(
        choices=YES_NO,
        empty_label=_('Is TARL center'),
        label=_('Is TARL center'),
    )
    active_during_emergency = ChoiceFilter(
        choices=YES_NO,
        empty_label=_('Active in emergency?'),
        label=_('Active in emergency?'),
    )

    class Meta:
        model = Center
        fields = [
            'name',
            'type',
            'governorate',
            'is_tarl',
            'active_during_emergency'
        ]

    def filter_is_active(self, queryset, name, value):
        if value == 'True':
            return queryset.filter(is_active=True)
        elif value == 'False':
            return queryset.filter(is_active=False)
        return queryset


