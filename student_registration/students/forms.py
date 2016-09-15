from __future__ import unicode_literals, absolute_import, division

from django.utils.translation import ugettext as _
from django import forms
from student_registration.students.models import (
    Student
)
from student_registration.registrations.models import Registration
from student_registration.locations.models import Location
from student_registration.schools.models import School


class StudentForm(forms.ModelForm):

    YESNO_CHOICES = ((0, _('No')), (1, _('Yes')))

    school = forms.ModelChoiceField(
                     queryset=School.objects.all(), widget=forms.Select,
                     required=False, to_field_name='name'
                )
    relation_to_adult = forms.ChoiceField(
                     choices=Registration.RELATION_TYPE, widget=forms.Select, required=False
                )
    enrolled_last_year = forms.ChoiceField(
                     choices=Registration.ENROLLMENT_TYPE, widget=forms.Select, required=False
                )
    location = forms.ModelChoiceField(
                     queryset=Location.objects.all(), widget=forms.Select,
                     required=False, to_field_name='name'
                )
    enrolled_last_year_school = forms.ModelChoiceField(
                     queryset=School.objects.all(), widget=forms.Select,
                     required=False, to_field_name='name'
                )
    related_to_family = forms.TypedChoiceField(
        choices=YESNO_CHOICES, widget=forms.RadioSelect, coerce=int, required=False
    )
    out_of_school_tow_years = forms.TypedChoiceField(
        choices=YESNO_CHOICES, widget=forms.RadioSelect, coerce=int, required=False
    )

    def __init__(self, *args, **kwargs):
        super(StudentForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Student
        fields = '__all__'
