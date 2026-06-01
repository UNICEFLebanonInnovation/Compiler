from django import forms
from django.utils.translation import gettext as _
from django_filters import (
    FilterSet,
    ModelChoiceFilter,
    ChoiceFilter,
    CharFilter,
    DateFromToRangeFilter,
    DateFilter,
    ModelMultipleChoiceFilter,
    MultipleChoiceFilter
)
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, ButtonHolder, Submit, HTML
import datetime


from student_registration.locations.models import Center, Location
from student_registration.students.models import Nationality
from .models import (
    Registration,
    EnrolledPrograms,
    MasterProgram,
    SubProgram,
    Donor,
    ProgramDocument,
    FundedBy,
    ProjectStatus,
    FocalPoint,
    ProgramDocumentIndicator
)
from student_registration.youth.models import Adolescent
from student_registration.clm.models import Disability, EducationalLevel
from student_registration.schools.models import PartnerOrganization


def _indicator_number_sort_key(indicator):
    try:
        return (0, [int(p) for p in indicator.number.split('.')])
    except (AttributeError, ValueError):
        return (1, indicator.number or '')


def _master_program_choices():
    return [
        (mp.id, "{} - {}".format(mp.number, mp.name))
        for mp in sorted(
            MasterProgram.objects.filter(active=True),
            key=_indicator_number_sort_key
        )
    ]


def _sub_program_choices(master_program_ids=None):
    queryset = SubProgram.objects.filter(master_program__active=True)
    if master_program_ids:
        queryset = queryset.filter(master_program_id__in=master_program_ids)

    return [
        (sp.id, "{} - {}".format(sp.number, sp.name))
        for sp in sorted(queryset, key=_indicator_number_sort_key)
    ]


def _location_choices(location_type=None, parent_ids=None):
    queryset = Location.objects.all()
    if location_type is None:
        queryset = queryset.filter(parent__isnull=True)
    else:
        queryset = queryset.filter(parent__isnull=False, type=location_type)

    if parent_ids:
        queryset = queryset.filter(parent_id__in=parent_ids)

    return queryset.values_list('id', 'name_en').order_by('name_en').distinct()


def _governorate_choices():
    return _location_choices()


def _district_choices(governorate_ids=None):
    return _location_choices(location_type=2, parent_ids=governorate_ids)


def _cadaster_choices(district_ids=None):
    return _location_choices(location_type=3, parent_ids=district_ids)


