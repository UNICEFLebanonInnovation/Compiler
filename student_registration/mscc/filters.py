from django.db.models import Q
from django.db.utils import NotSupportedError, OperationalError, ProgrammingError

from django_filters import (
    FilterSet,
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

    def _set_filter_choices(self, filter_name, choices):
        """Safely assign choices to a filter without raising DB errors."""

        flt = self.filters.get(filter_name)
        if not flt:
            return

        flt.extra['choices'] = choices
        flt.field.choices = choices

    def _build_choices(self, empty_label, queryset=None, extra_choices=None):
        """Return choices built from a queryset while handling DB errors."""

        extra_choices = list(extra_choices or [])
        choices = [('', empty_label)] + extra_choices

        if queryset is None:
            return choices

        try:
            choices.extend(queryset.values_list('id', 'name'))
        except (NotSupportedError, OperationalError, ProgrammingError):
            # The database might be unavailable or not supported in the
            # execution environment (e.g. CI using SQLite). In such cases we
            # silently fall back to the base choices so that importing the
            # filters module doesn't crash.
            pass

        return choices


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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._set_filter_choices(
            'round',
            self._build_choices(
                'Round',
                queryset=Round.objects.order_by('name'),
                extra_choices=[self.NO_ROUND_OPTION]
            )
        )
        self._set_filter_choices(
            'child__nationality',
            self._build_choices('Nationality', Nationality.objects.order_by('name').distinct())
        )
        self._set_filter_choices(
            'center',
            self._build_choices('Center', Center.objects.order_by('name').distinct())
        )
        self._set_filter_choices(
            'center__governorate',
            self._build_choices(
                'Governorate',
                Location.objects.filter(parent__isnull=True).order_by('name').distinct()
            )
        )
        self._set_filter_choices(
            'center__caza',
            self._build_choices(
                'Caza',
                Location.objects.filter(parent__isnull=False, type=2).order_by('name').distinct()
            )
        )
        self._set_filter_choices(
            'center__cadaster',
            self._build_choices(
                'Cadaster',
                Location.objects.filter(parent__isnull=False, type=3).order_by('name').distinct()
            )
        )

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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._set_filter_choices(
            'round',
            self._build_choices(
                'Round',
                queryset=Round.objects.order_by('name'),
                extra_choices=[self.NO_ROUND_OPTION]
            )
        )
        self._set_filter_choices(
            'partner',
            self._build_choices('Partner', PartnerOrganization.objects.order_by('name').distinct())
        )
        self._set_filter_choices(
            'center',
            self._build_choices('Center', Center.objects.order_by('name').distinct())
        )
        self._set_filter_choices(
            'child__nationality',
            self._build_choices('Nationality', Nationality.objects.order_by('name').distinct())
        )
        self._set_filter_choices(
            'center__governorate',
            self._build_choices(
                'Governorate',
                Location.objects.filter(parent__isnull=True).order_by('name').distinct()
            )
        )
        self._set_filter_choices(
            'center__caza',
            self._build_choices(
                'Caza',
                Location.objects.filter(parent__isnull=False, type=2).order_by('name').distinct()
            )
        )
        self._set_filter_choices(
            'center__cadaster',
            self._build_choices(
                'Cadaster',
                Location.objects.filter(parent__isnull=False, type=3).order_by('name').distinct()
            )
        )

    def filter_round(self, queryset, name, value):
        if value == 'no_round':
            return queryset.filter(round__isnull=True)
        return queryset.filter(**{name: value})

    def filter_education_program(self, queryset, name, value):
        return queryset.filter(education_service__education_program=value)
