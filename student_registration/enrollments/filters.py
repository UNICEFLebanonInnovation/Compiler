from django_filters import FilterSet

from .models import Enrollment


class EnrollmentFilter(FilterSet):
    class Meta:
        model = Enrollment
        fields = {
            'student__first_name': ['contains'],
            'student__father_name': ['contains'],
            'student__last_name': ['contains'],
            'student__mother_fullname': ['contains'],
            'student__id_number': ['exact'],
            'classroom': ['exact'],
            'section': ['exact'],
        }
