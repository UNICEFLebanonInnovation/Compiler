from django.utils.translation import ugettext as _

from django_filters import FilterSet, ModelChoiceFilter

from student_registration.locations.models import Location
from student_registration.schools.models import CLMRound, School, Section, ClassRoom


class TeacherFilter(FilterSet):

    class Meta:
        model = School
        fields = {
            'name': ['contains'],
        }
