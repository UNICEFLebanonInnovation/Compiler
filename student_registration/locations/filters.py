from django.utils.translation import ugettext as _

from django_filters import (
    FilterSet,
    ModelChoiceFilter,
    ChoiceFilter,
    CharFilter
)

from .models import (
    Center,
    Location
)


class CenterFilter(FilterSet):

    name = CharFilter(lookup_expr='icontains' )

    class Meta:
        model = Center
        fields = [
            'name',
            'type'
        ]


