from django.db.models import Q
from django.db.utils import OperationalError, ProgrammingError, NotSupportedError

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

# Utility helpers -----------------------------------------------------------


ROUND_EMPTY_CHOICE = ('no_round', 'No Round')


def _safe_values_list(queryset, include_no_round=False):
    """Evaluate a queryset safely during import time.

    Some environments (like the CI used for automated tests) do not provide
    the PostgreSQL version expected by the production system.  The queryset
    evaluations performed when this module is imported would normally trigger
    a database connection which then raises ``NotSupportedError``.  That in
    turn prevents Django from loading the filters module altogether.  By
    catching the relevant exceptions we allow the application to fall back to
    empty choices while still working with alternative database backends.
    """

    try:
        values = list(queryset)
    except (OperationalError, ProgrammingError, NotSupportedError):
        values = []

    if include_no_round:
        return [ROUND_EMPTY_CHOICE] + values

    return values


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
            ButtonHolder(Submit("submit", "Filter", css_class="btn btn-primary"),
                         HTML('<a href="" title="Async Download" class="btn btn-success download-report-async">Export</a>')
            )
        )
        for name, field in self.form.fields.items():
            label = field.label or name.replace('_', ' ').title()
            field.label = ''
            if isinstance(field.widget, (forms.TextInput, forms.NumberInput)):
                field.widget.attrs.setdefault('placeholder', label)


class MainFilter(PlaceholderFilterSet):
    NO_ROUND_OPTION = ROUND_EMPTY_CHOICE

    type = ChoiceFilter(choices=PACKAGE_TYPES, empty_label='Package type')
    child__first_name = CharFilter(lookup_expr='icontains' )
    child__father_name = CharFilter(lookup_expr='icontains')
    child__last_name = CharFilter(lookup_expr='icontains')
    child__mother_fullname = CharFilter(lookup_expr='icontains')
    child__number = CharFilter(lookup_expr='icontains')
    child__unicef_id = CharFilter(lookup_expr='icontains')
    child__gender = ChoiceFilter(choices=Child.GENDER, empty_label='Gender')
    child__nationality = ChoiceFilter(choices=_safe_values_list(
        Nationality.objects.values_list('id', 'name').order_by('name').distinct()
    ), empty_label='Nationality')
    round = ChoiceFilter(
        choices=_safe_values_list(
            Round.objects.values_list('id', 'name').order_by('name').distinct(),
            include_no_round=True,
        ),
        empty_label='Round',
        method='filter_round'
    )
    programme_type = ChoiceFilter(choices=EducationService.EDUCATION_PROGRAM,
                                  field_name='education_service__education_program',
                                  empty_label='Programme Type', method='filter_education_program')
    child__first_phone_number = CharFilter(lookup_expr='icontains')
    child__second_phone_number = CharFilter(lookup_expr='icontains')
    center = ChoiceFilter(choices=_safe_values_list(
        Center.objects.values_list('id', 'name').order_by('name').distinct()
    ), empty_label='Center')
    center__governorate = ChoiceFilter(choices=_safe_values_list(
        Location.objects.filter(parent__isnull=True).values_list('id', 'name').order_by('name').distinct()
    ), empty_label='Governorate')
    center__caza = ChoiceFilter(choices=_safe_values_list(
        Location.objects.filter(parent__isnull=False, type=2).values_list('id', 'name').order_by('name').distinct()
    ), empty_label='Caza')
    center__cadaster = ChoiceFilter(
        choices=_safe_values_list(
            Location.objects.filter(parent__isnull=False, type=3).values_list('id', 'name').order_by('name').distinct()
        ),
        empty_label='Cadaster')

    class Meta:
        model = Registration
        fields = []

    def filter_round(self, queryset, name, value):
        if value == 'no_round':
            return queryset.filter(round__isnull=True)
        return queryset.filter(**{name: value})

    def filter_education_program(self, queryset, name, value):
        return queryset.filter(education_service__education_program=value)


class FullFilter(PlaceholderFilterSet):
    NO_ROUND_OPTION = ROUND_EMPTY_CHOICE

    type = ChoiceFilter(choices=PACKAGE_TYPES, empty_label='Package type')
    partner = ChoiceFilter(choices=_safe_values_list(
        PartnerOrganization.objects.values_list('id', 'name').order_by('name').distinct()
    ), empty_label='Partner')

    round = ChoiceFilter(
        choices=_safe_values_list(
            Round.objects.values_list('id', 'name').order_by('name').distinct(),
            include_no_round=True,
        ),
        empty_label='Round',
        method='filter_round'
    )

    center = ChoiceFilter(choices=_safe_values_list(
        Center.objects.values_list('id', 'name').order_by('name').distinct()
    ), empty_label='Center')
    center__governorate = ChoiceFilter(choices=_safe_values_list(
        Location.objects.filter(parent__isnull=True).values_list('id', 'name').order_by('name').distinct()
    ), empty_label='Governorate')
    center__caza = ChoiceFilter(choices=_safe_values_list(
        Location.objects.filter(parent__isnull=False, type=2).values_list('id', 'name').order_by('name').distinct()
    ), empty_label='Caza')
    center__cadaster = ChoiceFilter(choices=_safe_values_list(
        Location.objects.filter(parent__isnull=False, type=3).values_list('id', 'name').order_by('name').distinct()
    ), empty_label='Cadaster')

    child__first_name = CharFilter(lookup_expr='icontains')
    child__father_name = CharFilter(lookup_expr='icontains')
    child__last_name = CharFilter(lookup_expr='icontains')
    child__mother_fullname = CharFilter(lookup_expr='icontains')
    child__number = CharFilter(lookup_expr='icontains')
    child__unicef_id = CharFilter(lookup_expr='icontains')
    child__gender = ChoiceFilter(choices=Child.GENDER, empty_label='Gender')
    child__nationality = ChoiceFilter(choices=_safe_values_list(
        Nationality.objects.values_list('id', 'name').order_by('name').distinct()
    ), empty_label='Nationality')
    programme_type = ChoiceFilter(choices=EducationService.EDUCATION_PROGRAM,
                                  field_name='education_service__education_program',
                                  empty_label='Programme Type', method='filter_education_program')

    child__first_phone_number = CharFilter(lookup_expr='icontains')
    child__second_phone_number = CharFilter(lookup_expr='icontains')
    deleted = ChoiceFilter(
        choices=DELETED_CHOICES,
        label='Deleted',
        empty_label='Deleted',
        method='filter_deleted',
    )

    class Meta:
        model = Registration
        fields = [
        ]


    def filter_deleted(self, queryset, name, value):
        if value == 'yes':
            return queryset.filter(deleted=True)
        elif value == 'no':
            return queryset.filter(Q(deleted=False) | Q(deleted__isnull=True))
        return queryset

    def filter_round(self, queryset, name, value):
        if value == 'no_round':
            return queryset.filter(round__isnull=True)
        return queryset.filter(**{name: value})

    def filter_education_program(self, queryset, name, value):
        return queryset.filter(education_service__education_program=value)
