from django.utils.translation import ugettext as _

from django_filters import FilterSet, ModelChoiceFilter
from collections import OrderedDict

from student_registration.schools.models import School
from student_registration.students.models import Teacher


class TeacherFilter(FilterSet):
    school = ModelChoiceFilter(queryset=School.objects.filter(is_closed=False), empty_label=_('School'))

    class Meta:
        model = Teacher
        fields = OrderedDict((
                ('first_name' , ['contains']),
                ('father_name', ['contains']),
                ('last_name', ['contains']),
                ('school', ['exact']),
        ))

