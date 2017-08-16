from django_filters import FilterSet

from .models import Outreach


class OutreachFilter(FilterSet):
    class Meta:
        model = Outreach
        fields = {
            'student__first_name': ['contains'],
            'student__father_name': ['contains'],
            'student__last_name': ['contains'],
            'student__mother_fullname': ['contains'],
            'student__id_number': ['exact'],
        }


class PreTestFilter(OutreachFilter):
    class Meta:
        model = Outreach


class PostTestFilter(OutreachFilter):
    class Meta:
        model = Outreach


class SchoolFilter(OutreachFilter):
    class Meta:
        model = Outreach
