from __future__ import unicode_literals, absolute_import, division

from django.utils.translation import ugettext as _
from django import forms
from student_registration.registrations.models import (
    RegisteringAdult,
    Registration,
)


class RegisteringAdultForm(forms.ModelForm):
    """
    Override model form to use custom Yes/No choices
    """
    YESNO_CHOICES = ((0, _('No')), (1, _('Yes')))
    PrincipalHouseHold = forms.TypedChoiceField(
        choices=YESNO_CHOICES, widget=forms.RadioSelect, coerce=int, required=False
    )
    previously_registered = forms.TypedChoiceField(
        choices=YESNO_CHOICES, widget=forms.RadioSelect, coerce=int, required=False
    )
    previously_registered_status = forms.TypedChoiceField(
        choices=YESNO_CHOICES, widget=forms.RadioSelect, coerce=int, required=False
    )
    child_enrolled_in_other_schools = forms.TypedChoiceField(
        choices=YESNO_CHOICES, widget=forms.RadioSelect, coerce=int, required=False
    )
    address = forms.CharField(widget=forms.Textarea(attrs=({'rows': 2, 'cols': 30})), required=False)
    wfp_case_number = forms.CharField(widget=forms.TextInput(attrs=({'maxlength': 10, 'placeholder': '12346788'})),
                                      required=False)
    csc_case_number = forms.CharField(widget=forms.TextInput(attrs=({'maxlength': 10, 'placeholder': '12346788'})),
                                      required=False)
    primary_phone = forms.CharField(widget=forms.TextInput(attrs=({'placeholder': '70123456'})),
                                    required=False)
    secondary_phone = forms.CharField(widget=forms.TextInput(attrs=({'placeholder': '70123456'})),
                                      required=False)
    first_name = forms.CharField(widget=forms.TextInput(attrs=({ 'placeholder': _('Enter household first name')})),
                                      required=False)
    father_name = forms.CharField(widget=forms.TextInput(attrs=({'placeholder': _("Enter household father's name")})),
                                 required=False)
    last_name = forms.CharField(widget=forms.TextInput(attrs=({'placeholder': _('Enter household last name')})),
                                 required=False)
    mother_fullname = forms.CharField(widget=forms.TextInput(attrs=({'placeholder': _('Enter household mother full name')})),
                                 required=False)
    age = forms.CharField(widget=forms.TextInput(attrs=({'placeholder': _('Enter household age')})),
                                 required=False)
    old_registry_id = forms.CharField(widget=forms.TextInput, required=False)

    def __init__(self, *args, **kwargs):
        super(RegisteringAdultForm, self).__init__(*args, **kwargs)

    class Meta:
        model = RegisteringAdult
        fields = '__all__'


class RegisteringChildForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(RegisteringChildForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Registration
        fields = '__all__'


class RegistrationForm(forms.Form):

    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Registration
        fields = '__all__'
