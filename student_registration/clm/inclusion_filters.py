from django import forms
from django.utils.translation import gettext as _

from django_filters import FilterSet, ModelChoiceFilter
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, ButtonHolder, Submit, HTML

from student_registration.locations.models import Location
from student_registration.schools.models import CLMRound
from student_registration.students.models import Nationality
from .models import Inclusion, Disability

class PlaceholderFilterSet(FilterSet):
    """Base FilterSet that hides labels and uses placeholders."""

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
                    '<a href="javascript:void(0);" onclick="checkRoundBeforeExport()" title="Download" class="btn btn-outline-success download-report">'
                    '<i class="lnr-download"></i>'
                    '</a>'
                ),
                css_class="d-flex gap-2"  # optional: layout/spacing
            ),
        )
        for name, field in self.form.fields.items():
            label = field.label or name.replace('_', ' ').title()
            field.label = ''
            if isinstance(field.widget, (forms.TextInput, forms.NumberInput)):
                field.widget.attrs.setdefault('placeholder', label)


class CommonFilter(PlaceholderFilterSet):
    round = ModelChoiceFilter(queryset=CLMRound.objects.filter(current_year_inclusion=True).all(), empty_label=_('Round'))
    governorate = ModelChoiceFilter(queryset=Location.objects.filter(parent__isnull=True), empty_label=_('Governorate'))
    district = ModelChoiceFilter(queryset=Location.objects.filter(parent__isnull=False), empty_label=_('District'))
    student__nationality = ModelChoiceFilter(queryset=Nationality.objects.exclude(id=9), empty_label=_('Nationality'))
    disability = ModelChoiceFilter(queryset=Disability.objects.filter(active=True), empty_label=_('Disability'))


class InclusionFilter(CommonFilter):

    class Meta:
        model = Inclusion
        fields = {
            'student__id_number': ['contains'],
            'student__number': ['contains'],
            'internal_number': ['contains'],
            'student__first_name': ['contains'],
            'student__father_name': ['contains'],
            'student__last_name': ['contains'],
            'student__mother_fullname': ['contains'],
            'student__nationality': ['exact'],
            'governorate': ['exact'],
            'district': ['exact'],
            'participation': ['exact'],
            'learning_result': ['exact'],
            'owner__username': ['contains'],
            'disability': ['exact'],
        }
