from __future__ import unicode_literals, absolute_import, division

from django.utils.translation import ugettext as _
from django import forms
from student_registration.students.models import (
    Student
)
from student_registration.registrations.models import (
    RegisteringAdult,
    Registration,
)


class RegisteringAdultForm(forms.Form):

    first_name = forms.CharField(
        max_length=255,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    def __init__(self, *args, **kwargs):
        super(RegisteringAdultForm, self).__init__(*args, **kwargs)

    class Meta:
        model = RegisteringAdult
        fields = '__all__'


class RegistrationForm(forms.Form):

    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Registration
        fields = '__all__'


class StudentForm(forms.Form):

    def __init__(self, *args, **kwargs):
        super(StudentForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Student
        fields = '__all__'
