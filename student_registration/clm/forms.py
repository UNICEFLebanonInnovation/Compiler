from __future__ import unicode_literals, absolute_import, division

from django.utils.translation import ugettext as _
from django import forms
from django.core.urlresolvers import reverse

from model_utils import Choices
from crispy_forms.helper import FormHelper
from crispy_forms.bootstrap import FormActions, Accordion, PrependedText, InlineCheckboxes, InlineRadios
from crispy_forms.layout import Layout, Fieldset, Button, Submit, Div, Field, HTML

from student_registration.students.models import (
    Student,
    IDType,
    Nationality,
)
from student_registration.schools.models import (
    School,
    Section,
    ClassRoom,
    EducationLevel,
    ClassLevel,
)
from student_registration.locations.models import Location
from .models import (
    CLM,
    BLN,
    RS,
    CBECE,
    Cycle,
    RSCycle,
    Referral,
    Disability,
    Site,
    Labour,
)
from .serializers import BLNSerializer, RSSerializer, CBECESerializer

YES_NO_CHOICE = ((1, "Yes"), (0, "No"))

YEARS = list(((str(x), x) for x in range(1930, 2051)))
YEARS.append(('', _('Birthday Year')))

DAYS = list(((str(x), x) for x in range(1, 32)))
DAYS.append(('', _('Birthday Day')))