class PlaceholderFilterSet(FilterSet):
    """Base FilterSet that hides labels and uses placeholders."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.form.helper = FormHelper(self.form)
        self.form.helper.form_method = "get"     # django-filter expects GET
        self.form.helper.form_class = "form-inline"
        self.form.helper.form_tag = True
        self._limit_sub_program_choices_to_selected_master_program()
        self._limit_location_choices_to_selected_parents()
        # self.form.helper.add_input(Submit("submit", "Filter"))
        # self.form.helper.add_input(Rest("Rest", "Cancel"))
        all_fields = list(self.form.fields)  # -> ['type', 'partner', 'round', ...]
        self.form.helper.layout = Layout(
            *all_fields,
            ButtonHolder(
                Submit("submit", "Filter", css_class="btn btn-primary"),
                HTML(
                    """
                     <button type="button" title="Reset" class="btn btn-warning text-white"
                            onclick="window.location.href='{% url 'youth:list' %}'">
                        Reset
                    </button>
                    """
                ),
                HTML(
                    '<a href="#" title="Download" class="btn btn-success download-report">'
                    'Export'
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

    def _get_selected_values(self, field_name):
        if not self.data:
            return []

        values = []
        if hasattr(self.data, 'getlist'):
            values.extend(self.data.getlist(field_name))
            values.extend(self.data.getlist('{}[]'.format(field_name)))

        raw_value = self.data.get(field_name)
        if raw_value:
            values.append(raw_value)

        selected_values = []
        for value in values:
            selected_values.extend(str(value).split(','))

        return [value for value in selected_values if value]

    def _set_choice_field_options(self, field_name, choices):
        existing_choices = list(self.form.fields[field_name].choices)
        empty_choices = existing_choices[:1] if existing_choices and existing_choices[0][0] == '' else []
        self.form.fields[field_name].choices = empty_choices + list(choices)

    def _limit_sub_program_choices_to_selected_master_program(self):
        if 'master_program' not in self.form.fields or 'sub_program' not in self.form.fields:
            return

        master_program_ids = self._get_selected_values('master_program')
        if master_program_ids:
            self.form.fields['sub_program'].choices = _sub_program_choices(master_program_ids)

    def _limit_location_choices_to_selected_parents(self):
        if 'adolescent__governorate' not in self.form.fields:
            return

        governorate_ids = self._get_selected_values('adolescent__governorate')
        district_ids = self._get_selected_values('adolescent__district')

        if governorate_ids and 'adolescent__district' in self.form.fields:
            self._set_choice_field_options('adolescent__district', _district_choices(governorate_ids))

        if district_ids and 'adolescent__cadaster' in self.form.fields:
            self._set_choice_field_options('adolescent__cadaster', _cadaster_choices(district_ids))


class MainFilter(PlaceholderFilterSet):
    adolescent__nationality = ChoiceFilter(choices=Nationality.objects.values_list('id', 'name_en')
                                .order_by('name').distinct(), empty_label='Nationality')

    adolescent__first_name = CharFilter(lookup_expr='icontains' )
    adolescent__father_name = CharFilter(lookup_expr='icontains')
    adolescent__last_name = CharFilter(lookup_expr='icontains')
    adolescent__number = CharFilter(lookup_expr='icontains')
    adolescent__unicef_id = CharFilter(lookup_expr='icontains')
    adolescent__first_phone_number = CharFilter(lookup_expr='icontains')

    class Meta:
        model = Registration
        fields = [
        ]


class FullFilter(PlaceholderFilterSet):
    partner = ChoiceFilter(
        choices=PartnerOrganization.objects.filter(active=True, is_youth=True).values_list('id', 'short_name').order_by('short_name').distinct(), empty_label='Partner')
    adolescent__governorate = ChoiceFilter(
        choices=_governorate_choices,
        empty_label='Governorate'
    )
    adolescent__district = ChoiceFilter(
        choices=_district_choices,
        empty_label='district'
    )
    adolescent__cadaster = ChoiceFilter(
        choices=_cadaster_choices,
        empty_label='Cadaster'
    )

    adolescent__first_name = CharFilter(lookup_expr='icontains')
    adolescent__father_name = CharFilter(lookup_expr='icontains')
    adolescent__last_name = CharFilter(lookup_expr='icontains')
    adolescent__unicef_id = CharFilter(lookup_expr='icontains')
    adolescent__gender = ChoiceFilter(choices=Adolescent.GENDER, empty_label='Gender')
    adolescent__nationality = ChoiceFilter(
        choices=Nationality.objects.values_list('id', 'name_en').order_by('name_en').distinct(),
        empty_label='Nationality'
    )

    adolescent__disability = ChoiceFilter(
        choices=Disability.objects.values_list('id', 'name_en').order_by('name_en').distinct(),
        empty_label='Disability'
    )
    adolescent__first_phone_number = CharFilter(lookup_expr='icontains')

    donor = ChoiceFilter(
        field_name='enrolled_programs__donor',
        choices=Donor.objects.values_list('id', 'name'),
        empty_label='Donor',
        method='filter_by_donor'
    )
    project_code = CharFilter(
        field_name='enrolled_programs__program_document__project_code',
        lookup_expr='icontains',
        label='Project Code'
    )
    program_document = ChoiceFilter(
        field_name='enrolled_programs__program_document',
        choices=ProgramDocument.objects.values_list('id', 'project_name'),
        empty_label='Program Document',
        method='filter_by_program_document'
    )

    start_date = DateFilter(
        field_name='enrolled_programs__completion_date',
        lookup_expr='gte', label='Start Date'
    )
    end_date = DateFilter(
        field_name='enrolled_programs__completion_date',
        lookup_expr='lte', label='End Date'
    )
    master_program = MultipleChoiceFilter(
        choices=_master_program_choices,
        field_name='enrolled_programs__master_program',
        label='Master Indicator',
        method='filter_by_master_program',
        widget=forms.SelectMultiple(attrs={'class': 'long-select'})
    )

    sub_program = MultipleChoiceFilter(
        choices=_sub_program_choices,
        field_name='enrolled_programs__sub_program',
        label='Sub Program',
        method='filter_by_sub_program',
        widget=forms.SelectMultiple(attrs={'class': 'long-select'})
    )

    class Meta:
        model = Registration
        fields = []

    def filter_by_master_program(self, queryset, name, value):
        if value:
            return queryset.filter(enrolled_programs__master_program__in=value)
        return queryset

    def filter_by_sub_program(self, queryset, name, value):
        if value:
            return queryset.filter(enrolled_programs__sub_program__in=value)
        return queryset

    def filter_by_donor(self, queryset, name, value):
        return queryset.filter(enrolled_programs__donor=value)

    def filter_by_program_document(self, queryset, name, value):
        return queryset.filter(enrolled_programs__program_document=value)


class PartnerFilter(PlaceholderFilterSet):

    adolescent__governorate = ChoiceFilter(
        choices=_governorate_choices,
        empty_label='Governorate'
    )
    adolescent__district = ChoiceFilter(
        choices=_district_choices,
        empty_label='District'
    )
    adolescent__cadaster = ChoiceFilter(
        choices=_cadaster_choices,
        empty_label='Cadaster'
    )

    adolescent__first_name = CharFilter(lookup_expr='icontains')
    adolescent__father_name = CharFilter(lookup_expr='icontains')
    adolescent__last_name = CharFilter(lookup_expr='icontains')
    adolescent__unicef_id = CharFilter(lookup_expr='icontains')
    adolescent__gender = ChoiceFilter(choices=Adolescent.GENDER, empty_label='Gender')
    adolescent__nationality = ChoiceFilter(
        choices=Nationality.objects.values_list('id', 'name_en').order_by('name_en').distinct(),
        empty_label='Nationality'
    )

    adolescent__disability = ChoiceFilter(
        choices=Disability.objects.values_list('id', 'name_en').order_by('name_en').distinct(),
        empty_label='Disability'
    )
    adolescent__first_phone_number = CharFilter(lookup_expr='icontains')

    donor = ChoiceFilter(
        field_name='enrolled_programs__donor',
        choices=Donor.objects.values_list('id', 'name'),
        empty_label='Donor',
        method='filter_by_donor'
    )
    project_code = CharFilter(
        field_name='enrolled_programs__program_document__project_code',
        lookup_expr='icontains',
        label='Project Code'
    )
    program_document = ChoiceFilter(
        field_name='enrolled_programs__program_document',
        choices=ProgramDocument.objects.values_list('id', 'project_name'),
        empty_label='Program Document',
        method='filter_by_program_document'
    )
    start_date = DateFilter(
        field_name='enrolled_programs__completion_date',
        lookup_expr='gte', label='Start Date'
    )
    end_date = DateFilter(
        field_name='enrolled_programs__completion_date',
        lookup_expr='lte', label='End Date'
    )
    master_program = MultipleChoiceFilter(
        choices=_master_program_choices,
        field_name='enrolled_programs__master_program',
        label='Master Indicator',
        method='filter_by_master_program',
        widget=forms.SelectMultiple(attrs={'class': 'long-select'})
    )

    sub_program = MultipleChoiceFilter(
        choices=_sub_program_choices,
        field_name='enrolled_programs__sub_program',
        label='Sub Program',
        method='filter_by_sub_program',
        widget=forms.SelectMultiple(attrs={'class': 'long-select'})
    )

    class Meta:
        model = Registration
        fields = []

    def filter_by_master_program(self, queryset, name, value):
        if value:
            return queryset.filter(enrolled_programs__master_program__in=value)
        return queryset

    def filter_by_sub_program(self, queryset, name, value):
        if value:
            return queryset.filter(enrolled_programs__sub_program__in=value)
        return queryset

    def filter_by_donor(self, queryset, name, value):
        return queryset.filter(enrolled_programs__donor=value)

    def filter_by_program_document(self, queryset, name, value):
        return queryset.filter(enrolled_programs__program_document=value)


class PDPlaceholderFilterSet(FilterSet):
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
                    """
                     <button type="button" title="Reset" class="btn btn-warning text-white"
                            onclick="window.location.href='{% url 'youth:pd_list' %}'">
                        Reset
                    </button>
                    """
                ),
                HTML(
                    '<a href="#" title="Download" class="btn btn-success download-report">'
                    'Export'
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


class PDFilter(PDPlaceholderFilterSet):
    current_year = datetime.datetime.now().year
    partner = ChoiceFilter(choices=PartnerOrganization.objects.filter(active=True, is_youth=True).values_list('id', 'short_name')
                                .order_by('short_name').distinct(), empty_label='Partner')
    funded_by = ChoiceFilter(choices=FundedBy.objects.filter(active=True).values_list('id', 'name')
                                 .order_by('name').distinct(), empty_label='Funded By')
    project_status = ChoiceFilter(choices=ProjectStatus.objects.values_list('id', 'name')
                                 .order_by('name').distinct(), empty_label='Status')
    project_code = CharFilter(lookup_expr='icontains')
    project_name = CharFilter(lookup_expr='icontains')
    implementing_partners = CharFilter(lookup_expr='icontains')
    focal_point = ChoiceFilter(choices=FocalPoint.objects.values_list('id', 'name')
                                 .order_by('name').distinct(), empty_label='Focal Point')

    start_date = DateFilter(field_name='start_date',
                            lookup_expr='gte', label='Start Date')
    end_date = DateFilter(field_name='end_date',
                          lookup_expr='lte', label='End Date')
    donors = ModelChoiceFilter(
        queryset=Donor.objects.filter(active=True).all(),
        label='Donors',
        required=False,
        empty_label='Select a Donor'
    )
    master_program = MultipleChoiceFilter(
        choices=lambda: [
            (mp.id, "{} - {}".format(mp.number, mp.name))
            for mp in sorted(
                MasterProgram.objects.filter(active=True),
                key=lambda m: [int(p) for p in m.number.split('.')]
            )
        ],
        label='Master Indicator',
        required=False,
        method='filter_by_master_program',
        widget=forms.SelectMultiple(attrs={'class': 'long-select'})
    )

    class Meta:
        model = ProgramDocument
        fields = [
        ]

    def filter_by_master_program(self, queryset, name, value):
        if value:
            return queryset.filter(
                indicators__master_indicator__in=value
            ).distinct()
        return queryset


class PDPartnerFilter(PDPlaceholderFilterSet):
    current_year = datetime.datetime.now().year
    funded_by = ChoiceFilter(choices=FundedBy.objects.filter(active=True).values_list('id', 'name')
                                 .order_by('name').distinct(), empty_label='Funded By')
    project_status = ChoiceFilter(choices=ProjectStatus.objects.values_list('id', 'name')
                                  .order_by('name').distinct(), empty_label='Status')
    project_code = CharFilter(lookup_expr='icontains')
    project_name = CharFilter(lookup_expr='icontains')
    implementing_partners = CharFilter(lookup_expr='icontains')
    focal_point = ChoiceFilter(choices=FocalPoint.objects.values_list('id', 'name')
                                 .order_by('name').distinct(), empty_label='Focal Point')

    start_date = DateFilter(field_name='start_date',
                            lookup_expr='gte', label='Start Date')
    end_date = DateFilter(field_name='end_date',
                          lookup_expr='lte', label='End Date')

    master_program = MultipleChoiceFilter(
        choices=lambda: [
            (mp.id, "{} - {}".format(mp.number, mp.name))
            for mp in sorted(
                MasterProgram.objects.filter(active=True),
                key=lambda m: [int(p) for p in m.number.split('.')]
            )
        ],
        label='Master Indicator',
        required=False,
        method='filter_by_master_program',
        widget=forms.SelectMultiple(attrs={'class': 'long-select'})
    )

    class Meta:
        model = ProgramDocument
        fields = [
        ]

    def filter_by_master_program(self, queryset, name, value):
        if value:
            return queryset.filter(
                indicators__master_indicator__in=value
            ).distinct()
        return queryset
