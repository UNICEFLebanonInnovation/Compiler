from django_filters import FilterSet

from .models import BLN, RS, CBECE


class BLNFilter(FilterSet):
    class Meta:
        model = BLN
        fields = {
            'student__first_name': ['contains'],
            'student__father_name': ['contains'],
            'student__last_name': ['contains'],
            'student__mother_fullname': ['contains'],
            # 'participation': ['exact'],
            # 'learning_result': ['exact'],
        }


class RSFilter(FilterSet):
    class Meta:
        model = RS
        fields = {
            'student__first_name': ['contains'],
            'student__father_name': ['contains'],
            'student__last_name': ['contains'],
            'student__mother_fullname': ['contains'],
            # 'participation': ['exact'],
            # 'learning_result': ['exact'],
        }


class CBECEFilter(FilterSet):
    class Meta:
        model = CBECE
        fields = {
            'student__first_name': ['contains'],
            'student__father_name': ['contains'],
            'student__last_name': ['contains'],
            'student__mother_fullname': ['contains'],
            # 'participation': ['exact'],
            # 'learning_result': ['exact'],
        }
