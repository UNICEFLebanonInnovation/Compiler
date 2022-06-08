from django.utils.translation import ugettext as _

from django_filters import FilterSet, ModelChoiceFilter

from student_registration.locations.models import Location
from student_registration.schools.models import CLMRound, School, Section, ClassRoom


class SchoolFilter(FilterSet):
    governorate = ModelChoiceFilter(queryset=Location.objects.filter(parent__isnull=True), empty_label=_('Governorate'))
    district = ModelChoiceFilter(queryset=Location.objects.filter(parent__isnull=False), empty_label=_('District'))

    class Meta:
        model = School
        fields = {
            # 'governorate': ['exact'],
            # 'district': ['exact'],
            'number': ['exact'],
            'name': ['contains'],
        }
