from django.db.models import Q

from django_filters import (
    FilterSet,
    ModelChoiceFilter,
    ChoiceFilter,
    CharFilter,
    BooleanFilter,
)
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, ButtonHolder, Submit, HTML
from django import forms

from student_registration.locations.models import Center, Location
from student_registration.students.models import Nationality
from .models import (
    Registration,
    EducationService,
    Round,
    PACKAGE_TYPES
)
from student_registration.child.models import Child
from student_registration.schools.models import PartnerOrganization

DELETED_CHOICES = [
    ('', 'All'),
    ('yes', 'Yes'),
    ('no', 'No'),
]

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
            ButtonHolder(Submit("submit", "Filter", css_class="btn btn-primary"),
                         HTML('<a href="" title="Async Download" class="btn btn-success download-report-async">Export</a>')
            )
        )
        for name, field in self.form.fields.items():
            label = field.label or name.replace('_', ' ').title()
            field.label = ''
            if isinstance(field.widget, (forms.TextInput, forms.NumberInput)):
                field.widget.attrs.setdefault('placeholder', label)

        self._apply_dynamic_choice_filters()

    @classmethod
    def dynamic_choice_factories(cls):
        """Mapping of filter names to callables returning choices at runtime."""
        return {}

    def _apply_dynamic_choice_filters(self):
        for name, factory in self.dynamic_choice_factories().items():
            if name not in self.filters:
                continue
            choices = factory() if callable(factory) else factory
            if choices is None:
                continue
            filter_obj = self.filters[name]
            # Update the underlying field and any rendered form widgets.
            filter_obj.extra['choices'] = choices
            filter_obj.field.choices = choices
            if name in self.form.fields:
                self.form.fields[name].choices = choices


class MainFilter(PlaceholderFilterSet):
    NO_ROUND_OPTION = ('no_round', 'No Round')

    type = ChoiceFilter(choices=PACKAGE_TYPES, empty_label='Package type')
    child__first_name = CharFilter(lookup_expr='icontains' )
    child__father_name = CharFilter(lookup_expr='icontains')
    child__last_name = CharFilter(lookup_expr='icontains')
    child__mother_fullname = CharFilter(lookup_expr='icontains')
    child__number = CharFilter(lookup_expr='icontains')
    child__unicef_id = CharFilter(lookup_expr='icontains')
    child__gender = ChoiceFilter(choices=Child.GENDER, empty_label='Gender')
    child__nationality = ChoiceFilter(choices=(), empty_label='Nationality')
    round = ChoiceFilter(
        choices=(),
        empty_label='Round',
        method='filter_round'
    )
    programme_type = ChoiceFilter(choices=EducationService.EDUCATION_PROGRAM,
                                  field_name='education_service__education_program',
                                  empty_label='Programme Type', method='filter_education_program')
    child__first_phone_number = CharFilter(lookup_expr='icontains')
    child__second_phone_number = CharFilter(lookup_expr='icontains')
    center = ChoiceFilter(choices=(), empty_label='Center')
    center__governorate = ChoiceFilter(choices=(), empty_label='Governorate')
    center__caza = ChoiceFilter(choices=(), empty_label='Caza')
    center__cadaster = ChoiceFilter(choices=(), empty_label='Cadaster')

    class Meta:
        model = Registration
        fields = []

    @classmethod
    def dynamic_choice_factories(cls):
        factories = dict(super().dynamic_choice_factories())
        factories.update({
            'child__nationality': lambda: list(
                Nationality.objects.values_list('id', 'name').order_by('name').distinct()
            ),
            'round': lambda cls=cls: [cls.NO_ROUND_OPTION] + list(
                Round.objects.values_list('id', 'name').order_by('name').distinct()
            ),
            'center': lambda: list(
                Center.objects.values_list('id', 'name').order_by('name').distinct()
            ),
            'center__governorate': lambda: list(
                Location.objects.filter(parent__isnull=True)
                .values_list('id', 'name').order_by('name').distinct()
            ),
            'center__caza': lambda: list(
                Location.objects.filter(parent__isnull=False, type=2)
                .values_list('id', 'name').order_by('name').distinct()
            ),
            'center__cadaster': lambda: list(
                Location.objects.filter(parent__isnull=False, type=3)
                .values_list('id', 'name').order_by('name').distinct()
            ),
        })
        return factories

    def filter_round(self, queryset, name, value):
        if value == 'no_round':
            return queryset.filter(round__isnull=True)
        return queryset.filter(**{name: value})

    def filter_education_program(self, queryset, name, value):
        return queryset.filter(education_service__education_program=value)


class FullFilter(PlaceholderFilterSet):
    NO_ROUND_OPTION = ('no_round', 'No Round')

    type = ChoiceFilter(choices=PACKAGE_TYPES, empty_label='Package type')
    partner = ChoiceFilter(choices=(), empty_label='Partner')

    round = ChoiceFilter(
        choices=(),
        empty_label='Round',
        method='filter_round'
    )

    center = ChoiceFilter(choices=(), empty_label='Center')
    center__governorate = ChoiceFilter(choices=(), empty_label='Governorate')
    center__caza = ChoiceFilter(choices=(), empty_label='Caza')
    center__cadaster = ChoiceFilter(choices=(), empty_label='Cadaster')

    child__first_name = CharFilter(lookup_expr='icontains')
    child__father_name = CharFilter(lookup_expr='icontains')
    child__last_name = CharFilter(lookup_expr='icontains')
    child__mother_fullname = CharFilter(lookup_expr='icontains')
    child__number = CharFilter(lookup_expr='icontains')
    child__unicef_id = CharFilter(lookup_expr='icontains')
    child__gender = ChoiceFilter(choices=Child.GENDER, empty_label='Gender')
    child__nationality = ChoiceFilter(choices=(), empty_label='Nationality')
    programme_type = ChoiceFilter(choices=EducationService.EDUCATION_PROGRAM,
                                  field_name='education_service__education_program',
                                  empty_label='Programme Type', method='filter_education_program')

    child__first_phone_number = CharFilter(lookup_expr='icontains')
    child__second_phone_number = CharFilter(lookup_expr='icontains')

    class Meta:
        model = Registration
        fields = [
        ]

    @classmethod
    def dynamic_choice_factories(cls):
        factories = dict(super().dynamic_choice_factories())
        factories.update({
            'partner': lambda: list(
                PartnerOrganization.objects.values_list('id', 'name')
                .order_by('name').distinct()
            ),
            'child__nationality': lambda: list(
                Nationality.objects.values_list('id', 'name').order_by('name').distinct()
            ),
            'round': lambda cls=cls: [cls.NO_ROUND_OPTION] + list(
                Round.objects.values_list('id', 'name').order_by('name').distinct()
            ),
            'center': lambda: list(
                Center.objects.values_list('id', 'name').order_by('name').distinct()
            ),
            'center__governorate': lambda: list(
                Location.objects.filter(parent__isnull=True)
                .values_list('id', 'name').order_by('name').distinct()
            ),
            'center__caza': lambda: list(
                Location.objects.filter(parent__isnull=False, type=2)
                .values_list('id', 'name').order_by('name').distinct()
            ),
            'center__cadaster': lambda: list(
                Location.objects.filter(parent__isnull=False, type=3)
                .values_list('id', 'name').order_by('name').distinct()
            ),
        })
        return factories

    def filter_round(self, queryset, name, value):
        if value == 'no_round':
            return queryset.filter(round__isnull=True)
        return queryset.filter(**{name: value})

    def filter_education_program(self, queryset, name, value):
        return queryset.filter(education_service__education_program=value)
