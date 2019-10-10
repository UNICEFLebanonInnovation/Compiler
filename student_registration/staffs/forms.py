from __future__ import unicode_literals, absolute_import, division
from django import forms
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _
from student_registration.students.models import Person, Nationality
from student_registration.staffs.models import Staffs, Bank, Certificate, University
from student_registration.locations.models import Location
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, Button, Submit, Div, Field, HTML


YEARS = list(((str(x), x) for x in range(Person.CURRENT_YEAR-20, Person.CURRENT_YEAR-2)))
YEARS.insert(0, ('', '---------'))

DAYS = list(((str(x), x) for x in range(1, 32)))
DAYS.insert(0, ('', '---------'))


class StaffForm(forms.ModelForm):

    #def __init__(self, *args, **kwargs):
     #   super(StaffForm, self).__init__(*args, **kwargs)

    first_name = forms.CharField(label=_('First Name'), widget=forms.TextInput(attrs={'size': '80'}))
    father_name = forms.CharField(label=_('Father Name'), widget=forms.TextInput(attrs={'size': '80'}))
    last_name = forms.CharField(label=_('Family Name'), widget=forms.TextInput(attrs={'size': '80'}))
    image = forms.ImageField(required=False)
    id_number = forms.CharField(max_length=30, required=True, label=_('ID number'))
    mother_fullname = forms.CharField(label=_('Mother fullname'), widget=forms.TextInput(attrs={'size': '80'}))
    sex = forms.ChoiceField(
        label=_("Sex"),
        widget=forms.Select(attrs={'style': 'width:110px'}), required=True,
        choices=(
            ('', '----------'),
            ('Male', _('Male')),
            ('Female', _('Female')),
        )
    )
    birthday_year = forms.ChoiceField(
        label=_("Birthday year"),
        widget=forms.Select(attrs={'style': 'width:110px'}), required=True,
        choices=YEARS
    )
    birthday_month = forms.ChoiceField(
        label=_("Birthday month"),
        widget=forms.Select(attrs={'style': 'width:110px'}), required=True,
        choices=(
            ('', '----------'),
            ('1', _('January')),
            ('2', _('February')),
            ('3', _('March')),
            ('4', _('April')),
            ('5', _('May')),
            ('6', _('June')),
            ('7', _('July')),
            ('8', _('August')),
            ('9', _('September')),
            ('10', _('October')),
            ('11', _('November')),
            ('12', _('December')),
        )
    )
    birthday_day = forms.ChoiceField(
        label=_("Birthday day"),
        widget=forms.Select(attrs={'style': 'width:110px'}), required=True,
        choices=DAYS
    )
    place_of_birth = forms.CharField(
        max_length=200,
        required=False,
        label=_('Place of birth'), widget=forms.TextInput(attrs={'size': '80'})
    )
    family_status = forms.ChoiceField(
        label=_('Staff status'),
        widget=forms.Select(attrs={'style': 'width:130px'}), required=False,
        choices=(
            ('married', _('Married')),
            ('engaged', _('Engaged')),
            ('divorced', _('Divorced')),
            ('widower', _('Widower')),
            ('single', _('Single')),
        )
    )
    phone = forms.CharField(max_length=24, label=_('Phone number'), required=True)
    address = forms.CharField(
        label=_('Address'),
        widget=forms.Textarea(attrs={'rows': 5,
                                     'cols': 80,
                                     'style': 'height: 5em;'}),
    )
    MinisterApproval = forms.ChoiceField(
        label=_("Minister Approval"),
        choices=(
            ('0', '--------'),
            ('Exceptional', _('Exceptional Approved')),
            ('AccordingToCond', _('Consent According to Conditions')),
            ('CadreOrCont', _('Cadre / Contractual')),
        )
    )
    nationality = forms.ModelChoiceField(
        label=_('Nationality'),
        queryset=Nationality.objects.all(), widget=forms.Select(attrs={'style': 'width:130px'}),
        required=True
    )
    bank = forms.ModelChoiceField(
        label=_('Bank'),
        queryset=Bank.objects.all(), widget=forms.Select(attrs={'style': 'width:130px'}),
        required=False
    )
    branch = forms.CharField(
        label=_('Branch'),
        widget=forms.TextInput(attrs={'size': '80'}),
        required=False
    )
    certificate = forms.ModelChoiceField(
        label=_('Certificate'),
        queryset=Certificate.objects.all(), widget=forms.Select(attrs={'style': 'width:130px'}),
        required=False
    )
    university = forms.ModelChoiceField(
        label=_('University'),
        queryset=University.objects.all(), widget=forms.Select(attrs={'style': 'width:130px'}),
        required=False
    )
    iban = forms.CharField(
        label=_('IBAN'),
        widget=forms.TextInput(attrs={'size': '80'}),
        required=False
    )
    Automated_Nb = forms.CharField(
        label=_('Automated Nb'),
        widget=forms.TextInput(attrs={'size': '80'}),
        required=False
    )
    Financial_Nb = forms.CharField(
        label=_('Financial Nb'),
        widget=forms.TextInput(attrs={'size': '80'}),
        required=False
    )
    governorate = forms.ModelChoiceField(
        label=_('Governorate'),
        queryset=Location.objects.filter(parent__isnull=True), widget=forms.Select(attrs={'style': 'width:130px'}),
        required=False
    )
    caza = forms.ModelChoiceField(
        label=_('Caza'),
        queryset=Location.objects.filter(parent__isnull=False), widget=forms.Select(attrs={'style': 'width:130px'}),
        required=False
    )

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(StaffForm, self).__init__(*args, **kwargs)
        instance = kwargs['instance'] if 'instance' in kwargs else ''

    class Meta:
        model = Staffs
        fields = [
            'image', 'first_name','father_name','last_name', 'sex', 'mother_fullname','birthday_year','birthday_month','birthday_day',
            'place_of_birth',
            'family_status',
            'id_number',
            'nationality', 'phone', 'governorate', 'caza', 'address',
            'certificate', 'university',
            'MinisterApproval',
            'Automated_Nb', 'Financial_Nb',
            'bank', 'branch', 'iban'
        ]


