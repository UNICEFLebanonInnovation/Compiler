from django.utils.translation import ugettext as _

from django_filters import FilterSet, ModelChoiceFilter

from model_utils import Choices
from student_registration.schools.models import EducationYear, Section, ClassRoom, School
from student_registration.students.models import Nationality
from .models import Enrollment


class CommonFilter(FilterSet):
    student__nationality = ModelChoiceFilter(queryset=Nationality.objects.all(), empty_label=_('Nationality'))
    section = ModelChoiceFilter(queryset=Section.objects.all(), empty_label=_('Section'))
    classroom = ModelChoiceFilter(queryset=ClassRoom.objects.all(), empty_label=_('Class'))


class EnrollmentFilter(CommonFilter):
    class Meta:
        model = Enrollment
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


class EnrollmentOldDataFilter(CommonFilter):
    education_year = ModelChoiceFilter(queryset=EducationYear.objects.filter(current_year=False),
                                       empty_label=_('Education year'))

    class Meta:
        model = Enrollment
        fields = {
            'education_year': ['exact'],
            'classroom': ['exact'],
            'section': ['exact'],
            'student__first_name': ['contains'],
            'student__father_name': ['contains'],
            'student__last_name': ['contains'],
            'student__mother_fullname': ['contains'],
            'student__id_number': ['contains'],
            'student__nationality': ['exact'],
        }


class Common_ByRegion_Filter(FilterSet):
    school = ModelChoiceFilter(queryset=School.objects.all(), empty_label=_('School'))
    classroom = ModelChoiceFilter(queryset=ClassRoom.objects.all(), empty_label=_('Class'))
    section = ModelChoiceFilter(queryset=Section.objects.all(), empty_label=_('Section'))
    student__nationality = ModelChoiceFilter(queryset=Nationality.objects.all(), empty_label=_('Nationality'))


class Enrollment_by_region_Filter(Common_ByRegion_Filter):
    class Meta:
        model = Enrollment
        fields = {
            'school': ['exact'],
            'is_justified': ['exact'],
            'classroom': ['exact'],
            'section': ['exact'],
            'student__first_name': ['contains'],
            'student__father_name': ['contains'],
            'student__last_name': ['contains'],
            'student__mother_fullname': ['contains'],
            'student__id_number': ['contains'],
            'student__nationality': ['exact'],
        }
