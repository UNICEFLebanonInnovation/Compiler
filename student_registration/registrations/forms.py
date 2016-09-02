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


class RegisteringAdultForm(forms.ModelForm):
    """
    Override model form to use custom Yes/No choices
    """
    YESNO_CHOICES = ((0, _('No')), (1, _('Yes')))

    previously_registered = forms.TypedChoiceField(
        choices=YESNO_CHOICES, widget=forms.RadioSelect, coerce=int
    )
    status = forms.TypedChoiceField(
        choices=YESNO_CHOICES, widget=forms.RadioSelect, coerce=int
    )
    child_enrolled_in_other_schools = forms.TypedChoiceField(
        choices=YESNO_CHOICES, widget=forms.RadioSelect, coerce=int
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
