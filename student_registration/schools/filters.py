from django.utils.translation import gettext_lazy as _
from django_filters import FilterSet, ChoiceFilter, ModelChoiceFilter
from student_registration.locations.models import Location
from student_registration.schools.models import CLMRound, School, Section, ClassRoom
from model_utils import Choices


class SchoolFilter(FilterSet):
    TRUE_FALSE = Choices(
        ('True', _("Yes")),
        ('False', _("No")),
    )

    governorate = ModelChoiceFilter(queryset=Location.objects.filter(parent__isnull=True), empty_label=_('Governorate'))
    district = ModelChoiceFilter(queryset=Location.objects.filter(parent__isnull=False), empty_label=_('District'))
    is_closed = ChoiceFilter(
        choices=TRUE_FALSE,
        empty_label=_('School is closed'),
        label=_('Is Closed'),
        method='filter_is_closed'
    )

    class Meta:
        model = School
        fields = {
            'number': ['exact'],
            'name': ['contains'],
        }

    def filter_is_closed(self, queryset, name, value):
        if value == 'True':
            return queryset.filter(is_closed=True)
        elif value == 'False':
            return queryset.filter(is_closed=False)
        return queryset
