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
    """Base FilterSet that hides labels, uses placeholders, and defers DB work."""

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

        self._apply_dynamic_choice_filters()

    @classmethod
    def dynamic_choice_factories(cls):
        return {}

    def _apply_dynamic_choice_filters(self):
        for name, factory in self.dynamic_choice_factories().items():
            if name not in self.filters:
                continue
            choices = factory() if callable(factory) else factory
            if choices is None:
                continue
            filter_obj = self.filters[name]
            filter_obj.extra['choices'] = choices
            filter_obj.field.choices = choices
            if name in self.form.fields:
                self.form.fields[name].choices = choices


class MainFilter(PlaceholderFilterSet):
    adolescent__nationality = ChoiceFilter(choices=(), empty_label='Nationality')

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

    @classmethod
    def dynamic_choice_factories(cls):
        factories = dict(super().dynamic_choice_factories())
        factories.update({
            'adolescent__nationality': lambda: list(
                Nationality.objects.values_list('id', 'name').order_by('name').distinct()
            ),
        })
        return factories


class FullFilter(PlaceholderFilterSet):
    partner = ChoiceFilter(choices=(), empty_label='Partner')
    adolescent__governorate = ChoiceFilter(choices=(), empty_label='Governorate')
    adolescent__district = ChoiceFilter(choices=(), empty_label='district')
    adolescent__cadaster = ChoiceFilter(choices=(), empty_label='Cadaster')

    adolescent__first_name = CharFilter(lookup_expr='icontains')
    adolescent__father_name = CharFilter(lookup_expr='icontains')
    adolescent__last_name = CharFilter(lookup_expr='icontains')
    adolescent__unicef_id = CharFilter(lookup_expr='icontains')
    adolescent__gender = ChoiceFilter(choices=Adolescent.GENDER, empty_label='Gender')
    adolescent__nationality = ChoiceFilter(choices=(), empty_label='Nationality')

    adolescent__disability = ChoiceFilter(choices=(), empty_label='Disability')
    adolescent__first_phone_number = CharFilter(lookup_expr='icontains')

    donor = ChoiceFilter(
        field_name='enrolled_programs__donor',
        choices=(),
        empty_label='Donor',
        method='filter_by_donor'
    )
    program_document = ChoiceFilter(
        field_name='enrolled_programs__program_document',
        choices=(),
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

    @classmethod
    def dynamic_choice_factories(cls):
        factories = dict(super().dynamic_choice_factories())
        factories.update({
            'partner': lambda: list(
                PartnerOrganization.objects.filter(active=True, is_youth=True)
                .values_list('id', 'short_name').order_by('short_name').distinct()
            ),
            'adolescent__governorate': lambda: list(
                Location.objects.filter(parent__isnull=True)
                .values_list('id', 'name').order_by('name').distinct()
            ),
            'adolescent__district': lambda: list(
                Location.objects.filter(parent__isnull=False, type=2)
                .values_list('id', 'name').order_by('name').distinct()
            ),
            'adolescent__cadaster': lambda: list(
                Location.objects.filter(parent__isnull=False, type=3)
                .values_list('id', 'name').order_by('name').distinct()
            ),
            'adolescent__nationality': lambda: list(
                Nationality.objects.values_list('id', 'name').order_by('name').distinct()
            ),
            'adolescent__disability': lambda: list(
                Disability.objects.values_list('id', 'name').order_by('name').distinct()
            ),
            'donor': lambda: list(
                Donor.objects.values_list('id', 'name')
            ),
            'program_document': lambda: list(
                ProgramDocument.objects.values_list('id', 'project_name')
            ),
        })
        return factories

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

    adolescent__governorate = ChoiceFilter(choices=(), empty_label='Governorate')
    adolescent__district = ChoiceFilter(choices=(), empty_label='District')
    adolescent__cadaster = ChoiceFilter(choices=(), empty_label='Cadaster')

    adolescent__first_name = CharFilter(lookup_expr='icontains')
    adolescent__father_name = CharFilter(lookup_expr='icontains')
    adolescent__last_name = CharFilter(lookup_expr='icontains')
    adolescent__unicef_id = CharFilter(lookup_expr='icontains')
    adolescent__gender = ChoiceFilter(choices=Adolescent.GENDER, empty_label='Gender')
    adolescent__nationality = ChoiceFilter(choices=(), empty_label='Nationality')

    adolescent__disability = ChoiceFilter(choices=(), empty_label='Disability')
    adolescent__first_phone_number = CharFilter(lookup_expr='icontains')

    donor = ChoiceFilter(
        field_name='enrolled_programs__donor',
        choices=(),
        empty_label='Donor',
        method='filter_by_donor'
    )
    program_document = ChoiceFilter(
        field_name='enrolled_programs__program_document',
        choices=(),
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

    @classmethod
    def dynamic_choice_factories(cls):
        factories = dict(super().dynamic_choice_factories())
        factories.update({
            'adolescent__governorate': lambda: list(
                Location.objects.filter(parent__isnull=True)
                .values_list('id', 'name').order_by('name').distinct()
            ),
            'adolescent__district': lambda: list(
                Location.objects.filter(parent__isnull=False, type=2)
                .values_list('id', 'name').order_by('name').distinct()
            ),
            'adolescent__cadaster': lambda: list(
                Location.objects.filter(parent__isnull=False, type=3)
                .values_list('id', 'name').order_by('name').distinct()
            ),
            'adolescent__nationality': lambda: list(
                Nationality.objects.values_list('id', 'name').order_by('name').distinct()
            ),
            'adolescent__disability': lambda: list(
                Disability.objects.values_list('id', 'name').order_by('name').distinct()
            ),
            'donor': lambda: list(
                Donor.objects.values_list('id', 'name')
            ),
            'program_document': lambda: list(
                ProgramDocument.objects.values_list('id', 'project_name')
            ),
        })
        return factories

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
    """Base FilterSet that hides labels, uses placeholders, and defers DB work."""

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

        self._apply_dynamic_choice_filters()

    @classmethod
    def dynamic_choice_factories(cls):
        return {}

    def _apply_dynamic_choice_filters(self):
        for name, factory in self.dynamic_choice_factories().items():
            if name not in self.filters:
                continue
            choices = factory() if callable(factory) else factory
            if choices is None:
                continue
            filter_obj = self.filters[name]
            filter_obj.extra['choices'] = choices
            filter_obj.field.choices = choices
            if name in self.form.fields:
                self.form.fields[name].choices = choices


class PDFilter(PDPlaceholderFilterSet):
    current_year = datetime.datetime.now().year
    partner = ChoiceFilter(choices=(), empty_label='Partner')
    funded_by = ChoiceFilter(choices=(), empty_label='Funded By')
    project_status = ChoiceFilter(choices=(), empty_label='Status')
    project_code = CharFilter(lookup_expr='icontains')
    project_name = CharFilter(lookup_expr='icontains')
    implementing_partners = CharFilter(lookup_expr='icontains')
    focal_point = ChoiceFilter(choices=(), empty_label='Focal Point')

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

    @classmethod
    def dynamic_choice_factories(cls):
        factories = dict(super().dynamic_choice_factories())
        factories.update({
            'partner': lambda: list(
                PartnerOrganization.objects.filter(active=True, is_youth=True)
                .values_list('id', 'short_name').order_by('short_name').distinct()
            ),
            'funded_by': lambda: list(
                FundedBy.objects.filter(active=True)
                .values_list('id', 'name').order_by('name').distinct()
            ),
            'project_status': lambda: list(
                ProjectStatus.objects.values_list('id', 'name')
                .order_by('name').distinct()
            ),
            'focal_point': lambda: list(
                FocalPoint.objects.values_list('id', 'name')
                .order_by('name').distinct()
            ),
        })
        return factories

    def filter_by_master_program(self, queryset, name, value):
        if value:
            return queryset.filter(
                indicators__master_indicator__in=value
            ).distinct()
        return queryset


class PDPartnerFilter(PDPlaceholderFilterSet):
    current_year = datetime.datetime.now().year
    funded_by = ChoiceFilter(choices=(), empty_label='Funded By')
    project_status = ChoiceFilter(choices=(), empty_label='Status')
    project_code = CharFilter(lookup_expr='icontains')
    project_name = CharFilter(lookup_expr='icontains')
    implementing_partners = CharFilter(lookup_expr='icontains')
    focal_point = ChoiceFilter(choices=(), empty_label='Focal Point')

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

    @classmethod
    def dynamic_choice_factories(cls):
        factories = dict(super().dynamic_choice_factories())
        factories.update({
            'funded_by': lambda: list(
                FundedBy.objects.filter(active=True)
                .values_list('id', 'name').order_by('name').distinct()
            ),
            'project_status': lambda: list(
                ProjectStatus.objects.values_list('id', 'name')
                .order_by('name').distinct()
            ),
            'focal_point': lambda: list(
                FocalPoint.objects.values_list('id', 'name')
                .order_by('name').distinct()
            ),
        })
        return factories

    def filter_by_master_program(self, queryset, name, value):
        if value:
            return queryset.filter(
                indicators__master_indicator__in=value
            ).distinct()
        return queryset
