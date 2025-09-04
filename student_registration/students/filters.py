from django.utils.translation import gettext as _

import django_filters
from django_filters import FilterSet, ModelChoiceFilter,CharFilter
from django.db.models import Value, CharField, Func
from django.db.models.functions import Concat,Cast
from collections import OrderedDict

from student_registration.schools.models import School, CLMRound
from student_registration.students.models import Teacher


class LPAD(Func):
    function = 'LPAD'
    output_field = CharField()


class TeacherFilter(FilterSet):
    round = ModelChoiceFilter(queryset=CLMRound.objects.filter(current_year=True).all(), empty_label=_('Round'))
    school = ModelChoiceFilter(queryset=School.objects.filter(is_closed=False), empty_label=_('School'))
    class Meta:
        model = Teacher
        fields = OrderedDict((
                ('first_name', ['contains']),
                ('father_name', ['contains']),
                ('last_name', ['contains']),
                ('unicef_id', ['contains']),
                ('school', ['exact']),
                ('round', ['exact']),
        ))


