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
    governorate = ModelChoiceFilter(queryset=Location.objects.filter(parent__isnull=True), empty_label=_('Governorate'))
    class Meta:
        model = Center
        fields = [
            'name',
            'type',
            'governorate'
        ]


