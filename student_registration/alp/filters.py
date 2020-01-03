from django.utils.translation import ugettext as _

from django_filters import FilterSet, ModelChoiceFilter

from student_registration.schools.models import School, Section, EducationLevel
from student_registration.students.models import Nationality
from .models import Outreach, ALPRound


class OutreachFilter(FilterSet):
    class Meta:
        model = Outreach
        fields = {
            'school': ['exact'],
            'student__first_name': ['contains'],
            'student__father_name': ['contains'],
            'student__last_name': ['contains'],
            'student__mother_fullname': ['contains'],
        }


class PreTest_allFilter(FilterSet):
    level = ModelChoiceFilter(queryset=EducationLevel.objects.all(), empty_label=_('Entrance test'))
    school = ModelChoiceFilter(queryset=School.objects.all(), empty_label=_('School'))

    class Meta:
        model = Outreach
        fields = {
            'school': ['exact'],
            'level': ['exact'],
            'pre_test_room': ['exact'],
            'student__first_name': ['contains'],
            'student__father_name': ['contains'],
            'student__last_name': ['contains'],
        }


class PreTestFilter(FilterSet):
    level = ModelChoiceFilter(queryset=EducationLevel.objects.all(), empty_label=_('Entrance test'))
    #school = ModelChoiceFilter(queryset=School.objects.all(), empty_label=_('School'))

    class Meta:
        model = Outreach
        fields = {
           # 'school': ['exact'],
            'level': ['exact'],
            'pre_test_room': ['exact'],
            'student__first_name': ['contains'],
            'student__father_name': ['contains'],
            'student__last_name': ['contains'],
        }


class PostTestFilter(FilterSet):
    registered_in_level = ModelChoiceFilter(queryset=EducationLevel.objects.all(), empty_label=_('Current Level'))
    school = ModelChoiceFilter(queryset=School.objects.all(), empty_label=_('School'))
    section = ModelChoiceFilter(queryset=Section.objects.all(), empty_label=_('Section'))

    class Meta:
        model = Outreach
        fields = {
            'school': ['exact'],
            'post_test_room': ['exact'],
            'registered_in_level': ['exact'],
            'section': ['exact'],
            'student__first_name': ['contains'],
            'student__father_name': ['contains'],
            'student__last_name': ['contains'],
        }


class SchoolFilter(FilterSet):
    registered_in_level = ModelChoiceFilter(queryset=EducationLevel.objects.all(), empty_label=_('Current Level'))
    section = ModelChoiceFilter(queryset=Section.objects.all(), empty_label=_('Section'))
    student__nationality = ModelChoiceFilter(queryset=Nationality.objects.all(), empty_label=_('Nationality'))

    class Meta:
        model = Outreach
        fields = {
            'registered_in_level': ['exact'],
            'section': ['exact'],
            'student__nationality': ['exact'],
            'student__first_name': ['contains'],
            'student__father_name': ['contains'],
            'student__last_name': ['contains'],
            'student__mother_fullname': ['contains'],
            'student__id_number': ['exact'],
        }
