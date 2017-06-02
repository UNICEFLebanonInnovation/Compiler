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

    # school = forms.ModelChoiceField(
    #                  queryset=School.objects.all(), widget=forms.Select,
    #                  required=False, to_field_name='id'
    #             )
    birthday_year = forms.ChoiceField(choices=((str(x), x) for x in range(1998, 2051)),
                                      widget=forms.Select, required=False)
    relation_to_adult = forms.ChoiceField(
                     choices=Registration.RELATION_TYPE, widget=forms.Select, required=False
                )
    enrolled_last_year = forms.ChoiceField(
                     choices=Registration.ENROLLMENT_TYPE, widget=forms.Select, required=False
                )
    enrolled_last_year_location = forms.ModelChoiceField(
                     queryset=Location.objects.all(), widget=forms.Select,
                     required=False, to_field_name='id'
                )
    enrolled_last_year_school = forms.ModelChoiceField(
                     queryset=School.objects.all(), widget=forms.Select,
                     required=False, to_field_name='id'
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


class StudentEnrollmentForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(StudentEnrollmentForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Student
        fields = (
            'first_name',
            'father_name',
            'last_name',
            'mother_fullname',
            'sex',
            'birthday_year',
            'birthday_month',
            'birthday_day',
            'nationality',
            'mother_nationality',
            'id_type',
            'id_number',
            'phone',
            'phone_prefix',
            'address',
            'number',
        )
