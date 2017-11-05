from django_filters import FilterSet

from .models import BLN, RS, CBECE


class BLNFilter(FilterSet):
    class Meta:
        model = BLN
        fields = {
            'round': ['exact'],
            'student__first_name': ['contains'],
            'student__father_name': ['contains'],
            'student__last_name': ['contains'],
            'student__mother_fullname': ['contains'],
            'student__nationality': ['exact'],
            'cycle': ['exact'],
            'governorate': ['exact'],
            'district': ['exact'],
            'participation': ['exact'],
            'learning_result': ['exact'],
        }


class RSFilter(FilterSet):
    class Meta:
        model = RS
        fields = {
            'round': ['exact'],
            'student__first_name': ['contains'],
            'student__father_name': ['contains'],
            'student__last_name': ['contains'],
            'student__mother_fullname': ['contains'],
            'student__nationality': ['exact'],
            'type': ['exact'],
            'site': ['exact'],
            'school': ['exact'],
            'governorate': ['exact'],
            'district': ['exact'],
            'registered_in_school': ['exact'],
            'shift': ['exact'],
            'grade': ['exact'],
            'participation': ['exact'],
            'learning_result': ['exact'],
        }


class CBECEFilter(FilterSet):
    class Meta:
        model = CBECE
        fields = {
            'round': ['exact'],
            'student__first_name': ['contains'],
            'student__father_name': ['contains'],
            'student__last_name': ['contains'],
            'student__mother_fullname': ['contains'],
            'student__nationality': ['exact'],
            'cycle': ['exact'],
            'site': ['exact'],
            'school': ['exact'],
            'governorate': ['exact'],
            'district': ['exact'],
            'participation': ['exact'],
            'learning_result': ['exact'],
        }
