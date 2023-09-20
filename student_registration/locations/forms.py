from __future__ import unicode_literals, absolute_import, division

from django.utils.translation import ugettext as _
from django import forms
from django.core.urlresolvers import reverse
from django.contrib import messages

from crispy_forms.helper import FormHelper

from crispy_forms.bootstrap import (
    FormActions,
    InlineCheckboxes
)
from dal import autocomplete


from student_registration.locations.models import Location
from .models import (
    Center,

)
from .serializers import CenterSerializer


class CenterAdminForm(forms.ModelForm):
    name = forms.CharField(
        label=_("Center name"),
        widget=forms.TextInput, required=True
    )
    governorate = forms.ModelChoiceField(
        queryset=Location.objects.filter(parent__isnull=True),
        widget=forms.Select,
        label=_('Governorate'),
        empty_label='-------',
        required=True,
        to_field_name='id',
    )
    caza = forms.ModelChoiceField(
        queryset=Location.objects.filter(parent__isnull=False, type=2),
        widget=forms.Select,
        label=_('Caza'),
        empty_label='-------',
        required=True,
        to_field_name='id',
    )
    cadaster = forms.ModelChoiceField(
        required=True,
        queryset=Location.objects.filter(parent__isnull=False, type=3),
        widget=autocomplete.ModelSelect2(url='location_autocomplete'),
        label=_('Cadaster')
    )
    p_code = forms.CharField(
        label=_("P-Code"),
        widget=forms.TextInput, required=True
    )
    type = forms.ChoiceField(
        label=_('Type'),
        widget=forms.Select, required=True,
        choices=(
            ('', '----------'),
            ('Municipality', _('Municipality')),
            ('Collective Settlement', _('Collective Settlement')),
            ('Informal Settlement', _('Informal Settlement')),
            ('Welfare Center', _('Welfare Center')),
            ('Community Hub', _('Community Hub')),
        ),
        initial=''
    )
    provided_packages = forms.MultipleChoiceField(
        required=False,
        widget=forms.CheckboxSelectMultiple,
        choices=(
                ('Education', 'Education'),
                ('Youth', 'Youth'),
                ('Health & Nutrition', 'Health & Nutrition'),
                ('Child Protection', 'Child Protection'),
                ('Social Protection', 'Social Protection'),
            ),
    )

    def __init__(self, *args, **kwargs):
        super(CenterAdminForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Center
        fields = '__all__'


class CenterForm(forms.ModelForm):
    name = forms.CharField(
        label=_("Center name"),
        widget=forms.TextInput, required=True
    )
    governorate = forms.ModelChoiceField(
        queryset=Location.objects.filter(parent__isnull=True),
        widget=forms.Select,
        label=_('Governorate'),
        empty_label='-------',
        required=True,
        to_field_name='id',
    )
    caza = forms.ModelChoiceField(
        queryset=Location.objects.filter(parent__isnull=False, type=2),
        widget=forms.Select,
        label=_('Caza'),
        empty_label='-------',
        required=True,
        to_field_name='id',
    )
    cadaster = forms.ModelChoiceField(
        required=True,
        queryset=Location.objects.filter(parent__isnull=False, type=3),
        widget=autocomplete.ModelSelect2(url='location_autocomplete'),
        label=_('Cadaster')
    )
    longitude = forms.FloatField(
        label=_('Center GPS (longitude)'),
        widget=forms.NumberInput(attrs=({'maxlength': 12})),
        min_value=0, required=True
    )
    latitude = forms.FloatField(
        label=_('Center GPS (latitude)'),
        widget=forms.NumberInput(attrs=({'maxlength': 12})),
        min_value=0, required=True
    )
    manager_name = forms.CharField(
        label=_("Center Manager name"),
        widget=forms.TextInput, required=True
    )
    phone_number = forms.RegexField(
        regex=r'^((03)|(70)|(71)|(76)|(78)|(79)|(81)|(86))-\d{6}$',
        widget=forms.TextInput(attrs={'placeholder': 'Format: XX-XXXXXX'}),
        required=True,
        label=_('Phone number')
    )
    email = forms.RegexField(
        regex=r'^\b[\w\.-]+@[\w\.-]+\.\w{2,4}\b',
        required=False,
        label=_('Email')
    )
    type = forms.ChoiceField(
        label=_('Type'),
        widget=forms.Select, required=True,
        choices=Center.TYPE,
        initial=''
    )
    provided_packages = forms.ChoiceField(
        label=_('Provided Services'),
        widget=forms.Select, required=True,
        choices=Center.PROVIDED_PACKAGES,
        initial=''
    )
    education_programs = forms.ChoiceField(
        label=_('Education Program'),
        widget=forms.Select, required=True,
        choices=Center.EDUCATION_PROGRAM,
        initial=''
    )
    youth_programs = forms.ChoiceField(
        label=_('Youth Program'),
        widget=forms.Select, required=True,
        choices=Center.YOUTH_PROGRAM,
        initial=''
    )
    admin_staff_number = forms.IntegerField(
        label=_('Number of Admin staff in the center'),
        widget=forms.TextInput, required=False
    )

    class Meta:
        model = Center
        fields = (
            'id',
            'name',
            'governorate',
            'caza',
            'cadaster',
            'longitude',
            'latitude',
            'manager_name',
            'phone_number',
            'email',
            'type',
            'provided_packages',
            'education_programs',
            'youth_programs',
            'admin_staff_number',
        )



