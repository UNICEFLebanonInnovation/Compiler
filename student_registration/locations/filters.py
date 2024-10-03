from django.utils.translation import gettext_lazy as _
from django_filters import (
    FilterSet,
    ModelChoiceFilter,
    ChoiceFilter,
    CharFilter
)
from model_utils import Choices
from .models import (
    Center,
    Location
)


class CenterFilter(FilterSet):
    TRUE_FALSE = Choices(
        ('True', _("Yes")),
        ('False', _("No")),
    )
    name = CharFilter(lookup_expr='icontains' )
    governorate = ModelChoiceFilter(queryset=Location.objects.filter(parent__isnull=True), empty_label=_('Governorate'))
    is_active = ChoiceFilter(
        choices=TRUE_FALSE,
        empty_label=_('Center is active'),
        label=_('Is Active'),
        method='filter_is_active'
    )

    class Meta:
        model = Center
        fields = [
            'name',
            'type',
            'governorate',

        ]

    def filter_is_active(self, queryset, name, value):
        if value == 'True':
            return queryset.filter(is_active=True)
        elif value == 'False':
            return queryset.filter(is_active=False)
        return queryset


