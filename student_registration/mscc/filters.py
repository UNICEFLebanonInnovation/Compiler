from django.utils.translation import ugettext as _

from django_filters import FilterSet, ModelChoiceFilter

from student_registration.locations.models import Center, Location
from student_registration.students.models import Nationality
from .models import (
    Registration,
)


# class CommonFilter(FilterSet):
    # round = ModelChoiceFilter(queryset=CLMRound.objects.all(), empty_label=_('Round'))
    # governorate = ModelChoiceFilter(queryset=Location.objects.filter(parent__isnull=True), empty_label=_('Governorate'))
    # center = ModelChoiceFilter(queryset=Center.objects.filter(), empty_label=_('Center'))
    # child__nationality = ModelChoiceFilter(queryset=Nationality.objects.exclude(id=9), empty_label=_('Nationality'))
    # disability = ModelChoiceFilter(queryset=Disability.objects.filter(active=True), empty_label=_('Disability'))


class MainFilter(FilterSet):

    class Meta:
        model = Registration
        fields = {
            # 'child__id_number': ['contains'],
            # 'child__number': ['contains'],
            'child__first_name': ['contains'],
            'child__father_name': ['contains'],
            'child__last_name': ['contains'],
            'child__mother_fullname': ['contains'],
            'child__nationality': ['exact'],
            # 'center__governorate': ['exact'],
            'center': ['exact'],
        }

