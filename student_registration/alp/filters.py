from django_filters import FilterSet

from .models import Outreach


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


class PreTestFilter(FilterSet):
    class Meta:
        model = Outreach
        fields = {
            'school': ['exact'],
            'student__first_name': ['contains'],
            'student__father_name': ['contains'],
            'student__last_name': ['contains'],
        }


class PostTestFilter(FilterSet):
    class Meta:
        model = Outreach
        fields = {
            'school': ['exact'],
            'registered_in_level': ['exact'],
            'student__first_name': ['contains'],
            'student__father_name': ['contains'],
            'student__last_name': ['contains'],
        }


class SchoolFilter(FilterSet):
    class Meta:
        model = Outreach
        fields = {
            'registered_in_level': ['exact'],
            'section': ['exact'],
            'student__first_name': ['contains'],
            'student__father_name': ['contains'],
            'student__last_name': ['contains'],
            'student__mother_fullname': ['contains'],
            'student__id_number': ['exact'],
        }
