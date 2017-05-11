from __future__ import unicode_literals, absolute_import, division

from django.utils.translation import ugettext as _
from django import forms
from student_registration.registrations.models import (
    RegisteringAdult,
    Registration,
    WaitingList,
)
from student_registration.schools.models import School
from student_registration.locations.models import Location
from student_registration.students.models import Nationality
from student_registration.students.models import IDType


class RegisteringAdultForm(forms.ModelForm):
    """
    Override model form to use custom Yes/No choices
    """
    YESNO_CHOICES = ((0, _('No')), (1, _('Yes')))

    school = forms.ModelChoiceField(
                     queryset=School.objects.all(), widget=forms.Select,
                     required=False, to_field_name='id'
                )
    nationality = forms.ModelChoiceField(
                     queryset=Nationality.objects.filter(id=1), widget=forms.Select,
                     required=False, to_field_name='id'
                )
    id_type = forms.ModelChoiceField(
        queryset=IDType.objects.filter(inuse=True), widget=forms.Select,
        required=False, to_field_name='id'
    )

    principal_applicant_living_in_house = forms.TypedChoiceField(
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
    address = forms.CharField(widget=forms.Textarea(attrs=({'rows': 2, 'cols': 30})),
                              required=False)
    wfp_case_number = forms.CharField(widget=forms.TextInput(attrs=({'maxlength': 12, 'placeholder': ''})),
                                      required=False)
    csc_case_number = forms.CharField(widget=forms.TextInput(attrs=({'maxlength': 12, 'placeholder': ''})),
                                      required=False)
    red_case_number = forms.CharField(widget=forms.TextInput(attrs=({'maxlength': 12, 'placeholder': ''})),
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
    previously_registered_number = forms.CharField(widget=forms.TextInput,
                                                   required=False)

    def __init__(self, *args, **kwargs):
        location = args[0]['location']
        locations = args[0]['locations']
        super(RegisteringAdultForm, self).__init__(*args, **kwargs)
        if len(locations):
            self.fields['school'].queryset = School.objects.filter(location_id__in=locations)
        else:
            self.fields['school'].queryset = School.objects.filter(location_id=location)

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


class WaitingListForm(forms.ModelForm):

    location = forms.ModelChoiceField(
                     queryset=Location.objects.all(), widget=forms.Select,
                     required=False, to_field_name='id'
                )
    school = forms.ModelChoiceField(
                     queryset=School.objects.all(), widget=forms.Select,
                     required=False, to_field_name='id'
                )
    phone_number = forms.CharField(widget=forms.TextInput(attrs=({'placeholder': '70123456'})),
                                    required=False)
    alternate_phone_number = forms.CharField(widget=forms.TextInput(attrs=({'placeholder': '70123456'})),
                                      required=False)
    first_name = forms.CharField(widget=forms.TextInput(attrs=({ 'placeholder': _('Enter household first name')})),
                                 required=False)
    father_name = forms.CharField(widget=forms.TextInput(attrs=({'placeholder': _("Enter household father's name")})),
                                  required=False)
    last_name = forms.CharField(widget=forms.TextInput(attrs=({'placeholder': _('Enter household last name')})),
                                required=False)
    mother_fullname = forms.CharField(widget=forms.TextInput(attrs=({'placeholder': _('Enter household mother full name')})),
                                      required=False)

    def __init__(self, *args, **kwargs):
        super(WaitingListForm, self).__init__(*args, **kwargs)
        self.fields['location'].queryset = Location.objects.filter(type_id=2)
        location = args[0]['location']
        locations = args[0]['locations']
        if len(locations):
            self.fields['school'].queryset = School.objects.filter(location_id__in=locations)
        else:
            self.fields['school'].queryset = School.objects.filter(location_id=location)
    class Meta:
        model = WaitingList
        fields = '__all__'

class HouseholdListSearchForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(HouseholdListSearchForm, self).__init__(*args, **kwargs)

    class Meta:
        model = RegisteringAdult
        fields = '__all__'

class SchoolModificationForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(SchoolModificationForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Registration
        fields = '__all__'
