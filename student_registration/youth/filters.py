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
        choices=Location.objects.filter(parent__isnull=True).values_list('id', 'name_en').order_by('name_en').distinct(),
        empty_label='Governorate'
    )
    adolescent__district = ChoiceFilter(
        choices=Location.objects.filter(parent__isnull=False, type=2).values_list('id', 'name_en').order_by('name_en').distinct(),
        empty_label='district'
    )
    adolescent__cadaster = ChoiceFilter(
        choices=Location.objects.filter(parent__isnull=False, type=3).values_list('id', 'name_en').order_by('name_en').distinct(),
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
        choices=lambda: [
            (mp.id, "{} - {}".format(mp.number, mp.name))
            for mp in sorted(
                MasterProgram.objects.filter(active=True
                                             # , created__year=datetime.datetime.now().year
                                             ),
                key=lambda m: [int(p) for p in m.number.split('.')]
            )
        ],
        field_name='enrolled_programs__master_program',
        label='Master Indicator',
        method='filter_by_master_program',
        widget=forms.SelectMultiple(attrs={'class': 'long-select'})
    )

    sub_program = MultipleChoiceFilter(
        choices=lambda: [
            (sp.id, "{} - {}".format(sp.number, sp.name))
            for sp in sorted(
                SubProgram.objects.filter(master_program__active=True),
                key=lambda s: [int(p) for p in s.number.split('.')]
            )
        ],
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
        choices=Location.objects.filter(parent__isnull=True).values_list('id', 'name_en').order_by('name_en').distinct(),
        empty_label='Governorate'
    )
    adolescent__district = ChoiceFilter(
        choices=Location.objects.filter(parent__isnull=False, type=2).values_list('id', 'name_en').order_by('name_en').distinct(),
        empty_label='District'
    )
    adolescent__cadaster = ChoiceFilter(
        choices=Location.objects.filter(parent__isnull=False, type=3).values_list('id', 'name_en').order_by('name_en').distinct(),
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
        choices=lambda: [
            (mp.id, "{} - {}".format(mp.number, mp.name))
            for mp in sorted(
                MasterProgram.objects.filter(active=True
                                             # , created__year=datetime.datetime.now().year
                                             ),
                key=lambda m: [int(p) for p in m.number.split('.')]
            )
        ],
        field_name='enrolled_programs__master_program',
        label='Master Indicator',
        method='filter_by_master_program',
        widget=forms.SelectMultiple(attrs={'class': 'long-select'})
    )

    sub_program = MultipleChoiceFilter(
        choices=lambda: [
            (sp.id, "{} - {}".format(sp.number, sp.name))
            for sp in sorted(
                SubProgram.objects.filter(master_program__active=True),
                key=lambda s: [int(p) for p in s.number.split('.')]
            )
        ],
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
