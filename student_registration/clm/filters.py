from django.utils.translation import ugettext as _

from django_filters import FilterSet, ModelChoiceFilter

from student_registration.locations.models import Location
from student_registration.schools.models import CLMRound, School, Section, ClassRoom
from student_registration.students.models import Nationality
from .models import BLN, RS, CBECE, Cycle


class CommonFilter(FilterSet):
    round = ModelChoiceFilter(queryset=CLMRound.objects.all(), empty_label=_('Round'))
    governorate = ModelChoiceFilter(queryset=Location.objects.filter(parent__isnull=True), empty_label=_('Governorate'))
    district = ModelChoiceFilter(queryset=Location.objects.filter(parent__isnull=False), empty_label=_('District'))
    student__nationality = ModelChoiceFilter(queryset=Nationality.objects.all(), empty_label=_('Nationality'))
    school = ModelChoiceFilter(queryset=School.objects.all(), empty_label=_('School'))
    registered_in_school = ModelChoiceFilter(queryset=School.objects.all(), empty_label=_('Registered in school'))
    section = ModelChoiceFilter(queryset=Section.objects.all(), empty_label=_('Section'))
    grade = ModelChoiceFilter(queryset=ClassRoom.objects.all(), empty_label=_('Class'))
    cycle = ModelChoiceFilter(queryset=Cycle.objects.all(), empty_label=_('Cycle'))


class BLNFilter(CommonFilter):

    class Meta:
        model = BLN
        fields = {
            'round': ['exact'],
            'student__id_number': ['contains'],
            'internal_number': ['contains'],
            'student__first_name': ['contains'],
            'student__father_name': ['contains'],
            'student__last_name': ['contains'],
            'student__mother_fullname': ['contains'],
            'student__nationality': ['exact'],
            'governorate': ['exact'],
            'district': ['exact'],
            'participation': ['exact'],
            'learning_result': ['exact'],
        }


class RSFilter(CommonFilter):
    class Meta:
        model = RS
        fields = {
            'round': ['exact'],
            'student__id_number': ['contains'],
            'internal_number': ['contains'],
            'student__first_name': ['contains'],
            'student__father_name': ['contains'],
            'student__last_name': ['contains'],
            'student__mother_fullname': ['contains'],
            'student__nationality': ['exact'],
            'type': ['exact'],
            'site': ['exact'],
            'school': ['exact'],
            'governorate': ['exact'],
            'district': ['exact'],
            'registered_in_school': ['exact'],
            'shift': ['exact'],
            'grade': ['exact'],
            'section': ['exact'],
            'participation': ['exact'],
            'learning_result': ['exact'],
        }


class CBECEFilter(CommonFilter):
    class Meta:
        model = CBECE
        fields = {
            'round': ['exact'],
            'student__id_number': ['contains'],
            'internal_number': ['contains'],
            'student__first_name': ['contains'],
            'student__father_name': ['contains'],
            'student__last_name': ['contains'],
            'student__mother_fullname': ['contains'],
            'student__nationality': ['exact'],
            'cycle': ['exact'],
            'site': ['exact'],
            'school': ['exact'],
            'governorate': ['exact'],
            'district': ['exact'],
            'participation': ['exact'],
            'learning_result': ['exact'],
        }
