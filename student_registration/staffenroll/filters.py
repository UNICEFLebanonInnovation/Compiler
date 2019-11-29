from django.utils.translation import ugettext as _

from django_filters import FilterSet, ModelChoiceFilter

from student_registration.schools.models import EducationYear, Section, ClassRoom
from student_registration.students.models import Nationality
from .models import StaffEnroll


class CommonFilter(FilterSet):
    section = ModelChoiceFilter(queryset=Section.objects.all(), empty_label=_('Section'))
    classroom = ModelChoiceFilter(queryset=ClassRoom.objects.all(), empty_label=_('Class'))


class StaffEnrollFilter(CommonFilter):
    class Meta:
        model = StaffEnroll
        fields = {
            'classroom': ['exact'],
            'section': ['exact'],
            'student__first_name': ['contains'],
            'student__father_name': ['contains'],
            'student__last_name': ['contains'],
            'student__mother_fullname': ['contains'],
            'student__id_number': ['contains'],
            'student__nationality': ['exact'],
        }


