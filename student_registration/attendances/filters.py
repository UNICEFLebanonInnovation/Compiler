from django.utils.translation import gettext as _

from django_filters import FilterSet, ModelChoiceFilter,ChoiceFilter


from student_registration.locations.models import Location
from student_registration.schools.models import CLMRound, School, Section, ClassRoom
# from .models import CLMAttendanceStudent, CLMAttendance
from student_registration.clm.models import Bridging


class CLMAttendanceStudentFilter(FilterSet):
    school = ModelChoiceFilter(queryset=School.objects.filter(is_closed=False), empty_label=_('School'))
    registration_level = ChoiceFilter(choices=Bridging.REGISTRATION_LEVEL)

    class Meta:
        model = Bridging
        fields = {
        }