class CommonForm(forms.ModelForm):

    new_registry = forms.TypedChoiceField(
        label=_("First time registered?"),
        choices=YES_NO_CHOICE,
        coerce=lambda x: bool(int(x)),
        widget=forms.RadioSelect,
        required=True,
    )
    student_outreached = forms.TypedChoiceField(
        label=_("Student outreached?"),
        choices=YES_NO_CHOICE,
        coerce=lambda x: bool(int(x)),
        widget=forms.RadioSelect,
        required=True,
    )
    have_barcode = forms.TypedChoiceField(
        label=_("Have barcode with him?"),
        choices=YES_NO_CHOICE,
        coerce=lambda x: bool(int(x)),
        widget=forms.RadioSelect,
        required=False,
    )
    search_barcode = forms.CharField(widget=forms.TextInput, required=False)
    search_student = forms.CharField(widget=forms.TextInput, required=False)

    cycle = forms.ModelChoiceField(
        queryset=Cycle.objects.all(), widget=forms.Select,
        empty_label=_('Programme Cycle'),
        required=False, to_field_name='id',
        initial=0
    )

    site = forms.ModelChoiceField(
        queryset=Site.objects.all(), widget=forms.Select,
        empty_label=_('Programme Site'),
        required=False, to_field_name='id',
        initial=0
    )

    governorate = forms.ModelChoiceField(
        queryset=Location.objects.filter(parent__isnull=True), widget=forms.Select,
        empty_label=_('Governorate'),
        required=True, to_field_name='id',
        initial=0
    )
    district = forms.ModelChoiceField(
        queryset=Location.objects.filter(parent__isnull=False), widget=forms.Select,
        empty_label=_('District'),
        required=True, to_field_name='id',
        initial=0
    )
    location = forms.CharField(widget=forms.TextInput, required=True)
    school = forms.ModelChoiceField(
        queryset=School.objects.all(), widget=forms.Select,
        empty_label=_('School'),
        required=False, to_field_name='id',
        initial=0
    )
    language = forms.MultipleChoiceField(
        choices=(
            ('english_arabic', _('English/Arabic')),
            ('french_arabic', _('French/Arabic'))
        ),
        widget=forms.CheckboxSelectMultiple,
        required=True
    )
    referral = forms.ModelChoiceField(
        queryset=Referral.objects.all(), widget=forms.Select,
        empty_label=_('Referral'),
        required=False, to_field_name='id',
        initial=0
    )
    shift = forms.ChoiceField(
        widget=forms.Select, required=False,
        choices=(
            ('', _('School shift')),
            ('first', _('First shift')),
            ('second', _('Second shift')),
        )
    )

    # registration_date = forms.DateField(
    #     required=True
    # )

    student_first_name = forms.CharField(widget=forms.TextInput, required=True)
    student_father_name = forms.CharField(widget=forms.TextInput, required=True)
    student_last_name = forms.CharField(widget=forms.TextInput, required=True)
    student_sex = forms.ChoiceField(
        widget=forms.Select, required=True,
        choices=(
            ('', _('Gender')),
            ('Male', _('Male')),
            ('Female', _('Female')),
        )
    )
    student_birthday_year = forms.ChoiceField(
        widget=forms.Select, required=True,
        choices=YEARS
    )
    student_birthday_month = forms.ChoiceField(
        widget=forms.Select, required=True,
        choices=(
            ('', _('Birthday Month')),
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
    student_birthday_day = forms.ChoiceField(
        widget=forms.Select, required=True,
        choices=DAYS
    )

    student_nationality = forms.ModelChoiceField(
        queryset=Nationality.objects.all(), widget=forms.Select,
        empty_label=_('Student nationality'),
        required=True, to_field_name='id',
    )

    student_mother_fullname = forms.CharField(widget=forms.TextInput, required=True)
    # student_mother_nationality = forms.ModelChoiceField(
    #     queryset=Nationality.objects.all(), widget=forms.Select,
    #     empty_label=_('Mather nationality'),
    #     required=True, to_field_name='id',
    # )
    # student_registered_in_unhcr = forms.TypedChoiceField(
    #     label=_("Registered in UNHCR?"),
    #     choices=YES_NO_CHOICE,
    #     coerce=lambda x: bool(int(x)),
    #     widget=forms.RadioSelect,
    #     required=True,
    # )
    # student_id_type = forms.ModelChoiceField(
    #     queryset=IDType.objects.all(), widget=forms.Select,
    #     required=True, to_field_name='id', empty_label=_('Student ID Type')
    # )
    # student_id_number = forms.CharField(widget=forms.TextInput, required=True)
    #
    # student_phone_prefix = forms.CharField(widget=forms.TextInput(attrs=({'maxlength': 2})), required=True)
    # student_phone = forms.CharField(widget=forms.TextInput(attrs=({'maxlength': 6})), required=True)
    student_address = forms.CharField(widget=forms.TextInput, required=True)
    student_p_code = forms.CharField(widget=forms.TextInput, required=True)

    child_muac = forms.ChoiceField(
        widget=forms.Select, required=True,
        choices=(
            ('', _('Child MUAC')),
            ('1', _('< 11.5 CM (severe malnutrition)')),
            ('2', _('< 12.5 CM (moderate malnutrition)')),
        )
    )
    disability = forms.ModelChoiceField(
        queryset=Disability.objects.all(), widget=forms.Select,
        empty_label=_('Disability'),
        required=True, to_field_name='id',
    )
    student_family_status = forms.ChoiceField(
        widget=forms.Select, required=True,
        choices=(
            ('', _('Family status')),
            ('married', _('Married')),
            ('engaged', _('Engaged')),
            ('divorced', _('Divorced')),
            ('widower', _('Widower')),
            ('single', _('Single')),
        )
    )
    student_have_children = forms.TypedChoiceField(
        label=_("Have children?"),
        choices=YES_NO_CHOICE,
        coerce=lambda x: bool(int(x)),
        widget=forms.RadioSelect,
        required=False,
    )

    have_labour = forms.TypedChoiceField(
        label=_("Have work?"),
        choices=YES_NO_CHOICE,
        coerce=lambda x: bool(int(x)),
        widget=forms.RadioSelect,
        required=False,
    )
    labours = forms.MultipleChoiceField(
        choices=Labour.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )
    labour_hours = forms.CharField(widget=forms.TextInput, required=True)
    hh_educational_level = forms.ModelChoiceField(
        queryset=EducationLevel.objects.all(), widget=forms.Select,
        empty_label=_('HH educational level'),
        required=False, to_field_name='id',
    )

    student_id = forms.CharField(widget=forms.HiddenInput, required=False)
    enrollment_id = forms.CharField(widget=forms.HiddenInput, required=False)
    student_outreach_child = forms.CharField(widget=forms.HiddenInput, required=False)
    # owner = forms.CharField(widget=forms.HiddenInput, required=False)
    # education_year = forms.CharField(widget=forms.HiddenInput, required=False)

    def __init__(self, *args, **kwargs):
        super(CommonForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_show_labels = False
        # self.helper.form_action = reverse('enrollments:add')
        # self.helper.layout = Layout(
        #     Fieldset(
        #         _('Registry'),
        #         Div(
        #             'student_id',
        #             'enrollment_id',
        #             'student_outreach_child',
        #             Div(InlineRadios('new_registry'), css_class='col-md-4'),
        #             Div(InlineRadios('student_outreached'), css_class='col-md-4'),
        #             Div(InlineRadios('have_barcode'), css_class='col-md-4 invisible', css_id='have_barcode_option'),
        #             css_class='row',
        #         ),
        #     ),
        #     Fieldset(
        #         _('Register by Barcode'),
        #         Div(
        #             Div(PrependedText('search_barcode', _('Search child by barcode')), css_class='col-md-6'),
        #             css_class='row',
        #         ),
        #         css_id='register_by_barcode', css_class='invisible'
        #     ),
        #     Fieldset(
        #         _('Search old student (fullname Or ID number)'),
        #         Div(
        #             Div('school_type', css_class='col-md-4'),
        #             Div('search_school', css_class='col-md-4'),
        #             Div(PrependedText('search_student', _('Search old student')), css_class='col-md-4'),
        #             css_class='row',
        #         ),
        #         css_id='search_options', css_class='invisible'
        #     ),
        #     Fieldset(
        #         _('Basic Data'),
        #         Div(
        #             Div(PrependedText('registration_date', _('Registration date')), css_class='col-md-4'),
        #             Div(PrependedText('outreach_barcode', _('Outreach Barcode')), css_class='col-md-4'),
        #             css_class='row',
        #         ),
        #         Div(
        #             Div(PrependedText('student_first_name', _('First Name')), css_class='col-md-4'),
        #             Div(PrependedText('student_father_name', _('Father Name')), css_class='col-md-4'),
        #             Div(PrependedText('student_last_name', _('Last Name')), css_class='col-md-4'),
        #             css_class='row',
        #         ),
        #         Div(
        #             Div('student_birthday_year', css_class='col-md-4'),
        #             Div('student_birthday_month', css_class='col-md-4'),
        #             Div('student_birthday_day', css_class='col-md-4'),
        #             css_class='row',
        #         ),
        #         Div(
        #             Div('student_sex', css_class='col-md-4'),
        #             Div('student_nationality', css_class='col-md-4'),
        #             css_class='row',
        #         ),
        #         Div(
        #             Div(PrependedText('student_mother_fullname', _('Mother Full name')), css_class='col-md-4'),
        #             Div('student_mother_nationality', css_class='col-md-4'),
        #             css_class='row',
        #         ),
        #         Div(
        #             Div(InlineRadios('student_registered_in_unhcr'), css_class='col-md-4'),
        #             Div('student_id_type', css_class='col-md-4'),
        #             Div(PrependedText('student_id_number', _('ID Number')), css_class='col-md-4'),
        #             css_class='row',
        #         ),
        #         Div(
        #             Div(PrependedText('student_phone_prefix', _('Prefix (2 digits)')), css_class='col-md-4'),
        #             Div(PrependedText('student_phone', _('Number (6 digits)')), css_class='col-md-4'),
        #             Div(PrependedText('student_address', _('Address')), css_class='col-md-4'),
        #             css_class='row',
        #         ),
        #         css_class='invisible child_data'
        #     ),
        #     Fieldset(
        #         _('Current situation'),
        #         Div(
        #             Div('classroom', css_class='col-md-6'),
        #             Div('section', css_class='col-md-6'),
        #             css_class='row',
        #         ),
        #         css_class='invisible child_data'
        #     ),
        #     FormActions(
        #         Submit('save', _('Save')),
        #         Button('cancel', _('Cancel'))
        #     )
        # )

    def save(self, request=None, instance=None, serializer=None):
        if instance:
            serializer = serializer(instance, data=request.POST)
            if serializer.is_valid():
                serializer.update(validated_data=serializer.validated_data)
        else:
            serializer = serializer(data=request.POST)
            if serializer.is_valid():
                instance = serializer.create(validated_data=serializer.validated_data)
                instance.school = request.user.school
                # instance.owner = request.user
                instance.save()

    class Meta:
        model = CLM
        fields = (
            'student_id',
            'enrollment_id',
            'student_first_name',
            'student_father_name',
            'student_last_name',
            'student_mother_fullname',
            'student_sex',
            'student_birthday_year',
            'student_birthday_month',
            'student_birthday_day',
            'student_nationality',
            'student_address',
            'student_p_code',
            'outreach_barcode',
            'cycle',
            'site',
            'governorate',
            'district',
            'location',
            'school',
            'language',
            'referral',
            'shift',
            'child_muac',
            'disability',
            'student_family_status',
            'student_have_children',
            'have_labour',
            'labours',
            'labour_hours',
            'hh_educational_level',
        )
        initial_fields = fields
        widgets = {}

    class Media:
        js = (
            'js/jquery-1.12.3.min.js',
            'js/jquery-ui-1.12.1.js',
            'js/validator.js',
            'js/registrations.js',
        )


class BLNForm(CommonForm):

    def save(self, request=None, instance=None, serializer=None):
        super(BLNForm, self).save()

    class Meta:
        model = BLN
        fields = CommonForm.Meta.fields

    class Media:
        js = (
            'js/jquery-1.12.3.min.js',
            'js/jquery-ui-1.12.1.js',
            'js/validator.js',
            'js/registrations.js',
        )

class RSForm(CommonForm):

    cycle = forms.ModelChoiceField(
        queryset=RSCycle.objects.all(), widget=forms.Select,
        empty_label=_('Programme Cycle'),
        required=True, to_field_name='id',
        initial=0
    )

    def save(self, request=None, instance=None, serializer=None):
        super(RSForm, self).save()

    class Meta:
        model = RS
        fields = CommonForm.Meta.fields


class CBECEForm(CommonForm):

    def save(self, request=None, instance=None, serializer=None):
        super(CBECEForm, self).save()

    class Meta:
        model = CBECE
        fields = CommonForm.Meta.fields
