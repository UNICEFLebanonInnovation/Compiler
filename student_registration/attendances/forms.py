from django import forms
from student_registration.attendances.models import AttendanceDt


class AttendanceDtdAdminForm(forms.ModelForm):

    class Meta:
        model = AttendanceDt
        fields = '__all__'
