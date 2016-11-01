from __future__ import unicode_literals, absolute_import, division

from django.utils.translation import ugettext as _
from django import forms
from student_registration.registrations.models import (
    WaitingList,
)
from student_registration.schools.models import School
from student_registration.locations.models import Location




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

