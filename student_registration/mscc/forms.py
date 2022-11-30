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
from crispy_forms.layout import Layout, Fieldset, Button, Submit, Div, Field, HTML
from dal import autocomplete

from student_registration.students.models import (
    Student,
    Person,
    Nationality,
    IDType,
)
from student_registration.schools.models import (
    School,
    ClassRoom,
    EducationalLevel,
    PartnerOrganization,
)
from student_registration.clm.models import CLM
from student_registration.locations.models import Location
from .models import (
    Registration,
    Center
)
from .serializers import MainSerializer

YES_NO_CHOICE = ((1, _("Yes")), (0, _("No")))

YEARS = list(((str(x), x) for x in range(Person.CURRENT_YEAR - 20, Person.CURRENT_YEAR - 2)))
YEARS.insert(0, ('', '---------'))

DAYS = list(((str(x), x) for x in range(1, 32)))
DAYS.insert(0, ('', '---------'))

MONTHS = (
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

FAMILY_STATUS = (
    ('', '----------'),
    ('married', _('Married')),
    ('engaged', _('Engaged')),
    ('divorced', _('Divorced')),
    ('widower', _('Widower')),
    ('single', _('Single')),
)

PARTICIPATION = (
    ('', '----------'),
    ('less_than_5days', _('Less than 5 absence days')),
    ('5_10_days', _('5 to 10 absence days')),
    ('10_15_days', _('10 to 15 absence days')),
    ('more_than_15days', _('More than 15 absence days')),
    ('no_absence', _('No Absence'))
)

LEARNING_RESULT = (
    ('', '----------'),
    ('repeat_level', _('Repeat level')),
    ('graduated_next_level', _('Referred to the next level')),
    ('graduated_to_formal_kg', _('Referred to formal education - KG')),
    ('graduated_to_formal_level1', _('Referred to formal education - Level 1')),
    ('referred_to_another_program', _('Referred to another program')),
    ('dropout', _('Dropout, referral not possible'))
)

REGISTRATION_LEVEL = (
    ('', '----------'),
    ('level_one', _('Level one')),
    ('level_two', _('Level two')),

)


class MainForm(forms.ModelForm):
    YEARS = list(((str(x), x) for x in range(Person.CURRENT_YEAR - 20, Person.CURRENT_YEAR - 3)))
    YEARS.insert(0, ('', '---------'))

    center = forms.ModelChoiceField(
        queryset=Center.objects.all(), widget=forms.Select,
        label=_('Center'),
        empty_label='-------',
        required=True, to_field_name='id',
    )

    child_first_name = forms.CharField(
        label=_("First name"),
        widget=forms.TextInput, required=True
    )
    child_father_name = forms.CharField(
        label=_("Father name"),
        widget=forms.TextInput, required=True
    )
    child_last_name = forms.CharField(
        label=_("Last name"),
        widget=forms.TextInput, required=True
    )
    child_sex = forms.ChoiceField(
        label=_("Sex"),
        widget=forms.Select, required=True,
        choices=(
            ('', '----------'),
            ('Male', _('Male')),
            ('Female', _('Female')),
        )
    )
    child_birthday_year = forms.ChoiceField(
        label=_("Birthday year"),
        widget=forms.Select, required=True,
        choices=YEARS
    )
    child_birthday_month = forms.ChoiceField(
        label=_("Birthday month"),
        widget=forms.Select, required=True,
        choices=MONTHS
    )
    child_birthday_day = forms.ChoiceField(
        label=_("Birthday day"),
        widget=forms.Select, required=True,
        choices=DAYS
    )
    child_nationality = forms.ModelChoiceField(
        label=_("Nationality"),
        queryset=Nationality.objects.exclude(id=9), widget=forms.Select,
        required=True, to_field_name='id',
    )
    main_caregiver_nationality = forms.ModelChoiceField(
        label=_("Nationality"),
        queryset=Nationality.objects.exclude(id=9), widget=forms.Select,
        required=False, to_field_name='id',
    )
    main_caregiver_nationality_other = forms.CharField(
        label=_('Please specify'),
        widget=forms.TextInput, required=False
    )
    child_mother_fullname = forms.CharField(
        label=_("Mother fullname"),
        widget=forms.TextInput, required=True
    )
    child_address = forms.CharField(
        label=_("The area where the child resides"),
        widget=forms.TextInput, required=True
    )
    child_p_code = forms.CharField(
        label=_('P-Code If a child lives in a tent / Brax in a random camp'),
        widget=forms.TextInput, required=False
    )

    child_id = forms.CharField(widget=forms.HiddenInput, required=False)
    enrollment_id = forms.CharField(widget=forms.HiddenInput, required=False)
    partner_name = forms.CharField(widget=forms.HiddenInput, required=False)

    child_family_status = forms.ChoiceField(
        label=_('What is the family status of the child?'),
        widget=forms.Select, required=True,
        choices=Student.FAMILY_STATUS,
        initial='single'
    )
    child_have_children = forms.TypedChoiceField(
        label=_("Does the child have children?"),
        choices=YES_NO_CHOICE,
        coerce=lambda x: bool(int(x)),
        widget=forms.RadioSelect,
        required=True,
    )
    child_number_children = forms.IntegerField(
        label=_('How many children does this child have?'),
        widget=forms.TextInput, required=False
    )

    have_labour_single_selection = forms.ChoiceField(
        label=_('Does the child participate in work?'),
        widget=forms.Select, required=True,
        choices=Registration.HAVE_LABOUR,
        initial='no'
    )
    labours_single_selection = forms.ChoiceField(
        label=_('What is the type of work ?'),
        widget=forms.Select, required=False,
        choices=Registration.LABOURS
    )
    labours_other_specify = forms.CharField(
        label=_(
            'Please specify(hotel, restaurant, transport, personal services such as cleaning, hair care, cooking and childcare)'),
        widget=forms.TextInput, required=False
    )

    labour_hours = forms.CharField(
        label=_('How many hours does this child work in a day?'),
        widget=forms.TextInput, required=False
    )
    labour_weekly_income = forms.ChoiceField(
        label=_('What is the income of the child per week?'),
        widget=forms.Select,
        choices=Registration.LABOUR_INCOME,
        initial='single',
        required=False
    )
    other_nationality = forms.CharField(
        label=_('Specify the nationality'),
        widget=forms.TextInput, required=False
    )
    phone_number = forms.RegexField(
        regex=r'^((03)|(70)|(71)|(76)|(78)|(79)|(81))-\d{6}$',
        widget=forms.TextInput(attrs={'placeholder': 'Format: XX-XXXXXX'}),
        required=True,
        label=_('Main Phone number')
    )
    phone_number_confirm = forms.RegexField(
        regex=r'^((03)|(70)|(71)|(76)|(78)|(79)|(81))-\d{6}$',
        widget=forms.TextInput(attrs={'placeholder': 'Format: XX-XXXXXX'}),
        required=True,
        label=_('Main Phone number confirm')
    )
    second_phone_number = forms.RegexField(
        regex=r'^((03)|(70)|(71)|(76)|(78)|(79)|(81))-\d{6}$',
        widget=forms.TextInput(attrs={'placeholder': 'Format: XX-XXXXXX'}),
        required=False,
        label=_('Second Phone Number')
    )
    second_phone_number_confirm = forms.RegexField(
        regex=r'^((03)|(70)|(71)|(76)|(78)|(79)|(81))-\d{6}$',
        widget=forms.TextInput(attrs={'placeholder': 'Format: XX-XXXXXX'}),
        required=False,
        label=_('Second Phone Number confirm')
    )

    source_of_identification = forms.ChoiceField(
        label=_("Source of identification of the child to MSCC"),
        widget=forms.Select,
        required=True,
        choices=(
            ('', '----------'),
            ('Dirassa', _('Dirassa')),
            ('Awarness Session', _('Awarness Session')),
            ('Child''s parents', _('Child''s parents')),
            ('From Hosted Community', _('From Hosted Community')),
            ('Sector Partners referral (CP, Education, Health, Wash, Youth, Palestenian program...) ',
             _('Sector Partners referral (CP, Education, Health, Wash, Youth, Palestenian program...) ')),
            ('From Profiling Database', _('From Profiling Database')),
            ('From Other NGO', _('From Other NGO')),
            ('From Displaced Community', _('From Displaced Community')),
            ('Referred by the municipality/Other formal sources', _('Referred by the municipality/Other formal sources')),
            ('Other Sources', _('Other Sources')),
        ),
        initial=''
    )
    source_of_identification_specify = forms.CharField(
        label=_('Please specify'),
        widget=forms.TextInput, required=False
    )
    cash_support_programmes = forms.MultipleChoiceField(
        label=_('Cash support programmes that child is already benefitting from'),
        choices=(
                ('', '----------'),
                ('Haddi', _('Haddi')),
                ('Education Cash assistance', _('Education Cash assistance')),
                ('UNHCR cash assistance', _('UNHCR cash assistance')),
                ('WFP cash assistance', _('WFP cash assistance')),
        ),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )
    packages_received = forms.MultipleChoiceField(
        label=_('Packages received/to be provided to child under MSCC'),
        choices=(
                ('', '----------'),
                ('Early Childhood Development', _('Early Childhood Development')),
                ('Education', _('Education')),
                ('Child Protection/Psychosocial support', _('Child Protection/Psychosocial support')),
                ('Youth Empowerment and engagement', _('Youth Empowerment and engagement')),
                ('Health and Nutrition', _('Health and Nutrition')),
                ('Parental and Caregiver Support', _('Parental and Caregiver Support')),
                ('Social Cash Assistance', _('Social Cash Assistance')),
            ),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    rims_case_number = forms.CharField(
        required=False,
        label=_('RIMS Case Number')
    )
    main_caregiver = forms.ChoiceField(
        label=_("Main Caregiver"),
        widget=forms.Select, required=True,
        choices=(
            ('', '----------'),
            ('mother', _('Mother')),
            ('father', _('Father')),
            ('other', _('Other')),
        )
    )

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(MainForm, self).__init__(*args, **kwargs)

        display_registry = ''
        instance = kwargs['instance'] if 'instance' in kwargs else ''
        form_action = reverse('clm:mscc_add')
        self.fields['clm_type'].initial = 'MSCC'
        self.fields['new_registry'].initial = 'yes'
        if instance:
            display_registry = ' d-none'
            form_action = reverse('clm:mscc_edit', kwargs={'pk': instance.id})

        self.helper = FormHelper()
        self.helper.form_show_labels = True
        self.helper.form_action = form_action
        self.helper.layout = Layout(
        Div(
                Div(
                    Div('center', css_class='col-md-3'),
                    css_class='row card-body'
                ),
            css_id='step-1'
        ),
            Div(
                Div(
                    Div('child_first_name', css_class='col-md-3'),
                    Div('child_father_name', css_class='col-md-3'),
                    Div('child_last_name', css_class='col-md-3'),
                    css_class='row card-body',
                ),
                Div(
                    Div('child_mother_fullname', css_class='col-md-3'),
                    Div('child_sex', css_class='col-md-3'),
                    css_class='row card-body',
                ),
                Div(
                    Div('child_birthday_year', css_class='col-md-2'),
                    Div('child_birthday_month', css_class='col-md-2'),
                    Div('child_birthday_day', css_class='col-md-2'),
                    css_class='row card-body',
                ),
                Div(
                    Div('child_nationality', css_class='col-md-3'),
                    Div('other_nationality', css_class='col-md-3'),
                    css_class='row card-body',
                ),
                Div(
                    Div('child_p_code', css_class='col-md-4'),
                    Div('child_address', css_class='col-md-4'),
                    css_class='row card-body',
                ),

                Div(
                    Div('child_family_status', css_class='col-md-4'),
                    Div('child_have_children', css_class='col-md-3', css_id='child_have_children'),
                    Div('child_number_children', css_class='col-md-3'),
                    css_class='row card-body',
                ),
                Div(
                    Div('source_of_identification', css_class='col-md-4'),
                    Div('source_of_identification_specify', css_class='col-md-4'),
                    css_class='row card-body',
                ),
                Div(
                    Div('cash_support_programmes', css_class='col-md-6 multiple-choice'),
                    Div('packages_received', css_class='col-md-6 multiple-choice'),
                    css_class='row card-body',
                ),
                css_id='step-2',
            ),
            Div(
                Div(
                    Div('father_educational_level', css_class='col-md-4'),
                    Div('hh_educational_level', css_class='col-md-4'),
                    css_class='row card-body',
                ),
                Div(
                    Div('second_phone_number', css_class='col-md-3'),
                    Div('second_phone_number_confirm', css_class='col-md-3'),
                    css_class='row card-body',
                ),
                Div(
                    Div('main_caregiver', css_class='col-md-3'),
                    css_class='row card-body',
                ),
                Div(
                    Div('main_caregiver_nationality', css_class='col-md-3'),
                    Div('main_caregiver_nationality_other', css_class='col-md-3'),
                    css_class='row d-none card-body',
                ),
                css_id='step-3',
            ),
            Div(
                Div(
                    Div('have_labour_single_selection', css_class='col-md-4'),
                    css_class='row card-body',
                ),
                Div(
                    Div('labours_single_selection', css_class='col-md-4', css_id='labours'),
                    Div('labours_other_specify', css_class='col-md-4'),
                    css_class='row card-body',
                    id='labour_details_1'
                ),
                Div(
                    Div('labour_hours', css_class='col-md-4', css_id='labour_hours'),
                    Div('labour_weekly_income', css_class='col-md-4'),
                    css_class='row card-body',
                    id='labour_details_2'
                ),
            # ),
            FormActions(
                Submit('save', 'Save', css_class='btn-shadow btn-wide float-right btn-pill mr-3 btn-hover-shine btn btn-success'),
                Submit('save_add_another','Save & add another', css_class='btn-shadow btn-wide float-right btn-pill mr-3 btn-hover-shine btn btn-success'),
                Submit('save_add_another','Save & go to Education', css_class='btn-shadow btn-wide float-right btn-pill mr-3 btn-hover-shine btn btn-info'),
                # HTML('<a class="btn btn-info cancel-button" href="/clm/mscc-list/" translation="' + _(
                #     'Are you sure you want to cancel this registration?') + '">' + _('Back to list') + '</a>'),
                # css_class='btn-shadow btn-wide float-right btn-pill mr-3 btn-hover-shine btn'
            ),
                css_id='step-4',
        ),
        )
        partner_id = 0
        if instance:
            if instance.owner.partner:
                partner_id = instance.owner.partner.id
        else:
            if self.request.user.partner:
                partner_id = self.request.user.partner.id
        if partner_id > 0:
            queryset = Center.objects.filter(partner_id=partner_id)
            self.fields['center'] = forms.ModelChoiceField(
                queryset=queryset, widget=forms.Select,
                label=_('Site / Center'),
                empty_label='-------',
                required=True, to_field_name='id',
            )

    def clean(self):
        cleaned_data = super(MainForm, self).clean()

        phone_number = cleaned_data.get("phone_number")
        phone_number_confirm = cleaned_data.get("phone_number_confirm")
        second_phone_number = cleaned_data.get("second_phone_number")
        second_phone_number_confirm = cleaned_data.get("second_phone_number_confirm")
        child_nationality = cleaned_data.get("child_nationality")
        other_nationality = cleaned_data.get("other_nationality")
        main_caregiver = cleaned_data.get("main_caregiver")
        other_caregiver_relationship = cleaned_data.get("other_caregiver_relationship")
        main_caregiver_nationality = cleaned_data.get("main_caregiver_nationality")
        main_caregiver_nationality_other = cleaned_data.get("main_caregiver_nationality_other")
        have_labour_single_selection = cleaned_data.get("have_labour_single_selection")
        labours_single_selection = cleaned_data.get("labours_single_selection")
        labour_hours = cleaned_data.get("labour_hours")
        labour_weekly_income = cleaned_data.get("labour_weekly_income")
        child_have_children = cleaned_data.get("child_have_children")
        child_number_children = cleaned_data.get("child_number_children")
        labours_other_specify = cleaned_data.get("labours_other_specify")

        source_of_identification = cleaned_data.get("source_of_identification")
        source_of_identification_specify = cleaned_data.get("source_of_identification_specify")
        rims_case_number = cleaned_data.get("rims_case_number")

        if source_of_identification == 'Other Sources':
            if not source_of_identification_specify:
                self.add_error('source_of_identification_specify', 'This field is required')
        if source_of_identification == 'RIMS':
            if not rims_case_number:
                self.add_error('rims_case_number', 'This field is required')

        if labours_single_selection == 'other_many_other':
            if not labours_other_specify:
                self.add_error('labours_other_specify', 'This field is required')
        if child_nationality.id == 6:
            if not other_nationality:
                self.add_error('other_nationality', 'This field is required')
        if main_caregiver == 'other':
            if not other_caregiver_relationship:
                self.add_error('other_caregiver_relationship', 'This field is required')
        if main_caregiver_nationality and main_caregiver_nationality.id == 6:
            if not main_caregiver_nationality_other:
                self.add_error('main_caregiver_nationality_other', 'This field is required')
        if child_have_children:
            if not child_number_children:
                self.add_error('child_number_children', 'This field is required')
        if have_labour_single_selection != 'no':
            if not labours_single_selection:
                self.add_error('labours_single_selection', 'This field is required')
            if not labour_hours:
                self.add_error('labour_hours', 'This field is required')
            if not labour_weekly_income:
                self.add_error('labour_weekly_income', 'This field is required')

        if phone_number != phone_number_confirm:
            msg = "The phone numbers are not matched"
            self.add_error('phone_number_confirm', msg)
        if second_phone_number != second_phone_number_confirm:
            msg = "The phone numbers are not matched"
            self.add_error('second_phone_number_confirm', msg)

        # if id_type == 'UNHCR Registered':
        #     if not case_number:
        #         self.add_error('case_number', 'This field is required')
        #
        #     if case_number != case_number_confirm:
        #         msg = "The case numbers are not matched"
        #         self.add_error('case_number_confirm', msg)
        #
        #     if parent_individual_case_number != parent_individual_case_number_confirm:
        #         msg = "The individual case numbers are not matched"
        #         self.add_error('parent_individual_case_number_confirm', msg)
        #
        #     if individual_case_number != individual_case_number_confirm:
        #         msg = "The individual case numbers are not matched"
        #         self.add_error('individual_case_number_confirm', msg)

        # if id_type == 'UNHCR Recorded':
        #     if not recorded_number:
        #         self.add_error('recorded_number', 'This field is required')
        #
        #     if recorded_number != recorded_number_confirm:
        #         msg = "The recorded numbers are not matched"
        #         self.add_error('recorded_number_confirm', msg)
        #
        # if id_type == 'Syrian national ID':
        #
        #     if not parent_syrian_national_number:
        #         self.add_error('parent_syrian_national_number', 'This field is required')
        #
        #     if not parent_syrian_national_number_confirm:
        #         self.add_error('parent_syrian_national_number_confirm', 'This field is required')
        #
        #     if parent_syrian_national_number_confirm and not len(parent_syrian_national_number_confirm) == 11:
        #         msg = "Please enter a valid number (11 digits)"
        #         self.add_error('parent_syrian_national_number_confirm', msg)
        #
        #     if parent_syrian_national_number and not len(parent_syrian_national_number) == 11:
        #         msg = "Please enter a valid number (11 digits)"
        #         self.add_error('parent_syrian_national_number', msg)
        #
        #     if parent_syrian_national_number != parent_syrian_national_number_confirm:
        #         msg = "The national numbers are not matched"
        #         self.add_error('parent_syrian_national_number_confirm', msg)
        #
        #     if syrian_national_number != syrian_national_number_confirm:
        #         msg = "The national numbers are not matched"
        #         self.add_error('syrian_national_number_confirm', msg)
        #
        # if id_type == 'Lebanese national ID':
        #     # if not parent_national_number:
        #     #     self.add_error('parent_national_number', 'This field is required')
        #     #
        #     # if not parent_national_number_confirm:
        #     #     self.add_error('parent_national_number_confirm', 'This field is required')
        #
        #     if parent_national_number and not len(parent_national_number) == 12:
        #         msg = "Please enter a valid number (12 digits)"
        #         self.add_error('parent_national_number', msg)
        #
        #     if parent_national_number_confirm and not len(parent_national_number_confirm) == 12:
        #         msg = "Please enter a valid number (12 digits)"
        #         self.add_error('parent_national_number_confirm', msg)
        #
        #     if parent_national_number != parent_national_number_confirm:
        #         msg = "The national numbers are not matched"
        #         self.add_error('parent_national_number_confirm', msg)
        #
        #     if national_number != national_number_confirm:
        #         msg = "The national numbers are not matched"
        #         self.add_error('national_number_confirm', msg)
        #
        # if id_type == 'Palestinian national ID':
        #     if not sop_parent_national_number:
        #         self.add_error('parent_sop_national_number', 'This field is required')
        #
        #     if not sop_parent_national_number_confirm:
        #         self.add_error('parent_sop_national_number_confirm', 'This field is required')
        #
        #     if sop_parent_national_number != sop_parent_national_number_confirm:
        #         msg = "The national numbers are not matched"
        #         self.add_error('parent_sop_national_number_confirm', msg)
        #
        #     if sop_national_number != sop_national_number_confirm:
        #         msg = "The national numbers are not matched"
        #         self.add_error('sop_national_number_confirm', msg)
        #
        # if id_type == 'Other nationality':
        #     if not parent_other_number:
        #         self.add_error('parent_other_number', 'This field is required')
        #
        #     if not parent_other_number_confirm:
        #         self.add_error('parent_other_number_confirm', 'This field is required')
        #
        #     if parent_other_number != parent_other_number_confirm:
        #         msg = "The ID numbers are not matched"
        #         self.add_error('parent_other_number_confirm', msg)
        #
        #     if other_number != other_number_confirm:
        #         msg = "The ID numbers are not matched"
        #         self.add_error('other_number_confirm', msg)

    def save(self, request=None, instance=None):
        if instance:
            serializer = MSCCSerializer(instance, data=request.POST)
            if serializer.is_valid():
                instance = serializer.update(validated_data=serializer.validated_data, instance=instance)
                instance.modified_by = request.user
                instance.save()
                request.session['instance_id'] = instance.id
                messages.success(request, _('Your data has been sent successfully to the server'))
            else:
                messages.warning(request, serializer.errors)
        else:
            serializer = MSCCSerializer(data=request.POST)
            if serializer.is_valid():
                instance = serializer.create(validated_data=serializer.validated_data)
                instance.owner = request.user
                instance.modified_by = request.user
                instance.partner = request.user.partner
                instance.save()
                request.session['instance_id'] = instance.id
                messages.success(request, _('Your data has been sent successfully to the server'))
            else:
                messages.warning(request, serializer.errors)

        return instance

    class Meta:
        model = Registration
        fields = (
            'center',
            'child_first_name',
            'child_father_name',
            'child_last_name',
            'child_sex',
            'child_birthday_month',
            'child_birthday_day',
            'child_nationality',
            'child_mother_fullname',
            'child_address',
            'child_p_code',
            'child_birthday_year',
            'have_labour_single_selection',
            'labours_single_selection',
            'labours_other_specify',
            'labour_hours',
            'source_of_identification',
            'source_of_identification_specify',
            'cash_support_programmes',
            'packages_received',
            'other_nationality',
            'child_have_children',
            'child_family_status',
            'child_number_children',
            'main_caregiver',
            'main_caregiver_nationality',
            'labour_weekly_income',
        )


class EducationSituationForm(forms.ModelForm):
    education_status = forms.ChoiceField(
        label=_('Education status'),
        widget=forms.Select, required=True,
        choices=(
            ('', '----------'),
            ('out of school', _('No Registered in any school before')),
            ('Was registered in formal school but didnt continue', _('Was registered in formal school but didnt continue')),
            ('Was registered in non formal program and was referred to MSCC', _('Was registered in non formal program and was referred to MSCC')),
            ('Was registered in non formal program but did not continue', _('Was registered in non formal program but did not continue')),
            ('Was enrolled in TVET Programs', _('Was enrolled in TVET Programse'))
        ),
        initial=''
    )
    miss_school_date = forms.DateField(
        label=_("Miss school date"),
        required=False,
    )
    dropout_program = forms.ChoiceField(
        label=_('Please specify programme'),
        widget=forms.Select, required=False,
        choices=(
            ('', '----------'),
            ('Was registered in CBECE level 1-2', _('Was registered in CBECE level 1-2')),
            ('other	please specify	Was registered in BLN program', _('other please specify	Was registered in BLN program')),
            ('Was registered in ALP program and didnt continue', _('Was registered in ALP program and didnt continue')),
            ('Was enrolled in Dirasa', _('Was enrolled in Dirasa')),
        ),
        initial=''
    )
    education_program = forms.ChoiceField(
        label=_('Please specify education programme in MSCC'),
        widget=forms.Select, required=True,
        choices=(
            ('', '----------'),
            ('BLN Level 1', _('BLN Level 1')),
            ('BLN Level 2', _('BLN Level 2')),
            ('YBLN', _('YBLN')),
            ('YFNL', _('YFNL')),
            ('CBECE Level 3', _('CBECE Level 3')),
            ('Retention Support', _('Retention Support')),
        ),
        initial=''
    )
    first_attendance_date = forms.DateField(
        label=_("First attendance date"),
        required=True
    )
    volunteering_experience = forms.ChoiceField(
        label=_("Does the adolescent have any volunteering experience?"),
        widget=forms.Select, required=False,
        choices=CLM.YES_NO,
        initial='yes'
    )
    previous_community_initiative = forms.ChoiceField(
        label=_("Was the adolescent part of any previous community based initiative?"),
        widget=forms.Select, required=False,
        choices=CLM.YES_NO,
        initial='yes'
    )
    enrollment_reason = forms.CharField(
        label=_('What is the reason for the adolescent enrollement in the programme?'),
        widget=forms.TextInput, required=False
    )
    pre_tests_administered = forms.ChoiceField(
        label=_("Were pre-tests administered to assess adolescents level?"),
        widget=forms.Select, required=False,
        choices=CLM.YES_NO,
        initial='yes'
    )

    clm_type = forms.CharField(widget=forms.HiddenInput, required=False)
    child_age = forms.IntegerField(widget=forms.HiddenInput, required=False)

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(EducationSituationForm, self).__init__(*args, **kwargs)

        instance = kwargs['instance'] if 'instance' in kwargs else ''
        self.fields['clm_type'].initial = 'MSCC'
        self.fields['child_age'].initial = instance.child_age

        form_action = reverse('clm:education_situation', kwargs={'pk': instance.id})

        self.helper = FormHelper()
        self.helper.form_show_labels = True
        self.helper.form_action = form_action
        self.helper.layout = Layout(
            Div(
                Div(
                    'clm_type',
                    'child_age',
                    css_class='d-none',
                ),
                Div(
                    Div('education_status', css_class='col-md-3'),
                    Div('miss_school_date', css_class='col-md-3'),
                    Div('dropout_program', css_class='col-md-3'),
                    css_class='row card-body',
                ),
                Div(
                    Div('first_attendance_date', css_class='col-md-4'),
                    Div('education_program', css_class='col-md-4'),
                    css_class='row card-body',
                ),
                css_id='step-1',
            ),
            Div(
                Div(
                    Div('volunteering_experience', css_class='col-md-4'),
                    Div('previous_community_initiative', css_class='col-md-4'),
                    css_class='row card-body',
                ),
                Div(
                    Div('enrollment_reason', css_class='col-md-4'),
                    Div('pre_tests_administered', css_class='col-md-4'),
                    css_class='row card-body',
                ),
                css_id='step-2',
            ),
            FormActions(
                Submit('save', 'Save', css_class='btn-shadow btn-wide float-right btn-pill mr-3 btn-hover-shine btn btn-success'),
            )
        )

    def clean(self):
        cleaned_data = super(EducationSituationForm, self).clean()

        education_status = cleaned_data.get("education_status")
        miss_school_date = cleaned_data.get("miss_school_date")
        if education_status != 'out of school':
            if not miss_school_date:
                self.add_error('miss_school_date', 'This field is required')

    def save(self, instance=None, request=None):
        instance = super(EducationSituationForm, self).save()
        # instance = super(MSCCEducationSituationForm, self).save(request=request, instance=instance, serializer=MSCCSerializer)

        instance.modified_by = request.user
        instance.save()
        messages.success(request, _('Your data has been sent successfully to the server'))

    class Meta:
        model = Registration
        fields = (
            'education_status',
            'miss_school_date',
            'dropout_program',
            'first_attendance_date',
            'education_program',
            'volunteering_experience',
            'previous_community_initiative',
            'enrollment_reason',
            'pre_tests_administered'
        )


class DiagnosticAssessmentForm(forms.ModelForm):

    attended_arabic = forms.ChoiceField(
        label=_("Attended Arabic test"),
        widget=forms.Select, required=True,
        choices=(('yes', _("Yes")), ('no', _("No"))),
        initial='yes'
    )

    modality_arabic = forms.MultipleChoiceField(
        label=_('Please indicate modality'),
        choices=CLM.MODALITY,
        widget=forms.CheckboxSelectMultiple,
        required=False
    )
    arabic = forms.FloatField(
        label=_('Results'),
        widget=forms.NumberInput(attrs=({'maxlength': 4})),
        min_value=0, required=False
    )
    attended_foreign_language = forms.ChoiceField(
        label=_("Attended Foreign Language test"),
        widget=forms.Select, required=True,
        choices=(('yes', _("Yes")), ('no', _("No"))),
        initial='yes'
    )
    modality_foreign_language = forms.MultipleChoiceField(
        label=_('Please indicate modality'),
        choices=CLM.MODALITY,
        widget=forms.CheckboxSelectMultiple,
        required=False
    )
    foreign_language = forms.FloatField(
        label=_('Results'),
        widget=forms.NumberInput(attrs=({'maxlength': 4})),
        min_value=0, required=False
    )
    attended_math = forms.ChoiceField(
        label=_("Attended Math test"),
        widget=forms.Select, required=True,
        choices=(('yes', _("Yes")), ('no', _("No"))),
        initial='yes'
    )
    modality_math = forms.MultipleChoiceField(
        label=_('Please indicate modality'),
        choices=CLM.MODALITY,
        widget=forms.CheckboxSelectMultiple,
        required=False
    )
    math = forms.FloatField(
        label=_('Results'),
        widget=forms.NumberInput(attrs=({'maxlength': 4})),
        min_value=0, required=False
    )

    clm_type = forms.CharField(widget=forms.HiddenInput, required=False)

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(DiagnosticAssessmentForm, self).__init__(*args, **kwargs)
        pre_test = ''
        pre_test_button = ' btn-outline-secondary disabled'
        instance = kwargs['instance'] if 'instance' in kwargs else ''
        self.fields['clm_type'].initial = 'MSCC'

        display_assessment = ''
        form_action = reverse('clm:diagnostic_assessment', kwargs={'pk': instance.id})

        if instance.pre_test:
            print('-------------------------------------------------')
            print(instance.pre_test)
            print('-------------------------------------------------')
            pre_test_button = ' btn-outline-success '
            pre_test = instance.assessment_form(
                stage='pre_test',
                assessment_slug='pre_test',
                callback=self.request.build_absolute_uri(
                    reverse('clm:diagnostic_assessment', kwargs={'pk': instance.id}))
            )

        self.helper = FormHelper()
        self.helper.form_show_labels = True
        self.helper.form_action = form_action
        self.helper.layout = Layout(
            Div(
                Div(
                    Div('attended_arabic', css_class='col-md-3'),
                    Div('modality_arabic', css_class='col-md-4 multiple-choice'),
                    Div('arabic', css_class='col-md-3'),
                    css_class='row card-body',
                ),
                Div(
                    Div('attended_foreign_language', css_class='col-md-3'),
                    Div('modality_foreign_language', css_class='col-md-4 multiple-choice'),
                    Div('foreign_language', css_class='col-md-3'),
                    css_class='row card-body',
                ),
                Div(
                    Div('attended_math', css_class='col-md-3'),
                    Div('modality_math', css_class='col-md-4 multiple-choice'),
                    Div('math', css_class='col-md-3'),
                    css_class='row card-body',
                ),
                css_id='step-1',
            ),
            FormActions(
                Submit('save', 'Save', css_class='btn-shadow btn-wide float-right btn-pill mr-3 btn-hover-shine btn btn-success'),
                # HTML('<a class="btn btn-info cancel-button" href="/clm/mscc-list/" translation="' +
                #      _('Are you sure you want to cancel this registration?') + '">' + _('Back to list') + '</a>'),
            )
        )

    def clean(self):
        cleaned_data = super(DiagnosticAssessmentForm, self).clean()

        attended_arabic = cleaned_data.get("attended_arabic")
        modality_arabic = cleaned_data.get("modality_arabic")
        arabic = cleaned_data.get("arabic")

        attended_foreign_language = cleaned_data.get("attended_foreign_language")
        modality_foreign_language = cleaned_data.get("modality_foreign_language")
        foreign_language = cleaned_data.get("foreign_language")

        attended_math = cleaned_data.get("attended_math")
        modality_math = cleaned_data.get("modality_math")
        math = cleaned_data.get("math")

        if attended_arabic == 'yes':
            if not modality_arabic:
                self.add_error('modality_arabic', 'This field is required')
            if arabic is None:
                self.add_error('arabic', 'This field is required')

        if attended_foreign_language == 'yes':
            if not modality_foreign_language:
                self.add_error('modality_foreign_language', 'This field is required')
            if foreign_language is None:
                self.add_error('foreign_language', 'This field is required')

        if attended_math == 'yes':
            if not modality_math:
                self.add_error('modality_math', 'This field is required')
            if math is None:
                self.add_error('math', 'This field is required')

            # # grades Max Value validation
            # registration_level = cleaned_data.get("registration_level")
            #
            # if registration_level == 'level_one':
            #     if arabic > 46:
            #         self.add_error('arabic', 'This value is greater that 46')
            #     # if foreign_language > 36:
            #     #     self.add_error('foreign_language', 'This value is greater that 36')
            #     if math > 20:
            #         self.add_error('math', 'This value is greater that 20')
            # else:
            #     if arabic > 56:
            #         self.add_error('arabic', 'This value is greater that 56')
            #     # if foreign_language > 56:
            #     #     self.add_error('foreign_language', 'This value is greater that 56')
            #     if math > 34:
            #         self.add_error('math', 'This value is greater that 34')


    def save(self, instance=None, request=None):
        instance = super(DiagnosticAssessmentForm, self).save()

        instance.modified_by = request.user

        instance.pre_test = {
                "Diagnostic_ASSESSMENT/attended_arabic": request.POST.get('attended_arabic'),
                "Diagnostic_ASSESSMENT/modality_arabic": request.POST.getlist('modality_arabic'),
                "Diagnostic_ASSESSMENT/arabic": request.POST.get('arabic'),

                "Diagnostic_ASSESSMENT/attended_foreign_language": request.POST.get('attended_foreign_language'),
                "Diagnostic_ASSESSMENT/modality_foreign_language": request.POST.getlist('modality_foreign_language'),
                "Diagnostic_ASSESSMENT/foreign_language": request.POST.get('foreign_language'),

                "Diagnostic_ASSESSMENT/attended_math": request.POST.get('attended_math'),
                "Diagnostic_ASSESSMENT/modality_math": request.POST.getlist('modality_math'),
                "Diagnostic_ASSESSMENT/math": request.POST.get('math'),
            }

        instance.save()
        messages.success(request, _('Your data has been sent successfully to the server'))

    class Meta:
        model = Registration
        fields = (
        )


class EducationAssessmentForm(forms.ModelForm):
    # REGISTRATION_LEVEL = (
    #     ('', '----------'),
    #     ('level_one', _('Level one')),
    #     ('level_two', _('Level two')),
    #     # ('level_three', _('Level three'))
    # )
    participation = forms.ChoiceField(
        label=_('How was the level of child participation in the program?'),
        widget=forms.Select, required=True,
        choices=(
                ('', '----------'),
                ('no_absence', _('No Absence')),
                ('less_than_5days', _('Less than 5 absence days')),
                ('5_10_days', _('5 to 10 absence days')),
                ('10_15_days', _('10 to 15 absence days')),
                ('15_25_days', _('15 to 25 absence days')),
                ('more_than_25days', _('More than 25 absence days')),

            ),
        initial=''
    )
    barriers_single = forms.ChoiceField(
        label=_('The main barriers affecting the daily attendance and performance '
                'of the child or drop out of programme? (Select more than one if applicable)'),
        choices=CLM.BARRIERS,
        widget=forms.Select,
        required=False
    )
    barriers_other = forms.CharField(
        label=_('Please specify'),
        widget=forms.TextInput, required=False
    )
    test_done = forms.ChoiceField(
        label=_("Post test has been done"),
        widget=forms.Select, required=True,
        choices=(('yes', _("Yes")), ('no', _("No"))),
        initial='yes'
    )
    round_complete = forms.ChoiceField(
        label=_("Round complete"),
        widget=forms.Select, required=False,
        choices=(('yes', _("Yes")), ('no', _("No"))),
        initial='yes'
    )
    attended_arabic = forms.ChoiceField(
        label=_("Attended Arabic test"),
        widget=forms.Select, required=True,
        choices=(('yes', _("Yes")), ('no', _("No"))),
        initial='yes'
    )

    modality_arabic = forms.MultipleChoiceField(
        label=_('Please indicate modality'),
        choices=CLM.MODALITY,
        widget=forms.CheckboxSelectMultiple,
        required=False
    )
    arabic = forms.FloatField(
        label=_('Results'),
        widget=forms.NumberInput(attrs=({'maxlength': 4})),
        min_value=0, required=False
    )
    attended_foreign_language = forms.ChoiceField(
        label=_("Attended Foreign Language test"),
        widget=forms.Select, required=True,
        choices=(('yes', _("Yes")), ('no', _("No"))),
        initial='yes'
    )
    modality_foreign_language = forms.MultipleChoiceField(
        label=_('Please indicate modality'),
        choices=CLM.MODALITY,
        widget=forms.CheckboxSelectMultiple,
        required=False
    )
    foreign_language = forms.FloatField(
        label=_('Results'),
        widget=forms.NumberInput(attrs=({'maxlength': 4})),
        min_value=0, required=False
    )
    attended_math = forms.ChoiceField(
        label=_("Attended Math test"),
        widget=forms.Select, required=True,
        choices=(('yes', _("Yes")), ('no', _("No"))),
        initial='yes'
    )
    modality_math = forms.MultipleChoiceField(
        label=_('Please indicate modality'),
        choices=CLM.MODALITY,
        widget=forms.CheckboxSelectMultiple,
        required=False
    )
    math = forms.FloatField(
        label=_('Results'),
        widget=forms.NumberInput(attrs=({'maxlength': 4})),
        min_value=0, required=False
    )
    learning_result = forms.ChoiceField(
        label=_('Based on the overall score, what is the recommended learning path?'),
        widget=forms.Select, required=True,
        choices=CLM.LEARNING_RESULT,
        initial=''
    )

    test_diagnostic_done = forms.ChoiceField(
        label=_("Did the adolescent undertake any Post Diagnostic tests?"),
        widget=forms.Select, required=False,
        choices=CLM.YES_NO,
        initial='yes'
    )
    receive_passing_grade = forms.ChoiceField(
        label=_("Did the adolescent receive a passing grade for the tests?"),
        widget=forms.Select, required=False,
        choices=CLM.YES_NO,
        initial='yes'
    )
    life_skills_completed = forms.ChoiceField(
        label=_("Did the adolescent complete the life skills package?"),
        widget=forms.Select, required=False,
        choices=CLM.YES_NO,
        initial='yes'
    )
    participate_volunteering = forms.ChoiceField(
        label=_("Did the adolescent participate in any volunteering opportunity during the course of the program?"),
        widget=forms.Select, required=False,
        choices=CLM.YES_NO,
        initial='yes'
    )
    volunteering_specify = forms.ChoiceField(
        label=_('Please specify the volunteering opportunity'),
        widget=forms.Select, required=False,
        choices=(
            ('', '----------'),
            ('Outreach', _('Outreach')),
            ('Data entry', _('Data entry')),
            ('Admin work', _('Admin work')),
            ('Awareness raising sessions', _('Awareness raising sessions')),
            ('Empowerment and leadership', _('Empowerment and leadership')),
            ('Other', _('Other')),
        ),
        initial=''
    )

    social_course = forms.ChoiceField(
        label=_("Did the adolescent benefit from any social innovation/entrepreneurship course?"),
        widget=forms.Select, required=False,
        choices=CLM.YES_NO,
        initial='yes'
    )
    yfs_course_completed = forms.ChoiceField(
        label=_("Did the adolescent complete the YFS course?"),
        widget=forms.Select, required=False,
        choices=CLM.YES_NO,
        initial='yes'
    )
    training_material = forms.ChoiceField(
        label=_('What training material was provided?'),
        widget=forms.Select, required=False,
        choices=(
            ('', '----------'),
            ('Printed workbook', _('Printed workbook')),
            ('Tablets', _('Tablets')),
            ('Access to digital content (learning Passport) ', _('Access to digital content (learning Passport) ')),
            ('Other', _('Other')),
        ),
        initial=''
    )
    participate_community_initiatives = forms.ChoiceField(
        label=_("Did the adolescent participate/come up in community based initiatives?"),
        widget=forms.Select, required=False,
        choices=CLM.YES_NO,
        initial='yes'
    )

    community_initiatives_specify = forms.CharField(
        label=_('Please specify'),
        widget=forms.TextInput, required=False
    )
    adolescent_attendance = forms.ChoiceField(
        label=_('What training material was provided?'),
        widget=forms.Select, required=True,
        choices=(
            ('', '----------'),
            ('Full attendance', _('Full attendance')),
            ('Absence for less than 5 days', _('Absence for less than 5 days')),
            ('Absence for more than 5 days', _('Absence for more than 5 days')),
            ('Dropout', _('Dropout')),
        ),
        initial=''
    )
    adolescent_dropout_reason = forms.CharField(
        label=_('Reason for dropout'),
        widget=forms.TextInput, required=False
    )

    adolescent_dropout_date = forms.DateField(
        label=_("Dropout Date"),
        required=False
    )
    clm_type = forms.CharField(widget=forms.HiddenInput, required=False)

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(EducationAssessmentForm, self).__init__(*args, **kwargs)
        post_test = ''
        post_test_button = ' btn-outline-secondary disabled'
        instance = kwargs['instance'] if 'instance' in kwargs else ''
        self.fields['clm_type'].initial = 'MSCC'

        display_assessment = ''
        form_action = reverse('clm:education_assessment', kwargs={'pk': instance.id})

        if instance.post_test:
            post_test_button = ' btn-outline-success '
            post_test = instance.assessment_form(
                stage='post_test',
                assessment_slug='post_test',
                callback=self.request.build_absolute_uri(
                    reverse('clm:education_assessment', kwargs={'pk': instance.id}))
            )

        self.helper = FormHelper()
        self.helper.form_show_labels = True
        self.helper.form_action = form_action
        self.helper.layout = Layout(
            Div(
                Div(
                    Div('participation', css_class='col-md-4'),
                    Div('barriers_single', css_class='col-md-4'),
                    Div('barriers_other', css_class='col-md-4'),
                    css_class='row card-body',
                ),
                Div(
                    Div('test_done', css_class='col-md-4'),
                    Div('round_complete', css_class='col-md-4'),
                    css_class='row card-body',
                ),
                Div(
                    Div('attended_arabic', css_class='col-md-2'),
                    Div('modality_arabic', css_class='col-md-2  multiple-choice'),
                    Div('arabic', css_class='col-md-2'),
                    css_class='row grades card-body',
                ),

                Div(
                    Div('attended_foreign_language', css_class='col-md-2'),
                    Div('modality_foreign_language', css_class='col-md-2  multiple-choice'),
                    Div('foreign_language', css_class='col-md-2'),
                    css_class='row grades card-body',
                ),
                Div(
                    Div('attended_math', css_class='col-md-2'),
                    Div('modality_math', css_class='col-md-2  multiple-choice'),
                    Div('math', css_class='col-md-2'),
                    css_class='row grades card-body',
                ),
                css_id='step-1'
            ),
            Div(
                Div(
                    Div('test_diagnostic_done', css_class='col-md-3'),
                    Div('receive_passing_grade', css_class='col-md-3'),
                    Div('life_skills_completed', css_class='col-md-3'),
                    css_class='row card-body',
                ),
                Div(
                    Div('participate_volunteering', css_class='col-md-3'),
                    Div('volunteering_specify', css_class='col-md-3'),
                    css_class='row card-body',
                ),
                Div(
                    Div('social_course', css_class='col-md-3'),
                    Div('yfs_course_completed', css_class='col-md-3'),
                    Div('training_material', css_class='col-md-3'),
                    css_class='row card-body',
                ),
                Div(
                    Div('learning_result', css_class='col-md-3'),
                    Div('participate_community_initiatives', css_class='col-md-3'),
                    Div('community_initiatives_specify', css_class='col-md-3'),
                    css_class='row card-body',
                ),
                Div(
                    Div('adolescent_attendance', css_class='col-md-3'),
                    Div('adolescent_dropout_reason', css_class='col-md-3'),
                    Div('adolescent_dropout_date', css_class='col-md-3'),
                    css_class='row card-body',
                ),
                css_id='step-2',
            ),
            FormActions(
                Submit('save', 'Save', css_class='btn-shadow btn-wide float-right btn-pill mr-3 btn-hover-shine btn btn-success'),
                # HTML('<a class="btn btn-info cancel-button" href="/clm/mscc-list/" translation="' +
                #      _('Are you sure you want to cancel this registration?') + '">' + _('Back to list') + '</a>'),
            )
        )

    def clean(self):
        cleaned_data = super(EducationAssessmentForm, self).clean()
        participation = cleaned_data.get("participation")
        barriers_single = cleaned_data.get("barriers_single")
        barriers_other = cleaned_data.get("barriers_other")
        if participation != 'no_absence':
            if not barriers_single:
                self.add_error('barriers_single', 'This field is required')

        if barriers_single == 'other':
            if not barriers_other:
                self.add_error('barriers_other', 'This field is required')

        attended_arabic = cleaned_data.get("attended_arabic")
        modality_arabic = cleaned_data.get("modality_arabic")
        arabic = cleaned_data.get("arabic")

        attended_foreign_language = cleaned_data.get("attended_foreign_language")
        modality_foreign_language = cleaned_data.get("modality_foreign_language")
        foreign_language = cleaned_data.get("foreign_language")

        attended_math = cleaned_data.get("attended_math")
        modality_math = cleaned_data.get("modality_math")
        math = cleaned_data.get("math")

        test_done = cleaned_data.get("test_done")
        round_complete = cleaned_data.get("round_complete")

        if test_done == 'yes':
            if not round_complete:
                self.add_error('round_complete', 'This field is required')

            if attended_arabic == 'yes':
                if not modality_arabic:
                    self.add_error('modality_arabic', 'This field is required')
                if arabic is None:
                    self.add_error('arabic', 'This field is required')

            if attended_foreign_language == 'yes':
                if not modality_foreign_language:
                    self.add_error('modality_foreign_language', 'This field is required')
                if foreign_language is None:
                    self.add_error('foreign_language', 'This field is required')

            if attended_math == 'yes':
                if not modality_math:
                    self.add_error('modality_math', 'This field is required')
                if math is None:
                    self.add_error('math', 'This field is required')

            # # grades Max Value validation
            # registration_level = cleaned_data.get("registration_level")
            #
            # if registration_level == 'level_one':
            #     if arabic > 46:
            #         self.add_error('arabic', 'This value is greater that 46')
            #     # if foreign_language > 36:
            #     #     self.add_error('foreign_language', 'This value is greater that 36')
            #     if math > 20:
            #         self.add_error('math', 'This value is greater that 20')
            # else:
            #     if arabic > 56:
            #         self.add_error('arabic', 'This value is greater that 56')
            #     # if foreign_language > 56:
            #     #     self.add_error('foreign_language', 'This value is greater that 56')
            #     if math > 34:
            #         self.add_error('math', 'This value is greater that 34')



        test_diagnostic_done = cleaned_data.get("test_diagnostic_done")
        receive_passing_grade = cleaned_data.get("receive_passing_grade")
        if test_diagnostic_done == 'yes':
            if not receive_passing_grade:
                self.add_error('receive_passing_grade', 'This field is required')

        participate_volunteering = cleaned_data.get("participate_volunteering")
        volunteering_specify = cleaned_data.get("volunteering_specify")
        if participate_volunteering == 'yes':
            if not volunteering_specify:
                self.add_error('volunteering_specify', 'This field is required')

        yfs_course_completed = cleaned_data.get("yfs_course_completed")
        training_material = cleaned_data.get("training_material")
        if yfs_course_completed == 'yes':
            if not training_material:
                self.add_error('training_material', 'This field is required')

        participate_community_initiatives = cleaned_data.get("participate_community_initiatives")
        community_initiatives_specify = cleaned_data.get("community_initiatives_specify")
        if participate_community_initiatives == 'yes':
            if not community_initiatives_specify:
                self.add_error('community_initiatives_specify', 'This field is required')

        adolescent_attendance = cleaned_data.get("adolescent_attendance")
        adolescent_dropout_reason = cleaned_data.get("adolescent_dropout_reason")
        adolescent_dropout_date = cleaned_data.get("adolescent_dropout_date")
        if adolescent_attendance == 'Dropout':
            if not adolescent_dropout_reason:
                self.add_error('adolescent_dropout_reason', 'This field is required')
            if not adolescent_dropout_date:
                self.add_error('adolescent_dropout_date', 'This field is required')

    def save(self, instance=None, request=None):
        instance = super(EducationAssessmentForm, self).save()
        instance.post_test = {
                "Education_ASSESSMENT/attended_arabic": request.POST.get('attended_arabic'),
                "Education_ASSESSMENT/modality_arabic": request.POST.getlist('modality_arabic'),
                "Education_ASSESSMENT/arabic": request.POST.get('arabic'),

                "Education_ASSESSMENT/attended_foreign_language": request.POST.get('attended_foreign_language'),
                "Education_ASSESSMENT/modality_foreign_language": request.POST.getlist('modality_foreign_language'),
                "Education_ASSESSMENT/foreign_language": request.POST.get('foreign_language'),

                "Education_ASSESSMENT/attended_math": request.POST.get('attended_math'),
                "Education_ASSESSMENT/modality_math": request.POST.getlist('modality_math'),
                "Education_ASSESSMENT/math": request.POST.get('math'),
            }

        instance.save()
        messages.success(request, _('Your data has been sent successfully to the server'))

    class Meta:
        model = Registration
        fields = (
            'participation',
            'barriers_single',
            'barriers_other',
            'test_done',
            'round_complete',
            'test_diagnostic_done',
            'receive_passing_grade',
            'life_skills_completed',
            'participate_volunteering',
            'volunteering_specify',
            'social_course',
            'yfs_course_completed',
            'training_material',
            'participate_community_initiatives',
            'community_initiatives_specify',
            'adolescent_attendance',
            'adolescent_dropout_reason',
            'adolescent_dropout_date',
            'learning_result',
        )
