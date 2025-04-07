from django.utils.translation import ugettext as _

import django_filters
from django_filters import FilterSet, ModelChoiceFilter
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
    id_reference_display = django_filters.CharFilter(method='filter_id_reference', label='ID Reference')


    class Meta:
        model = Teacher
        fields = OrderedDict((
                ('first_name', ['contains']),
                ('father_name', ['contains']),
                ('last_name', ['contains']),
                ('school', ['exact']),
                ('round', ['exact']),
        ))

    def filter_id_reference(self, queryset, name, value):
        return queryset.annotate(
            id_reference=Concat(
                Value('TCH-'),
                LPAD(Cast('id', CharField(max_length=10)), 5, Value('0'))
            )
        ).filter(id_reference__icontains=value)


    def filter_id_reference(self, queryset, name, value):
        return queryset.annotate(
            id_reference_display=Concat(
                Value('TCH-'),
                LPAD(Cast('id', CharField(max_length=10)), 5, Value('0'))
            )
        ).filter(id_reference_display__icontains=value)

