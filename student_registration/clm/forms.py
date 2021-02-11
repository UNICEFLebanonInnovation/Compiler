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
from student_registration.locations.models import Location
from .models import (
    CLM,
    BLN,
    ABLN,
    RS,
    CBECE,
    Cycle,
    Disability,
    Assessment,
    CLMRound,
    ABLN_FC
)
from .serializers import BLNSerializer, RSSerializer, CBECESerializer, ABLNSerializer

YES_NO_CHOICE = ((1, _("Yes")), (0, _("No")))

YEARS = list(((str(x), x) for x in range(Person.CURRENT_YEAR-20, Person.CURRENT_YEAR-2)))
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


class CommonForm(forms.ModelForm):

    search_clm_student = forms.CharField(
        label=_("Search a student"),
        widget=forms.TextInput,
        required=False
    )
    governorate = forms.ModelChoiceField(
        queryset=Location.objects.filter(parent__isnull=True), widget=forms.Select,
        label=_('Governorate'),
        empty_label='-------',
        required=True, to_field_name='id',
        # initial=0
    )
    district = forms.ModelChoiceField(
        queryset=Location.objects.filter(parent__isnull=False), widget=forms.Select,
        label=_('District'),
        empty_label='-------',
        required=True, to_field_name='id',
        # initial=0
    )
    cadaster = forms.ModelChoiceField(
        queryset=Location.objects.filter(parent__isnull=False), widget=forms.Select,
        label=_('Cadaster'),
        empty_label='-------',
        required=True, to_field_name='id',
        # initial=0
    )
    location = forms.CharField(
        label=_("Location"),
        widget=forms.TextInput, required=True
    )
    round = forms.ModelChoiceField(
        queryset=CLMRound.objects.all(), widget=forms.Select,
        label=_('Round'),
        empty_label='-------',
        required=True, to_field_name='id',
        initial=0
    )
    # round_start_date = forms.DateField(
    #     label=_("Round start date"),
    #     required=True
    # )
    language = forms.ChoiceField(
        label=_('The language supported in the program'),
        widget=forms.Select,
        choices=CLM.LANGUAGES, required=True,
        initial='english_arabic'
    )

    student_first_name = forms.CharField(
        label=_("First name"),
        widget=forms.TextInput, required=True
    )
    student_father_name = forms.CharField(
        label=_("Father name"),
        widget=forms.TextInput, required=True
    )
    student_last_name = forms.CharField(
        label=_("Last name"),
        widget=forms.TextInput, required=True
    )
    student_sex = forms.ChoiceField(
        label=_("Sex"),
        widget=forms.Select, required=True,
        choices=(
            ('', '----------'),
            ('Male', _('Male')),
            ('Female', _('Female')),
        )
    )
    # student_birthday_year = forms.ChoiceField(
    #     label=_("Birthday year"),
    #     widget=forms.Select, required=True,
    #     choices=YEARS
    # )
    student_birthday_month = forms.ChoiceField(
        label=_("Birthday month"),
        widget=forms.Select, required=True,
        choices=MONTHS
    )
    student_birthday_day = forms.ChoiceField(
        label=_("Birthday day"),
        widget=forms.Select, required=True,
        choices=DAYS
    )
    student_nationality = forms.ModelChoiceField(
        label=_("Nationality"),
        queryset=Nationality.objects.exclude(id=9), widget=forms.Select,
        required=True, to_field_name='id',
    )
    main_caregiver_nationality = forms.ModelChoiceField(
        label=_("Nationality"),
        queryset=Nationality.objects.exclude(id=9), widget=forms.Select,
        required=True, to_field_name='id',
    )
    student_mother_fullname = forms.CharField(
        label=_("Mother fullname"),
        widget=forms.TextInput, required=True
    )
    student_address = forms.CharField(
        label=_("The area where the child resides"),
        widget=forms.TextInput, required=True
    )
    student_p_code = forms.CharField(
        label=_('P-Code If a child lives in a tent / Brax in a random camp'),
        widget=forms.TextInput, required=False
    )
    # student_id_number = forms.CharField(
    #     label=_('ID number'),
    #     widget=forms.TextInput, required=False
    # )

    disability = forms.ModelChoiceField(
        queryset=Disability.objects.filter(active=True), widget=forms.Select,
        label=_('Does the child have any disability or special need?'),
        required=True, to_field_name='id',
        initial=1
    )
    hh_educational_level = forms.ModelChoiceField(
        queryset=EducationalLevel.objects.exclude(id=3), widget=forms.Select,
        label=_('What is the educational level of the mother?'),
        required=True, to_field_name='id',
    )
    father_educational_level = forms.ModelChoiceField(
        queryset=EducationalLevel.objects.exclude(id=3), widget=forms.Select,
        label=_('What is the educational level of the father?'),
        required=True, to_field_name='id',
    )
    student_id = forms.CharField(widget=forms.HiddenInput, required=False)
    enrollment_id = forms.CharField(widget=forms.HiddenInput, required=False)
    clm_type = forms.CharField(widget=forms.HiddenInput, required=False)


    # participation = forms.ChoiceField(
    #     label=_('How was the level of child participation in the program?'),
    #     widget=forms.Select, required=False,
    #     choices=PARTICIPATION,
    #     initial=''
    # )
    # barriers = forms.MultipleChoiceField(
    #     label=_('The main barriers affecting the daily attendance and performance of the child or drop out of programme? (Select more than one if applicable)'),
    #     choices=CLM.BARRIERS,
    #     widget=forms.CheckboxSelectMultiple,
    #     required=False
    # )
    # learning_result = forms.ChoiceField(
    #     label=_('Based on the overall score, what is the recommended learning path?'),
    #     widget=forms.Select, required=False,
    #     choices=(
    #         ('', '----------'),
    #         ('repeat_level', _('Repeat level')),
    #         ('graduated_next_level', _('Referred to the next level')),
    #         ('graduated_to_formal_kg', _('Referred to formal education - KG')),
    #         ('graduated_to_formal_level1', _('Referred to formal education - Level 1')),
    #         ('referred_to_another_program', _('Referred to another program')),
    #         # ('dropout', _('Dropout from school'))
    #     ),
    #     initial=''
    # )

    def __init__(self, *args, **kwargs):
        super(CommonForm, self).__init__(*args, **kwargs)

    # def clean(self):
    #     from django.db.models import Q
    #     cleaned_data = super(CommonForm, self).clean()
    #     id_number = cleaned_data.get('student_id_number')
    #     internal_number = cleaned_data.get('internal_number')
    #     queryset = self.Meta.model.objects.all()
    #
    #     if queryset.filter(Q(student__id_number=id_number) | Q(internal_number=internal_number)).count():
    #         raise forms.ValidationError(
    #             _("Child already registered in your organization")
    #         )

    def save(self, request=None, instance=None, serializer=None):
        if instance:
            serializer = serializer(instance, data=request.POST)
            if serializer.is_valid():
                instance = serializer.update(validated_data=serializer.validated_data, instance=instance)
                instance.modified_by = request.user
                instance.save()
                request.session['instance_id'] = instance.id
                messages.success(request, _('Your data has been sent successfully to the server'))
            else:
                messages.warning(request, serializer.errors)
        else:
            serializer = serializer(data=request.POST)
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
        model = CLM
        fields = (
            'first_attendance_date',
            'round',
            'governorate',
            'district',
            'cadaster',
            'location',
            'language',
            'student_first_name',
            'student_father_name',
            'student_last_name',
            'student_sex',
            'student_birthday_month',
            'student_birthday_day',
            'student_nationality',
            'student_mother_fullname',
            'student_address',
            'student_p_code',
            # 'student_id_number',
            'internal_number',
            'disability',
            # 'have_labour',
            # 'labours',
            # 'labour_hours',
            'hh_educational_level',
            'father_educational_level',
            # 'participation',
            # 'barriers',
            # 'learning_result',
            'student_id',
            'enrollment_id',
            # 'comments',
            # 'unsuccessful_pretest_reason',
            # 'unsuccessful_posttest_reason',
        )
        initial_fields = fields
        widgets = {}

    class Media:
        js = (
            # 'js/jquery-3.3.1.min.js',
            # 'js/jquery-ui-1.12.1.js',
            # 'js/validator.js',
            # 'js/registrations.js',
        )


class BLNForm(CommonForm):

    REGISTRATION_LEVEL = (
        ('', '----------'),
        ('level_one', _('Level one')),
        ('level_two', _('Level two')),
        ('level_three', _('Level three'))
    )

    YEARS_BLN = list(((str(x), x) for x in range(Person.CURRENT_YEAR - 15, Person.CURRENT_YEAR - 8)))
    YEARS_BLN.insert(0, ('', '---------'))
    first_attendance_date = forms.DateField(
        label=_("First attendance date"),
        required=True
    )
    miss_school_date = forms.DateField(
        label=_("Miss school date"),
        required=False,
    )

    new_registry = forms.ChoiceField(
        label=_("First time registered?"),
        widget=forms.Select, required=True,
        choices=(('yes', _("Yes")), ('no', _("No"))),
        initial='yes'
    )

    round = forms.ModelChoiceField(
        queryset=CLMRound.objects.filter(current_round_bln=True), widget=forms.Select,
        label=_('Round'),
        empty_label='-------',
        required=True, to_field_name='id',
    )

    round_start_date = forms.DateField(
        label=_("Round start date"),
        required=False
    )
    registration_level = forms.ChoiceField(
        label=_("Registration level"),
        widget=forms.Select, required=True,
        choices=REGISTRATION_LEVEL
    )
    student_birthday_year = forms.ChoiceField(
        label=_("Birthday year"),
        widget=forms.Select, required=True,
        choices=YEARS_BLN
    )

    student_family_status = forms.ChoiceField(
        label=_('What is the family status of the child?'),
        widget=forms.Select, required=True,
        choices=Student.FAMILY_STATUS,
        initial='single'
    )
    student_have_children = forms.TypedChoiceField(
        label=_("Does the child have children?"),
        choices=YES_NO_CHOICE,
        coerce=lambda x: bool(int(x)),
        widget=forms.RadioSelect,
        required=True,
    )
    student_number_children = forms.IntegerField(
        label=_('How many children does this child have?'),
        widget=forms.TextInput, required=False
    )

    have_labour_single_selection = forms.ChoiceField(
        label=_('Does the child participate in work?'),
        widget=forms.Select, required=True,
        choices=CLM.HAVE_LABOUR,
        initial='no'
    )
    labours_single_selection = forms.ChoiceField(
        label=_('What is the type of work ?'),
        widget=forms.Select, required=False,
        choices=CLM.LABOURS
    )
    labours_other_specify = forms.CharField(
        label=_('Please specify(hotel, restaurant, transport, personal services such as cleaning, hair care, cooking and childcare)'),
        widget=forms.TextInput, required=False
    )

    labour_hours = forms.CharField(
        label=_('How many hours does this child work in a day?'),
        widget=forms.TextInput, required=False
    )
    labour_weekly_income = forms.ChoiceField(
        label=_('What is the income of the child per week?'),
        widget=forms.Select,
        choices=Student.STUDENT_INCOME,
        initial='single',
        required=False
    )
    education_status = forms.ChoiceField(
        label=_('Education status'),
        widget=forms.Select, required=True,
        choices=(
            ('', '----------'),
            ('out of school', _('Out of school')),
            ('enrolled in formal education but did not continue', _("Enrolled in formal education but did not continue")),
            ('enrolled in BLN', _("Enrolled in BLN")),
        ),
        initial=''
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
    id_type = forms.ChoiceField(
        label=_("ID type of the caretaker"),
        widget=forms.Select(attrs=({'translation': _('Child no ID confirmation popup message')})),
        required=True,
        choices=(
            ('', '----------'),
            ('UNHCR Registered', _('UNHCR Registered')),
            ('UNHCR Recorded', _("UNHCR Recorded")),
            ('Syrian national ID', _("Syrian national ID")),
            ('Palestinian national ID', _("Palestinian national ID")),
            ('Lebanese national ID', _("Lebanese national ID")),
            ('Other nationality', _("Other nationality")),
            ('Child have no ID', _("Child have no ID"))
        ),
        initial=''
    )
    case_number = forms.RegexField(
        regex=r'^((245)|(380)|(568)|(705)|(781)|(909)|(947)|(954)|(LEB)|(leb))-[0-9][0-9][C]\d{5}$',
        widget=forms.TextInput(attrs={'placeholder': 'Format: XXX-XXCXXXXX'}),
        required=False,
        label=_('UNHCR Case Number')
    )
    case_number_confirm = forms.RegexField(
        regex=r'^((245)|(380)|(568)|(705)|(781)|(909)|(947)|(954)|(LEB)|(leb))-[0-9][0-9][C]\d{5}$',
        widget=forms.TextInput(attrs={'placeholder': 'Format: XXX-XXCXXXXX'}),
        required=False,
        label=_('Confirm UNHCR Case Number')
    )
    parent_individual_case_number = forms.RegexField(
        regex=r'^((245)|(380)|(568)|(705)|(781)|(909)|(947)|(954)|(LEB)|(leb))-[0-9]{8}$',
        widget=forms.TextInput(attrs={'placeholder': 'Format: XXX-XXXXXXXX'}),
        required=False,
        label=_(
            'Caretaker Individual ID from the certificate (Optional, in case not listed in the certificate)')
    )
    parent_individual_case_number_confirm = forms.RegexField(
        regex=r'^((245)|(380)|(568)|(705)|(781)|(909)|(947)|(954)|(LEB)|(leb))-[0-9]{8}$',
        widget=forms.TextInput(attrs={'placeholder': 'Format: XXX-XXXXXXXX'}),
        required=False,
        label=_(
            'Confirm Caretaker Individual ID from the certificate (Optional, in case not listed in the certificate)')
    )
    individual_case_number = forms.RegexField(
        regex=r'^((245)|(380)|(568)|(705)|(781)|(909)|(947)|(954)|(LEB)|(leb))-[0-9]{8}$',
        widget=forms.TextInput(attrs={'placeholder': 'Format: XXX-XXXXXXXX'}),
        required=False,
        label=_(
            'Individual ID of the Child from the certificate (Optional, in case not listed in the certificate)')
    )
    individual_case_number_confirm = forms.RegexField(
        regex=r'^((245)|(380)|(568)|(705)|(781)|(909)|(947)|(954)|(LEB)|(leb))-[0-9]{8}$',
        widget=forms.TextInput(attrs={'placeholder': 'Format: XXX-XXXXXXXX'}),
        required=False,
        label=_(
                'Confirm Individual ID of the Child from the certificate (Optional, in case not listed in the certificate)')
    )
    recorded_number = forms.RegexField(
        regex=r'^((245)|(380)|(568)|(705)|(781)|(909)|(947)|(954)|(LEB)|(leb))-[0-9][0-9][C]\d{5}$',
        widget=forms.TextInput(attrs={'placeholder': 'Format: LEB-XXCXXXXX'}),
        required=False,
        label=_('UNHCR Barcode number (Shifra number)')
    )
    recorded_number_confirm = forms.RegexField(
        regex=r'^((245)|(380)|(568)|(705)|(781)|(909)|(947)|(954)|(LEB)|(leb))-[0-9][0-9][C]\d{5}$',
        widget=forms.TextInput(attrs={'placeholder': 'Format: LEB-XXCXXXXX'}),
        required=False,
        label=_('Confirm UNHCR Barcode number (Shifra number)')
    )

    national_number = forms.RegexField(
        regex=r'^\d{12}$',
        widget=forms.TextInput(attrs={'placeholder': 'Format: XXXXXXXXXXXX'}),
        required=False,
        label=_('Lebanese ID number of the child (Optional)')
    )
    national_number_confirm = forms.RegexField(
        regex=r'^\d{12}$',
        widget=forms.TextInput(attrs={'placeholder': 'Format: XXXXXXXXXXXX'}),
        required=False,
        label=_('Confirm Lebanese ID number of the child (optional)')
    )
    syrian_national_number = forms.RegexField(
        regex=r'^\d{11}$',
        required=False,
        label=_('National ID number of the child (Optional)')
    )
    syrian_national_number_confirm = forms.RegexField(
        regex=r'^\d{11}$',
        required=False,
        label=_('Confirm National ID number of the child (Optional)')
    )
    sop_national_number = forms.CharField(
        required=False,
        label=_('Palestinian ID number of the child (Optional)')
    )
    sop_national_number_confirm = forms.CharField(
        required=False,
        label=_('Confirm Palestinian ID number of the child (optional)')
    )
    parent_national_number = forms.RegexField(
        regex=r'^\d{12}$',
        widget=forms.TextInput(attrs={'placeholder': 'Format: XXXXXXXXXXXX'}),
        required=False,
        label=_('Lebanese ID number of the caretaker (Mandatory)')
    )
    parent_national_number_confirm = forms.RegexField(
        regex=r'^\d{12}$',
        widget=forms.TextInput(attrs={'placeholder': 'Format: XXXXXXXXXXXX'}),
        required=False,
        label=_('Confirm Lebanese ID number of the caretaker (Mandatory)')
    )
    parent_syrian_national_number = forms.RegexField(
        regex=r'^\d{11}$',
        required=False,
        label=_('National ID number of the Caretaker (Mandatory)')
    )
    parent_syrian_national_number_confirm = forms.RegexField(
        regex=r'^\d{11}$',
        required=False,
        label=_('Confirm National ID number of the Caretaker (Mandatory)')
    )
    parent_sop_national_number = forms.CharField(
        # regex=r'^\d{11}$',
        required=False,
        label=_('Palestinian ID number of the Caretaker (Mandatory)')
    )
    parent_sop_national_number_confirm = forms.CharField(
        # regex=r'^\d{11}$',
        required=False,
        label=_('Confirm Palestinian ID number of the Caretaker (Mandatory)')
    )

    parent_other_number = forms.CharField(
        required=False,
        label=_('ID number of the Caretaker (Mandatory)')
    )
    parent_other_number_confirm = forms.CharField(
        required=False,
        label=_('Confirm ID number of the Caretaker (Mandatory)')
    )
    other_number = forms.CharField(
        required=False,
        label=_(' ID number of the child (Optional)')
    )
    other_number_confirm = forms.CharField(
        required=False,
        label=_('Confirm ID number of the child (optional)')
    )

    no_child_id_confirmation = forms.CharField(widget=forms.HiddenInput, required=False)
    no_parent_id_confirmation = forms.CharField(widget=forms.HiddenInput, required=False)

    source_of_identification = forms.ChoiceField(
        label=_("Source of identification of the child to BLN"),
        widget=forms.Select,
        required=True,
        choices=(
            ('', '----------'),
            ('Referred by CP partner', _('Referred by CP partner')),
            ('Referred by youth partner', _('Referred by youth partner')),
            ('Family walked in to NGO', _('Family walked in to NGO')),
            ('Referral from another NGO', _('Referral from another NGO')),
            ('Referral from another Municipality', _('Referral from Municipality')),
            ('Direct outreach', _('Direct outreach')),
            ('List database', _('List database')),
            ('abln', _('ABLN'))
        ),
        initial=''
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
    attended_english = forms.ChoiceField(
        label=_("Attended English test"),
        widget=forms.Select, required=True,
        choices=(('yes', _("Yes")), ('no', _("No"))),
        initial='yes'
    )
    modality_english  = forms.MultipleChoiceField(
        label=_('Please indicate modality'),
        choices=CLM.MODALITY,
        widget=forms.CheckboxSelectMultiple,
        required=False
    )
    english = forms.FloatField(
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
    attended_social = forms.ChoiceField(
        label=_("Attended Social test"),
        widget=forms.Select, required=True,
        choices=(('yes', _("Yes")), ('no', _("No"))),
        initial='yes'
    )
    modality_social  = forms.MultipleChoiceField(
        label=_('Please indicate modality'),
        choices=CLM.MODALITY,
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    social_emotional = forms.FloatField(
        label=_('Results'),
        widget=forms.NumberInput(attrs=({'maxlength': 4})),
        min_value=0, required=False
    )
    attended_artistic = forms.ChoiceField(
        label=_("Attended Artistic test"),
        widget=forms.Select, required=True,
        choices=(('yes', _("Yes")), ('no', _("No"))),
        initial='yes'
    )
    modality_artistic = forms.MultipleChoiceField(
        label=_('Please indicate modality'),
        choices=CLM.MODALITY,
        widget=forms.CheckboxSelectMultiple,
        required=False
    )
    artistic = forms.FloatField(
        label=_('Results'),
        widget=forms.NumberInput(attrs=({'maxlength': 4})),
        min_value=0, required=False
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

    main_caregiver_nationality_other =  forms.CharField(
        label=_('Please specify'),
        widget=forms.TextInput, required=False
    )

    # student_p_code = forms.CharField(
    #     label=_('P-Code If a child lives in a tent / Brax in a random camp'),
    #     widget=forms.TextInput, required=False
    # )

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(BLNForm, self).__init__(*args, **kwargs)

        display_registry = ''
        instance = kwargs['instance'] if 'instance' in kwargs else ''
        form_action = reverse('clm:bln_add')
        self.fields['clm_type'].initial = 'BLN'
        self.fields['new_registry'].initial = 'yes'
        if instance:
            display_registry = ' d-none'
            form_action = reverse('clm:bln_edit', kwargs={'pk': instance.id})

        self.helper = FormHelper()
        self.helper.form_show_labels = True
        self.helper.form_action = form_action
        self.helper.layout = Layout(
            Fieldset(
                None,
                Div(
                    HTML('<span>A.1</span>'), css_class='block_tag'),
                Div(
                    HTML('<h4 id="alternatives-to-hidden-labels">' + _(
                        'Search CLM student') + '</h4>')
                ),
                Div(
                    'clm_type',
                    'student_id',
                    'enrollment_id',
                    css_class='row',
                ),
                Div(
                    HTML('<span class="badge badge-default"></span>'),
                    Div('search_clm_student', css_class='col-md-3'),
                    css_class='row',
                ),
                Div(
                    HTML('<p>' + _(
                        'Search by the following keywords: child first name, father name, last name, '
                        'child number or partner internal number') + '</p>'),
                ),
                css_id='search_options', css_class='bd-callout bd-callout-warning child_data E_right_border' + display_registry
            ),
            Fieldset(
                None,
                Div(
                    HTML('<span>A</span>'), css_class='block_tag'),
                Div(
                    HTML('<h4 id="alternatives-to-hidden-labels">' + _('General Information') + '</h4>')
                ),
                Div(

                    HTML('<span class="badge badge-default">1</span>'),
                    Div('new_registry', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">2</span>'),
                    Div('round', css_class='col-md-3'),
                    # HTML('<span class="badge badge-default">3</span>'),
                    Div('round_start_date', css_class='col-md-3 d-none'),
                    css_class='row',
                ),
                Div(
                    HTML('<span class="badge badge-default">3</span>'),
                    Div('governorate', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">4</span>'),
                    Div('district', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">5</span>'),
                    Div('cadaster', css_class='col-md-3'),
                    css_class='row',
                ),
                Div(
                    HTML('<span class="badge badge-default">6</span>'),
                    Div('location', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">7</span>'),
                    Div('language', css_class='col-md-3'),
                    css_class='row',
                ),
                Div(
                    HTML('<span class="badge badge-default">8</span>'),
                    Div('student_address', css_class='col-md-3'),
                    css_class='row',
                ),

                Div(
                    HTML('<span class="badge badge-default">9</span>'),
                    Div('registration_level', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">10</span>'),
                    Div('first_attendance_date', css_class='col-md-3'),
                    css_class='row',
                ),
                css_class='bd-callout bd-callout-warning child_data A_right_border'
            ),
            Fieldset(
                None,
                Div(HTML('<span>B</span>'), css_class='block_tag'),
                Div(
                    HTML('<h4 id="alternatives-to-hidden-labels">' + _('Child Information') + '</h4>')
                ),
                Div(
                    HTML('<span class="badge badge-default">1</span>'),
                    Div('student_first_name', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">2</span>'),
                    Div('student_father_name', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">3</span>'),
                    Div('student_last_name', css_class='col-md-3'),
                    css_class='row',
                ),
                Div(
                    HTML('<span class="badge badge-default">4</span>'),
                    Div('student_mother_fullname', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">5</span>'),
                    Div('student_sex', css_class='col-md-3'),
                    css_class='row',
                ),
                Div(
                    HTML('<span class="badge badge-default">6</span>'),
                    Div('student_nationality', css_class='col-md-3'),
                    HTML('<span class="badge badge-default" id="span_other_nationality">6.1</span>'),
                    Div('other_nationality', css_class='col-md-3'),
                    css_class='row',
                ),
                Div(
                    HTML('<span class="badge badge-default">7</span>'),
                    Div('student_birthday_year', css_class='col-md-2'),
                    HTML('<span class="badge badge-default">8</span>'),
                    Div('student_birthday_month', css_class='col-md-2'),
                    HTML('<span class="badge badge-default">9</span>'),
                    Div('student_birthday_day', css_class='col-md-2'),
                    css_class='row',
                ),
                Div(
                    HTML('<span class="badge badge-default">10</span>'),
                    Div('student_p_code', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">11</span>'),
                    Div('disability', css_class='col-md-3'),
                    css_class='row',
                ),

                Div(
                    HTML('<span class="badge badge-default">12</span>'),
                    Div('education_status', css_class='col-md-3'),
                    HTML('<span class="badge badge-default" id="span_miss_school_date">12.1</span>'),
                    Div('miss_school_date', css_class='col-md-3'),
                    css_class='row',
                ),
                Div(
                    HTML('<span class="badge badge-default">13</span>'),
                    Div('internal_number', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">14</span>'),
                    Div('source_of_identification', css_class='col-md-3'),
                    css_class='row',
                ),
                Div(
                    HTML('<span class="badge badge-default">16</span>'),
                    Div('source_of_transportation', css_class='col-md-3'),
                    css_class='row d-none',
                ),
                css_class='bd-callout bd-callout-warning child_data B_right_border'
            ),
            Fieldset(
                None,
                Div(HTML('<span>C</span>'), css_class='block_tag'),
                Div(
                    HTML('<h4 id="alternatives-to-hidden-labels">' + _('Parent/Caregiver Information') + '</h4>')
                ),
                Div(
                    HTML('<span class="badge badge-default">1</span>'),
                    Div('hh_educational_level', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">2</span>'),
                    Div('father_educational_level', css_class='col-md-3'),
                    css_class='row',
                ),
                Div(
                    HTML('<span class="badge badge-default">3</span>'),
                    Div('phone_number', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">3.1</span>'),
                    Div('phone_number_confirm', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">3.2</span>'),
                    Div('phone_owner', css_class='col-md-3'),
                    css_class='row',
                ),
                Div(
                    HTML('<span class="badge badge-default">4</span>'),
                    Div('second_phone_number', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">4.1</span>'),
                    Div('second_phone_number_confirm', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">4.2</span>'),
                    Div('second_phone_owner', css_class='col-md-3'),
                    css_class='row',
                ),
                Div(
                    HTML('<span class="badge badge-default">5</span>'),
                    Div('main_caregiver', css_class='col-md-3'),
                    HTML('<span class="badge badge-default" id="span_other_caregiver_relationship">5.1</span>'),
                    Div('other_caregiver_relationship', css_class='col-md-3'),
                    css_class='row',
                ),
                Div(
                    HTML('<span class="badge badge-default">6</span>'),
                    Div('main_caregiver_nationality', css_class='col-md-3'),
                    HTML('<span class="badge badge-default" id="span_main_caregiver_nationality_other">6.1</span>'),
                    Div('main_caregiver_nationality_other', css_class='col-md-3'),
                    css_class='row',
                ),
                Div(
                    HTML('<span class="badge badge-default">7</span>'),
                    Div('caretaker_first_name', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">8</span>'),
                    Div('caretaker_middle_name', css_class='col-md-3'),
                    css_class='row',
                ),
                Div(
                    HTML('<span class="badge badge-default">9</span>'),
                    Div('caretaker_last_name', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">10</span>'),
                    Div('caretaker_mother_name', css_class='col-md-3'),
                    css_class='row',
                ),
                Div(
                    HTML('<span class="badge badge-default">11</span>'),
                    Div('id_type', css_class='col-md-3'),
                    css_class='row',
                ),
                Div(
                    HTML('<span class="badge badge-default">12</span>'),
                    Div('case_number', css_class='col-md-4'),
                    HTML('<span class="badge badge-default">13</span>'),
                    Div('case_number_confirm', css_class='col-md-4'),
                    HTML('<span style="padding-top: 37px;">' +
                         '<a class="image-link" href="/static/images/unhcr_certificate.jpg" target="_blank">' +
                         '<img src="/static/images/icon-help.png" width="25px" height="25px;"/></a></span>'),
                    css_class='row child_id child_id1',
                ),
                Div(
                    HTML('<span class="badge badge-default">13</span>'),
                    Div('parent_individual_case_number', css_class='col-md-4'),
                    HTML('<span class="badge badge-default">14</span>'),
                    Div('parent_individual_case_number_confirm', css_class='col-md-4'),
                    HTML('<span style="padding-top: 37px;">' +
                         '<a class="image-link" href="/static/images/UNHCR_individualID.jpg" target="_blank">' +
                         '<img src="/static/images/icon-help.png" width="25px" height="25px;"/></a></span>'),
                    css_class='row child_id child_id1',
                ),
                Div(
                    HTML('<span class="badge badge-default">15</span>'),
                    Div('individual_case_number', css_class='col-md-4'),
                    HTML('<span class="badge badge-default">16</span>'),
                    Div('individual_case_number_confirm', css_class='col-md-4'),
                    HTML('<span style="padding-top: 37px;">' +
                         '<a class="image-link" href="/static/images/UNHCR_individualID.jpg" target="_blank">' +
                         '<img src="/static/images/icon-help.png" width="25px" height="25px;"/></a></span>'),
                    css_class='row child_id child_id1',
                ),
                Div(
                    HTML('<span class="badge badge-default">17</span>'),
                    Div('recorded_number', css_class='col-md-4'),
                    HTML('<span class="badge badge-default">18</span>'),
                    Div('recorded_number_confirm', css_class='col-md-4'),
                    HTML('<span style="padding-top: 37px;">' +
                         '<a class="image-link" href="/static/images/UNHCR_barcode.jpg" target="_blank">' +
                         '<img src="/static/images/icon-help.png" width="25px" height="25px;"/></a></span>'),
                    css_class='row child_id child_id2',
                ),
                Div(
                    HTML('<span class="badge badge-default">19</span>'),
                    Div('parent_national_number', css_class='col-md-4'),
                    HTML('<span class="badge badge-default">20</span>'),
                    Div('parent_national_number_confirm', css_class='col-md-4'),
                    HTML('<span style="padding-top: 37px;">' +
                         '<a class="image-link" href="/static/images/lebanese_nationalID.png" target="_blank">' +
                         '<img src="/static/images/icon-help.png" width="25px" height="25px;"/></a></span>'),
                    css_class='row child_id child_id3',
                ),
                Div(
                    HTML('<span class="badge badge-default">21</span>'),
                    Div('national_number', css_class='col-md-4'),
                    HTML('<span class="badge badge-default">22</span>'),
                    Div('national_number_confirm', css_class='col-md-4'),
                    HTML('<span style="padding-top: 37px;">' +
                         '<a class="image-link" href="/static/images/lebanese_nationalID.png" target="_blank">' +
                         '<img src="/static/images/icon-help.png" width="25px" height="25px;"/></a></span>'),
                    css_class='row child_id child_id3',
                ),
                Div(
                    HTML('<span class="badge badge-default">23</span>'),
                    Div('parent_syrian_national_number', css_class='col-md-4'),
                    HTML('<span class="badge badge-default">24</span>'),
                    Div('parent_syrian_national_number_confirm', css_class='col-md-4'),
                    HTML('<span style="padding-top: 37px;">' +
                         '<a class="image-link" href="/static/images/Syrian_passport.png" target="_blank">' +
                         '<img src="/static/images/icon-help.png" width="25px" height="25px;"/></a></span>'),
                    css_class='row child_id child_id4',
                ),
                Div(
                    HTML('<span class="badge badge-default">25</span>'),
                    Div('syrian_national_number', css_class='col-md-4'),
                    HTML('<span class="badge badge-default">26</span>'),
                    Div('syrian_national_number_confirm', css_class='col-md-4'),
                    HTML('<span style="padding-top: 37px;">' +
                         '<a class="image-link" href="/static/images/Syrian_passport.png" target="_blank">' +
                         '<img src="/static/images/icon-help.png" width="25px" height="25px;"/></a></span>'),
                    css_class='row child_id child_id4',
                ),
                Div(
                    HTML('<span class="badge badge-default">27</span>'),
                    Div('parent_sop_national_number', css_class='col-md-4'),
                    HTML('<span class="badge badge-default">28</span>'),
                    Div('parent_sop_national_number_confirm', css_class='col-md-4'),
                    HTML('<span style="padding-top: 37px;">' +
                         '<a class="image-link" href="/static/images/Palestinian_from_Lebanon.png" target="_blank">' +
                         '<img src="/static/images/icon-help.png" width="25px" height="25px;"/></a></span>'),
                    css_class='row child_id child_id5',
                ),
                Div(
                    HTML('<span class="badge badge-default">29</span>'),
                    Div('sop_national_number', css_class='col-md-4'),
                    HTML('<span class="badge badge-default">30</span>'),
                    Div('sop_national_number_confirm', css_class='col-md-4'),
                    HTML('<span style="padding-top: 37px;">' +
                         '<a class="image-link" href="/static/images/Palestinian_from_Lebanon.png" target="_blank">' +
                         '<img src="/static/images/icon-help.png" width="25px" height="25px;"/></a></span>'),
                    css_class='row child_id child_id5',
                ),
                Div(
                    HTML('<span class="badge badge-default">31</span>'),
                    Div('parent_other_number', css_class='col-md-4'),
                    HTML('<span class="badge badge-default">32</span>'),
                    Div('parent_other_number_confirm', css_class='col-md-4'),
                    css_class='row child_id child_id6',
                ),
                Div(
                    HTML('<span class="badge badge-default">33</span>'),
                    Div('other_number', css_class='col-md-4'),
                    HTML('<span class="badge badge-default">34</span>'),
                    Div('other_number_confirm', css_class='col-md-4'),
                    css_class='row child_id child_id6',
                ),
                css_class='bd-callout bd-callout-warning child_data C_right_border'
            ),

            Fieldset(
                None,
                Div(HTML('<span>D</span>'), css_class='block_tag'),
                Div(
                    HTML('<h4 id="alternatives-to-hidden-labels">' + _('Family Status') + '</h4>')
                ),
                Div(
                    HTML('<span class="badge badge-default">1</span>'),
                    Div('student_family_status', css_class='col-md-4'),
                    HTML('<span class="badge badge-default" id=span_student_have_children">1.1</span>'),
                    Div('student_have_children', css_class='col-md-4', css_id='student_have_children'),
                    HTML('<span class="badge badge-default" id="span_student_number_children">1.2</span>'),
                    Div('student_number_children', css_class='col-md-3'),
                    css_class='row',
                ),
                Div(
                    HTML('<span class="badge badge-default">3</span>'),
                    Div('have_labour_single_selection', css_class='col-md-3'),
                    css_class='row',
                ),
                Div(
                    HTML('<span class="badge badge-default">3.1</span>'),
                    Div('labours_single_selection', css_class='col-md-3', css_id='labours'),
                    HTML('<span class="badge badge-default" id="span_labours_other_specify">3.1.1</span>'),
                    Div('labours_other_specify', css_class='col-md-3'),
                    css_class='row',
                    id='labour_details_1'
                ),
                Div(
                    HTML('<span class="badge badge-default">3.2</span>'),
                    Div('labour_hours', css_class='col-md-3', css_id='labour_hours'),
                    HTML('<span class="badge badge-default">3.3</span>'),
                    Div('labour_weekly_income', css_class='col-md-3'),
                    css_class='row',
                    id='labour_details_2'
                ),
                css_class='bd-callout bd-callout-warning child_data D_right_border'
            ),
            Fieldset(
                None,
                Div(
                    HTML('<span>E</span>'), css_class='block_tag'),
                Div(
                    HTML('<h4 id="alternatives-to-hidden-labels">' + _('Assessment data') + '</h4>')
                ),
                Div(
                    HTML('<span class="badge badge-default">1</span>'),
                    Div('attended_arabic', css_class='col-md-2'),
                    HTML('<span class="badge badge-default" id="span_modality_arabic">1.1</span>'),
                    Div('modality_arabic',css_class='col-md-2 multiple-checbkoxes'),
                    HTML('<span class="badge badge-default" id="span_arabic">1.2</span>'),
                    Div('arabic', css_class='col-md-2'),
                    css_class='row',
                ),
                Div(
                    HTML('<span class="badge badge-default">2</span>'),
                    Div('attended_english', css_class='col-md-2'),
                    HTML('<span class="badge badge-default" id="span_modality_english">2.1</span>'),
                    Div('modality_english', css_class='col-md-2 multiple-checbkoxes'),
                    HTML('<span class="badge badge-default" id="span_english">2.2</span>'),
                    Div('english', css_class='col-md-2'),
                    css_class='row',
                ),
                Div(
                    HTML('<span class="badge badge-default">3</span>'),
                    Div('attended_math', css_class='col-md-2'),
                    HTML('<span class="badge badge-default" id="span_modality_math">3.1</span>'),
                    Div('modality_math', css_class='col-md-2 multiple-checbkoxes'),
                    HTML('<span class="badge badge-default" id="span_math">3.2</span>'),
                    Div('math', css_class='col-md-2'),
                    css_class='row',
                ),

                Div(
                    HTML('<span class="badge badge-default">4</span>'),
                    Div('attended_social', css_class='col-md-2'),
                    HTML('<span class="badge badge-default" id="span_modality_social">4.1</span>'),
                    Div('modality_social', css_class='col-md-2 multiple-checbkoxes'),
                    HTML('<span class="badge badge-default" id="span_social_emotional">4.2</span>'),
                    Div('social_emotional', css_class='col-md-2'),
                    css_class='row',
                ),

                Div(
                    HTML('<span class="badge badge-default">5</span>'),
                    Div('attended_artistic', css_class='col-md-2'),
                    HTML('<span class="badge badge-default" id="span_modality_artistic">5.1</span>'),
                    Div('modality_artistic', css_class='col-md-2 multiple-checbkoxes'),
                    HTML('<span class="badge badge-default" id="span_artistic">5.2</span>'),
                    Div('artistic', css_class='col-md-2'),
                    css_class='row',
                ),
                css_class='bd-callout bd-callout-warning E_right_border'
            ),
            FormActions(
                Submit('save', _('Save'), css_class='col-md-2'),
                Submit('save_add_another', _('Save and add another'), css_class='col-md-2 child_data col-md-2'),
                HTML('<a class="btn btn-info cancel-button" href="/clm/bln-list/" translation="' + _('Are you sure you want to cancel this registration?') + '">' + _('Back to list') + '</a>'),
                css_class='button-group'
            )
        )

    def clean(self):
        cleaned_data = super(BLNForm, self).clean()

        phone_number = cleaned_data.get("phone_number")
        phone_number_confirm = cleaned_data.get("phone_number_confirm")
        second_phone_number = cleaned_data.get("second_phone_number")
        second_phone_number_confirm = cleaned_data.get("second_phone_number_confirm")
        id_type = cleaned_data.get("id_type")
        case_number = cleaned_data.get("case_number")
        case_number_confirm = cleaned_data.get("case_number_confirm")
        individual_case_number = cleaned_data.get("individual_case_number")
        individual_case_number_confirm = cleaned_data.get("individual_case_number_confirm")
        recorded_number = cleaned_data.get("recorded_number")
        recorded_number_confirm = cleaned_data.get("recorded_number_confirm")
        national_number = cleaned_data.get("national_number")
        national_number_confirm = cleaned_data.get("national_number_confirm")
        syrian_national_number = cleaned_data.get("syrian_national_number")
        syrian_national_number_confirm = cleaned_data.get("syrian_national_number_confirm")
        sop_national_number = cleaned_data.get("sop_national_number")
        sop_national_number_confirm = cleaned_data.get("sop_national_number_confirm")

        parent_individual_case_number = cleaned_data.get("parent_individual_case_number")
        parent_individual_case_number_confirm = cleaned_data.get("parent_individual_case_number_confirm")
        parent_national_number = cleaned_data.get("parent_national_number")
        parent_national_number_confirm = cleaned_data.get("parent_national_number_confirm")
        sop_parent_national_number = cleaned_data.get("parent_sop_national_number")
        sop_parent_national_number_confirm = cleaned_data.get("parent_sop_national_number_confirm")
        parent_syrian_national_number = cleaned_data.get("parent_syrian_national_number")
        parent_syrian_national_number_confirm = cleaned_data.get("parent_syrian_national_number_confirm")
        parent_other_number = cleaned_data.get("parent_other_number")
        parent_other_number_confirm = cleaned_data.get("parent_other_number_confirm")
        other_number = cleaned_data.get("other_number")
        other_number_confirm = cleaned_data.get("other_number_confirm")
        education_status = cleaned_data.get("education_status")
        miss_school_date = cleaned_data.get("miss_school_date")
        student_nationality = cleaned_data.get("student_nationality")
        other_nationality = cleaned_data.get("other_nationality")
        main_caregiver = cleaned_data.get("main_caregiver")
        other_caregiver_relationship = cleaned_data.get("other_caregiver_relationship")
        main_caregiver_nationality = cleaned_data.get("main_caregiver_nationality")
        main_caregiver_nationality_other = cleaned_data.get("main_caregiver_nationality_other")
        have_labour_single_selection = cleaned_data.get("have_labour_single_selection")
        labours_single_selection = cleaned_data.get("labours_single_selection")
        labour_hours = cleaned_data.get("labour_hours")
        labour_weekly_income = cleaned_data.get("labour_weekly_income")
        student_have_children = cleaned_data.get("student_have_children")
        student_number_children = cleaned_data.get("student_number_children")
        labours_other_specify = cleaned_data.get("labours_other_specify")

        attended_arabic = cleaned_data.get("attended_arabic")
        modality_arabic = cleaned_data.get("modality_arabic")
        arabic = cleaned_data.get("arabic")

        attended_english = cleaned_data.get("attended_english")
        modality_english = cleaned_data.get("modality_english")
        english = cleaned_data.get("english")

        attended_artistic = cleaned_data.get("attended_artistic")
        modality_artistic = cleaned_data.get("modality_artistic")
        artistic = cleaned_data.get("artistic")

        attended_math = cleaned_data.get("attended_math")
        modality_math = cleaned_data.get("modality_math")
        math = cleaned_data.get("math")

        attended_social = cleaned_data.get("attended_social")
        modality_social = cleaned_data.get("modality_social")
        social_emotional = cleaned_data.get("social_emotional")

        if attended_arabic == 'yes':
            if not modality_arabic:
                self.add_error('modality_arabic', 'This field is required')
            if arabic is None:
                self.add_error('arabic', 'This field is required')

        if attended_english == 'yes':
            if not modality_english:
                self.add_error('modality_english', 'This field is required')
            if english is None:
                self.add_error('english', 'This field is required')

        if attended_artistic == 'yes':
            if not modality_artistic:
                self.add_error('modality_artistic', 'This field is required')
            if artistic is None:
                self.add_error('artistic', 'This field is required')

        if attended_math == 'yes':
            if not modality_math:
                self.add_error('modality_math', 'This field is required')
            if math is None:
                self.add_error('math', 'This field is required')

        if attended_social == 'yes':
            if not modality_social:
                self.add_error('modality_social', 'This field is required')
            if social_emotional is None:
                self.add_error('social_emotional', 'This field is required')


        if labours_single_selection == 'other_many_other':
            if not labours_other_specify:
                self.add_error('labours_other_specify', 'This field is required')

        if education_status != 'out of school':
            if not miss_school_date:
                self.add_error('miss_school_date', 'This field is required')
        if student_nationality.id == 6:
            if not other_nationality:
                self.add_error('other_nationality', 'This field is required')
        if main_caregiver == 'other':
            if not other_caregiver_relationship:
                self.add_error('other_caregiver_relationship', 'This field is required')
        if main_caregiver_nationality.id == 6:
            if not main_caregiver_nationality_other:
                self.add_error('main_caregiver_nationality_other', 'This field is required')
        if student_have_children:
            if not student_number_children:
                self.add_error('student_number_children', 'This field is required')
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

        if id_type == 'UNHCR Registered':
            if not case_number:
                self.add_error('case_number', 'This field is required')

            if case_number != case_number_confirm:
                msg = "The case numbers are not matched"
                self.add_error('case_number_confirm', msg)

            if parent_individual_case_number != parent_individual_case_number_confirm:
                msg = "The individual case numbers are not matched"
                self.add_error('parent_individual_case_number_confirm', msg)

            if individual_case_number != individual_case_number_confirm:
                msg = "The individual case numbers are not matched"
                self.add_error('individual_case_number_confirm', msg)

        if id_type == 'UNHCR Recorded':
            if not recorded_number:
                self.add_error('recorded_number', 'This field is required')

            if recorded_number != recorded_number_confirm:
                msg = "The recorded numbers are not matched"
                self.add_error('recorded_number_confirm', msg)

        if id_type == 'Syrian national ID':

            if not parent_syrian_national_number:
                self.add_error('parent_syrian_national_number', 'This field is required')

            if not parent_syrian_national_number_confirm:
                self.add_error('parent_syrian_national_number_confirm', 'This field is required')

            if parent_syrian_national_number_confirm and not len(parent_syrian_national_number_confirm) == 11:
                msg = "Please enter a valid number (11 digits)"
                self.add_error('parent_syrian_national_number_confirm', msg)

            if parent_syrian_national_number and not len(parent_syrian_national_number) == 11:
                msg = "Please enter a valid number (11 digits)"
                self.add_error('parent_syrian_national_number', msg)

            if parent_syrian_national_number != parent_syrian_national_number_confirm:
                msg = "The national numbers are not matched"
                self.add_error('parent_syrian_national_number_confirm', msg)

            if syrian_national_number != syrian_national_number_confirm:
                msg = "The national numbers are not matched"
                self.add_error('syrian_national_number_confirm', msg)

        if id_type == 'Lebanese national ID':
            if not parent_national_number:
                self.add_error('parent_national_number', 'This field is required')

            if not parent_national_number_confirm:
                self.add_error('parent_national_number_confirm', 'This field is required')

            if parent_national_number and not len(parent_national_number) == 12:
                msg = "Please enter a valid number (12 digits)"
                self.add_error('parent_national_number', msg)

            if parent_national_number_confirm and not len(parent_national_number_confirm) == 12:
                msg = "Please enter a valid number (12 digits)"
                self.add_error('parent_national_number_confirm', msg)

            if parent_national_number != parent_national_number_confirm:
                msg = "The national numbers are not matched"
                self.add_error('parent_national_number_confirm', msg)

            if national_number != national_number_confirm:
                msg = "The national numbers are not matched"
                self.add_error('national_number_confirm', msg)

        if id_type == 'Palestinian national ID':
            if not sop_parent_national_number:
                self.add_error('parent_sop_national_number', 'This field is required')

            if not sop_parent_national_number_confirm:
                self.add_error('parent_sop_national_number_confirm', 'This field is required')

            if sop_parent_national_number != sop_parent_national_number_confirm:
                msg = "The national numbers are not matched"
                self.add_error('parent_sop_national_number_confirm', msg)

            if sop_national_number != sop_national_number_confirm:
                msg = "The national numbers are not matched"
                self.add_error('sop_national_number_confirm', msg)

        if id_type == 'Other nationality':
            if not parent_other_number:
                self.add_error('parent_other_number', 'This field is required')

            if not parent_other_number_confirm:
                self.add_error('parent_other_number_confirm', 'This field is required')

            if parent_other_number != parent_other_number_confirm:
                msg = "The ID numbers are not matched"
                self.add_error('parent_other_number_confirm', msg)

            if other_number != other_number_confirm:
                msg = "The ID numbers are not matched"
                self.add_error('other_number_confirm', msg)

        # grades Max Value validation
        registration_level = cleaned_data.get("registration_level")
        arabic = cleaned_data.get("arabic")
        english = cleaned_data.get("english")
        math = cleaned_data.get("math")
        social_emotional = cleaned_data.get("social_emotional")
        artistic = cleaned_data.get("artistic")

        if registration_level == 'level_one':
            if arabic > 44:
                self.add_error('arabic', 'This value is greater that 44')
            if english > 36:
                self.add_error('english', 'This value is greater that 36')
            if math > 18:
                self.add_error('math', 'This value is greater that 18')
            if social_emotional > 24:
                self.add_error('social_emotional', 'This value is greater that 24')
            if artistic > 8:
                self.add_error('artistic', 'This value is greater that 8')
        elif registration_level == 'level_two':
            if arabic > 52:
                self.add_error('arabic', 'This value is greater that 52')
            if english > 56:
                self.add_error('english', 'This value is greater that 56')
            if math > 30:
                self.add_error('math', 'This value is greater that 30')
            if social_emotional > 24:
                self.add_error('social_emotional', 'This value is greater that 24')
            if artistic > 8:
                self.add_error('artistic', 'This value is greater that 8')
        else:
            if arabic > 58:
                self.add_error('arabic', 'This value is greater that 58')
            if english > 60:
                self.add_error('english', 'This value is greater that 60')
            if math > 32:
                self.add_error('math', 'This value is greater that 32')
            if social_emotional > 24:
                self.add_error('social_emotional', 'This value is greater that 24')
            if artistic > 8:
                self.add_error('artistic', 'This value is greater that 8')


    def save(self, request=None, instance=None, serializer=None):
        instance = super(BLNForm, self).save(request=request, instance=instance, serializer=BLNSerializer)
        instance.pre_test = {
            "BLN_ASSESSMENT/attended_arabic": request.POST.get('attended_arabic'),
            "BLN_ASSESSMENT/modality_arabic": request.POST.getlist('modality_arabic'),
            "BLN_ASSESSMENT/arabic": request.POST.get('arabic'),

            "BLN_ASSESSMENT/attended_english": request.POST.get('attended_english'),
            "BLN_ASSESSMENT/modality_english": request.POST.getlist('modality_english'),
            "BLN_ASSESSMENT/english": request.POST.get('english'),

            "BLN_ASSESSMENT/attended_artistic": request.POST.get('attended_artistic'),
            "BLN_ASSESSMENT/modality_artistic": request.POST.getlist('modality_artistic'),
            "BLN_ASSESSMENT/artistic": request.POST.get('artistic'),

            "BLN_ASSESSMENT/attended_math": request.POST.get('attended_math'),
            "BLN_ASSESSMENT/modality_math": request.POST.getlist('modality_math'),
            "BLN_ASSESSMENT/math": request.POST.get('math'),

            "BLN_ASSESSMENT/attended_social": request.POST.get('attended_social'),
            "BLN_ASSESSMENT/modality_social": request.POST.getlist('modality_social'),
            "BLN_ASSESSMENT/social_emotional": request.POST.get('social_emotional'),
        }

        instance.save()

    class Meta:
        model = BLN
        fields = CommonForm.Meta.fields + (
            'first_attendance_date',
            'student_birthday_year',
            'have_labour_single_selection',
            'labours_single_selection',
            'labours_other_specify',
            'labour_hours',
            'phone_number',
            'phone_number_confirm',
            'phone_owner',
            'second_phone_number',
            'second_phone_number_confirm',
            'second_phone_owner',
            'id_type',
            'case_number',
            'case_number_confirm',
            'individual_case_number',
            'individual_case_number_confirm',
            'parent_individual_case_number',
            'parent_individual_case_number_confirm',
            'recorded_number',
            'recorded_number_confirm',
            'national_number',
            'national_number_confirm',
            'syrian_national_number',
            'syrian_national_number_confirm',
            'sop_national_number',
            'sop_national_number_confirm',
            'parent_national_number',
            'parent_national_number_confirm',
            'parent_syrian_national_number',
            'parent_syrian_national_number_confirm',
            'parent_sop_national_number',
            'parent_sop_national_number_confirm',
            'parent_other_number',
            'parent_other_number_confirm',
            'other_number',
            'other_number_confirm',
            'no_child_id_confirmation',
            'source_of_identification',
            'other_nationality',
            'education_status',
            'caretaker_first_name',
            'caretaker_middle_name',
            'caretaker_last_name',
            'caretaker_mother_name',
            'miss_school_date',
            'student_have_children',
            'student_family_status',
            'student_number_children',
            'round_start_date',
            'cadaster',
            'registration_level',
            'main_caregiver',
            'main_caregiver_nationality',
            'other_caregiver_relationship',
            'labour_weekly_income',
            'source_of_transportation',
            'student_p_code'
        )

    class Media:
        js = (
            # 'js/jquery-3.3.1.min.js',
            # 'js/jquery-ui-1.12.1.js',
            # 'js/validator.js',
            # 'js/registrations.js',
        )

class ABLNForm(CommonForm):
    REGISTRATION_LEVEL = (
        ('', '----------'),
        ('level_one', _('Level one')),
        ('level_two', _('Level two')),
        # ('level_three', _('Level three'))
    )
    YEARS_ABLN = list(((str(x), x) for x in range(Person.CURRENT_YEAR - 15, Person.CURRENT_YEAR - 8)))
    YEARS_ABLN.insert(0, ('', '---------'))

    first_attendance_date = forms.DateField(
        label=_("First attendance date"),
        required=True
    )
    miss_school_date = forms.DateField(
        label=_("Miss school date"),
        required=False,
    )

    new_registry = forms.ChoiceField(
        label=_("First time registered?"),
        widget=forms.Select, required=True,
        choices=(('yes', _("Yes")), ('no', _("No"))),
        initial='yes'
    )

    round = forms.ModelChoiceField(
        queryset=CLMRound.objects.filter(current_round_abln=True), widget=forms.Select,
        label=_('Round'),
        empty_label='-------',
        required=True, to_field_name='id',
    )

    round_start_date = forms.DateField(
        label=_("Round start date"),
        required=False
    )
    registration_level = forms.ChoiceField(
        label=_("Registration level"),
        widget=forms.Select, required=True,
        choices=REGISTRATION_LEVEL
    )
    student_birthday_year = forms.ChoiceField(
        label=_("Birthday year"),
        widget=forms.Select, required=True,
        choices=YEARS_ABLN
    )

    student_family_status = forms.ChoiceField(
        label=_('What is the family status of the child?'),
        widget=forms.Select, required=True,
        choices=Student.FAMILY_STATUS,
        initial='single'
    )
    student_have_children = forms.TypedChoiceField(
        label=_("Does the child have children?"),
        choices=YES_NO_CHOICE,
        coerce=lambda x: bool(int(x)),
        widget=forms.RadioSelect,
        required=True,
    )
    student_number_children = forms.IntegerField(
        label=_('How many children does this child have?'),
        widget=forms.TextInput, required=False
    )

    have_labour_single_selection = forms.ChoiceField(
        label=_('Does the child participate in work?'),
        widget=forms.Select, required=True,
        choices=CLM.HAVE_LABOUR,
        initial='no'
    )
    labours_single_selection = forms.ChoiceField(
        label=_('What is the type of work ?'),
        widget=forms.Select, required=False,
        choices=CLM.LABOURS
    )
    labours_other_specify = forms.CharField(
        label=_('Please specify(hotel, restaurant, transport, personal services such as cleaning, hair care, cooking and childcare)'),
        widget=forms.TextInput, required=False
    )
    labour_hours = forms.CharField(
        label=_('How many hours does this child work in a day?'),
        widget=forms.TextInput, required=False
    )
    labour_weekly_income = forms.ChoiceField(
        label=_('What is the income of the child per week?'),
        widget=forms.Select,
        choices=Student.STUDENT_INCOME,
        initial='single',
        required=False
    )
    education_status = forms.ChoiceField(
        label=_('Education status'),
        widget=forms.Select, required=True,
        choices=(
            ('', '----------'),
            ('out of school', _('Out of school')),
            ('enrolled in formal education but did not continue', _("Enrolled in formal education but did not continue")),
            ('enrolled in ABLN', _("Enrolled in ABLN")),
        ),
        initial=''
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
    id_type = forms.ChoiceField(
        label=_("ID type of the caretaker"),
        widget=forms.Select(attrs=({'translation': _('Child no ID confirmation popup message')})),
        required=True,
        choices=(
            ('', '----------'),
            ('UNHCR Registered', _('UNHCR Registered')),
            ('UNHCR Recorded', _("UNHCR Recorded")),
            ('Syrian national ID', _("Syrian national ID")),
            ('Palestinian national ID', _("Palestinian national ID")),
            ('Lebanese national ID', _("Lebanese national ID")),
            ('Other nationality', _("Other nationality")),
            ('Child have no ID', _("Child have no ID"))
        ),
        initial=''
    )
    case_number = forms.RegexField(
        regex=r'^((245)|(380)|(568)|(705)|(781)|(909)|(947)|(954)|(LEB)|(leb))-[0-9][0-9][C]\d{5}$',
        widget=forms.TextInput(attrs={'placeholder': 'Format: XXX-XXCXXXXX'}),
        required=False,
        label=_('UNHCR Case Number')
    )
    case_number_confirm = forms.RegexField(
        regex=r'^((245)|(380)|(568)|(705)|(781)|(909)|(947)|(954)|(LEB)|(leb))-[0-9][0-9][C]\d{5}$',
        widget=forms.TextInput(attrs={'placeholder': 'Format: XXX-XXCXXXXX'}),
        required=False,
        label=_('Confirm UNHCR Case Number')
    )
    parent_individual_case_number = forms.RegexField(
        regex=r'^((245)|(380)|(568)|(705)|(781)|(909)|(947)|(954)|(LEB)|(leb))-[0-9]{8}$',
        widget=forms.TextInput(attrs={'placeholder': 'Format: XXX-XXXXXXXX'}),
        required=False,
        label=_(
            'Caretaker Individual ID from the certificate (Optional, in case not listed in the certificate)')
    )
    parent_individual_case_number_confirm = forms.RegexField(
        regex=r'^((245)|(380)|(568)|(705)|(781)|(909)|(947)|(954)|(LEB)|(leb))-[0-9]{8}$',
        widget=forms.TextInput(attrs={'placeholder': 'Format: XXX-XXXXXXXX'}),
        required=False,
        label=_(
            'Confirm Caretaker Individual ID from the certificate (Optional, in case not listed in the certificate)')
    )
    individual_case_number = forms.RegexField(
        regex=r'^((245)|(380)|(568)|(705)|(781)|(909)|(947)|(954)|(LEB)|(leb))-[0-9]{8}$',
        widget=forms.TextInput(attrs={'placeholder': 'Format: XXX-XXXXXXXX'}),
        required=False,
        label=_(
            'Individual ID of the Child from the certificate (Optional, in case not listed in the certificate)')
    )
    individual_case_number_confirm = forms.RegexField(
        regex=r'^((245)|(380)|(568)|(705)|(781)|(909)|(947)|(954)|(LEB)|(leb))-[0-9]{8}$',
        widget=forms.TextInput(attrs={'placeholder': 'Format: XXX-XXXXXXXX'}),
        required=False,
        label=_(
                'Confirm Individual ID of the Child from the certificate (Optional, in case not listed in the certificate)')
    )
    recorded_number = forms.RegexField(
        regex=r'^((245)|(380)|(568)|(705)|(781)|(909)|(947)|(954)|(LEB)|(leb))-[0-9][0-9][C]\d{5}$',
        widget=forms.TextInput(attrs={'placeholder': 'Format: LEB-XXCXXXXX'}),
        required=False,
        label=_('UNHCR Barcode number (Shifra number)')
    )
    recorded_number_confirm = forms.RegexField(
        regex=r'^((245)|(380)|(568)|(705)|(781)|(909)|(947)|(954)|(LEB)|(leb))-[0-9][0-9][C]\d{5}$',
        widget=forms.TextInput(attrs={'placeholder': 'Format: LEB-XXCXXXXX'}),
        required=False,
        label=_('Confirm UNHCR Barcode number (Shifra number)')
    )

    national_number = forms.RegexField(
        regex=r'^\d{12}$',
        widget=forms.TextInput(attrs={'placeholder': 'Format: XXXXXXXXXXXX'}),
        required=False,
        label=_('Lebanese ID number of the child (Optional)')
    )
    national_number_confirm = forms.RegexField(
        regex=r'^\d{12}$',
        widget=forms.TextInput(attrs={'placeholder': 'Format: XXXXXXXXXXXX'}),
        required=False,
        label=_('Confirm Lebanese ID number of the child (optional)')
    )
    syrian_national_number = forms.RegexField(
        regex=r'^\d{11}$',
        required=False,
        label=_('National ID number of the child (Optional)')
    )
    syrian_national_number_confirm = forms.RegexField(
        regex=r'^\d{11}$',
        required=False,
        label=_('Confirm National ID number of the child (Optional)')
    )
    sop_national_number = forms.CharField(
        required=False,
        label=_('Palestinian ID number of the child (Optional)')
    )
    sop_national_number_confirm = forms.CharField(
        required=False,
        label=_('Confirm Palestinian ID number of the child (optional)')
    )
    parent_national_number = forms.RegexField(
        regex=r'^\d{12}$',
        widget=forms.TextInput(attrs={'placeholder': 'Format: XXXXXXXXXXXX'}),
        required=False,
        label=_('Lebanese ID number of the caretaker (Mandatory)')
    )
    parent_national_number_confirm = forms.RegexField(
        regex=r'^\d{12}$',
        widget=forms.TextInput(attrs={'placeholder': 'Format: XXXXXXXXXXXX'}),
        required=False,
        label=_('Confirm Lebanese ID number of the caretaker (Mandatory)')
    )
    parent_national_number = forms.RegexField(
        regex=r'^\d{12}$',
        widget=forms.TextInput(attrs={'placeholder': 'Format: XXXXXXXXXXXX'}),
        required=False,
        label=_('Lebanese ID number of the caretaker (Mandatory)')
    )
    parent_syrian_national_number = forms.RegexField(
        regex=r'^\d{11}$',
        required=False,
        label=_('National ID number of the Caretaker (Mandatory)')
    )
    parent_syrian_national_number_confirm = forms.RegexField(
        regex=r'^\d{11}$',
        required=False,
        label=_('Confirm National ID number of the Caretaker (Mandatory)')
    )
    parent_sop_national_number = forms.CharField(
        # regex=r'^\d{11}$',
        required=False,
        label=_('Palestinian ID number of the Caretaker (Mandatory)')
    )
    parent_sop_national_number_confirm = forms.CharField(
        # regex=r'^\d{11}$',
        required=False,
        label=_('Confirm Palestinian ID number of the Caretaker (Mandatory)')
    )

    parent_other_number = forms.CharField(
        required=False,
        label=_('ID number of the Caretaker (Mandatory)')
    )
    parent_other_number_confirm = forms.CharField(
        required=False,
        label=_('Confirm ID number of the Caretaker (Mandatory)')
    )
    other_number = forms.CharField(
        required=False,
        label=_(' ID number of the child (Optional)')
    )
    other_number_confirm = forms.CharField(
        required=False,
        label=_('Confirm ID number of the child (optional)')
    )

    no_child_id_confirmation = forms.CharField(widget=forms.HiddenInput, required=False)
    no_parent_id_confirmation = forms.CharField(widget=forms.HiddenInput, required=False)

    source_of_identification = forms.ChoiceField(
        label=_("Source of identification of the child to ABLN"),
        widget=forms.Select,
        required=True,
        choices=(
            ('', '----------'),
            ('Referred by CP partner', _('Referred by CP partner')),
            ('Referred by youth partner', _('Referred by youth partner')),
            ('Family walked in to NGO', _('Family walked in to NGO')),
            ('Referral from another NGO', _('Referral from another NGO')),
            ('Referral from another Municipality', _('Referral from Municipality')),
            ('Direct outreach', _('Direct outreach')),
            ('List database', _('List database')),
            # ('bln', _('BLN'))
        ),
        initial=''
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
    # attended_english = forms.ChoiceField(
    #     label=_("Attended English test"),
    #     widget=forms.Select, required=True,
    #     choices=(('yes', _("Yes")), ('no', _("No"))),
    #     initial='yes'
    # )
    # modality_english = forms.ChoiceField(
    #     label=_("Please indicate modality"),
    #     widget=forms.Select, required=False,
    #     choices=(
    #         ('', '----------'),
    #         ('online', _("Online Forms")),
    #         ('phone', _("Phone / Whatasapp")),
    #         ('parents', _("Asking Parents")),
    #         ('offline', _("Offline(F2F)"))
    #     )
    # )
    # english = forms.FloatField(
    #     label=_('Results'),
    #     widget=forms.NumberInput(attrs=({'maxlength': 4})),
    #     min_value=0, required=False
    # )
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
    attended_social = forms.ChoiceField(
        label=_("Attended Social test"),
        widget=forms.Select, required=True,
        choices=(('yes', _("Yes")), ('no', _("No"))),
        initial='yes'
    )
    modality_social = forms.MultipleChoiceField(
        label=_('Please indicate modality'),
        choices=CLM.MODALITY,
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    social_emotional = forms.FloatField(
        label=_('Results'),
        widget=forms.NumberInput(attrs=({'maxlength': 4})),
        min_value=0, required=False
    )

    attended_artistic = forms.ChoiceField(
        label=_("Attended Artistic test"),
        widget=forms.Select, required=True,
        choices=(('yes', _("Yes")), ('no', _("No"))),
        initial='yes'
    )
    modality_artistic  = forms.MultipleChoiceField(
        label=_('Please indicate modality'),
        choices=CLM.MODALITY,
        widget=forms.CheckboxSelectMultiple,
        required=False
    )
    artistic = forms.FloatField(
        label=_('Results'),
        widget=forms.NumberInput(attrs=({'maxlength': 4})),
        min_value=0, required=False
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

    main_caregiver_nationality_other =  forms.CharField(
        label=_('specify'),
        widget=forms.TextInput, required=False
    )

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(ABLNForm, self).__init__(*args, **kwargs)

        display_registry = ''
        instance = kwargs['instance'] if 'instance' in kwargs else ''
        form_action = reverse('clm:abln_add')
        self.fields['clm_type'].initial = 'ABLN'
        self.fields['new_registry'].initial = 'yes'
        if instance:
            display_registry = ' d-none'
            form_action = reverse('clm:abln_edit', kwargs={'pk': instance.id})

        self.helper = FormHelper()
        self.helper.form_show_labels = True
        self.helper.form_action = form_action
        self.helper.layout = Layout(
            Fieldset(
                None,
                Div( HTML('<span>A</span>'), css_class='block_tag'),
                Div(
                    HTML('<h4 id="alternatives-to-hidden-labels">' + _(
                        'Search CLM student') + '</h4>')
                ),
                Div(
                    'clm_type',
                    'student_id',
                    'enrollment_id',
                    css_class='row',
                ),
                Div(
                    HTML('<span class="badge badge-default">1</span>'),

                    Div('search_clm_student', css_class='col-md-3'),
                    css_class='row',
                ),
                Div(
                    HTML('<p>' + _(
                        'Search by the following keywords: child first name, father name, last name, '
                        'child number or partner internal number') + '</p>'),
                ),
                css_id='search_options', css_class='bd-callout bd-callout-warning child_data E_right_border' + display_registry
            ),
            Fieldset(
                None,
                Div(
                    HTML('<span>A</span>'), css_class='block_tag'),
                Div(
                    HTML('<h4 id="alternatives-to-hidden-labels">' + _('General Information') + '</h4>')
                ),
                Div(

                    HTML('<span class="badge badge-default">1</span>'),
                    Div('new_registry', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">2</span>'),
                    Div('round', css_class='col-md-3'),
                    # HTML('<span class="badge badge-default">3</span>'),
                    Div('round_start_date', css_class='col-md-3 d-none'),
                    css_class='row',
                ),
                Div(
                    HTML('<span class="badge badge-default">3</span>'),
                    Div('governorate', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">4</span>'),
                    Div('district', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">5</span>'),
                    Div('cadaster', css_class='col-md-3'),
                    css_class='row',
                ),
                Div(
                    HTML('<span class="badge badge-default">6</span>'),
                    Div('location', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">7</span>'),
                    Div('language', css_class='col-md-3'),
                    css_class='row',
                ),
                Div(
                    HTML('<span class="badge badge-default">8</span>'),
                    Div('student_address', css_class='col-md-3'),
                    css_class='row',
                ),

                Div(
                    HTML('<span class="badge badge-default">9</span>'),
                    Div('registration_level', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">10</span>'),
                    Div('first_attendance_date', css_class='col-md-3'),
                    css_class='row',
                ),
                css_class='bd-callout bd-callout-warning child_data A_right_border'
            ),
            Fieldset(
                None,
                Div(HTML('<span>B</span>'), css_class='block_tag'),
                Div(
                    HTML('<h4 id="alternatives-to-hidden-labels">' + _('Child Information') + '</h4>')
                ),
                Div(
                    HTML('<span class="badge badge-default">1</span>'),
                    Div('student_first_name', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">2</span>'),
                    Div('student_father_name', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">3</span>'),
                    Div('student_last_name', css_class='col-md-3'),
                    css_class='row',
                ),
                Div(
                    HTML('<span class="badge badge-default">4</span>'),
                    Div('student_mother_fullname', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">5</span>'),
                    Div('student_sex', css_class='col-md-3'),
                    css_class='row',
                ),
                Div(
                    HTML('<span class="badge badge-default">6</span>'),
                    Div('student_nationality', css_class='col-md-3'),
                    HTML('<span class="badge badge-default" id="span_other_nationality">6.1</span>'),
                    Div('other_nationality', css_class='col-md-3'),
                    css_class='row',
                ),
                Div(
                    HTML('<span class="badge badge-default">7</span>'),
                    Div('student_birthday_year', css_class='col-md-2'),
                    HTML('<span class="badge badge-default">8</span>'),
                    Div('student_birthday_month', css_class='col-md-2'),
                    HTML('<span class="badge badge-default">9</span>'),
                    Div('student_birthday_day', css_class='col-md-2'),
                    css_class='row',
                ),
                Div(
                    HTML('<span class="badge badge-default">10</span>'),
                    Div('student_p_code', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">11</span>'),
                    Div('disability', css_class='col-md-3'),
                    css_class='row',
                ),

                Div(
                    HTML('<span class="badge badge-default">12</span>'),
                    Div('education_status', css_class='col-md-3'),
                    HTML('<span class="badge badge-default" id="span_miss_school_date">12.1</span>'),
                    Div('miss_school_date', css_class='col-md-3'),
                    css_class='row',
                ),
                Div(
                    HTML('<span class="badge badge-default">13</span>'),
                    Div('internal_number', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">14</span>'),
                    Div('source_of_identification', css_class='col-md-3'),
                    css_class='row',
                ),
                Div(
                    HTML('<span class="badge badge-default">16</span>'),
                    Div('source_of_transportation', css_class='col-md-3'),
                    css_class='row d-none',
                ),
                css_class='bd-callout bd-callout-warning child_data B_right_border'
            ),
            Fieldset(
                None,
                Div(HTML('<span>C</span>'), css_class='block_tag'),
                Div(
                    HTML('<h4 id="alternatives-to-hidden-labels">' + _('Parent/Caregiver Information') + '</h4>')
                ),
                Div(
                    HTML('<span class="badge badge-default">1</span>'),
                    Div('hh_educational_level', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">2</span>'),
                    Div('father_educational_level', css_class='col-md-3'),
                    css_class='row',
                ),
                Div(
                    HTML('<span class="badge badge-default">3</span>'),
                    Div('phone_number', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">3.1</span>'),
                    Div('phone_number_confirm', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">3.2</span>'),
                    Div('phone_owner', css_class='col-md-3'),
                    css_class='row',
                ),
                Div(
                    HTML('<span class="badge badge-default">4</span>'),
                    Div('second_phone_number', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">4.1</span>'),
                    Div('second_phone_number_confirm', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">4.2</span>'),
                    Div('second_phone_owner', css_class='col-md-3'),
                    css_class='row',
                ),
                Div(
                    HTML('<span class="badge badge-default">5</span>'),
                    Div('main_caregiver', css_class='col-md-3'),
                    HTML('<span class="badge badge-default" id="span_other_caregiver_relationship">5.1</span>'),
                    Div('other_caregiver_relationship', css_class='col-md-3'),
                    css_class='row',
                ),
                Div(
                    HTML('<span class="badge badge-default">6</span>'),
                    Div('main_caregiver_nationality', css_class='col-md-3'),
                    HTML('<span class="badge badge-default" id="span_main_caregiver_nationality_other">6.1</span>'),
                    Div('main_caregiver_nationality_other', css_class='col-md-3'),
                    css_class='row',
                ),
                Div(
                    HTML('<span class="badge badge-default">7</span>'),
                    Div('caretaker_first_name', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">8</span>'),
                    Div('caretaker_middle_name', css_class='col-md-3'),
                    css_class='row',
                ),
                Div(
                    HTML('<span class="badge badge-default">9</span>'),
                    Div('caretaker_last_name', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">10</span>'),
                    Div('caretaker_mother_name', css_class='col-md-3'),
                    css_class='row',
                ),
                Div(
                    HTML('<span class="badge badge-default">11</span>'),
                    Div('id_type', css_class='col-md-3'),
                    css_class='row',
                ),
                Div(
                    HTML('<span class="badge badge-default">12</span>'),
                    Div('case_number', css_class='col-md-4'),
                    HTML('<span class="badge badge-default">13</span>'),
                    Div('case_number_confirm', css_class='col-md-4'),
                    HTML('<span style="padding-top: 37px;">' +
                         '<a  class="image-link" href="/static/images/unhcr_certificate.jpg" target="_blank">' +
                         '<img src="/static/images/icon-help.png" width="25px" height="25px;"/></a></span>'),
                    css_class='row child_id child_id1',
                ),
                Div(
                    HTML('<span class="badge badge-default">13</span>'),
                    Div('parent_individual_case_number', css_class='col-md-4'),
                    HTML('<span class="badge badge-default">14</span>'),
                    Div('parent_individual_case_number_confirm', css_class='col-md-4'),
                    HTML('<span style="padding-top: 37px;">' +
                         '<a class="image-link" href="/static/images/UNHCR_individualID.jpg" target="_blank">' +
                         '<img src="/static/images/icon-help.png" width="25px" height="25px;"/></a></span>'),
                    css_class='row child_id child_id1',
                ),
                Div(
                    HTML('<span class="badge badge-default">15</span>'),
                    Div('individual_case_number', css_class='col-md-4'),
                    HTML('<span class="badge badge-default">16</span>'),
                    Div('individual_case_number_confirm', css_class='col-md-4'),
                    HTML('<span style="padding-top: 37px;">' +
                         '<a  class="image-link" href="/static/images/UNHCR_individualID.jpg" target="_blank">' +
                         '<img src="/static/images/icon-help.png" width="25px" height="25px;"/></a></span>'),
                    css_class='row child_id child_id1',
                ),
                Div(
                    HTML('<span class="badge badge-default">17</span>'),
                    Div('recorded_number', css_class='col-md-4'),
                    HTML('<span class="badge badge-default">18</span>'),
                    Div('recorded_number_confirm', css_class='col-md-4'),
                    HTML('<span style="padding-top: 37px;">' +
                         '<a  class="image-link" href="/static/images/UNHCR_barcode.jpg" target="_blank">' +
                         '<img src="/static/images/icon-help.png" width="25px" height="25px;"/></a></span>'),
                    css_class='row child_id child_id2',
                ),
                Div(
                    HTML('<span class="badge badge-default">19</span>'),
                    Div('parent_national_number', css_class='col-md-4'),
                    HTML('<span class="badge badge-default">20</span>'),
                    Div('parent_national_number_confirm', css_class='col-md-4'),
                    HTML('<span style="padding-top: 37px;">' +
                         '<a  class="image-link" href="/static/images/lebanese_nationalID.png" target="_blank">' +
                         '<img src="/static/images/icon-help.png" width="25px" height="25px;"/></a></span>'),
                    css_class='row child_id child_id3',
                ),

                Div(
                    HTML('<span class="badge badge-default">21</span>'),
                    Div('national_number', css_class='col-md-4'),
                    HTML('<span class="badge badge-default">22</span>'),
                    Div('national_number_confirm', css_class='col-md-4'),
                    HTML('<span style="padding-top: 37px;">' +
                         '<a  class="image-link" href="/static/images/lebanese_nationalID.png" target="_blank">' +
                         '<img src="/static/images/icon-help.png" width="25px" height="25px;"/></a></span>'),
                    css_class='row child_id child_id3',
                ),
                Div(
                    HTML('<span class="badge badge-default">23</span>'),
                    Div('parent_syrian_national_number', css_class='col-md-4'),
                    HTML('<span class="badge badge-default">24</span>'),
                    Div('parent_syrian_national_number_confirm', css_class='col-md-4'),
                    HTML('<span style="padding-top: 37px;">' +
                         '<a  class="image-link" href="/static/images/Syrian_passport.png" target="_blank">' +
                         '<img src="/static/images/icon-help.png" width="25px" height="25px;"/></a></span>'),
                    css_class='row child_id child_id4',
                ),
                Div(
                    HTML('<span class="badge badge-default">25</span>'),
                    Div('syrian_national_number', css_class='col-md-4'),
                    HTML('<span class="badge badge-default">26</span>'),
                    Div('syrian_national_number_confirm', css_class='col-md-4'),
                    HTML('<span style="padding-top: 37px;">' +
                         '<a  class="image-link" href="/static/images/Syrian_passport.png" target="_blank">' +
                         '<img src="/static/images/icon-help.png" width="25px" height="25px;"/></a></span>'),
                    css_class='row child_id child_id4',
                ),
                Div(
                    HTML('<span class="badge badge-default">27</span>'),
                    Div('parent_sop_national_number', css_class='col-md-4'),
                    HTML('<span class="badge badge-default">28</span>'),
                    Div('parent_sop_national_number_confirm', css_class='col-md-4'),
                    HTML('<span style="padding-top: 37px;">' +
                         '<a  class="image-link" href="/static/images/Palestinian_from_Lebanon.png" target="_blank">' +
                         '<img src="/static/images/icon-help.png" width="25px" height="25px;"/></a></span>'),
                    css_class='row child_id child_id5',
                ),
                Div(
                    HTML('<span class="badge badge-default">29</span>'),
                    Div('sop_national_number', css_class='col-md-4'),
                    HTML('<span class="badge badge-default">30</span>'),
                    Div('sop_national_number_confirm', css_class='col-md-4'),
                    HTML('<span style="padding-top: 37px;">' +
                         '<a  class="image-link" href="/static/images/Palestinian_from_Lebanon.png" target="_blank">' +
                         '<img src="/static/images/icon-help.png" width="25px" height="25px;"/></a></span>'),
                    css_class='row child_id child_id5',
                ),
                Div(
                    HTML('<span class="badge badge-default">31</span>'),
                    Div('parent_other_number', css_class='col-md-4'),
                    HTML('<span class="badge badge-default">32</span>'),
                    Div('parent_other_number_confirm', css_class='col-md-4'),
                    css_class='row child_id child_id6',
                ),
                Div(
                    HTML('<span class="badge badge-default">33</span>'),
                    Div('other_number', css_class='col-md-4'),
                    HTML('<span class="badge badge-default">34</span>'),
                    Div('other_number_confirm', css_class='col-md-4'),
                    css_class='row child_id child_id6',
                ),
                css_class='bd-callout bd-callout-warning child_data C_right_border'
            ),

            Fieldset(
                None,
                Div(HTML('<span>D</span>'), css_class='block_tag'),
                Div(
                    HTML('<h4 id="alternatives-to-hidden-labels">' + _('Family Status') + '</h4>')
                ),
                Div(
                    HTML('<span class="badge badge-default">1</span>'),
                    Div('student_family_status', css_class='col-md-3'),
                    HTML('<span class="badge badge-default" id="span_student_have_children">1.1</span>'),
                    Div('student_have_children', css_class='col-md-3', css_id='student_have_children'),
                    HTML('<span class="badge badge-default" id="span_student_number_children">1.2</span>'),
                    Div('student_number_children', css_class='col-md-3'),
                    css_class='row',
                ),
                Div(
                    HTML('<span class="badge badge-default">3</span>'),
                    Div('have_labour_single_selection', css_class='col-md-3'),
                    css_class='row',
                ),
                Div(
                    HTML('<span class="badge badge-default">3.1</span>'),
                    Div('labours_single_selection', css_class='col-md-3', css_id='labours'),
                    HTML('<span class="badge badge-default" id="span_labours_other_specify">3.1.1</span>'),
                    Div('labours_other_specify', css_class='col-md-3'),
                    css_class='row',
                    id='labour_details_1'
                ),
                Div(
                    HTML('<span class="badge badge-default">3.2</span>'),
                    Div('labour_hours', css_class='col-md-3', css_id='labour_hours'),
                    HTML('<span class="badge badge-default">3.3</span>'),
                    Div('labour_weekly_income', css_class='col-md-3'),
                    css_class='row',
                    id='labour_details_2'
                ),
                css_class='bd-callout bd-callout-warning child_data D_right_border'
            ),
            Fieldset(
                None,
                Div(
                    HTML('<span>E</span>'), css_class='block_tag'),
                Div(
                    HTML('<h4 id="alternatives-to-hidden-labels">' + _('Assessment data') + '</h4>')
                ),
                Div(
                    HTML('<span class="badge badge-default">1</span>'),
                    Div('attended_arabic', css_class='col-md-2'),
                    HTML('<span class="badge badge-default" id="span_modality_arabic">1.1</span>'),
                    Div('modality_arabic', css_class='col-md-2 multiple-checbkoxes'),
                    HTML('<span class="badge badge-default" id="span_arabic">1.2</span>'),
                    Div('arabic', css_class='col-md-2'),
                    css_class='row',
                ),
                # Div(
                #     HTML('<span class="badge badge-default">2</span>'),
                #     Div('attended_english', css_class='col-md-2'),
                #     HTML('<span class="badge badge-default" id="span_modality_english">2.1</span>'),
                #     Div('modality_english', css_class='col-md-2 multiple-checbkoxes'),
                #     HTML('<span class="badge badge-default" id="span_english">2.2</span>'),
                #     Div('english', css_class='col-md-2'),
                #     css_class='row',
                # ),
                Div(
                    HTML('<span class="badge badge-default">2</span>'),
                    Div('attended_math', css_class='col-md-2'),
                    HTML('<span class="badge badge-default" id="span_modality_math">2.1</span>'),
                    Div('modality_math', css_class='col-md-2 multiple-checbkoxes'),
                    HTML('<span class="badge badge-default" id="span_math">2.2</span>'),
                    Div('math', css_class='col-md-2'),
                    css_class='row',
                ),

                Div(
                    HTML('<span class="badge badge-default">3</span>'),
                    Div('attended_social', css_class='col-md-2'),
                    HTML('<span class="badge badge-default" id="span_modality_social">3.1</span>'),
                    Div('modality_social', css_class='col-md-2 multiple-checbkoxes'),
                    HTML('<span class="badge badge-default" id="span_social_emotional">3.2</span>'),
                    Div('social_emotional', css_class='col-md-2'),
                    css_class='row',
                ),

                Div(
                    HTML('<span class="badge badge-default">4</span>'),
                    Div('attended_artistic', css_class='col-md-2'),
                    HTML('<span class="badge badge-default" id="span_modality_artistic">4.1</span>'),
                    Div('modality_artistic', css_class='col-md-2 multiple-checbkoxes'),
                    HTML('<span class="badge badge-default" id="span_artistic">4.2</span>'),
                    Div('artistic', css_class='col-md-2'),
                    css_class='row',
                ),
                css_class='bd-callout bd-callout-warning E_right_border'
            ),
            FormActions(
                Submit('save', _('Save'), css_class='col-md-2'),
                Submit('save_add_another', _('Save and add another'), css_class='col-md-2 child_data col-md-2'),
                HTML('<a class="btn btn-info cancel-button" href="/clm/abln-list/" translation="' + _('Are you sure you want to cancel this registration?') + '">' + _('Back to list') + '</a>'),
                css_class='button-group'
            )
        )

    def clean(self):
        cleaned_data = super(ABLNForm, self).clean()

        phone_number = cleaned_data.get("phone_number")
        phone_number_confirm = cleaned_data.get("phone_number_confirm")
        second_phone_number = cleaned_data.get("second_phone_number")
        second_phone_number_confirm = cleaned_data.get("second_phone_number_confirm")
        id_type = cleaned_data.get("id_type")
        case_number = cleaned_data.get("case_number")
        case_number_confirm = cleaned_data.get("case_number_confirm")
        individual_case_number = cleaned_data.get("individual_case_number")
        individual_case_number_confirm = cleaned_data.get("individual_case_number_confirm")
        recorded_number = cleaned_data.get("recorded_number")
        recorded_number_confirm = cleaned_data.get("recorded_number_confirm")
        national_number = cleaned_data.get("national_number")
        national_number_confirm = cleaned_data.get("national_number_confirm")
        syrian_national_number = cleaned_data.get("syrian_national_number")
        syrian_national_number_confirm = cleaned_data.get("syrian_national_number_confirm")
        sop_national_number = cleaned_data.get("sop_national_number")
        sop_national_number_confirm = cleaned_data.get("sop_national_number_confirm")
        parent_individual_case_number = cleaned_data.get("parent_individual_case_number")
        parent_individual_case_number_confirm = cleaned_data.get("parent_individual_case_number_confirm")
        parent_national_number = cleaned_data.get("parent_national_number")
        parent_national_number_confirm = cleaned_data.get("parent_national_number_confirm")
        sop_parent_national_number = cleaned_data.get("parent_sop_national_number")
        sop_parent_national_number_confirm = cleaned_data.get("parent_sop_national_number_confirm")
        parent_syrian_national_number = cleaned_data.get("parent_syrian_national_number")
        parent_syrian_national_number_confirm = cleaned_data.get("parent_syrian_national_number_confirm")
        parent_other_number = cleaned_data.get("parent_other_number")
        parent_other_number_confirm = cleaned_data.get("parent_other_number_confirm")
        other_number = cleaned_data.get("other_number")
        other_number_confirm = cleaned_data.get("other_number_confirm")
        education_status = cleaned_data.get("education_status")
        miss_school_date = cleaned_data.get("miss_school_date")
        student_nationality = cleaned_data.get("student_nationality")
        other_nationality = cleaned_data.get("other_nationality")
        main_caregiver = cleaned_data.get("main_caregiver")
        other_caregiver_relationship = cleaned_data.get("other_caregiver_relationship")
        main_caregiver_nationality = cleaned_data.get("main_caregiver_nationality")
        main_caregiver_nationality_other = cleaned_data.get("main_caregiver_nationality_other")
        have_labour_single_selection = cleaned_data.get("have_labour_single_selection")
        labours_single_selection = cleaned_data.get("labours_single_selection")
        labour_hours = cleaned_data.get("labour_hours")
        labour_weekly_income = cleaned_data.get("labour_weekly_income")
        student_family_status = cleaned_data.get("student_family_status")
        student_have_children = cleaned_data.get("student_have_children")
        student_number_children = cleaned_data.get("student_number_children")

        labours_other_specify = cleaned_data.get("labours_other_specify")
        attended_arabic = cleaned_data.get("attended_arabic")
        modality_arabic = cleaned_data.get("modality_arabic")
        arabic = cleaned_data.get("arabic")

        attended_english = cleaned_data.get("attended_english")
        modality_english = cleaned_data.get("modality_english")
        english = cleaned_data.get("english")

        attended_artistic = cleaned_data.get("attended_artistic")
        modality_artistic = cleaned_data.get("modality_artistic")
        artistic = cleaned_data.get("artistic")

        attended_math = cleaned_data.get("attended_math")
        modality_math = cleaned_data.get("modality_math")
        math = cleaned_data.get("math")

        attended_social = cleaned_data.get("attended_social")
        modality_social = cleaned_data.get("modality_social")
        social_emotional = cleaned_data.get("social_emotional")

        if attended_arabic == 'yes':
            if not modality_arabic:
                self.add_error('modality_arabic', 'This field is required')
            if arabic is None:
                self.add_error('arabic', 'This field is required')

        if attended_english == 'yes':
            if not modality_english:
                self.add_error('modality_english', 'This field is required')
            if english is None:
                self.add_error('english', 'This field is required')

        if attended_artistic == 'yes':
            if not modality_artistic:
                self.add_error('modality_artistic', 'This field is required')
            if artistic is None:
                self.add_error('artistic', 'This field is required')

        if attended_math == 'yes':
            if not modality_math:
                self.add_error('modality_math', 'This field is required')
            if math is None:
                self.add_error('math', 'This field is required')

        if attended_social == 'yes':
            if not modality_social:
                self.add_error('modality_social', 'This field is required')
            if social_emotional is None:
                self.add_error('social_emotional', 'This field is required')

        if labours_single_selection == 'other_many_other':
            if not labours_other_specify:
                self.add_error('labours_other_specify', 'This field is required')

        if education_status != 'out of school':
            if not miss_school_date:
                self.add_error('miss_school_date', 'This field is required')
        if student_nationality.id == 6:
            if not other_nationality:
                self.add_error('other_nationality', 'This field is required')
        if main_caregiver == 'other':
            if not other_caregiver_relationship:
                self.add_error('other_caregiver_relationship', 'This field is required')
        if main_caregiver_nationality.id == 6:
            if not main_caregiver_nationality_other:
                self.add_error('main_caregiver_nationality_other', 'This field is required')
        if student_family_status!='single' and student_have_children:
            if not student_number_children:
                self.add_error('student_number_children', 'This field is required')
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

        if id_type == 'UNHCR Registered':
            if not case_number:
                self.add_error('case_number', 'This field is required')

            if case_number != case_number_confirm:
                msg = "The case numbers are not matched"
                self.add_error('case_number_confirm', msg)

            if parent_individual_case_number != parent_individual_case_number_confirm:
                msg = "The individual case numbers are not matched"
                self.add_error('parent_individual_case_number_confirm', msg)

            if individual_case_number != individual_case_number_confirm:
                msg = "The individual case numbers are not matched"
                self.add_error('individual_case_number_confirm', msg)

        if id_type == 'UNHCR Recorded':
            if not recorded_number:
                self.add_error('recorded_number', 'This field is required')

            if recorded_number != recorded_number_confirm:
                msg = "The recorded numbers are not matched"
                self.add_error('recorded_number_confirm', msg)

        if id_type == 'Syrian national ID':

            if not parent_syrian_national_number:
                self.add_error('parent_syrian_national_number', 'This field is required')

            if not parent_syrian_national_number_confirm:
                self.add_error('parent_syrian_national_number_confirm', 'This field is required')

            if parent_syrian_national_number_confirm and not len(parent_syrian_national_number_confirm) == 11:
                msg = "Please enter a valid number (11 digits)"
                self.add_error('parent_syrian_national_number_confirm', msg)

            if parent_syrian_national_number and not len(parent_syrian_national_number) == 11:
                msg = "Please enter a valid number (11 digits)"
                self.add_error('parent_syrian_national_number', msg)

            if parent_syrian_national_number != parent_syrian_national_number_confirm:
                msg = "The national numbers are not matched"
                self.add_error('parent_syrian_national_number_confirm', msg)

            if syrian_national_number != syrian_national_number_confirm:
                msg = "The national numbers are not matched"
                self.add_error('syrian_national_number_confirm', msg)

        if id_type == 'Lebanese national ID':
            if not parent_national_number:
                self.add_error('parent_national_number', 'This field is required')

            if not parent_national_number_confirm:
                self.add_error('parent_national_number_confirm', 'This field is required')

            if parent_national_number and not len(parent_national_number) == 12:
                msg = "Please enter a valid number (12 digits)"
                self.add_error('parent_national_number', msg)

            if parent_national_number_confirm and not len(parent_national_number_confirm) == 12:
                msg = "Please enter a valid number (12 digits)"
                self.add_error('parent_national_number_confirm', msg)

            if parent_national_number != parent_national_number_confirm:
                msg = "The national numbers are not matched"
                self.add_error('parent_national_number_confirm', msg)

            if national_number != national_number_confirm:
                msg = "The national numbers are not matched"
                self.add_error('national_number_confirm', msg)

        if id_type == 'Palestinian national ID':
            if not sop_parent_national_number:
                self.add_error('parent_sop_national_number', 'This field is required')

            if not sop_parent_national_number_confirm:
                self.add_error('parent_sop_national_number_confirm', 'This field is required')

            if sop_parent_national_number != sop_parent_national_number_confirm:
                msg = "The national numbers are not matched"
                self.add_error('parent_sop_national_number_confirm', msg)

            if sop_national_number != sop_national_number_confirm:
                msg = "The national numbers are not matched"
                self.add_error('sop_national_number_confirm', msg)

        if id_type == 'Other nationality':
            if not parent_other_number:
                self.add_error('parent_other_number', 'This field is required')

            if not parent_other_number_confirm:
                self.add_error('parent_other_number_confirm', 'This field is required')

            if parent_other_number != parent_other_number_confirm:
                msg = "The ID numbers are not matched"
                self.add_error('parent_other_number_confirm', msg)

            if other_number != other_number_confirm:
                msg = "The ID numbers are not matched"
                self.add_error('other_number_confirm', msg)

        #grades Max Value validation
        registration_level = cleaned_data.get("registration_level")
        arabic = cleaned_data.get("arabic")
        # english = cleaned_data.get("english")
        math = cleaned_data.get("math")
        social_emotional = cleaned_data.get("social_emotional")
        artistic = cleaned_data.get("artistic")

        if registration_level == 'level_one':
            if arabic > 40:
                self.add_error('arabic', 'This value is greater that 40')
            # if english > '36':
            #     self.add_error('english', 'This value is greater that 36')
            if math > 20:
                self.add_error('math', 'This value is greater that 20')
            if social_emotional > 24:
                self.add_error('social_emotional', 'This value is greater that 24')
            if artistic > 8:
                self.add_error('artistic', 'This value is greater that 8')
        else:
            if arabic > 52:
                self.add_error('arabic', 'This value is greater that 52')
            # if english > 56:
            #     self.add_error('english', 'This value is greater that 56')
            if math > 34:
                self.add_error('math', 'This value is greater that 34')
            if social_emotional > 24:
                self.add_error('social_emotional', 'This value is greater that 24')
            if artistic > 8:
                self.add_error('artistic', 'This value is greater that 8')

    def save(self, request=None, instance=None, serializer=None):
        instance = super(ABLNForm, self).save(request=request, instance=instance, serializer=ABLNSerializer)
        instance.pre_test = {
            "ABLN_ASSESSMENT/attended_arabic": request.POST.get('attended_arabic'),
            "ABLN_ASSESSMENT/modality_arabic": request.POST.getlist('modality_arabic'),
            "ABLN_ASSESSMENT/arabic": request.POST.get('arabic'),

            # "ABLN_ASSESSMENT/attended_english": request.POST.get('attended_english'),
            # "ABLN_ASSESSMENT/modality_english": request.POST.getlist('modality_english'),
            # "ABLN_ASSESSMENT/english": request.POST.get('english'),

            "ABLN_ASSESSMENT/attended_artistic": request.POST.get('attended_artistic'),
            "ABLN_ASSESSMENT/modality_artistic": request.POST.getlist('modality_artistic'),
            "ABLN_ASSESSMENT/artistic": request.POST.get('artistic'),

            "ABLN_ASSESSMENT/attended_math": request.POST.get('attended_math'),
            "ABLN_ASSESSMENT/modality_math": request.POST.getlist('modality_math'),
            "ABLN_ASSESSMENT/math": request.POST.get('math'),

            "ABLN_ASSESSMENT/attended_social": request.POST.get('attended_social'),
            "ABLN_ASSESSMENT/modality_social": request.POST.getlist('modality_social'),
            "ABLN_ASSESSMENT/social_emotional": request.POST.get('social_emotional'),
        }

        instance.save()

    class Meta:
        model = ABLN
        fields = CommonForm.Meta.fields + (
            'first_attendance_date',
            'student_birthday_year',
            'have_labour_single_selection',
            'labours_single_selection',
            'labours_other_specify',
            'labour_hours',
            'phone_number',
            'phone_number_confirm',
            'phone_owner',
            'second_phone_owner',
            'second_phone_number',
            'second_phone_number_confirm',
            'id_type',
            'case_number',
            'case_number_confirm',
            'individual_case_number',
            'individual_case_number_confirm',
            'parent_individual_case_number',
            'parent_individual_case_number_confirm',
            'recorded_number',
            'recorded_number_confirm',
            'national_number',
            'national_number_confirm',
            'syrian_national_number',
            'syrian_national_number_confirm',
            'sop_national_number',
            'sop_national_number_confirm',
            'parent_national_number',
            'parent_national_number_confirm',
            'parent_syrian_national_number',
            'parent_syrian_national_number_confirm',
            'parent_sop_national_number',
            'parent_sop_national_number_confirm',
            'parent_other_number',
            'parent_other_number_confirm',
            'other_number',
            'other_number_confirm',
            'no_child_id_confirmation',
            'source_of_identification',
            'other_nationality',
            'education_status',
            'caretaker_first_name',
            'caretaker_middle_name',
            'caretaker_last_name',
            'caretaker_mother_name',
            'miss_school_date',
            'student_have_children',
            'student_family_status',
            'student_number_children',
            'round_start_date',
            'cadaster',
            'registration_level',
            'main_caregiver',
            'main_caregiver_nationality',
            'other_caregiver_relationship',
            'labour_weekly_income',
            'source_of_transportation',
            'student_p_code'
        )

    class Media:
        js = (
            # 'js/jquery-3.3.1.min.js',
            # 'js/jquery-ui-1.12.1.js',
            # 'js/validator.js',
            # 'js/registrations.js',
        )

class RSForm(CommonForm):

    YEARS_CB = list(((str(x), x) for x in range(Person.CURRENT_YEAR - 21, Person.CURRENT_YEAR - 5)))
    YEARS_CB.insert(0, ('', '---------'))

    cycle = forms.ModelChoiceField(
        queryset=Cycle.objects.all(), widget=forms.Select,
        label=_('In which cycle is this child registered?'),
        required=False, to_field_name='id',
        initial=0
    )
    # site = forms.ChoiceField(
    #     widget=forms.Select, required=True,
    #     label=_('Where is the program?'),
    #     choices=(
    #         ('', '--------'),
    #         ('in_school', _('Inside the school')),
    #         ('out_school', _('Outside the school')),
    #     )
    # )
    school = forms.ModelChoiceField(
        queryset=School.objects.all(), widget=forms.Select,
        label=_('The school where the child is attending the program'),
        empty_label='-------',
        required=False, to_field_name='id',
        initial=0
    )

    referral = forms.MultipleChoiceField(
        label=_('Where was the child referred?'),
        choices=CLM.REFERRAL,
        widget=forms.CheckboxSelectMultiple,
        required=False,
    )
    child_muac = forms.ChoiceField(
        label=_("What is the measurement of the child's arm circumference? (Centimeter)"),
        widget=forms.Select, required=False,
        choices=(
            ('', '-------'),
            ('1', _('< 11.5 CM (severe malnutrition)')),
            ('2', _('< 12.5 CM (moderate malnutrition)')),
        )
    )
    final_grade = forms.FloatField(
        label=_('Final grade') + ' (/80)', required=False,
        widget=forms.NumberInput,
        min_value=0, max_value=80
    )
    # learning_result = forms.ChoiceField(
    #     label=_('Based on the overall score, what is the recommended learning path?'),
    #     widget=forms.Select, required=False,
    #     choices=(
    #         ('', '----------'),
    #         ('repeat_level', _('Repeat level')),
    #         ('graduated_next_level', _('Referred to the next level')),
    #         ('graduated_to_formal_education_level1', _('Referred to formal education - Level 1')),
    #         ('referred_to_another_program', _('Referred to another program')),
    #     ),
    #     initial=''
    # )

    student_birthday_year = forms.ChoiceField(
        label=_("Birthday year"),
        widget=forms.Select, required=True,
        choices=YEARS_CB
    )

    first_attendance_date = forms.DateField(
        label=_("First attendance date"),
        required=True
    )
    miss_school = forms.ChoiceField(
        label=_("Miss school?"),
        widget=forms.Select, required=True,
        choices=(('yes', _("Yes")), ('no', _("No"))),
        initial='no'
    )
    miss_school_date = forms.DateField(
        label=_("Miss school date"),
        required=False,
    )
    new_registry = forms.ChoiceField(
        label=_("First time registered?"),
        widget=forms.Select, required=True,
        choices=(('yes', _("Yes")), ('no', _("No"))),
        initial='yes'
    )

    round = forms.ModelChoiceField(
        queryset=CLMRound.objects.filter(current_round_rs=True), widget=forms.Select,
        label=_('Round'),
        empty_label='-------',
        required=True, to_field_name='id',
    )
    # round = forms.ModelChoiceField(
    #     queryset=CLMRound.objects.all(), widget=forms.Select,
    #     label=_('Round'),
    #     empty_label='-------',
    #     required=True, to_field_name='id',
    # )

    round_start_date = forms.DateField(
        label=_("Round start date"),
        required=False
    )
    student_family_status = forms.ChoiceField(
        label=_('What is the family status of the child?'),
        widget=forms.Select, required=True,
        choices=Student.FAMILY_STATUS,
        initial='single'
    )
    student_have_children = forms.TypedChoiceField(
        label=_("Does the child have children?"),
        choices=YES_NO_CHOICE,
        coerce=lambda x: bool(int(x)),
        widget=forms.RadioSelect,
        required=True,
    )
    student_number_children = forms.IntegerField(
        label=_('How many children does this child have?'),
        widget=forms.TextInput, required=False
    )
    have_labour_single_selection = forms.ChoiceField(
        label=_('Does the child participate in work?'),
        widget=forms.Select, required=True,
        choices=CLM.HAVE_LABOUR,
        initial='no'
    )
    labours_single_selection = forms.ChoiceField(
        label=_('What is the type of work ?'),
        widget=forms.Select, required=False,
        choices=CLM.LABOURS
    )
    labours_other_specify = forms.CharField(
        label=_('Please specify(hotel, restaurant, transport, personal services such as cleaning, hair care, cooking and childcare)'),
        widget=forms.TextInput, required=False
    )
    labour_hours = forms.CharField(
        label=_('How many hours does this child work in a day?'),
        widget=forms.TextInput, required=False
    )
    labour_weekly_income = forms.ChoiceField(
        label=_('What is the income of the child per week?'),
        widget=forms.Select,
        choices=Student.STUDENT_INCOME,
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
    id_type = forms.ChoiceField(
        label=_("ID type of the caretaker"),
        widget=forms.Select(attrs=({'translation': _('Child no ID confirmation popup message')})),
        required=False,
        choices=(
            ('', '----------'),
            ('UNHCR Registered', _('UNHCR Registered')),
            ('UNHCR Recorded', _("UNHCR Recorded")),
            ('Syrian national ID', _("Syrian national ID")),
            ('Palestinian national ID', _("Palestinian national ID")),
            ('Lebanese national ID', _("Lebanese national ID")),
            ('Other nationality', _("Other nationality")),
            ('Child have no ID', _("Child have no ID"))
        ),
        initial=''
    )
    case_number = forms.RegexField(
        regex=r'^((245)|(380)|(568)|(705)|(781)|(909)|(947)|(954)|(LEB)|(leb))-[0-9][0-9][C]\d{5}$',
        widget=forms.TextInput(attrs={'placeholder': 'Format: XXX-XXCXXXXX'}),
        required=False,
        label=_('UNHCR Case Number')
    )
    case_number_confirm = forms.RegexField(
        regex=r'^((245)|(380)|(568)|(705)|(781)|(909)|(947)|(954)|(LEB)|(leb))-[0-9][0-9][C]\d{5}$',
        widget=forms.TextInput(attrs={'placeholder': 'Format: XXX-XXCXXXXX'}),
        required=False,
        label=_('Confirm UNHCR Case Number')
    )
    parent_individual_case_number = forms.RegexField(
        regex=r'^((245)|(380)|(568)|(705)|(781)|(909)|(947)|(954)|(LEB)|(leb))-[0-9]{8}$',
        widget=forms.TextInput(attrs={'placeholder': 'Format: XXX-XXXXXXXX'}),
        required=False,
        label=_(
            'Caretaker Individual ID from the certificate (Optional, in case not listed in the certificate)')
    )
    parent_individual_case_number_confirm = forms.RegexField(
        regex=r'^((245)|(380)|(568)|(705)|(781)|(909)|(947)|(954)|(LEB)|(leb))-[0-9]{8}$',
        widget=forms.TextInput(attrs={'placeholder': 'Format: XXX-XXXXXXXX'}),
        required=False,
        label=_(
            'Confirm Caretaker Individual ID from the certificate (Optional, in case not listed in the certificate)')
    )
    individual_case_number = forms.RegexField(
        regex=r'^((245)|(380)|(568)|(705)|(781)|(909)|(947)|(954)|(LEB)|(leb))-[0-9]{8}$',
        widget=forms.TextInput(attrs={'placeholder': 'Format: XXX-XXXXXXXX'}),
        required=False,
        label=_(
            'Individual ID of the Child from the certificate (Optional, in case not listed in the certificate)')
    )
    individual_case_number_confirm = forms.RegexField(
        regex=r'^((245)|(380)|(568)|(705)|(781)|(909)|(947)|(954)|(LEB)|(leb))-[0-9]{8}$',
        widget=forms.TextInput(attrs={'placeholder': 'Format: XXX-XXXXXXXX'}),
        required=False,
        label=_(
            'Confirm Individual ID of the Child from the certificate (Optional, in case not listed in the certificate)')
    )
    recorded_number = forms.RegexField(
        regex=r'^((245)|(380)|(568)|(705)|(781)|(909)|(947)|(954)|(LEB)|(leb))-[0-9][0-9][C]\d{5}$',
        widget=forms.TextInput(attrs={'placeholder': 'Format: LEB-XXCXXXXX'}),
        required=False,
        label=_('UNHCR Barcode number (Shifra number)')
    )
    recorded_number_confirm = forms.RegexField(
        regex=r'^((245)|(380)|(568)|(705)|(781)|(909)|(947)|(954)|(LEB)|(leb))-[0-9][0-9][C]\d{5}$',
        widget=forms.TextInput(attrs={'placeholder': 'Format: LEB-XXCXXXXX'}),
        required=False,
        label=_('Confirm UNHCR Barcode number (Shifra number)')
    )

    national_number = forms.RegexField(
        regex=r'^\d{12}$',
        widget=forms.TextInput(attrs={'placeholder': 'Format: XXXXXXXXXXXX'}),
        required=False,
        label=_('Lebanese ID number of the child (Optional)')
    )
    national_number_confirm = forms.RegexField(
        regex=r'^\d{12}$',
        widget=forms.TextInput(attrs={'placeholder': 'Format: XXXXXXXXXXXX'}),
        required=False,
        label=_('Confirm Lebanese ID number of the child (optional)')
    )
    syrian_national_number = forms.RegexField(
        regex=r'^\d{11}$',
        required=False,
        label=_('National ID number of the child (Optional)')
    )
    syrian_national_number_confirm = forms.RegexField(
        regex=r'^\d{11}$',
        required=False,
        label=_('Confirm National ID number of the child (Optional)')
    )
    sop_national_number = forms.CharField(
        required=False,
        label=_('Palestinian ID number of the child (Optional)')
    )
    sop_national_number_confirm = forms.CharField(
        required=False,
        label=_('Confirm Palestinian ID number of the child (optional)')
    )
    parent_national_number = forms.RegexField(
        regex=r'^\d{12}$',
        widget=forms.TextInput(attrs={'placeholder': 'Format: XXXXXXXXXXXX'}),
        required=False,
        label=_('Lebanese ID number of the caretaker (Mandatory)')
    )
    parent_national_number_confirm = forms.RegexField(
        regex=r'^\d{12}$',
        widget=forms.TextInput(attrs={'placeholder': 'Format: XXXXXXXXXXXX'}),
        required=False,
        label=_('Confirm Lebanese ID number of the caretaker (Mandatory)')
    )
    parent_syrian_national_number = forms.RegexField(
        regex=r'^\d{11}$',
        required=False,
        label=_('National ID number of the Caretaker (Mandatory)')
    )
    parent_syrian_national_number_confirm = forms.RegexField(
        regex=r'^\d{11}$',
        required=False,
        label=_('Confirm National ID number of the Caretaker (Mandatory)')
    )
    parent_sop_national_number = forms.CharField(
        # regex=r'^\d{11}$',
        required=False,
        label=_('Palestinian ID number of the Caretaker (Mandatory)')
    )
    parent_sop_national_number_confirm = forms.CharField(
        # regex=r'^\d{11}$',
        required=False,
        label=_('Confirm Palestinian ID number of the Caretaker (Mandatory)')
    )

    parent_other_number = forms.CharField(
        required=False,
        label=_('ID number of the Caretaker (Mandatory)')
    )
    parent_other_number_confirm = forms.CharField(
        required=False,
        label=_('Confirm ID number of the Caretaker (Mandatory)')
    )
    other_number = forms.CharField(
        required=False,
        label=_(' ID number of the child (Optional)')
    )
    other_number_confirm = forms.CharField(
        required=False,
        label=_('Confirm ID number of the child (optional)')
    )

    no_child_id_confirmation = forms.CharField(widget=forms.HiddenInput, required=False)
    no_parent_id_confirmation = forms.CharField(widget=forms.HiddenInput, required=False)

    source_of_identification = forms.ChoiceField(
        label=_("Source of identification of the child to RS"),
        widget=forms.Select,
        required=True,
        choices=(
            ('', '----------'),
            ('Referral from school directors', _('Referral from school directors')),
            ('From Profiling Database (MEHE)', _('From Profiling Database (MEHE)')),
            ('Other Sources', _('Other Sources'))
        ),
        initial=''
    )

    source_of_identification_specify = forms.CharField(
        label=_('Please specify'),
        widget=forms.TextInput, required=False
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
    attended_english = forms.ChoiceField(
        label=_("Attended English test"),
        widget=forms.Select, required=True,
        choices=(('yes', _("Yes")), ('no', _("No"))),
        initial='yes'
    )
    modality_english = forms.MultipleChoiceField(
        label=_('Please indicate modality'),
        choices=CLM.MODALITY,
        widget=forms.CheckboxSelectMultiple,
        required=False
    )
    english = forms.FloatField(
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
    attended_biology = forms.ChoiceField(
        label=_("Attended biology test"),
        widget=forms.Select, required=True,
        choices=(('yes', _("Yes")), ('no', _("No"))),
        initial='yes'
    )
    modality_biology = forms.MultipleChoiceField(
        label=_('Please indicate modality'),
        choices=CLM.MODALITY,
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    biology = forms.FloatField(
        label=_('Results'),
        widget=forms.NumberInput(attrs=({'maxlength': 4})),
        min_value=0, required=False
    )
    attended_science = forms.ChoiceField(
        label=_("Attended RS Science test"),
        widget=forms.Select, required=True,
        choices=(('yes', _("Yes")), ('no', _("No"))),
        initial='yes'
    )
    modality_science = forms.MultipleChoiceField(
        label=_('Please indicate modality'),
        choices=CLM.MODALITY,
        widget=forms.CheckboxSelectMultiple,
        required=False
    )
    science = forms.FloatField(
        label=_('Results'),
        widget=forms.NumberInput(attrs=({'maxlength': 4})),
        min_value=0, required=False
    )
    attended_chemistry = forms.ChoiceField(
        label=_("Attended chemistry test"),
        widget=forms.Select, required=True,
        choices=(('yes', _("Yes")), ('no', _("No"))),
        initial='yes'
    )
    modality_chemistry  = forms.MultipleChoiceField(
        label=_('Please indicate modality'),
        choices=CLM.MODALITY,
        widget=forms.CheckboxSelectMultiple,
        required=False
    )
    chemistry = forms.FloatField(
        label=_('Results'),
        widget=forms.NumberInput(attrs=({'maxlength': 4})),
        min_value=0, required=False
    )

    attended_physics = forms.ChoiceField(
        label=_("Attended physics test"),
        widget=forms.Select, required=True,
        choices=(('yes', _("Yes")), ('no', _("No"))),
        initial='yes'
    )
    modality_physics  = forms.MultipleChoiceField(
        label=_('Please indicate modality'),
        choices=CLM.MODALITY,
        widget=forms.CheckboxSelectMultiple,
        required=False
    )
    physics = forms.FloatField(
        label=_('Results'),
        widget=forms.NumberInput(attrs=({'maxlength': 4})),
        min_value=0, required=False
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
    main_caregiver_nationality = forms.ModelChoiceField(
        label=_("Nationality"),
        queryset=Nationality.objects.exclude(id=9), widget=forms.Select,
        required=False, to_field_name='id',
    )

    student_p_code = forms.CharField(
        label=_('P-Code If a child lives in a tent / Brax in a random camp'),
        widget=forms.TextInput, required=False
    )

    student_number_children = forms.IntegerField(
        label=_('How many children does this child have?'),
        widget=forms.TextInput, required=False
    )
    grade_level = forms.ChoiceField(
        label=_("What was the child education level when first joining formal education in lebanon"),
        widget=forms.Select, required=True,
        choices=RS.GRADE_LEVEL
    )

    source_join_fe = forms.ChoiceField(
        label=_("From where did the child first come to join  FE"),
        widget=forms.Select, required=True,
        choices=RS.SOURCE_JOIN_FE
    )
    registered_in_school = forms.CharField(
        label=_('School of Enrollment'),
        widget=forms.TextInput, required=True
    )
    shift = forms.ChoiceField(
        label=_("Shift"),
        widget=forms.Select, required=True,
        choices=RS.SCHOOL_SHIFTS
    )
    grade_registration =  forms.ChoiceField(
        label=_("Grade of registeration"),
        widget=forms.Select, required=True,
        choices=(
            ('', '----------'),
            ('6', _('6')),
            ('7', _('7')),
            ('8', _('8')),
            ('9', _('9')),
        )
    )


    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(RSForm, self).__init__(*args, **kwargs)

        display_registry = ''
        instance = kwargs['instance'] if 'instance' in kwargs else ''
        form_action = reverse('clm:rs_add')
        self.fields['clm_type'].initial = 'RS'
        self.fields['new_registry'].initial = 'yes'
        if instance:
            display_registry = ' d-none'
            form_action = reverse('clm:rs_edit', kwargs={'pk': instance.id})
            if instance.cycle_id == 3:
                display_final_grade = ''

        self.helper = FormHelper()
        self.helper.form_show_labels = True
        self.helper.form_action = form_action
        self.helper.layout = Layout(
            Fieldset(
                None,
                Div(
                    HTML('<span>A.1</span>'), css_class='block_tag'),
                Div(
                    HTML('<h4 id="alternatives-to-hidden-labels">' + _(
                        'Search CLM student') + '</h4>')
                ),
                Div(
                    'clm_type',
                    'student_id',
                    'enrollment_id',
                    css_class='row',
                ),
                Div(
                    HTML('<span class="badge badge-default"></span>'),
                    Div('search_clm_student', css_class='col-md-3'),
                    css_class='row',
                ),
                Div(
                    HTML('<p>' + _(
                        'Search by the following keywords: child first name, father name, last name, '
                        'child number or partner internal number') + '</p>'),
                ),
                css_id='search_options',
                css_class='bd-callout bd-callout-warning child_data E_right_border' + display_registry
            ),
            Fieldset(
                None,
                Div(
                    HTML('<span>A</span>'), css_class='block_tag'),
                Div(
                    HTML('<h4 id="alternatives-to-hidden-labels">' + _('General Information') + '</h4>')
                ),
                Div(

                    HTML('<span class="badge badge-default">1</span>'),
                    Div('new_registry', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">2</span>'),
                    Div('round', css_class='col-md-3'),
                    # HTML('<span class="badge badge-default">3</span>'),
                    Div('round_start_date', css_class='col-md-3 d-none'),
                    css_class='row',
                ),
                Div(
                    HTML('<span class="badge badge-default">3</span>'),
                    Div('governorate', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">4</span>'),
                    Div('district', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">5</span>'),
                    Div('cadaster', css_class='col-md-3'),
                    css_class='row',
                ),
                Div(
                    HTML('<span class="badge badge-default">6</span>'),
                    Div('location', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">7</span>'),
                    Div('language', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">8</span>'),
                    Div('grade_registration', css_class='col-md-3'),
                    css_class='row',
                ),
                Div(
                    HTML('<span class="badge badge-default">9</span>'),
                    Div('student_address', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">10</span>'),
                    Div('first_attendance_date', css_class='col-md-3'),
                    css_class='row',
                ),

                Div(
                    HTML('<span class="badge badge-default">11</span>'),
                    Div('registered_in_school', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">12</span>'),
                    Div('shift', css_class='col-md-3'),
                    css_class='row',
                ),

                #
                css_class='bd-callout bd-callout-warning child_data A_right_border'
            ),
            Fieldset(
                None,
                Div(HTML('<span>B</span>'), css_class='block_tag'),
                Div(
                    HTML('<h4 id="alternatives-to-hidden-labels">' + _('Child Information') + '</h4>')
                ),
                Div(
                    HTML('<span class="badge badge-default">1</span>'),
                    Div('student_first_name', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">2</span>'),
                    Div('student_father_name', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">3</span>'),
                    Div('student_last_name', css_class='col-md-3'),
                    css_class='row',
                ),
                Div(
                    HTML('<span class="badge badge-default">4</span>'),
                    Div('student_mother_fullname', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">5</span>'),
                    Div('student_sex', css_class='col-md-3'),
                    css_class='row',
                ),
                Div(
                    HTML('<span class="badge badge-default">6</span>'),
                    Div('student_nationality', css_class='col-md-3'),
                    HTML('<span class="badge badge-default" id="span_other_nationality">6.1</span>'),
                    Div('other_nationality', css_class='col-md-3'),
                    css_class='row',
                ),
                Div(
                    HTML('<span class="badge badge-default">7</span>'),
                    Div('student_birthday_year', css_class='col-md-2'),
                    HTML('<span class="badge badge-default">8</span>'),
                    Div('student_birthday_month', css_class='col-md-2'),
                    HTML('<span class="badge badge-default">9</span>'),
                    Div('student_birthday_day', css_class='col-md-2'),
                    css_class='row',
                ),
                Div(
                    HTML('<span class="badge badge-default">10</span>'),
                    Div('student_p_code', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">11</span>'),
                    Div('disability', css_class='col-md-3'),
                    css_class='row',
                ),
                Div(
                    HTML('<span class="badge badge-default">12</span>'),
                    Div('grade_level', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">13</span>'),
                    Div('source_join_fe', css_class='col-md-3'),
                    css_class='row',
                ),
                Div(
                    HTML('<span class="badge badge-default">14</span>'),
                    Div('internal_number', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">15</span>'),
                    Div('miss_school', css_class='col-md-3'),
                    HTML('<span class="badge badge-default" id="span_miss_school_date">15.1</span>'),
                    Div('miss_school_date', css_class='col-md-3'),
                    css_class='row',
                ),
                Div(
                    HTML('<span class="badge badge-default">16</span>'),
                    Div('source_of_identification', css_class='col-md-3'),
                    HTML('<span class="badge badge-default" id="span_source_of_identification_specify">16.1</span>'),
                    Div('source_of_identification_specify', css_class='col-md-3'),
                    css_class='row',
                ),
                # Div(
                #     HTML('<span class="badge badge-default">17</span>'),
                #     Div('source_of_transportation', css_class='col-md-3'),
                #     css_class='row d-none',
                # ),
                css_class='bd-callout bd-callout-warning child_data B_right_border'
            ),
            Fieldset(
                None,
                Div(HTML('<span>C</span>'), css_class='block_tag'),
                Div(
                    HTML('<h4 id="alternatives-to-hidden-labels">' + _('Parent/Caregiver Information') + '</h4>')
                ),
                Div(
                    HTML('<span class="badge badge-default">1</span>'),
                    Div('hh_educational_level', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">2</span>'),
                    Div('father_educational_level', css_class='col-md-3'),
                    css_class='row',
                ),
                Div(
                    HTML('<span class="badge badge-default">3</span>'),
                    Div('phone_number', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">3.1</span>'),
                    Div('phone_number_confirm', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">3.2</span>'),
                    Div('phone_owner', css_class='col-md-3'),
                    css_class='row',
                ),
                Div(
                    HTML('<span class="badge badge-default">4</span>'),
                    Div('second_phone_number', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">4.1</span>'),
                    Div('second_phone_number_confirm', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">4.2</span>'),
                    Div('second_phone_owner', css_class='col-md-3'),
                    css_class='row',
                ),
                Div(
                    HTML('<span class="badge badge-default">5</span>'),
                    Div('main_caregiver', css_class='col-md-3'),
                    # HTML('<span class="badge badge-default">5.1</span>'),
                    # Div('main_caregiver_nationality', css_class='col-md-3'),
                    HTML('<span class="badge badge-default" id="span_other_caregiver_relationship">5.1</span>'),
                    Div('other_caregiver_relationship', css_class='col-md-3'),
                    css_class='row',
                ),
                # Div(
                #     HTML('<span class="badge badge-default">6</span>'),
                #     Div('caretaker_first_name', css_class='col-md-3'),
                #     HTML('<span class="badge badge-default">7</span>'),
                #     Div('caretaker_middle_name', css_class='col-md-3'),
                #     css_class='row',
                # ),
                # Div(
                #     HTML('<span class="badge badge-default">8</span>'),
                #     Div('caretaker_last_name', css_class='col-md-3'),
                #     HTML('<span class="badge badge-default">9</span>'),
                #     Div('caretaker_mother_name', css_class='col-md-3'),
                #     css_class='row',
                # ),
                # Div(
                #     HTML('<span class="badge badge-default">10</span>'),
                #     Div('id_type', css_class='col-md-3'),
                #     css_class='row',
                # ),
                Div(
                    HTML('<span class="badge badge-default">11</span>'),
                    Div('case_number', css_class='col-md-4'),
                    HTML('<span class="badge badge-default">12</span>'),
                    Div('case_number_confirm', css_class='col-md-4'),
                    HTML('<span style="padding-top: 37px;">' +
                         '<a class="image-link" href="/static/images/unhcr_certificate.jpg" target="_blank">' +
                         '<img src="/static/images/icon-help.png" width="25px" height="25px;"/></a></span>'),
                    css_class='row child_id child_id1',
                ),
                Div(
                    HTML('<span class="badge badge-default">13</span>'),
                    Div('parent_individual_case_number', css_class='col-md-4'),
                    HTML('<span class="badge badge-default">14</span>'),
                    Div('parent_individual_case_number_confirm', css_class='col-md-4'),
                    HTML('<span style="padding-top: 37px;">' +
                         '<a class="image-link" href="/static/images/UNHCR_individualID.jpg" target="_blank">' +
                         '<img src="/static/images/icon-help.png" width="25px" height="25px;"/></a></span>'),
                    css_class='row child_id child_id1',
                ),
                Div(
                    HTML('<span class="badge badge-default">15</span>'),
                    Div('individual_case_number', css_class='col-md-4'),
                    HTML('<span class="badge badge-default">16</span>'),
                    Div('individual_case_number_confirm', css_class='col-md-4'),
                    HTML('<span style="padding-top: 37px;">' +
                         '<a class="image-link" href="/static/images/UNHCR_individualID.jpg" target="_blank">' +
                         '<img src="/static/images/icon-help.png" width="25px" height="25px;"/></a></span>'),
                    css_class='row child_id child_id1',
                ),
                Div(
                    HTML('<span class="badge badge-default">17</span>'),
                    Div('recorded_number', css_class='col-md-4'),
                    HTML('<span class="badge badge-default">18</span>'),
                    Div('recorded_number_confirm', css_class='col-md-4'),
                    HTML('<span style="padding-top: 37px;">' +
                         '<a class="image-link" href="/static/images/UNHCR_barcode.jpg" target="_blank">' +
                         '<img src="/static/images/icon-help.png" width="25px" height="25px;"/></a></span>'),
                    css_class='row child_id child_id2',
                ),
                Div(
                    HTML('<span class="badge badge-default">19</span>'),
                    Div('parent_national_number', css_class='col-md-4'),
                    HTML('<span class="badge badge-default">20</span>'),
                    Div('parent_national_number_confirm', css_class='col-md-4'),
                    HTML('<span style="padding-top: 37px;">' +
                         '<a class="image-link" href="/static/images/lebanese_nationalID.png" target="_blank">' +
                         '<img src="/static/images/icon-help.png" width="25px" height="25px;"/></a></span>'),
                    css_class='row child_id child_id3',
                ),
                Div(
                    HTML('<span class="badge badge-default">21</span>'),
                    Div('national_number', css_class='col-md-4'),
                    HTML('<span class="badge badge-default">22</span>'),
                    Div('national_number_confirm', css_class='col-md-4'),
                    HTML('<span style="padding-top: 37px;">' +
                         '<a class="image-link" href="/static/images/lebanese_nationalID.png" target="_blank">' +
                         '<img src="/static/images/icon-help.png" width="25px" height="25px;"/></a></span>'),
                    css_class='row child_id child_id3',
                ),
                Div(
                    HTML('<span class="badge badge-default">23</span>'),
                    Div('parent_syrian_national_number', css_class='col-md-4'),
                    HTML('<span class="badge badge-default">24</span>'),
                    Div('parent_syrian_national_number_confirm', css_class='col-md-4'),
                    HTML('<span style="padding-top: 37px;">' +
                         '<a class="image-link" href="/static/images/Syrian_passport.png" target="_blank">' +
                         '<img src="/static/images/icon-help.png" width="25px" height="25px;"/></a></span>'),
                    css_class='row child_id child_id4',
                ),
                Div(
                    HTML('<span class="badge badge-default">25</span>'),
                    Div('syrian_national_number', css_class='col-md-4'),
                    HTML('<span class="badge badge-default">26</span>'),
                    Div('syrian_national_number_confirm', css_class='col-md-4'),
                    HTML('<span style="padding-top: 37px;">' +
                         '<a class="image-link" href="/static/images/Syrian_passport.png" target="_blank">' +
                         '<img src="/static/images/icon-help.png" width="25px" height="25px;"/></a></span>'),
                    css_class='row child_id child_id4',
                ),
                Div(
                    HTML('<span class="badge badge-default">27</span>'),
                    Div('parent_sop_national_number', css_class='col-md-4'),
                    HTML('<span class="badge badge-default">28</span>'),
                    Div('parent_sop_national_number_confirm', css_class='col-md-4'),
                    HTML('<span style="padding-top: 37px;">' +
                         '<a class="image-link" href="/static/images/Palestinian_from_Lebanon.png" target="_blank">' +
                         '<img src="/static/images/icon-help.png" width="25px" height="25px;"/></a></span>'),
                    css_class='row child_id child_id5',
                ),
                Div(
                    HTML('<span class="badge badge-default">29</span>'),
                    Div('sop_national_number', css_class='col-md-4'),
                    HTML('<span class="badge badge-default">30</span>'),
                    Div('sop_national_number_confirm', css_class='col-md-4'),
                    HTML('<span style="padding-top: 37px;">' +
                         '<a class="image-link" href="/static/images/Palestinian_from_Lebanon.png" target="_blank">' +
                         '<img src="/static/images/icon-help.png" width="25px" height="25px;"/></a></span>'),
                    css_class='row child_id child_id5',
                ),
                Div(
                    HTML('<span class="badge badge-default">31</span>'),
                    Div('parent_other_number', css_class='col-md-4'),
                    HTML('<span class="badge badge-default">32</span>'),
                    Div('parent_other_number_confirm', css_class='col-md-4'),
                    css_class='row child_id child_id6',
                ),
                Div(
                    HTML('<span class="badge badge-default">33</span>'),
                    Div('other_number', css_class='col-md-4'),
                    HTML('<span class="badge badge-default">34</span>'),
                    Div('other_number_confirm', css_class='col-md-4'),
                    css_class='row child_id child_id6',
                ),
                css_class='bd-callout bd-callout-warning child_data C_right_border'
            ),

            Fieldset(
                None,
                Div(HTML('<span>D</span>'), css_class='block_tag'),
                Div(
                    HTML('<h4 id="alternatives-to-hidden-labels">' + _('Family Status') + '</h4>')
                ),
                Div(
                    HTML('<span class="badge badge-default">1</span>'),
                    Div('student_family_status', css_class='col-md-4'),
                    HTML('<span class="badge badge-default" id=span_student_have_children">1.1</span>'),
                    Div('student_have_children', css_class='col-md-4', css_id='student_have_children'),
                    HTML('<span class="badge badge-default" id="span_student_number_children">1.2</span>'),
                    Div('student_number_children', css_class='col-md-3'),
                    css_class='row',
                ),
                Div(
                    HTML('<span class="badge badge-default">2</span>'),
                    Div('have_labour_single_selection', css_class='col-md-3'),
                    css_class='row',
                ),
                Div(
                    HTML('<span class="badge badge-default">2.1</span>'),
                    Div('labours_single_selection', css_class='col-md-3', css_id='labours'),
                    HTML('<span class="badge badge-default" id="span_labours_other_specify">2.1.1</span>'),
                    Div('labours_other_specify', css_class='col-md-3'),
                    css_class='row',
                    id='labour_details_1'
                ),
                Div(
                    HTML('<span class="badge badge-default">2.2</span>'),
                    Div('labour_hours', css_class='col-md-3', css_id='labour_hours'),
                    HTML('<span class="badge badge-default">2.3</span>'),
                    Div('labour_weekly_income', css_class='col-md-3'),
                    css_class='row',
                    id='labour_details_2'
                ),
                css_class='bd-callout bd-callout-warning child_data D_right_border'
            ),

            Fieldset(
                None,
                Div(
                    HTML('<span>E</span>'), css_class='block_tag'),
                Div(
                    HTML('<h4 id="alternatives-to-hidden-labels">' + _('Assessment data') + '</h4>')
                ),
                Div(
                    HTML('<span class="badge badge-default">1</span>'),
                    Div('attended_arabic', css_class='col-md-2'),
                    HTML('<span class="badge badge-default" id="span_modality_arabic">1.1</span>'),
                    Div('modality_arabic', css_class='col-md-2 multiple-checbkoxes'),
                    HTML('<span class="badge badge-default" id="span_arabic">1.2</span>'),
                    Div('arabic', css_class='col-md-2'),
                    css_class='row',
                ),
                Div(
                    HTML('<span class="badge badge-default">2</span>'),
                    Div('attended_english', css_class='col-md-2'),
                    HTML('<span class="badge badge-default" id="span_modality_english">2.1</span>'),
                    Div('modality_english', css_class='col-md-2 multiple-checbkoxes'),
                    HTML('<span class="badge badge-default" id="span_english">2.2</span>'),
                    Div('english', css_class='col-md-2'),
                    css_class='row',
                ),
                Div(
                    HTML('<span class="badge badge-default">3</span>'),
                    Div('attended_math', css_class='col-md-2'),
                    HTML('<span class="badge badge-default" id="span_modality_math">3.1</span>'),
                    Div('modality_math', css_class='col-md-2 multiple-checbkoxes'),
                    HTML('<span class="badge badge-default" id="span_math">3.2</span>'),
                    Div('math', css_class='col-md-2'),
                    css_class='row',
                ),
                Div(
                    HTML('<span class="badge badge-default">4</span>'),
                    Div('attended_science', css_class='col-md-2'),
                    HTML('<span class="badge badge-default" id="span_modality_science">4.1</span>'),
                    Div('modality_science', css_class='col-md-2 multiple-checbkoxes'),
                    HTML('<span class="badge badge-default" id="span_science">4.2</span>'),
                    Div('science', css_class='col-md-2'),
                    css_class='row grd6',
                ),
                Div(
                    HTML('<span class="badge badge-default">4</span>'),
                    Div('attended_biology', css_class='col-md-2'),
                    HTML('<span class="badge badge-default" id="span_modality_biology">4.1</span>'),
                    Div('modality_biology', css_class='col-md-2 multiple-checbkoxes'),
                    HTML('<span class="badge badge-default" id="span_biology">4.2</span>'),
                    Div('biology', css_class='col-md-2'),
                    css_class='row grd7',
                ),

                Div(
                    HTML('<span class="badge badge-default">5</span>'),
                    Div('attended_chemistry', css_class='col-md-2'),
                    HTML('<span class="badge badge-default" id="span_modality_chemistry">5.1</span>'),
                    Div('modality_chemistry', css_class='col-md-2 multiple-checbkoxes'),
                    HTML('<span class="badge badge-default" id="span_chemistry">5.2</span>'),
                    Div('chemistry', css_class='col-md-2'),
                    css_class='row grd7',
                ),

                Div(
                    HTML('<span class="badge badge-default">6</span>'),
                    Div('attended_physics', css_class='col-md-2'),
                    HTML('<span class="badge badge-default" id="span_modality_physics">6.1</span>'),
                    Div('modality_physics', css_class='col-md-2 multiple-checbkoxes'),
                    HTML('<span class="badge badge-default" id="span_physics">6.2</span>'),
                    Div('physics', css_class='col-md-2'),
                    css_class='row grd7',
                ),


                css_class='bd-callout bd-callout-warning E_right_border'
            ),
            FormActions(
                Submit('save', _('Save'), css_class='col-md-2'),
                Submit('save_add_another', _('Save and add another'), css_class='col-md-2 child_data col-md-2'),
                HTML('<a class="btn btn-info cancel-button" href="/clm/rs-list/" translation="' + _(
                    'Are you sure you want to cancel this registration?') + '">' + _('Back to list') + '</a>'),
                css_class='button-group'
            )
        )
    def clean(self):
        cleaned_data = super(RSForm, self).clean()

        phone_number = cleaned_data.get("phone_number")
        phone_number_confirm = cleaned_data.get("phone_number_confirm")
        second_phone_number = cleaned_data.get("second_phone_number")
        second_phone_number_confirm = cleaned_data.get("second_phone_number_confirm")
        id_type = cleaned_data.get("id_type")
        case_number = cleaned_data.get("case_number")
        case_number_confirm = cleaned_data.get("case_number_confirm")
        individual_case_number = cleaned_data.get("individual_case_number")
        individual_case_number_confirm = cleaned_data.get("individual_case_number_confirm")
        recorded_number = cleaned_data.get("recorded_number")
        recorded_number_confirm = cleaned_data.get("recorded_number_confirm")
        national_number = cleaned_data.get("national_number")
        national_number_confirm = cleaned_data.get("national_number_confirm")
        syrian_national_number = cleaned_data.get("syrian_national_number")
        syrian_national_number_confirm = cleaned_data.get("syrian_national_number_confirm")
        sop_national_number = cleaned_data.get("sop_national_number")
        sop_national_number_confirm = cleaned_data.get("sop_national_number_confirm")

        parent_individual_case_number = cleaned_data.get("parent_individual_case_number")
        parent_individual_case_number_confirm = cleaned_data.get("parent_individual_case_number_confirm")
        parent_national_number = cleaned_data.get("parent_national_number")
        parent_national_number_confirm = cleaned_data.get("parent_national_number_confirm")
        sop_parent_national_number = cleaned_data.get("parent_sop_national_number")
        sop_parent_national_number_confirm = cleaned_data.get("parent_sop_national_number_confirm")
        parent_syrian_national_number = cleaned_data.get("parent_syrian_national_number")
        parent_syrian_national_number_confirm = cleaned_data.get("parent_syrian_national_number_confirm")
        parent_other_number = cleaned_data.get("parent_other_number")
        parent_other_number_confirm = cleaned_data.get("parent_other_number_confirm")
        other_number = cleaned_data.get("other_number")
        other_number_confirm = cleaned_data.get("other_number_confirm")
        miss_school_date = cleaned_data.get("miss_school_date")
        miss_school = cleaned_data.get("miss_school")
        student_nationality = cleaned_data.get("student_nationality")
        other_nationality = cleaned_data.get("other_nationality")
        main_caregiver = cleaned_data.get("main_caregiver")
        other_caregiver_relationship = cleaned_data.get("other_caregiver_relationship")
        have_labour_single_selection = cleaned_data.get("have_labour_single_selection")
        labours_single_selection = cleaned_data.get("labours_single_selection")
        labour_hours = cleaned_data.get("labour_hours")
        labour_weekly_income = cleaned_data.get("labour_weekly_income")
        student_have_children = cleaned_data.get("student_have_children")
        student_number_children = cleaned_data.get("student_number_children")
        labours_other_specify = cleaned_data.get("labours_other_specify")

        source_of_identification = cleaned_data.get("source_of_identification")
        source_of_identification_specify = cleaned_data.get("source_of_identification_specify")

        if source_of_identification == 'Other Sources':
            if not source_of_identification_specify:
                self.add_error('source_of_identification_specify', 'This field is required')


        if miss_school == 'yes':
            if not miss_school_date:
                self.add_error('miss_school_date', 'This field is required')

        attended_arabic = cleaned_data.get("attended_arabic")
        modality_arabic = cleaned_data.get("modality_arabic")
        arabic = cleaned_data.get("arabic")

        attended_english = cleaned_data.get("attended_english")
        modality_english = cleaned_data.get("modality_english")
        english = cleaned_data.get("english")

        attended_math = cleaned_data.get("attended_math")
        modality_math = cleaned_data.get("modality_math")
        math = cleaned_data.get("math")

        attended_science = cleaned_data.get("attended_science")
        modality_science = cleaned_data.get("modality_science")
        science = cleaned_data.get("science")

        attended_biology = cleaned_data.get("attended_biology")
        modality_biology = cleaned_data.get("modality_biology")
        biology = cleaned_data.get("biology")

        attended_chemistry = cleaned_data.get("attended_chemistry")
        modality_chemistry = cleaned_data.get("modality_chemistry")
        chemistry = cleaned_data.get("chemistry")

        attended_physics = cleaned_data.get("attended_physics")
        modality_physics = cleaned_data.get("modality_physics")
        physics = cleaned_data.get("physics")
        grade_registration = cleaned_data.get("grade_registration")

        if attended_arabic == 'yes':
            if not modality_arabic:
                self.add_error('modality_arabic', 'This field is required')
            if arabic is None:
                self.add_error('arabic', 'This field is required')

        if attended_english == 'yes':
            if not modality_english:
                self.add_error('modality_english', 'This field is required')
            if english is None:
                self.add_error('english', 'This field is required')

        if attended_math == 'yes':
            if not modality_math:
                self.add_error('modality_math', 'This field is required')
            if math is None:
                self.add_error('math', 'This field is required')

        if grade_registration == '6':
            if attended_science == 'yes':
                if not modality_science:
                    self.add_error('modality_science', 'This field is required')
                if science is None:
                    self.add_error('science', 'This field is required')

        elif grade_registration == '7' or grade_registration == '8' or grade_registration == '9':
            if attended_biology == 'yes':
                if not modality_biology:
                    self.add_error('modality_biology', 'This field is required')
                if biology is None:
                    self.add_error('biology', 'This field is required')
            if attended_chemistry == 'yes':
                if not modality_chemistry:
                    self.add_error('modality_chemistry', 'This field is required')
                if chemistry is None:
                    self.add_error('chemistry', 'This field is required')
            if attended_physics == 'yes':
                if not modality_physics:
                    self.add_error('modality_physics', 'This field is required')
                if physics is None:
                    self.add_error('physics', 'This field is required')

        if labours_single_selection == 'other_many_other':
            if not labours_other_specify:
                self.add_error('labours_other_specify', 'This field is required')

        if student_nationality.id == 6:
            if not other_nationality:
                self.add_error('other_nationality', 'This field is required')
        if main_caregiver == 'other':
            if not other_caregiver_relationship:
                self.add_error('other_caregiver_relationship', 'This field is required')
        if student_have_children:
            if not student_number_children:
                self.add_error('student_number_children', 'This field is required')
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

        if id_type == 'UNHCR Registered':
            if not case_number:
                self.add_error('case_number', 'This field is required')

            if case_number != case_number_confirm:
                msg = "The case numbers are not matched"
                self.add_error('case_number_confirm', msg)

            if parent_individual_case_number != parent_individual_case_number_confirm:
                msg = "The individual case numbers are not matched"
                self.add_error('parent_individual_case_number_confirm', msg)

            if individual_case_number != individual_case_number_confirm:
                msg = "The individual case numbers are not matched"
                self.add_error('individual_case_number_confirm', msg)

        if id_type == 'UNHCR Recorded':
            if not recorded_number:
                self.add_error('recorded_number', 'This field is required')

            if recorded_number != recorded_number_confirm:
                msg = "The recorded numbers are not matched"
                self.add_error('recorded_number_confirm', msg)

        if id_type == 'Syrian national ID':

            if not parent_syrian_national_number:
                self.add_error('parent_syrian_national_number', 'This field is required')

            if not parent_syrian_national_number_confirm:
                self.add_error('parent_syrian_national_number_confirm', 'This field is required')

            if parent_syrian_national_number_confirm and not len(parent_syrian_national_number_confirm) == 11:
                msg = "Please enter a valid number (11 digits)"
                self.add_error('parent_syrian_national_number_confirm', msg)

            if parent_syrian_national_number and not len(parent_syrian_national_number) == 11:
                msg = "Please enter a valid number (11 digits)"
                self.add_error('parent_syrian_national_number', msg)

            if parent_syrian_national_number != parent_syrian_national_number_confirm:
                msg = "The national numbers are not matched"
                self.add_error('parent_syrian_national_number_confirm', msg)

            if syrian_national_number != syrian_national_number_confirm:
                msg = "The national numbers are not matched"
                self.add_error('syrian_national_number_confirm', msg)

        if id_type == 'Lebanese national ID':
            if not parent_national_number:
                self.add_error('parent_national_number', 'This field is required')

            if not parent_national_number_confirm:
                self.add_error('parent_national_number_confirm', 'This field is required')

            if parent_national_number and not len(parent_national_number) == 12:
                msg = "Please enter a valid number (12 digits)"
                self.add_error('parent_national_number', msg)

            if parent_national_number_confirm and not len(parent_national_number_confirm) == 12:
                msg = "Please enter a valid number (12 digits)"
                self.add_error('parent_national_number_confirm', msg)

            if parent_national_number != parent_national_number_confirm:
                msg = "The national numbers are not matched"
                self.add_error('parent_national_number_confirm', msg)

            if national_number != national_number_confirm:
                msg = "The national numbers are not matched"
                self.add_error('national_number_confirm', msg)

        if id_type == 'Palestinian national ID':
            if not sop_parent_national_number:
                self.add_error('parent_sop_national_number', 'This field is required')

            if not sop_parent_national_number_confirm:
                self.add_error('parent_sop_national_number_confirm', 'This field is required')

            if sop_parent_national_number != sop_parent_national_number_confirm:
                msg = "The national numbers are not matched"
                self.add_error('parent_sop_national_number_confirm', msg)

            if sop_national_number != sop_national_number_confirm:
                msg = "The national numbers are not matched"
                self.add_error('sop_national_number_confirm', msg)

        if id_type == 'Other nationality':
            if not parent_other_number:
                self.add_error('parent_other_number', 'This field is required')

            if not parent_other_number_confirm:
                self.add_error('parent_other_number_confirm', 'This field is required')

            if parent_other_number != parent_other_number_confirm:
                msg = "The ID numbers are not matched"
                self.add_error('parent_other_number_confirm', msg)

            if other_number != other_number_confirm:
                msg = "The ID numbers are not matched"
                self.add_error('other_number_confirm', msg)

        #grades Max Value validation
        if grade_registration == '6':
            if arabic > 20:
                self.add_error('arabic', 'This value is greater that 20')
            if english > 20:
                self.add_error('english', 'This value is greater that 20')
            if math > 20:
                self.add_error('math', 'This value is greater that 20')
            if science > 20:
                self.add_error('science', 'This value is greater that 20')

        elif grade_registration == '7' or grade_registration == '8' or grade_registration == '9':
            if arabic > 60:
                self.add_error('arabic', 'This value is greater that 60')
            if english > 40:
                self.add_error('english', 'This value is greater that 40')
            if math > 60:
                self.add_error('math', 'This value is greater that 60')
            if biology > 20:
                self.add_error('biology', 'This value is greater that 20')
            if chemistry > 20:
                self.add_error('chemistry', 'This value is greater that 20')
            if physics > 20:
                self.add_error('physics', 'This value is greater that 20')


    def save(self, request=None, instance=None, serializer=None):
        instance = super(RSForm, self).save(request=request, instance=instance, serializer=RSSerializer)
        instance.pre_test = {
            # arabic, english, math, science, biology, chemistry, physics
            "RS_ASSESSMENT/attended_arabic": request.POST.get('attended_arabic'),
            "RS_ASSESSMENT/modality_arabic": request.POST.getlist('modality_arabic'),
            "RS_ASSESSMENT/arabic": request.POST.get('arabic'),

            "RS_ASSESSMENT/attended_english": request.POST.get('attended_english'),
            "RS_ASSESSMENT/modality_english": request.POST.getlist('modality_english'),
            "RS_ASSESSMENT/english": request.POST.get('english'),

            "RS_ASSESSMENT/attended_math": request.POST.get('attended_math'),
            "RS_ASSESSMENT/modality_math": request.POST.getlist('modality_math'),
            "RS_ASSESSMENT/math": request.POST.get('math'),

            "RS_ASSESSMENT/attended_science": request.POST.get('attended_science'),
            "RS_ASSESSMENT/modality_science": request.POST.getlist('modality_science'),
            "RS_ASSESSMENT/science": request.POST.get('science'),

            "RS_ASSESSMENT/attended_biology": request.POST.get('attended_biology'),
            "RS_ASSESSMENT/modality_biology": request.POST.getlist('modality_biology'),
            "RS_ASSESSMENT/biology": request.POST.get('biology'),

            "RS_ASSESSMENT/attended_chemistry": request.POST.get('attended_chemistry'),
            "RS_ASSESSMENT/modality_chemistry": request.POST.getlist('modality_chemistry'),
            "RS_ASSESSMENT/chemistry": request.POST.get('chemistry'),

            "RS_ASSESSMENT/attended_physics": request.POST.get('attended_physics'),
            "RS_ASSESSMENT/modality_physics": request.POST.getlist('modality_physics'),
            "RS_ASSESSMENT/physics": request.POST.get('physics'),
        }
        instance.save()

    class Meta:
        model = RS
        fields = CommonForm.Meta.fields + (
            'first_attendance_date',
            'student_birthday_year',
            'have_labour_single_selection',
            'labours_single_selection',
            'labours_other_specify',
            'labour_hours',
            'phone_number',
            'phone_number_confirm',
            'phone_owner',
            'second_phone_number',
            'second_phone_number_confirm',
            'second_phone_owner',
            # 'id_type',
            'case_number',
            'case_number_confirm',
            'individual_case_number',
            'individual_case_number_confirm',
            'parent_individual_case_number',
            'parent_individual_case_number_confirm',
            'recorded_number',
            'recorded_number_confirm',
            'national_number',
            'national_number_confirm',
            'syrian_national_number',
            'syrian_national_number_confirm',
            'sop_national_number',
            'sop_national_number_confirm',
            'parent_national_number',
            'parent_national_number_confirm',
            'parent_syrian_national_number',
            'parent_syrian_national_number_confirm',
            'parent_sop_national_number',
            'parent_sop_national_number_confirm',
            'parent_other_number',
            'parent_other_number_confirm',
            'other_number',
            'other_number_confirm',
            'no_child_id_confirmation',
            'source_of_identification',
            'source_of_identification_specify',
            'other_nationality',
            # 'caretaker_first_name',
            # 'caretaker_middle_name',
            # 'caretaker_last_name',
            # 'caretaker_mother_name',
            'miss_school',
            'miss_school_date',
            'student_have_children',
            'student_family_status',
            'student_number_children',
            'round_start_date',
            'cadaster',
            'main_caregiver',
            # 'main_caregiver_nationality',
            'other_caregiver_relationship',
            'labour_weekly_income',
            # 'source_of_transportation',
            'student_p_code',
            'grade_level',
            'source_join_fe',
            'grade_registration',
            'registered_in_school',
            'shift'
        )

    class Media:
        js = (
            # 'js/jquery-3.3.1.min.js',
            # 'js/jquery-ui-1.12.1.js',
            # 'js/validator.js',
            # 'js/registrations.js',
        )

class CBECEForm(CommonForm):
    REGISTRATION_LEVEL = (
        ('', '----------'),
        ('level_two', _('Level two')),
        ('level_three', _('Level three'))
    )

    YEARS_CB = list(((str(x), x) for x in range(Person.CURRENT_YEAR - 7, Person.CURRENT_YEAR - 3)))
    YEARS_CB.insert(0, ('', '---------'))

    cycle = forms.ModelChoiceField(
        queryset=Cycle.objects.all(), widget=forms.Select,
        label=_('In which cycle is this child registered?'),
        required=False, to_field_name='id',
        initial=0
    )
    # site = forms.ChoiceField(
    #     widget=forms.Select, required=True,
    #     label=_('Where is the program?'),
    #     choices=(
    #         ('', '--------'),
    #         ('in_school', _('Inside the school')),
    #         ('out_school', _('Outside the school')),
    #     )
    # )
    school = forms.ModelChoiceField(
        queryset=School.objects.all(), widget=forms.Select,
        label=_('The school where the child is attending the program'),
        empty_label='-------',
        required=False, to_field_name='id',
        initial=0
    )

    referral = forms.MultipleChoiceField(
        label=_('Where was the child referred?'),
        choices=CLM.REFERRAL,
        widget=forms.CheckboxSelectMultiple,
        required=False,
    )
    child_muac = forms.ChoiceField(
        label=_("What is the measurement of the child's arm circumference? (Centimeter)"),
        widget=forms.Select, required=False,
        choices=(
            ('', '-------'),
            ('1', _('< 11.5 CM (severe malnutrition)')),
            ('2', _('< 12.5 CM (moderate malnutrition)')),
        )
    )
    final_grade = forms.FloatField(
        label=_('Final grade') + ' (/80)', required=False,
        widget=forms.NumberInput,
        min_value=0, max_value=80
    )
    # learning_result = forms.ChoiceField(
    #     label=_('Based on the overall score, what is the recommended learning path?'),
    #     widget=forms.Select, required=False,
    #     choices=(
    #         ('', '----------'),
    #         ('repeat_level', _('Repeat level')),
    #         ('graduated_next_level', _('Referred to the next level')),
    #         ('graduated_to_formal_education_level1', _('Referred to formal education - Level 1')),
    #         ('referred_to_another_program', _('Referred to another program')),
    #     ),
    #     initial=''
    # )

    student_birthday_year = forms.ChoiceField(
        label=_("Birthday year"),
        widget=forms.Select, required=True,
        choices=YEARS_CB
    )

    first_attendance_date = forms.DateField(
        label=_("First attendance date"),
        required=True
    )
    miss_school_date = forms.DateField(
        label=_("Miss school date"),
        required=False,
    )
    new_registry = forms.ChoiceField(
        label=_("First time registered?"),
        widget=forms.Select, required=True,
        choices=(('yes', _("Yes")), ('no', _("No"))),
        initial='yes'
    )

    round = forms.ModelChoiceField(
        queryset=CLMRound.objects.filter(current_round_cbece=True), widget=forms.Select,
        label=_('Round'),
        empty_label='-------',
        required=True, to_field_name='id',
    )

    round_start_date = forms.DateField(
        label=_("Round start date"),
        required=False
    )


    have_labour_single_selection = forms.ChoiceField(
        label=_('Does the child participate in work?'),
        widget=forms.Select, required=True,
        choices=CLM.HAVE_LABOUR,
        initial='no'
    )
    labours_single_selection = forms.ChoiceField(
        label=_('What is the type of work ?'),
        widget=forms.Select, required=False,
        choices=CLM.LABOURS
    )
    labours_other_specify = forms.CharField(
        label=_('Please specify(hotel, restaurant, transport, personal services such as cleaning, hair care, cooking and childcare)'),
        widget=forms.TextInput, required=False
    )
    labour_hours = forms.CharField(
        label=_('How many hours does this child work in a day?'),
        widget=forms.TextInput, required=False
    )
    labour_weekly_income = forms.ChoiceField(
        label=_('What is the income of the child per week?'),
        widget=forms.Select,
        choices=Student.STUDENT_INCOME,
        initial='single',
        required=False
    )
    education_status = forms.ChoiceField(
        label=_('Education status'),
        widget=forms.Select, required=True,
        choices=(
            ('', '----------'),
            ('out of school', _('Out of school')),
            ('enrolled in formal education but did not continue',
             _("Enrolled in formal education but did not continue")),
            ('enrolled in CBECE', _("Enrolled in CBECE")),
        ),
        initial=''
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
    id_type = forms.ChoiceField(
        label=_("ID type of the caretaker"),
        widget=forms.Select(attrs=({'translation': _('Child no ID confirmation popup message')})),
        required=False,
        choices=(
            ('', '----------'),
            ('UNHCR Registered', _('UNHCR Registered')),
            ('UNHCR Recorded', _("UNHCR Recorded")),
            ('Syrian national ID', _("Syrian national ID")),
            ('Palestinian national ID', _("Palestinian national ID")),
            ('Lebanese national ID', _("Lebanese national ID")),
            ('Other nationality', _("Other nationality")),
            ('Child have no ID', _("Child have no ID"))
        ),
        initial=''
    )
    case_number = forms.RegexField(
        regex=r'^((245)|(380)|(568)|(705)|(781)|(909)|(947)|(954)|(LEB)|(leb))-[0-9][0-9][C]\d{5}$',
        widget=forms.TextInput(attrs={'placeholder': 'Format: XXX-XXCXXXXX'}),
        required=False,
        label=_('UNHCR Case Number')
    )
    case_number_confirm = forms.RegexField(
        regex=r'^((245)|(380)|(568)|(705)|(781)|(909)|(947)|(954)|(LEB)|(leb))-[0-9][0-9][C]\d{5}$',
        widget=forms.TextInput(attrs={'placeholder': 'Format: XXX-XXCXXXXX'}),
        required=False,
        label=_('Confirm UNHCR Case Number')
    )
    parent_individual_case_number = forms.RegexField(
        regex=r'^((245)|(380)|(568)|(705)|(781)|(909)|(947)|(954)|(LEB)|(leb))-[0-9]{8}$',
        widget=forms.TextInput(attrs={'placeholder': 'Format: XXX-XXXXXXXX'}),
        required=False,
        label=_(
            'Caretaker Individual ID from the certificate (Optional, in case not listed in the certificate)')
    )
    parent_individual_case_number_confirm = forms.RegexField(
        regex=r'^((245)|(380)|(568)|(705)|(781)|(909)|(947)|(954)|(LEB)|(leb))-[0-9]{8}$',
        widget=forms.TextInput(attrs={'placeholder': 'Format: XXX-XXXXXXXX'}),
        required=False,
        label=_(
            'Confirm Caretaker Individual ID from the certificate (Optional, in case not listed in the certificate)')
    )
    individual_case_number = forms.RegexField(
        regex=r'^((245)|(380)|(568)|(705)|(781)|(909)|(947)|(954)|(LEB)|(leb))-[0-9]{8}$',
        widget=forms.TextInput(attrs={'placeholder': 'Format: XXX-XXXXXXXX'}),
        required=False,
        label=_(
            'Individual ID of the Child from the certificate (Optional, in case not listed in the certificate)')
    )
    individual_case_number_confirm = forms.RegexField(
        regex=r'^((245)|(380)|(568)|(705)|(781)|(909)|(947)|(954)|(LEB)|(leb))-[0-9]{8}$',
        widget=forms.TextInput(attrs={'placeholder': 'Format: XXX-XXXXXXXX'}),
        required=False,
        label=_(
            'Confirm Individual ID of the Child from the certificate (Optional, in case not listed in the certificate)')
    )
    recorded_number = forms.RegexField(
        regex=r'^((245)|(380)|(568)|(705)|(781)|(909)|(947)|(954)|(LEB)|(leb))-[0-9][0-9][C]\d{5}$',
        widget=forms.TextInput(attrs={'placeholder': 'Format: LEB-XXCXXXXX'}),
        required=False,
        label=_('UNHCR Barcode number (Shifra number)')
    )
    recorded_number_confirm = forms.RegexField(
        regex=r'^((245)|(380)|(568)|(705)|(781)|(909)|(947)|(954)|(LEB)|(leb))-[0-9][0-9][C]\d{5}$',
        widget=forms.TextInput(attrs={'placeholder': 'Format: LEB-XXCXXXXX'}),
        required=False,
        label=_('Confirm UNHCR Barcode number (Shifra number)')
    )

    national_number = forms.RegexField(
        regex=r'^\d{12}$',
        widget=forms.TextInput(attrs={'placeholder': 'Format: XXXXXXXXXXXX'}),
        required=False,
        label=_('Lebanese ID number of the child (Optional)')
    )
    national_number_confirm = forms.RegexField(
        regex=r'^\d{12}$',
        widget=forms.TextInput(attrs={'placeholder': 'Format: XXXXXXXXXXXX'}),
        required=False,
        label=_('Confirm Lebanese ID number of the child (optional)')
    )
    syrian_national_number = forms.RegexField(
        regex=r'^\d{11}$',
        required=False,
        label=_('National ID number of the child (Optional)')
    )
    syrian_national_number_confirm = forms.RegexField(
        regex=r'^\d{11}$',
        required=False,
        label=_('Confirm National ID number of the child (Optional)')
    )
    sop_national_number = forms.CharField(
        required=False,
        label=_('Palestinian ID number of the child (Optional)')
    )
    sop_national_number_confirm = forms.CharField(
        required=False,
        label=_('Confirm Palestinian ID number of the child (optional)')
    )
    parent_national_number = forms.RegexField(
        regex=r'^\d{12}$',
        widget=forms.TextInput(attrs={'placeholder': 'Format: XXXXXXXXXXXX'}),
        required=False,
        label=_('Lebanese ID number of the caretaker (Mandatory)')
    )
    parent_national_number_confirm = forms.RegexField(
        regex=r'^\d{12}$',
        widget=forms.TextInput(attrs={'placeholder': 'Format: XXXXXXXXXXXX'}),
        required=False,
        label=_('Confirm Lebanese ID number of the caretaker (Mandatory)')
    )
    parent_syrian_national_number = forms.RegexField(
        regex=r'^\d{11}$',
        required=False,
        label=_('National ID number of the Caretaker (Mandatory)')
    )
    parent_syrian_national_number_confirm = forms.RegexField(
        regex=r'^\d{11}$',
        required=False,
        label=_('Confirm National ID number of the Caretaker (Mandatory)')
    )
    parent_sop_national_number = forms.CharField(
        # regex=r'^\d{11}$',
        required=False,
        label=_('Palestinian ID number of the Caretaker (Mandatory)')
    )
    parent_sop_national_number_confirm = forms.CharField(
        # regex=r'^\d{11}$',
        required=False,
        label=_('Confirm Palestinian ID number of the Caretaker (Mandatory)')
    )

    parent_other_number = forms.CharField(
        required=False,
        label=_('ID number of the Caretaker (Mandatory)')
    )
    parent_other_number_confirm = forms.CharField(
        required=False,
        label=_('Confirm ID number of the Caretaker (Mandatory)')
    )
    other_number = forms.CharField(
        required=False,
        label=_(' ID number of the child (Optional)')
    )
    other_number_confirm = forms.CharField(
        required=False,
        label=_('Confirm ID number of the child (optional)')
    )

    no_child_id_confirmation = forms.CharField(widget=forms.HiddenInput, required=False)
    no_parent_id_confirmation = forms.CharField(widget=forms.HiddenInput, required=False)

    source_of_identification = forms.ChoiceField(
        label=_("Source of identification of the child to CBECE"),
        widget=forms.Select,
        required=True,
        choices=(
            ('', '----------'),
            ('Referred by CP partner', _('Referred by CP partner')),
            ('Family walked in to NGO', _('Family walked in to NGO')),
            ('Referral from another NGO', _('Referral from another NGO')),
            ('Referral from another Municipality', _('Referral from Municipality')),
            ('Direct outreach', _('Direct outreach')),
            ('List database', _('List database')),
            ('From hosted community', _('From hosted community')),
            ('From displaced community', _('From displaced community'))
        ),
        initial=''
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
    attended_english = forms.ChoiceField(
        label=_("Attended English test"),
        widget=forms.Select, required=True,
        choices=(('yes', _("Yes")), ('no', _("No"))),
        initial='yes'
    )
    modality_english = forms.MultipleChoiceField(
        label=_('Please indicate modality'),
        choices=CLM.MODALITY,
        widget=forms.CheckboxSelectMultiple,
        required=False
    )
    english = forms.FloatField(
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
    attended_social = forms.ChoiceField(
        label=_("Attended Social test"),
        widget=forms.Select, required=True,
        choices=(('yes', _("Yes")), ('no', _("No"))),
        initial='yes'
    )
    modality_social = forms.MultipleChoiceField(
        label=_('Please indicate modality'),
        choices=CLM.MODALITY,
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    social_emotional = forms.FloatField(
        label=_('Results'),
        widget=forms.NumberInput(attrs=({'maxlength': 4})),
        min_value=0, required=False
    )

    attended_psychomotor = forms.ChoiceField(
        label=_("Attended Psychomotor test"),
        widget=forms.Select, required=True,
        choices=(('yes', _("Yes")), ('no', _("No"))),
        initial='yes'
    )
    modality_psychomotor  = forms.MultipleChoiceField(
        label=_('Please indicate modality'),
        choices=CLM.MODALITY,
        widget=forms.CheckboxSelectMultiple,
        required=False
    )
    psychomotor = forms.FloatField(
        label=_('Results'),
        widget=forms.NumberInput(attrs=({'maxlength': 4})),
        min_value=0, required=False
    )
    attended_science = forms.ChoiceField(
        label=_("Attended Science test"),
        widget=forms.Select, required=True,
        choices=(('yes', _("Yes")), ('no', _("No"))),
        initial='yes'
    )
    modality_science = forms.MultipleChoiceField(
        label=_('Please indicate modality'),
        choices=CLM.MODALITY,
        widget=forms.CheckboxSelectMultiple,
        required=False
    )
    science = forms.FloatField(
        label=_('Results'),
        widget=forms.NumberInput(attrs=({'maxlength': 4})),
        min_value=0, required=False
    )
    attended_artistic = forms.ChoiceField(
        label=_("Attended Artistic test"),
        widget=forms.Select, required=True,
        choices=(('yes', _("Yes")), ('no', _("No"))),
        initial='yes'
    )
    modality_artistic  = forms.MultipleChoiceField(
        label=_('Please indicate modality'),
        choices=CLM.MODALITY,
        widget=forms.CheckboxSelectMultiple,
        required=False
    )
    artistic = forms.FloatField(
        label=_('Results'),
        widget=forms.NumberInput(attrs=({'maxlength': 4})),
        min_value=0, required=False
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
    main_caregiver_nationality = forms.ModelChoiceField(
        label=_("Nationality"),
        queryset=Nationality.objects.exclude(id=9), widget=forms.Select,
        required=False, to_field_name='id',
    )

    student_p_code = forms.CharField(
        label=_('P-Code If a child lives in a tent / Brax in a random camp'),
        widget=forms.TextInput, required=False
    )

    student_number_children = forms.IntegerField(
        label=_('How many children does this child have?'),
        widget=forms.TextInput, required=False
    )

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(CBECEForm, self).__init__(*args, **kwargs)

        display_registry = ''
        instance = kwargs['instance'] if 'instance' in kwargs else ''
        form_action = reverse('clm:cbece_add')
        self.fields['clm_type'].initial = 'CBECE'
        self.fields['new_registry'].initial = 'yes'
        if instance:
            display_registry = ' d-none'
            form_action = reverse('clm:cbece_edit', kwargs={'pk': instance.id})
            if instance.cycle_id == 3:
                display_final_grade = ''

        self.helper = FormHelper()
        self.helper.form_show_labels = True
        self.helper.form_action = form_action
        self.helper.layout = Layout(
            Fieldset(
                None,
                Div(
                    HTML('<span>A.1</span>'), css_class='block_tag'),
                Div(
                    HTML('<h4 id="alternatives-to-hidden-labels">' + _(
                        'Search CLM student') + '</h4>')
                ),
                Div(
                    'clm_type',
                    'student_id',
                    'enrollment_id',
                    css_class='row',
                ),
                Div(
                    HTML('<span class="badge badge-default"></span>'),
                    Div('search_clm_student', css_class='col-md-3'),
                    css_class='row',
                ),
                Div(
                    HTML('<p>' + _(
                        'Search by the following keywords: child first name, father name, last name, '
                        'child number or partner internal number') + '</p>'),
                ),
                css_id='search_options',
                css_class='bd-callout bd-callout-warning child_data E_right_border' + display_registry
            ),
            Fieldset(
                None,
                Div(
                    HTML('<span>A</span>'), css_class='block_tag'),
                Div(
                    HTML('<h4 id="alternatives-to-hidden-labels">' + _('General Information') + '</h4>')
                ),
                Div(

                    HTML('<span class="badge badge-default">1</span>'),
                    Div('new_registry', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">2</span>'),
                    Div('round', css_class='col-md-3'),
                    # HTML('<span class="badge badge-default">3</span>'),
                    Div('round_start_date', css_class='col-md-3 d-none'),
                    css_class='row',
                ),
                Div(
                    HTML('<span class="badge badge-default">3</span>'),
                    Div('governorate', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">4</span>'),
                    Div('district', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">5</span>'),
                    Div('cadaster', css_class='col-md-3'),
                    css_class='row',
                ),
                Div(
                    HTML('<span class="badge badge-default">6</span>'),
                    Div('location', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">7</span>'),
                    Div('language', css_class='col-md-3'),
                    css_class='row',
                ),
                Div(
                    HTML('<span class="badge badge-default">8</span>'),
                    Div('student_address', css_class='col-md-3'),
                    css_class='row',
                ),

                Div(
                    HTML('<span class="badge badge-default">9</span>'),
                    Div('registration_level', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">10</span>'),
                    Div('first_attendance_date', css_class='col-md-3'),
                    css_class='row',
                ),
                css_class='bd-callout bd-callout-warning child_data A_right_border'
            ),
            Fieldset(
                None,
                Div(HTML('<span>B</span>'), css_class='block_tag'),
                Div(
                    HTML('<h4 id="alternatives-to-hidden-labels">' + _('Child Information') + '</h4>')
                ),
                Div(
                    HTML('<span class="badge badge-default">1</span>'),
                    Div('student_first_name', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">2</span>'),
                    Div('student_father_name', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">3</span>'),
                    Div('student_last_name', css_class='col-md-3'),
                    css_class='row',
                ),
                Div(
                    HTML('<span class="badge badge-default">4</span>'),
                    Div('student_mother_fullname', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">5</span>'),
                    Div('student_sex', css_class='col-md-3'),
                    css_class='row',
                ),
                Div(
                    HTML('<span class="badge badge-default">6</span>'),
                    Div('student_nationality', css_class='col-md-3'),
                    HTML('<span class="badge badge-default" id="span_other_nationality">6.1</span>'),
                    Div('other_nationality', css_class='col-md-3'),
                    css_class='row',
                ),
                Div(
                    HTML('<span class="badge badge-default">7</span>'),
                    Div('student_birthday_year', css_class='col-md-2'),
                    HTML('<span class="badge badge-default">8</span>'),
                    Div('student_birthday_month', css_class='col-md-2'),
                    HTML('<span class="badge badge-default">9</span>'),
                    Div('student_birthday_day', css_class='col-md-2'),
                    css_class='row',
                ),
                Div(
                    HTML('<span class="badge badge-default">10</span>'),
                    Div('student_p_code', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">11</span>'),
                    Div('disability', css_class='col-md-3'),
                    css_class='row',
                ),

                Div(
                    HTML('<span class="badge badge-default">12</span>'),
                    Div('education_status', css_class='col-md-3'),
                    HTML('<span class="badge badge-default" id="span_miss_school_date">12.1</span>'),
                    Div('miss_school_date', css_class='col-md-3'),
                    css_class='row',
                ),
                Div(
                    HTML('<span class="badge badge-default">13</span>'),
                    Div('internal_number', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">14</span>'),
                    Div('source_of_identification', css_class='col-md-3'),
                    css_class='row',
                ),
                Div(
                    HTML('<span class="badge badge-default">16</span>'),
                    Div('source_of_transportation', css_class='col-md-3'),
                    css_class='row d-none',
                ),
                css_class='bd-callout bd-callout-warning child_data B_right_border'
            ),
            Fieldset(
                None,
                Div(HTML('<span>C</span>'), css_class='block_tag'),
                Div(
                    HTML('<h4 id="alternatives-to-hidden-labels">' + _('Parent/Caregiver Information') + '</h4>')
                ),
                Div(
                    HTML('<span class="badge badge-default">1</span>'),
                    Div('hh_educational_level', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">2</span>'),
                    Div('father_educational_level', css_class='col-md-3'),
                    css_class='row',
                ),
                Div(
                    HTML('<span class="badge badge-default">3</span>'),
                    Div('phone_number', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">3.1</span>'),
                    Div('phone_number_confirm', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">3.2</span>'),
                    Div('phone_owner', css_class='col-md-3'),
                    css_class='row',
                ),
                Div(
                    HTML('<span class="badge badge-default">4</span>'),
                    Div('second_phone_number', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">4.1</span>'),
                    Div('second_phone_number_confirm', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">4.2</span>'),
                    Div('second_phone_owner', css_class='col-md-3'),
                    css_class='row',
                ),
                Div(
                    HTML('<span class="badge badge-default">5</span>'),
                    Div('main_caregiver', css_class='col-md-3'),
                    # HTML('<span class="badge badge-default">5.1</span>'),
                    # Div('main_caregiver_nationality', css_class='col-md-3'),
                    HTML('<span class="badge badge-default" id="span_other_caregiver_relationship">5.1</span>'),
                    Div('other_caregiver_relationship', css_class='col-md-3'),
                    css_class='row',
                ),
                # Div(
                #     HTML('<span class="badge badge-default">6</span>'),
                #     Div('caretaker_first_name', css_class='col-md-3'),
                #     HTML('<span class="badge badge-default">7</span>'),
                #     Div('caretaker_middle_name', css_class='col-md-3'),
                #     css_class='row',
                # ),
                # Div(
                #     HTML('<span class="badge badge-default">8</span>'),
                #     Div('caretaker_last_name', css_class='col-md-3'),
                #     HTML('<span class="badge badge-default">9</span>'),
                #     Div('caretaker_mother_name', css_class='col-md-3'),
                #     css_class='row',
                # ),
                # Div(
                #     HTML('<span class="badge badge-default">10</span>'),
                #     Div('id_type', css_class='col-md-3'),
                #     css_class='row',
                # ),
                Div(
                    HTML('<span class="badge badge-default">11</span>'),
                    Div('case_number', css_class='col-md-4'),
                    HTML('<span class="badge badge-default">12</span>'),
                    Div('case_number_confirm', css_class='col-md-4'),
                    HTML('<span style="padding-top: 37px;">' +
                         '<a class="image-link" href="/static/images/unhcr_certificate.jpg" target="_blank">' +
                         '<img src="/static/images/icon-help.png" width="25px" height="25px;"/></a></span>'),
                    css_class='row child_id child_id1',
                ),
                Div(
                    HTML('<span class="badge badge-default">13</span>'),
                    Div('parent_individual_case_number', css_class='col-md-4'),
                    HTML('<span class="badge badge-default">14</span>'),
                    Div('parent_individual_case_number_confirm', css_class='col-md-4'),
                    HTML('<span style="padding-top: 37px;">' +
                         '<a class="image-link" href="/static/images/UNHCR_individualID.jpg" target="_blank">' +
                         '<img src="/static/images/icon-help.png" width="25px" height="25px;"/></a></span>'),
                    css_class='row child_id child_id1',
                ),
                Div(
                    HTML('<span class="badge badge-default">15</span>'),
                    Div('individual_case_number', css_class='col-md-4'),
                    HTML('<span class="badge badge-default">16</span>'),
                    Div('individual_case_number_confirm', css_class='col-md-4'),
                    HTML('<span style="padding-top: 37px;">' +
                         '<a class="image-link" href="/static/images/UNHCR_individualID.jpg" target="_blank">' +
                         '<img src="/static/images/icon-help.png" width="25px" height="25px;"/></a></span>'),
                    css_class='row child_id child_id1',
                ),
                Div(
                    HTML('<span class="badge badge-default">17</span>'),
                    Div('recorded_number', css_class='col-md-4'),
                    HTML('<span class="badge badge-default">18</span>'),
                    Div('recorded_number_confirm', css_class='col-md-4'),
                    HTML('<span style="padding-top: 37px;">' +
                         '<a class="image-link" href="/static/images/UNHCR_barcode.jpg" target="_blank">' +
                         '<img src="/static/images/icon-help.png" width="25px" height="25px;"/></a></span>'),
                    css_class='row child_id child_id2',
                ),
                Div(
                    HTML('<span class="badge badge-default">19</span>'),
                    Div('parent_national_number', css_class='col-md-4'),
                    HTML('<span class="badge badge-default">20</span>'),
                    Div('parent_national_number_confirm', css_class='col-md-4'),
                    HTML('<span style="padding-top: 37px;">' +
                         '<a class="image-link" href="/static/images/lebanese_nationalID.png" target="_blank">' +
                         '<img src="/static/images/icon-help.png" width="25px" height="25px;"/></a></span>'),
                    css_class='row child_id child_id3',
                ),
                Div(
                    HTML('<span class="badge badge-default">21</span>'),
                    Div('national_number', css_class='col-md-4'),
                    HTML('<span class="badge badge-default">22</span>'),
                    Div('national_number_confirm', css_class='col-md-4'),
                    HTML('<span style="padding-top: 37px;">' +
                         '<a class="image-link" href="/static/images/lebanese_nationalID.png" target="_blank">' +
                         '<img src="/static/images/icon-help.png" width="25px" height="25px;"/></a></span>'),
                    css_class='row child_id child_id3',
                ),
                Div(
                    HTML('<span class="badge badge-default">23</span>'),
                    Div('parent_syrian_national_number', css_class='col-md-4'),
                    HTML('<span class="badge badge-default">24</span>'),
                    Div('parent_syrian_national_number_confirm', css_class='col-md-4'),
                    HTML('<span style="padding-top: 37px;">' +
                         '<a class="image-link" href="/static/images/Syrian_passport.png" target="_blank">' +
                         '<img src="/static/images/icon-help.png" width="25px" height="25px;"/></a></span>'),
                    css_class='row child_id child_id4',
                ),
                Div(
                    HTML('<span class="badge badge-default">25</span>'),
                    Div('syrian_national_number', css_class='col-md-4'),
                    HTML('<span class="badge badge-default">26</span>'),
                    Div('syrian_national_number_confirm', css_class='col-md-4'),
                    HTML('<span style="padding-top: 37px;">' +
                         '<a class="image-link" href="/static/images/Syrian_passport.png" target="_blank">' +
                         '<img src="/static/images/icon-help.png" width="25px" height="25px;"/></a></span>'),
                    css_class='row child_id child_id4',
                ),
                Div(
                    HTML('<span class="badge badge-default">27</span>'),
                    Div('parent_sop_national_number', css_class='col-md-4'),
                    HTML('<span class="badge badge-default">28</span>'),
                    Div('parent_sop_national_number_confirm', css_class='col-md-4'),
                    HTML('<span style="padding-top: 37px;">' +
                         '<a class="image-link" href="/static/images/Palestinian_from_Lebanon.png" target="_blank">' +
                         '<img src="/static/images/icon-help.png" width="25px" height="25px;"/></a></span>'),
                    css_class='row child_id child_id5',
                ),
                Div(
                    HTML('<span class="badge badge-default">29</span>'),
                    Div('sop_national_number', css_class='col-md-4'),
                    HTML('<span class="badge badge-default">30</span>'),
                    Div('sop_national_number_confirm', css_class='col-md-4'),
                    HTML('<span style="padding-top: 37px;">' +
                         '<a class="image-link" href="/static/images/Palestinian_from_Lebanon.png" target="_blank">' +
                         '<img src="/static/images/icon-help.png" width="25px" height="25px;"/></a></span>'),
                    css_class='row child_id child_id5',
                ),
                Div(
                    HTML('<span class="badge badge-default">31</span>'),
                    Div('parent_other_number', css_class='col-md-4'),
                    HTML('<span class="badge badge-default">32</span>'),
                    Div('parent_other_number_confirm', css_class='col-md-4'),
                    css_class='row child_id child_id6',
                ),
                Div(
                    HTML('<span class="badge badge-default">33</span>'),
                    Div('other_number', css_class='col-md-4'),
                    HTML('<span class="badge badge-default">34</span>'),
                    Div('other_number_confirm', css_class='col-md-4'),
                    css_class='row child_id child_id6',
                ),
                css_class='bd-callout bd-callout-warning child_data C_right_border'
            ),

            Fieldset(
                None,
                Div(HTML('<span>D</span>'), css_class='block_tag'),
                Div(
                    HTML('<h4 id="alternatives-to-hidden-labels">' + _('Family Status') + '</h4>')
                ),
                Div(
                    HTML('<span class="badge badge-default">3</span>'),
                    Div('have_labour_single_selection', css_class='col-md-3'),
                    css_class='row',
                ),
                Div(
                    HTML('<span class="badge badge-default">3.1</span>'),
                    Div('labours_single_selection', css_class='col-md-3', css_id='labours'),
                    HTML('<span class="badge badge-default" id="span_labours_other_specify">3.1.1</span>'),
                    Div('labours_other_specify', css_class='col-md-3'),
                    css_class='row',
                    id='labour_details_1'
                ),
                Div(
                    HTML('<span class="badge badge-default">3.2</span>'),
                    Div('labour_hours', css_class='col-md-3', css_id='labour_hours'),
                    HTML('<span class="badge badge-default">3.3</span>'),
                    Div('labour_weekly_income', css_class='col-md-3'),
                    css_class='row',
                    id='labour_details_2'
                ),
                css_class='bd-callout bd-callout-warning child_data D_right_border'
            ),

            Fieldset(
                None,
                Div(
                    HTML('<span>E</span>'), css_class='block_tag'),
                Div(
                    HTML('<h4 id="alternatives-to-hidden-labels">' + _('Assessment data') + '</h4>')
                ),
                Div(
                    HTML('<span class="badge badge-default">1</span>'),
                    Div('attended_arabic', css_class='col-md-2'),
                    HTML('<span class="badge badge-default" id="span_modality_arabic">1.1</span>'),
                    Div('modality_arabic', css_class='col-md-2 multiple-checbkoxes'),
                    HTML('<span class="badge badge-default" id="span_arabic">1.2</span>'),
                    Div('arabic', css_class='col-md-2'),
                    css_class='row',
                ),
                Div(
                    HTML('<span class="badge badge-default">2</span>'),
                    Div('attended_english', css_class='col-md-2'),
                    HTML('<span class="badge badge-default" id="span_modality_english">2.1</span>'),
                    Div('modality_english', css_class='col-md-2 multiple-checbkoxes'),
                    HTML('<span class="badge badge-default" id="span_english">2.2</span>'),
                    Div('english', css_class='col-md-2'),
                    css_class='row',
                ),
                Div(
                    HTML('<span class="badge badge-default">3</span>'),
                    Div('attended_math', css_class='col-md-2'),
                    HTML('<span class="badge badge-default" id="span_modality_math">3.1</span>'),
                    Div('modality_math', css_class='col-md-2 multiple-checbkoxes'),
                    HTML('<span class="badge badge-default" id="span_math">3.2</span>'),
                    Div('math', css_class='col-md-2'),
                    css_class='row',
                ),
                Div(
                    HTML('<span class="badge badge-default">4</span>'),
                    Div('attended_science', css_class='col-md-2'),
                    HTML('<span class="badge badge-default" id="span_modality_science">4.1</span>'),
                    Div('modality_science', css_class='col-md-2 multiple-checbkoxes'),
                    HTML('<span class="badge badge-default" id="span_science">4.2</span>'),
                    Div('science', css_class='col-md-2'),
                    css_class='row',
                ),

                Div(
                    HTML('<span class="badge badge-default">5</span>'),
                    Div('attended_social', css_class='col-md-2'),
                    HTML('<span class="badge badge-default" id="span_modality_social">5.1</span>'),
                    Div('modality_social', css_class='col-md-2 multiple-checbkoxes'),
                    HTML('<span class="badge badge-default" id="span_social_emotional">5.2</span>'),
                    Div('social_emotional', css_class='col-md-2'),
                    css_class='row',
                ),

                Div(
                    HTML('<span class="badge badge-default">6</span>'),
                    Div('attended_psychomotor', css_class='col-md-2'),
                    HTML('<span class="badge badge-default" id="span_modality_psychomotor">6.1</span>'),
                    Div('modality_psychomotor', css_class='col-md-2 multiple-checbkoxes'),
                    HTML('<span class="badge badge-default" id="span_psychomotor">6.2</span>'),
                    Div('psychomotor', css_class='col-md-2'),
                    css_class='row',
                ),

                Div(
                    HTML('<span class="badge badge-default">7</span>'),
                    Div('attended_artistic', css_class='col-md-2'),
                    HTML('<span class="badge badge-default" id="span_modality_artistic">7.1</span>'),
                    Div('modality_artistic', css_class='col-md-2 multiple-checbkoxes'),
                    HTML('<span class="badge badge-default" id="span_artistic">7.2</span>'),
                    Div('artistic', css_class='col-md-2'),
                    css_class='row',
                ),


                css_class='bd-callout bd-callout-warning E_right_border'
            ),
            FormActions(
                Submit('save', _('Save'), css_class='col-md-2'),
                Submit('save_add_another', _('Save and add another'), css_class='col-md-2 child_data col-md-2'),
                HTML('<a class="btn btn-info cancel-button" href="/clm/cbece-list/" translation="' + _(
                    'Are you sure you want to cancel this registration?') + '">' + _('Back to list') + '</a>'),
                css_class='button-group'
            )
        )
    def clean(self):
        cleaned_data = super(CBECEForm, self).clean()

        phone_number = cleaned_data.get("phone_number")
        phone_number_confirm = cleaned_data.get("phone_number_confirm")
        second_phone_number = cleaned_data.get("second_phone_number")
        second_phone_number_confirm = cleaned_data.get("second_phone_number_confirm")
        id_type = cleaned_data.get("id_type")
        case_number = cleaned_data.get("case_number")
        case_number_confirm = cleaned_data.get("case_number_confirm")
        individual_case_number = cleaned_data.get("individual_case_number")
        individual_case_number_confirm = cleaned_data.get("individual_case_number_confirm")
        recorded_number = cleaned_data.get("recorded_number")
        recorded_number_confirm = cleaned_data.get("recorded_number_confirm")
        national_number = cleaned_data.get("national_number")
        national_number_confirm = cleaned_data.get("national_number_confirm")
        syrian_national_number = cleaned_data.get("syrian_national_number")
        syrian_national_number_confirm = cleaned_data.get("syrian_national_number_confirm")
        sop_national_number = cleaned_data.get("sop_national_number")
        sop_national_number_confirm = cleaned_data.get("sop_national_number_confirm")

        parent_individual_case_number = cleaned_data.get("parent_individual_case_number")
        parent_individual_case_number_confirm = cleaned_data.get("parent_individual_case_number_confirm")
        parent_national_number = cleaned_data.get("parent_national_number")
        parent_national_number_confirm = cleaned_data.get("parent_national_number_confirm")
        sop_parent_national_number = cleaned_data.get("parent_sop_national_number")
        sop_parent_national_number_confirm = cleaned_data.get("parent_sop_national_number_confirm")
        parent_syrian_national_number = cleaned_data.get("parent_syrian_national_number")
        parent_syrian_national_number_confirm = cleaned_data.get("parent_syrian_national_number_confirm")
        parent_other_number = cleaned_data.get("parent_other_number")
        parent_other_number_confirm = cleaned_data.get("parent_other_number_confirm")
        other_number = cleaned_data.get("other_number")
        other_number_confirm = cleaned_data.get("other_number_confirm")
        education_status = cleaned_data.get("education_status")
        miss_school_date = cleaned_data.get("miss_school_date")
        student_nationality = cleaned_data.get("student_nationality")
        other_nationality = cleaned_data.get("other_nationality")
        main_caregiver = cleaned_data.get("main_caregiver")
        other_caregiver_relationship = cleaned_data.get("other_caregiver_relationship")
        have_labour_single_selection = cleaned_data.get("have_labour_single_selection")
        labours_single_selection = cleaned_data.get("labours_single_selection")
        labour_hours = cleaned_data.get("labour_hours")
        labour_weekly_income = cleaned_data.get("labour_weekly_income")
        student_have_children = cleaned_data.get("student_have_children")
        student_number_children = cleaned_data.get("student_number_children")

        labours_other_specify = cleaned_data.get("labours_other_specify")

        attended_arabic = cleaned_data.get("attended_arabic")
        modality_arabic = cleaned_data.get("modality_arabic")
        arabic = cleaned_data.get("arabic")

        attended_english = cleaned_data.get("attended_english")
        modality_english = cleaned_data.get("modality_english")
        english = cleaned_data.get("english")

        attended_psychomotor = cleaned_data.get("attended_psychomotor")
        modality_psychomotor = cleaned_data.get("modality_psychomotor")
        psychomotor = cleaned_data.get("psychomotor")

        attended_math = cleaned_data.get("attended_math")
        modality_math = cleaned_data.get("modality_math")
        math = cleaned_data.get("math")

        attended_social = cleaned_data.get("attended_social")
        modality_social = cleaned_data.get("modality_social")
        social_emotional = cleaned_data.get("social_emotional")

        attended_science = cleaned_data.get("attended_science")
        modality_science = cleaned_data.get("modality_science")
        science = cleaned_data.get("science")

        attended_artistic = cleaned_data.get("attended_artistic")
        modality_artistic = cleaned_data.get("modality_artistic")
        artistic = cleaned_data.get("artistic")


        if attended_science == 'yes':
            if not modality_science:
                self.add_error('modality_science', 'This field is required')
            if science is None:
                self.add_error('science', 'This field is required')

        if attended_artistic == 'yes':
            if not modality_artistic:
                self.add_error('modality_artistic', 'This field is required')
            if artistic is None:
                self.add_error('artistic', 'This field is required')


        if attended_arabic == 'yes':
            if not modality_arabic:
                self.add_error('modality_arabic', 'This field is required')
            if arabic is None:
                self.add_error('arabic', 'This field is required')

        if attended_english == 'yes':
            if not modality_english:
                self.add_error('modality_english', 'This field is required')
            if english is None:
                self.add_error('english', 'This field is required')

        if attended_psychomotor == 'yes':
            if not modality_psychomotor:
                self.add_error('modality_psychomotor', 'This field is required')
            if psychomotor is None:
                self.add_error('psychomotor', 'This field is required')

        if attended_math == 'yes':
            if not modality_math:
                self.add_error('modality_math', 'This field is required')
            if math is None:
                self.add_error('math', 'This field is required')

        if attended_social == 'yes':
            if not modality_social:
                self.add_error('modality_social', 'This field is required')
            if social_emotional is None:
                self.add_error('social_emotional', 'This field is required')

        if labours_single_selection == 'other_many_other':
            if not labours_other_specify:
                self.add_error('labours_other_specify', 'This field is required')

        if education_status != 'out of school':
            if not miss_school_date:
                self.add_error('miss_school_date', 'This field is required')

        if student_nationality.id == 6:
            if not other_nationality:
                self.add_error('other_nationality', 'This field is required')
        if main_caregiver == 'other':
            if not other_caregiver_relationship:
                self.add_error('other_caregiver_relationship', 'This field is required')
        if student_have_children:
            if not student_number_children:
                self.add_error('student_number_children', 'This field is required')
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

        if id_type == 'UNHCR Registered':
            if not case_number:
                self.add_error('case_number', 'This field is required')

            if case_number != case_number_confirm:
                msg = "The case numbers are not matched"
                self.add_error('case_number_confirm', msg)

            if parent_individual_case_number != parent_individual_case_number_confirm:
                msg = "The individual case numbers are not matched"
                self.add_error('parent_individual_case_number_confirm', msg)

            if individual_case_number != individual_case_number_confirm:
                msg = "The individual case numbers are not matched"
                self.add_error('individual_case_number_confirm', msg)

        if id_type == 'UNHCR Recorded':
            if not recorded_number:
                self.add_error('recorded_number', 'This field is required')

            if recorded_number != recorded_number_confirm:
                msg = "The recorded numbers are not matched"
                self.add_error('recorded_number_confirm', msg)

        if id_type == 'Syrian national ID':

            if not parent_syrian_national_number:
                self.add_error('parent_syrian_national_number', 'This field is required')

            if not parent_syrian_national_number_confirm:
                self.add_error('parent_syrian_national_number_confirm', 'This field is required')

            if parent_syrian_national_number_confirm and not len(parent_syrian_national_number_confirm) == 11:
                msg = "Please enter a valid number (11 digits)"
                self.add_error('parent_syrian_national_number_confirm', msg)

            if parent_syrian_national_number and not len(parent_syrian_national_number) == 11:
                msg = "Please enter a valid number (11 digits)"
                self.add_error('parent_syrian_national_number', msg)

            if parent_syrian_national_number != parent_syrian_national_number_confirm:
                msg = "The national numbers are not matched"
                self.add_error('parent_syrian_national_number_confirm', msg)

            if syrian_national_number != syrian_national_number_confirm:
                msg = "The national numbers are not matched"
                self.add_error('syrian_national_number_confirm', msg)

        if id_type == 'Lebanese national ID':
            if not parent_national_number:
                self.add_error('parent_national_number', 'This field is required')

            if not parent_national_number_confirm:
                self.add_error('parent_national_number_confirm', 'This field is required')

            if parent_national_number and not len(parent_national_number) == 12:
                msg = "Please enter a valid number (12 digits)"
                self.add_error('parent_national_number', msg)

            if parent_national_number_confirm and not len(parent_national_number_confirm) == 12:
                msg = "Please enter a valid number (12 digits)"
                self.add_error('parent_national_number_confirm', msg)

            if parent_national_number != parent_national_number_confirm:
                msg = "The national numbers are not matched"
                self.add_error('parent_national_number_confirm', msg)

            if national_number != national_number_confirm:
                msg = "The national numbers are not matched"
                self.add_error('national_number_confirm', msg)

        if id_type == 'Palestinian national ID':
            if not sop_parent_national_number:
                self.add_error('parent_sop_national_number', 'This field is required')

            if not sop_parent_national_number_confirm:
                self.add_error('parent_sop_national_number_confirm', 'This field is required')

            if sop_parent_national_number != sop_parent_national_number_confirm:
                msg = "The national numbers are not matched"
                self.add_error('parent_sop_national_number_confirm', msg)

            if sop_national_number != sop_national_number_confirm:
                msg = "The national numbers are not matched"
                self.add_error('sop_national_number_confirm', msg)

        if id_type == 'Other nationality':
            if not parent_other_number:
                self.add_error('parent_other_number', 'This field is required')

            if not parent_other_number_confirm:
                self.add_error('parent_other_number_confirm', 'This field is required')

            if parent_other_number != parent_other_number_confirm:
                msg = "The ID numbers are not matched"
                self.add_error('parent_other_number_confirm', msg)

            if other_number != other_number_confirm:
                msg = "The ID numbers are not matched"
                self.add_error('other_number_confirm', msg)

        #grades Max Value validation
        registration_level = cleaned_data.get("registration_level")
        arabic = cleaned_data.get("arabic")
        english = cleaned_data.get("english")
        math = cleaned_data.get("math")
        social_emotional = cleaned_data.get("social_emotional")
        psychomotor = cleaned_data.get("psychomotor")
        science = cleaned_data.get("science")
        artistic = cleaned_data.get("artistic")

        if registration_level == 'level_two':
            if arabic > 48:
                self.add_error('arabic', 'This value is greater that 48')
            if english > 48:
                self.add_error('english', 'This value is greater that 48')
            if math > 44:
                self.add_error('math', 'This value is greater that 44')
            if social_emotional > 40:
                self.add_error('social_emotional', 'This value is greater that 40')
            if psychomotor > 34:
                self.add_error('psychomotor', 'This value is greater that 34')
            if science > 36:
                self.add_error('science', 'This value is greater that 36')
            if artistic > 12:
                self.add_error('artistic', 'This value is greater that 12')
        else:
            if arabic > 60:
                self.add_error('arabic', 'This value is greater that 60')
            if english > 60:
                self.add_error('english', 'This value is greater that 60')
            if math > 46:
                self.add_error('math', 'This value is greater that 46')
            if social_emotional > 40:
                self.add_error('social_emotional', 'This value is greater that 40')
            if psychomotor > 36:
                self.add_error('psychomotor', 'This value is greater that 36')
            if science > 36:
                self.add_error('science', 'This value is greater that 36')
            if artistic > 12:
                self.add_error('artistic', 'This value is greater that 12')


    def save(self, request=None, instance=None, serializer=None):
        instance = super(CBECEForm, self).save(request=request, instance=instance, serializer=CBECESerializer)
        instance.pre_test = {
            "CBECE_ASSESSMENT/attended_arabic": request.POST.get('attended_arabic'),
            "CBECE_ASSESSMENT/modality_arabic": request.POST.getlist('modality_arabic'),
            "CBECE_ASSESSMENT/arabic": request.POST.get('arabic'),

            "CBECE_ASSESSMENT/attended_english": request.POST.get('attended_english'),
            "CBECE_ASSESSMENT/modality_english": request.POST.getlist('modality_english'),
            "CBECE_ASSESSMENT/english": request.POST.get('english'),

            "CBECE_ASSESSMENT/attended_psychomotor": request.POST.get('attended_psychomotor'),
            "CBECE_ASSESSMENT/modality_psychomotor": request.POST.getlist('modality_psychomotor'),
            "CBECE_ASSESSMENT/psychomotor": request.POST.get('psychomotor'),

            "CBECE_ASSESSMENT/attended_math": request.POST.get('attended_math'),
            "CBECE_ASSESSMENT/modality_math": request.POST.getlist('modality_math'),
            "CBECE_ASSESSMENT/math": request.POST.get('math'),

            "CBECE_ASSESSMENT/attended_social": request.POST.get('attended_social'),
            "CBECE_ASSESSMENT/modality_social": request.POST.getlist('modality_social'),
            "CBECE_ASSESSMENT/social_emotional": request.POST.get('social_emotional'),

            "CBECE_ASSESSMENT/attended_science": request.POST.get('attended_science'),
            "CBECE_ASSESSMENT/modality_science": request.POST.getlist('modality_science'),
            "CBECE_ASSESSMENT/science": request.POST.get('science'),

            "CBECE_ASSESSMENT/attended_artistic": request.POST.get('attended_artistic'),
            "CBECE_ASSESSMENT/modality_artistic": request.POST.getlist('modality_artistic'),
            "CBECE_ASSESSMENT/artistic": request.POST.get('artistic'),
        }
        instance.save()

    class Meta:
        model = CBECE
        fields = CommonForm.Meta.fields + (
            'first_attendance_date',
            'student_birthday_year',
            'have_labour_single_selection',
            'labours_single_selection',
            'labours_other_specify',
            'labour_hours',
            'phone_number',
            'phone_number_confirm',
            'phone_owner',
            'second_phone_number',
            'second_phone_number_confirm',
            'second_phone_owner',
            # 'id_type',
            'case_number',
            'case_number_confirm',
            'individual_case_number',
            'individual_case_number_confirm',
            'parent_individual_case_number',
            'parent_individual_case_number_confirm',
            'recorded_number',
            'recorded_number_confirm',
            'national_number',
            'national_number_confirm',
            'syrian_national_number',
            'syrian_national_number_confirm',
            'sop_national_number',
            'sop_national_number_confirm',
            'parent_national_number',
            'parent_national_number_confirm',
            'parent_syrian_national_number',
            'parent_syrian_national_number_confirm',
            'parent_sop_national_number',
            'parent_sop_national_number_confirm',
            'parent_other_number',
            'parent_other_number_confirm',
            'other_number',
            'other_number_confirm',
            'no_child_id_confirmation',
            'source_of_identification',
            'other_nationality',
            'education_status',
            # 'caretaker_first_name',
            # 'caretaker_middle_name',
            # 'caretaker_last_name',
            # 'caretaker_mother_name',
            'miss_school_date',
            'round_start_date',
            'cadaster',
            'registration_level',
            'main_caregiver',
            # 'main_caregiver_nationality',
            'other_caregiver_relationship',
            'labour_weekly_income',
            'source_of_transportation',
            'student_p_code',
        )

    class Media:
        js = (
            # 'js/jquery-3.3.1.min.js',
            # 'js/jquery-ui-1.12.1.js',
            # 'js/validator.js',
            # 'js/registrations.js',
        )

class CBECEMonitoringQuestionerForm(forms.ModelForm):
    basic_stationery = forms.ChoiceField(
        label=_("Did the child receive basic stationery?"),
        widget=forms.Select, required=True,
        choices=CLM.YES_NO
    )
    # pss_kit = forms.ChoiceField(
    #         label=_("Did the child benefit from the PSS kit?"),
    #         widget=forms.Select, required=True,
    #         choices=CLM.YES_NO
    #     )
    remote_learning = forms.ChoiceField(
        label=_("Was the child involved in remote learning?"),
        widget=forms.Select, required=True,
        choices=CLM.YES_NO
    )
    remote_learning_reasons_not_engaged = forms.ChoiceField(
        label=_("what other reasons for this child not being engaged?"),
        widget=forms.Select, required=False,
        choices=(
            ('', '----------'),
            ('child_relocated', _('Child relocated')),
            ('child_is_not_reachable', _('Child is not reachable')),
            ('child_did_not_fit_the_criteria', _('Child did not fit the criteria - enrolled in previous FE')),
            ('Other', _('Other')),
        ),
    )
    reasons_not_engaged_other = forms.CharField(
        label=_('Please specify'),
        widget=forms.TextInput, required=False
    )
    reliable_internet = forms.ChoiceField(
        label=_("Does the family have reliable internet service in their area during remote learning?"),
        widget=forms.Select, required=True,
        choices=CLM.YES_NO_SOMETIMES
    )
    gender_participate = forms.ChoiceField(
        label=_(
            "Did both girls and boys in the same family participate in the class and have access to the phone/device?"),
        widget=forms.Select, required=True,
        choices=CLM.YES_NO
    )
    gender_participate_explain = forms.CharField(
        label=_('Explain'),
        widget=forms.TextInput, required=False
    )
    remote_learning_engagement = forms.ChoiceField(
        label=_("Frequency of Child Engagement in remote learning?"),
        widget=forms.Select, required=True,
        choices=CLM.PERCENT
    )
    meet_learning_outcomes = forms.ChoiceField(
        label=_("How well did the child meet the learning outcomes?"),
        widget=forms.Select, required=True,
        choices=CLM.PERCENT
    )
    parent_learning_support_rate = forms.ChoiceField(
        label=_(
            "How do you rate the parents learning support provided to the child through this Remote learning phase?"),
        widget=forms.Select, required=True,
        choices=CLM.PERCENT
    )
    covid_message = forms.ChoiceField(
        label=_(
            "Has the child directly been reached with awareness directlymessaging on Covid-19 and prevention measures?"),
        widget=forms.Select, required=True,
        choices=CLM.YES_NO
    )
    covid_message_how_often = forms.ChoiceField(
        label=_("How often?"),
        widget=forms.Select, required=False,
        choices=CLM.HOW_OFTEN
    )

    covid_parents_message = forms.ChoiceField(
        label=_("Has the parents directly been reached with awareness messaging on Covid-19 and prevention measures?"),
        widget=forms.Select, required=True,
        choices=CLM.YES_NO
    )
    covid_parents_message_how_often = forms.ChoiceField(
        label=_("How often?"),
        widget=forms.Select, required=False,
        choices=CLM.HOW_OFTEN
    )

    follow_up_done = forms.ChoiceField(
        label=_("Was any follow-up done to ensure messages were well received, understood and adopted?"),
        widget=forms.Select, required=True,
        choices=CLM.YES_NO
    )
    follow_up_done_with_who = forms.ChoiceField(
        label=_("With who child and/or caregiver?"),
        widget=forms.Select, required=False,
        choices=CLM.WITH_WHO
    )

    def __init__(self, *args, **kwargs):
        super(CBECEMonitoringQuestionerForm, self).__init__(*args, **kwargs)

        instance = kwargs['instance']

        self.helper = FormHelper()
        self.helper.form_show_labels = True
        self.helper.form_action = reverse('clm:cbece_monitoring_questioner', kwargs={'pk': instance.id})
        self.helper.layout = Layout(
            Fieldset(
                None,
                Div(HTML('<span>A</span>'), css_class='block_tag'),

                Div(
                    HTML('<span class="badge badge-default">1</span>'),
                    Div('basic_stationery', css_class='col-md-3'),
                    css_class='row',
                ),
                Div(
                    HTML('<span class="badge badge-default">2</span>'),
                    Div('remote_learning', css_class='col-md-3'),
                    HTML('<span class="badge badge-default" id="span_remote_learning_reasons_not_engaged">2.1</span>'),
                    Div('remote_learning_reasons_not_engaged', css_class='col-md-3'),
                    HTML('<span class="badge badge-default" id="span_reasons_not_engaged_other">2.2</span>'),
                    Div('reasons_not_engaged_other', css_class='col-md-3'),
                    css_class='row',
                ),
                Div(
                    HTML('<span class="badge badge-default">3</span>'),
                    Div('reliable_internet', css_class='col-md-3'),
                    css_class='row',
                ),
                Div(
                    HTML('<span class="badge badge-default">4</span>'),
                    Div('gender_participate', css_class='col-md-3'),
                    HTML('<span class="badge badge-default" id="span_gender_participate_explain">4.1</span>'),
                    Div('gender_participate_explain', css_class='col-md-3'),
                    css_class='row',
                ),
                Div(
                    HTML('<span class="badge badge-default">5</span>'),
                    Div('remote_learning_engagement', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">6</span>'),
                    Div('meet_learning_outcomes', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">7</span>'),
                    Div('parent_learning_support_rate', css_class='col-md-3'),
                    css_class='row',
                ),
                Div(
                    HTML('<span class="badge badge-default">8</span>'),
                    Div('covid_message', css_class='col-md-3'),
                    HTML('<span class="badge badge-default" id="span_covid_message_how_often">8.1</span>'),
                    Div('covid_message_how_often', css_class='col-md-3'),
                    css_class='row',
                ),
                Div(
                    HTML('<span class="badge badge-default">9</span>'),
                    Div('covid_parents_message', css_class='col-md-3'),
                    HTML('<span class="badge badge-default" id="span_covid_parents_message_how_often">9.1</span>'),
                    Div('covid_parents_message_how_often', css_class='col-md-3'),
                    css_class='row',
                ),
                Div(
                    HTML('<span class="badge badge-default">10</span>'),
                    Div('follow_up_done', css_class='col-md-3'),
                    HTML('<span class="badge badge-default" id="span_follow_up_done_with_who">10.1</span>'),
                    Div('follow_up_done_with_who', css_class='col-md-3'),
                    css_class='row',
                ),
                css_class='bd-callout bd-callout-warning child_data A_right_border'
            ),
            FormActions(
                Submit('save', _('Save')),
                HTML('<a class="btn btn-info" href="/clm/cbece-list/">' + _('Back to list') + '</a>'),
            )
        )

    def clean(self):
        cleaned_data = super(CBECEMonitoringQuestionerForm, self).clean()
        covid_message = cleaned_data.get("covid_message")
        covid_message_how_often = cleaned_data.get("covid_message_how_often")
        covid_parents_message = cleaned_data.get("covid_parents_message")
        covid_parents_message_how_often = cleaned_data.get("covid_parents_message_how_often")
        gender_participate = cleaned_data.get("gender_participate")
        gender_participate_explain = cleaned_data.get("gender_participate_explain")
        follow_up_done = cleaned_data.get("follow_up_done")
        follow_up_done_with_who = cleaned_data.get("follow_up_done_with_who")
        remote_learning = cleaned_data.get("remote_learning")
        remote_learning_reasons_not_engaged = cleaned_data.get("remote_learning_reasons_not_engaged")
        reasons_not_engaged_other = cleaned_data.get("reasons_not_engaged_other")

        if remote_learning == 'no':
            if not remote_learning_reasons_not_engaged:
                self.add_error('remote_learning_reasons_not_engaged', 'This field is required')

        if remote_learning_reasons_not_engaged == 'Other':
            if not reasons_not_engaged_other:
                self.add_error('reasons_not_engaged_other', 'This field is required')

        if covid_message == 'yes':
            if not covid_message_how_often:
                self.add_error('covid_message_how_often', 'This field is required')

        if covid_parents_message == 'yes':
            if not covid_parents_message_how_often:
                self.add_error('covid_parents_message_how_often', 'This field is required')

        if gender_participate == 'no':
            if not gender_participate_explain:
                self.add_error('gender_participate_explain', 'This field is required')

        if follow_up_done == 'yes':
            if not follow_up_done_with_who:
                self.add_error('follow_up_done_with_who', 'This field is required')

    def save(self, instance=None, request=None):
        instance = super(CBECEMonitoringQuestionerForm, self).save()
        instance.modified_by = request.user
        instance.save()
        messages.success(request, _('Your data has been sent successfully to the server'))


    class Meta:
        model = CBECE
        fields = (
            'basic_stationery',
            # 'pss_kit',
            'remote_learning',
            'remote_learning_reasons_not_engaged',
            'reasons_not_engaged_other',
            'reliable_internet',
            'gender_participate',
            'gender_participate_explain',
            'remote_learning_engagement',
            'meet_learning_outcomes',
            'parent_learning_support_rate',
            'covid_message',
            'covid_message_how_often',
            'covid_parents_message',
            'covid_parents_message_how_often',
            'follow_up_done',
            'follow_up_done_with_who',
        )

    class Media:
        js = (
            # 'js/validator.js',
        )

class BLNMonitoringQuestionerForm(forms.ModelForm):
    basic_stationery = forms.ChoiceField(
        label=_("Did the child receive basic stationery?"),
        widget=forms.Select, required=True,
        choices=CLM.YES_NO
    )
    pss_kit = forms.ChoiceField(
            label=_("Did the child benefit from the PSS kit?"),
            widget=forms.Select, required=True,
            choices=CLM.YES_NO
        )
    remote_learning = forms.ChoiceField(
        label=_("Was the child involved in remote learning?"),
        widget=forms.Select, required=True,
        choices=CLM.YES_NO
    )
    remote_learning_reasons_not_engaged = forms.ChoiceField(
        label=_("what other reasons for this child not being engaged?"),
        widget=forms.Select, required=False,
        choices=(
            ('', '----------'),
            ('child_relocated', _('Child relocated')),
            ('child_is_not_reachable', _('Child is not reachable')),
            ('child_did_not_fit_the_criteria', _('Child did not fit the criteria - enrolled in previous FE')),
            ('Other', _('Other')),
        ),
    )
    reasons_not_engaged_other = forms.CharField(
        label=_('Please specify'),
        widget=forms.TextInput, required=False
    )
    reliable_internet = forms.ChoiceField(
        label=_("Does the family have reliable internet service in their area during remote learning?"),
        widget=forms.Select, required=True,
        choices=CLM.YES_NO_SOMETIMES
    )
    gender_participate = forms.ChoiceField(
        label=_(
            "Did both girls and boys in the same family participate in the class and have access to the phone/device?"),
        widget=forms.Select, required=True,
        choices=CLM.YES_NO
    )
    gender_participate_explain = forms.CharField(
        label=_('Explain'),
        widget=forms.TextInput, required=False
    )
    remote_learning_engagement = forms.ChoiceField(
        label=_("Frequency of Child Engagement in remote learning?"),
        widget=forms.Select, required=True,
        choices=CLM.PERCENT
    )
    meet_learning_outcomes = forms.ChoiceField(
        label=_("How well did the child meet the learning outcomes?"),
        widget=forms.Select, required=True,
        choices=CLM.PERCENT
    )
    parent_learning_support_rate = forms.ChoiceField(
        label=_(
            "How do you rate the parents learning support provided to the child through this Remote learning phase?"),
        widget=forms.Select, required=True,
        choices=CLM.PERCENT
    )
    covid_message = forms.ChoiceField(
        label=_(
            "Has the child directly been reached with awareness directlymessaging on Covid-19 and prevention measures?"),
        widget=forms.Select, required=True,
        choices=CLM.YES_NO
    )
    covid_message_how_often = forms.ChoiceField(
        label=_("How often?"),
        widget=forms.Select, required=False,
        choices=CLM.HOW_OFTEN
    )

    covid_parents_message = forms.ChoiceField(
        label=_("Has the parents directly been reached with awareness messaging on Covid-19 and prevention measures?"),
        widget=forms.Select, required=True,
        choices=CLM.YES_NO
    )
    covid_parents_message_how_often = forms.ChoiceField(
        label=_("How often?"),
        widget=forms.Select, required=False,
        choices=CLM.HOW_OFTEN
    )

    follow_up_done = forms.ChoiceField(
        label=_("Was any follow-up done to ensure messages were well received, understood and adopted?"),
        widget=forms.Select, required=True,
        choices=CLM.YES_NO
    )
    follow_up_done_with_who = forms.ChoiceField(
        label=_("With who child and/or caregiver?"),
        widget=forms.Select, required=False,
        choices=CLM.WITH_WHO
    )

    def __init__(self, *args, **kwargs):
        super(BLNMonitoringQuestionerForm, self).__init__(*args, **kwargs)

        instance = kwargs['instance']

        self.helper = FormHelper()
        self.helper.form_show_labels = True
        self.helper.form_action = reverse('clm:bln_monitoring_questioner', kwargs={'pk': instance.id})
        self.helper.layout = Layout(
            Fieldset(
                None,
                Div(HTML('<span>A</span>'), css_class='block_tag'),

                Div(
                    HTML('<span class="badge badge-default">1</span>'),
                    Div('basic_stationery', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">2</span>'),
                    Div('pss_kit', css_class='col-md-3'),
                    css_class='row',
                ),
                Div(
                    HTML('<span class="badge badge-default">3</span>'),
                    Div('remote_learning', css_class='col-md-3'),
                    HTML('<span class="badge badge-default" id="span_remote_learning_reasons_not_engaged">3.1</span>'),
                    Div('remote_learning_reasons_not_engaged', css_class='col-md-3'),
                    HTML('<span class="badge badge-default" id="span_reasons_not_engaged_other">3.2</span>'),
                    Div('reasons_not_engaged_other', css_class='col-md-3'),
                    css_class='row',
                ),

                Div(
                    HTML('<span class="badge badge-default">4</span>'),
                    Div('reliable_internet', css_class='col-md-3'),
                    css_class='row',
                ),
                Div(
                    HTML('<span class="badge badge-default">5</span>'),
                    Div('gender_participate', css_class='col-md-3'),
                    HTML('<span class="badge badge-default" id="span_gender_participate_explain">5.1</span>'),
                    Div('gender_participate_explain', css_class='col-md-3'),
                    css_class='row',
                ),
                Div(
                    HTML('<span class="badge badge-default">6</span>'),
                    Div('remote_learning_engagement', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">7</span>'),
                    Div('meet_learning_outcomes', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">8</span>'),
                    Div('parent_learning_support_rate', css_class='col-md-3'),
                    css_class='row',
                ),
                Div(
                    HTML('<span class="badge badge-default">9</span>'),
                    Div('covid_message', css_class='col-md-3'),
                    HTML('<span class="badge badge-default" id="span_covid_message_how_often">9.1</span>'),
                    Div('covid_message_how_often', css_class='col-md-3'),
                    css_class='row',
                ),
                Div(
                    HTML('<span class="badge badge-default">10</span>'),
                    Div('covid_parents_message', css_class='col-md-3'),
                    HTML('<span class="badge badge-default" id="span_covid_parents_message_how_often">10.1</span>'),
                    Div('covid_parents_message_how_often', css_class='col-md-3'),
                    css_class='row',
                ),
                Div(
                    HTML('<span class="badge badge-default">11</span>'),
                    Div('follow_up_done', css_class='col-md-3'),
                    HTML('<span class="badge badge-default" id="span_follow_up_done_with_who">11.1</span>'),
                    Div('follow_up_done_with_who', css_class='col-md-3'),
                    css_class='row',
                ),
                css_class='bd-callout bd-callout-warning child_data A_right_border'
            ),
            FormActions(
                Submit('save', _('Save')),
                HTML('<a class="btn btn-info" href="/clm/bln-list/">' + _('Back to list') + '</a>'),
            )
        )

    def clean(self):
        cleaned_data = super(BLNMonitoringQuestionerForm, self).clean()

        covid_message = cleaned_data.get("covid_message")
        covid_message_how_often = cleaned_data.get("covid_message_how_often")
        covid_parents_message = cleaned_data.get("covid_parents_message")
        covid_parents_message_how_often = cleaned_data.get("covid_parents_message_how_often")
        gender_participate = cleaned_data.get("gender_participate")
        gender_participate_explain = cleaned_data.get("gender_participate_explain")
        follow_up_done = cleaned_data.get("follow_up_done")
        follow_up_done_with_who = cleaned_data.get("follow_up_done_with_who")
        remote_learning = cleaned_data.get("remote_learning")
        remote_learning_reasons_not_engaged = cleaned_data.get("remote_learning_reasons_not_engaged")
        reasons_not_engaged_other = cleaned_data.get("reasons_not_engaged_other")

        if remote_learning == 'no':
            if not remote_learning_reasons_not_engaged:
                self.add_error('remote_learning_reasons_not_engaged', 'This field is required')

        if remote_learning_reasons_not_engaged == 'Other':
            if not reasons_not_engaged_other:
                self.add_error('reasons_not_engaged_other', 'This field is required')


        if covid_message == 'yes':
            if not covid_message_how_often:
                self.add_error('covid_message_how_often', 'This field is required')

        if covid_parents_message == 'yes':
            if not covid_parents_message_how_often:
                self.add_error('covid_parents_message_how_often', 'This field is required')


        if gender_participate == 'no':
            if not gender_participate_explain:
                self.add_error('gender_participate_explain', 'This field is required')

        if follow_up_done == 'yes':
            if not follow_up_done_with_who:
                self.add_error('follow_up_done_with_who', 'This field is required')

    def save(self, instance=None, request=None):
        instance = super(BLNMonitoringQuestionerForm, self).save()
        instance.modified_by = request.user
        instance.save()
        messages.success(request, _('Your data has been sent successfully to the server'))


    class Meta:
        model = BLN
        fields = (
            'basic_stationery',
            'pss_kit',
            'remote_learning',
            'remote_learning_reasons_not_engaged',
            'reasons_not_engaged_other',
            'reliable_internet',
            'gender_participate',
            'gender_participate_explain',
            'remote_learning_engagement',
            'meet_learning_outcomes',
            'parent_learning_support_rate',
            'covid_message',
            'covid_message_how_often',
            'covid_parents_message',
            'covid_parents_message_how_often',
            'follow_up_done',
            'follow_up_done_with_who',
        )

    class Media:
        js = (
            # 'js/validator.js',
        )

class ABLNMonitoringQuestionerForm(forms.ModelForm):
    basic_stationery = forms.ChoiceField(
        label=_("Did the child receive basic stationery?"),
        widget=forms.Select, required=True,
        choices=CLM.YES_NO
    )
    # pss_kit = forms.ChoiceField(
    #         label=_("Did the child benefit from the PSS kit?"),
    #         widget=forms.Select, required=True,
    #         choices=CLM.YES_NO
    #     )
    remote_learning = forms.ChoiceField(
        label=_("'Was the child involved in remote learning?"),
        widget=forms.Select, required=True,
        choices=CLM.YES_NO
    )
    remote_learning_reasons_not_engaged = forms.ChoiceField(
        label=_("what other reasons for this child not being engaged?"),
        widget=forms.Select, required=False,
        choices=(
            ('', '----------'),
            ('child_relocated', _('Child relocated')),
            ('child_is_not_reachable', _('Child is not reachable')),
            ('child_did_not_fit_the_criteria', _('Child did not fit the criteria - enrolled in previous FE')),
            ('Other', _('Other')),
        ),
    )
    reasons_not_engaged_other = forms.CharField(
        label=_('Please specify'),
        widget=forms.TextInput, required=False
    )
    reliable_internet = forms.ChoiceField(
        label=_("Does the family have reliable internet service in their area during remote learning?"),
        widget=forms.Select, required=True,
        choices=CLM.YES_NO_SOMETIMES
    )
    gender_participate = forms.ChoiceField(
        label=_(
            "Did both girls and boys in the same family participate in the class and have access to the phone/device?"),
        widget=forms.Select, required=True,
        choices=CLM.YES_NO
    )
    gender_participate_explain = forms.CharField(
        label=_('Explain'),
        widget=forms.TextInput, required=False
    )
    remote_learning_engagement = forms.ChoiceField(
        label=_("Frequency of Child Engagement in remote learning?"),
        widget=forms.Select, required=True,
        choices=CLM.PERCENT
    )
    meet_learning_outcomes = forms.ChoiceField(
        label=_("How well did the child meet the learning outcomes?"),
        widget=forms.Select, required=True,
        choices=CLM.PERCENT
    )
    parent_learning_support_rate = forms.ChoiceField(
        label=_(
            "How do you rate the parents learning support provided to the child through this Remote learning phase?"),
        widget=forms.Select, required=True,
        choices=CLM.PERCENT
    )
    covid_message = forms.ChoiceField(
        label=_(
            "Has the child directly been reached with awareness directlymessaging on Covid-19 and prevention measures?"),
        widget=forms.Select, required=True,
        choices=CLM.YES_NO
    )
    covid_message_how_often = forms.ChoiceField(
        label=_("How often?"),
        widget=forms.Select, required=False,
        choices=CLM.HOW_OFTEN
    )

    covid_parents_message = forms.ChoiceField(
        label=_("Has the parents directly been reached with awareness messaging on Covid-19 and prevention measures?"),
        widget=forms.Select, required=True,
        choices=CLM.YES_NO
    )
    covid_parents_message_how_often = forms.ChoiceField(
        label=_("How often?"),
        widget=forms.Select, required=False,
        choices=CLM.HOW_OFTEN
    )

    follow_up_done = forms.ChoiceField(
        label=_("Was any follow-up done to ensure messages were well received, understood and adopted?"),
        widget=forms.Select, required=True,
        choices=CLM.YES_NO
    )
    follow_up_done_with_who = forms.ChoiceField(
        label=_("With who child and/or caregiver?"),
        widget=forms.Select, required=False,
        choices=CLM.WITH_WHO
    )

    def __init__(self, *args, **kwargs):
        super(ABLNMonitoringQuestionerForm, self).__init__(*args, **kwargs)

        instance = kwargs['instance']

        self.helper = FormHelper()
        self.helper.form_show_labels = True
        self.helper.form_action = reverse('clm:abln_monitoring_questioner', kwargs={'pk': instance.id})
        self.helper.layout = Layout(
            Fieldset(
                None,
                Div(HTML('<span>A</span>'), css_class='block_tag'),

                Div(
                    HTML('<span class="badge badge-default">1</span>'),
                    Div('basic_stationery', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">2</span>'),
                    Div('pss_kit', css_class='col-md-3'),
                    css_class='row',
                ),
                Div(
                    HTML('<span class="badge badge-default">3</span>'),
                    Div('remote_learning', css_class='col-md-3'),
                    HTML('<span class="badge badge-default" id="span_remote_learning_reasons_not_engaged">3.1</span>'),
                    Div('remote_learning_reasons_not_engaged', css_class='col-md-3'),
                    HTML('<span class="badge badge-default" id="span_reasons_not_engaged_other">3.2</span>'),
                    Div('reasons_not_engaged_other', css_class='col-md-3'),
                    css_class='row',
                ),

                Div(
                    HTML('<span class="badge badge-default">4</span>'),
                    Div('reliable_internet', css_class='col-md-3'),
                    css_class='row',
                ),
                Div(
                    HTML('<span class="badge badge-default">5</span>'),
                    Div('gender_participate', css_class='col-md-3'),
                    HTML('<span class="badge badge-default" id="span_gender_participate_explain">5.1</span>'),
                    Div('gender_participate_explain', css_class='col-md-3'),
                    css_class='row',
                ),
                Div(
                    HTML('<span class="badge badge-default">6</span>'),
                    Div('remote_learning_engagement', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">7</span>'),
                    Div('meet_learning_outcomes', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">8</span>'),
                    Div('parent_learning_support_rate', css_class='col-md-3'),
                    css_class='row',
                ),
                Div(
                    HTML('<span class="badge badge-default">9</span>'),
                    Div('covid_message', css_class='col-md-3'),
                    HTML('<span class="badge badge-default" id="span_covid_message_how_often">9.1</span>'),
                    Div('covid_message_how_often', css_class='col-md-3'),
                    css_class='row',
                ),
                Div(
                    HTML('<span class="badge badge-default">10</span>'),
                    Div('covid_parents_message', css_class='col-md-3'),
                    HTML('<span class="badge badge-default" id="span_covid_parents_message_how_often">10.1</span>'),
                    Div('covid_parents_message_how_often', css_class='col-md-3'),
                    css_class='row',
                ),
                Div(
                    HTML('<span class="badge badge-default">11</span>'),
                    Div('follow_up_done', css_class='col-md-3'),
                    HTML('<span class="badge badge-default" id="span_follow_up_done_with_who">11.1</span>'),
                    Div('follow_up_done_with_who', css_class='col-md-3'),
                    css_class='row',
                ),
                css_class='bd-callout bd-callout-warning child_data A_right_border'
            ),
            FormActions(
                Submit('save', _('Save')),
                HTML('<a class="btn btn-info" href="/clm/abln-list/">' + _('Back to list') + '</a>'),
            )
        )

    def clean(self):
        cleaned_data = super(ABLNMonitoringQuestionerForm, self).clean()

        covid_message = cleaned_data.get("covid_message")
        covid_message_how_often = cleaned_data.get("covid_message_how_often")
        covid_parents_message = cleaned_data.get("covid_parents_message")
        covid_parents_message_how_often = cleaned_data.get("covid_parents_message_how_often")
        gender_participate = cleaned_data.get("gender_participate")
        gender_participate_explain = cleaned_data.get("gender_participate_explain")
        follow_up_done = cleaned_data.get("follow_up_done")
        follow_up_done_with_who = cleaned_data.get("follow_up_done_with_who")
        remote_learning = cleaned_data.get("remote_learning")
        remote_learning_reasons_not_engaged = cleaned_data.get("remote_learning_reasons_not_engaged")
        reasons_not_engaged_other = cleaned_data.get("reasons_not_engaged_other")

        if remote_learning == 'no':
            if not remote_learning_reasons_not_engaged:
                self.add_error('remote_learning_reasons_not_engaged', 'This field is required')

        if remote_learning_reasons_not_engaged == 'Other':
            if not reasons_not_engaged_other:
                self.add_error('reasons_not_engaged_other', 'This field is required')


        if covid_message == 'yes':
            if not covid_message_how_often:
                self.add_error('covid_message_how_often', 'This field is required')

        if covid_parents_message == 'yes':
            if not covid_parents_message_how_often:
                self.add_error('covid_parents_message_how_often', 'This field is required')

        if gender_participate == 'no':
            if not gender_participate_explain:
                self.add_error('gender_participate_explain', 'This field is required')

        if follow_up_done == 'yes':
            if not follow_up_done_with_who:
                self.add_error('follow_up_done_with_who', 'This field is required')

    def save(self, instance=None, request=None):
        instance = super(ABLNMonitoringQuestionerForm, self).save()
        instance.modified_by = request.user
        instance.save()
        messages.success(request, _('Your data has been sent successfully to the server'))


    class Meta:
        model = ABLN
        fields = (
            'basic_stationery',
            'pss_kit',
            'remote_learning',
            'remote_learning_reasons_not_engaged',
            'reasons_not_engaged_other',
            'reliable_internet',
            'gender_participate',
            'gender_participate_explain',
            'remote_learning_engagement',
            'meet_learning_outcomes',
            'parent_learning_support_rate',
            'covid_message',
            'covid_message_how_often',
            'covid_parents_message',
            'covid_parents_message_how_often',
            'follow_up_done',
            'follow_up_done_with_who',
        )

    class Media:
        js = (
            # 'js/validator.js',
        )

class ABLNAssessmentForm(forms.ModelForm):
    REGISTRATION_LEVEL = (
        ('', '----------'),
        ('level_one', _('Level one')),
        ('level_two', _('Level two')),
        # ('level_three', _('Level three'))
    )
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
    learning_result = forms.ChoiceField(
        label=_('Based on the overall score, what is the recommended learning path?'),
        widget=forms.Select, required=True,
        choices=(
            ('', '----------'),
            # ('graduated_to_abln_next_level', _('Graduated to the next level')),
            ('graduated_to_abln_next_round_same_level', _('Graduated to the next round, same level')),
            ('graduated_to_abln_next_round_higher_level', _('Graduated to the next round, higher level')),
            ('referred_to_alp', _('referred to ALP')),
            ('referred_public_school', _('Referred to public school')),
            ('referred_to_tvet', _('Referred to TVET')),
            ('referred_to_ybln', _('Referred to YBLN')),
            ('dropout', _('Dropout, referral not possible')),
            ('referred_to_bln', _('Referred to BLN')),
        ),
        initial=''
    )
    barriers_single = forms.ChoiceField(
        label=_('The main barriers affecting the daily attendance and performance '
                'of the child or drop out of programme? (Select more than one if applicable)'),
        choices=CLM.BARRIERS,
        widget=forms.Select,
        required=True
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

    basic_stationery = forms.ChoiceField(
        label=_("Did the child receive basic stationery?"),
        widget=forms.Select, required=True,
        choices=CLM.YES_NO
    )
    pss_kit = forms.ChoiceField(
            label=_("Did the child benefit from the PSS kit?"),
            widget=forms.Select, required=True,
            choices=CLM.YES_NO
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
    # attended_english = forms.ChoiceField(
    #     label=_("Attended English test"),
    #     widget=forms.Select, required=True,
    #     choices=(('yes', _("Yes")), ('no', _("No"))),
    #     initial='yes'
    # )
    # modality_english = forms.MultipleChoiceField(
    #     label=_('Please indicate modality'),
    #     choices=CLM.MODALITY,
    #     widget=forms.CheckboxSelectMultiple,
    #     required=False
    # )
    # english = forms.FloatField(
    #     label=_('Results'),
    #     widget=forms.NumberInput(attrs=({'maxlength': 4})),
    #     min_value=0, required=False
    # )
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
    attended_social = forms.ChoiceField(
        label=_("Attended Social test"),
        widget=forms.Select, required=True,
        choices=(('yes', _("Yes")), ('no', _("No"))),
        initial='yes'
    )
    modality_social = forms.MultipleChoiceField(
        label=_('Please indicate modality'),
        choices=CLM.MODALITY,
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    social_emotional = forms.FloatField(
        label=_('Results'),
        widget=forms.NumberInput(attrs=({'maxlength': 4})),
        min_value=0, required=False
    )
    attended_psychomotor = forms.ChoiceField(
        label=_("Attended Psychomotor test"),
        widget=forms.Select, required=True,
        choices=(('yes', _("Yes")), ('no', _("No"))),
        initial='yes'
    )
    modality_psychomotor = forms.MultipleChoiceField(
        label=_('Please indicate modality'),
        choices=CLM.MODALITY,
        widget=forms.CheckboxSelectMultiple,
        required=False
    )
    psychomotor = forms.FloatField(
        label=_('Results'),
        widget=forms.NumberInput(attrs=({'maxlength': 4})),
        min_value=0, required=False
    )

    follow_up_type = forms.ChoiceField(
        label=_('Type of follow up'),
        widget=forms.Select, required=False,
        choices=(
            ('none', _('----------')),
            ('Phone', _('Phone Call')),
            ('House visit', _('House Visit')),
            ('Family Visit', _('Family Visit')),
        ),
        initial=''
    )
    phone_call_number = forms.IntegerField(
        label=_('Please enter the number phone calls'),
        widget=forms.NumberInput(attrs=({'maxlength': 4})),
        min_value=0, required=False
    )
    house_visit_number = forms.IntegerField(
        label=_('Please enter the number of house visits'),
        widget=forms.NumberInput(attrs=({'maxlength': 4})),
        min_value=0, required=False
    )
    family_visit_number = forms.IntegerField(
        label=_('Please enter the number parent visits'),
        widget=forms.NumberInput(attrs=({'maxlength': 4})),
        min_value=0, required=False
    )
    phone_call_follow_up_result = forms.ChoiceField(
        label=_('Result of follow up'),
        widget=forms.Select, required=False,
        choices=(
            ('child back', _('Child returned to Round')),
            ('child transfer to difficulty center', _('Child referred to specialized services')),
            ('child transfer to protection', _('Child referred to protection')),
            ('child transfer to medical', _('Child referred to Health programme')),
            ('Intensive followup', _('Follow-up with parents')),
            ('dropout', _('Dropout/No Interest')),
        ),
        initial=''
    )
    house_visit_follow_up_result = forms.ChoiceField(
        label=_('Result of follow up'),
        widget=forms.Select, required=False,
        choices=(
            ('child back', _('Child returned to Round')),
            ('child transfer to difficulty center', _('Child referred to specialized services')),
            ('child transfer to protection', _('Child referred to protection')),
            ('child transfer to medical', _('Child referred to Health programme')),
            ('Intensive followup', _('Follow-up with parents')),
            ('dropout', _('Dropout/No Interest')),
        ),
        initial=''
    )
    family_visit_follow_up_result = forms.ChoiceField(
        label=_('Result of follow up'),
        widget=forms.Select, required=False,
        choices=(
            ('child back', _('Child returned to Round')),
            ('child transfer to difficulty center', _('Child referred to specialized services')),
            ('child transfer to protection', _('Child referred to protection')),
            ('child transfer to medical', _('Child referred to Health programme')),
            ('Intensive followup', _('Follow-up with parents')),
            ('dropout', _('Dropout/No Interest')),
        ),
        initial=''
    )
    cp_referral = forms.ChoiceField(
        label=_("CP Followup"),
        widget=forms.Select, required=True,
        choices=(
            ('', '----------'),
            ('yes', _("Yes")),
            ('no', _("No")))
    )
    pss_session_attended = forms.ChoiceField(
        label=_("Attended PSS Session"),
        widget=forms.Select, required=True,
        choices=(('yes', _("Yes")), ('no', _("No")))
    )
    pss_session_number = forms.IntegerField(
        label=_('Please enter the number of sessions'),
        widget=forms.NumberInput(attrs=({'maxlength': 4})),
        min_value=0, required=False
    )
    pss_session_modality = forms.MultipleChoiceField(
        label=_('Please indicate modality'),
        choices=CLM.SESSION_MODALITY,
        widget=forms.CheckboxSelectMultiple,
        required=False
    )
    pss_parent_attended = forms.ChoiceField(
        label=_("Parent who attended the parents meeting"),
        widget=forms.Select, required=False,
        choices=(
            ('', '----------'),
            ('mother', _('Mother')),
            ('father', _('Father')),
            ('other', _('Other')),
        )
    )
    pss_parent_attended_other = forms.CharField(
        label=_('Please specify'),
        widget=forms.TextInput, required=False
    )
    covid_session_attended = forms.ChoiceField(
        label=_("Attended covid Session"),
        widget=forms.Select, required=True,
        choices=(('yes', _("Yes")), ('no', _("No")))
    )
    covid_session_number = forms.IntegerField(
        label=_('Please enter the number of sessions'),
        widget=forms.NumberInput(attrs=({'maxlength': 4})),
        min_value=0, required=False
    )
    covid_session_modality = forms.MultipleChoiceField(
        label=_('Please indicate modality'),
        choices=CLM.SESSION_MODALITY,
        widget=forms.CheckboxSelectMultiple,
        required=False
    )
    covid_parent_attended = forms.ChoiceField(
        label=_("Parent who attended the parents meeting"),
        widget=forms.Select, required=False,
        choices=(
            ('', '----------'),
            ('mother', _('Mother')),
            ('father', _('Father')),
            ('other', _('Other')),
        )
    )
    covid_parent_attended_other = forms.CharField(
        label=_('Please specify'),
        widget=forms.TextInput, required=False
    )
    followup_session_attended = forms.ChoiceField(
        label=_("Attended followup Session"),
        widget=forms.Select, required=True,
        choices=(('yes', _("Yes")), ('no', _("No")))
    )
    followup_session_number = forms.IntegerField(
        label=_('Please enter the number of sessions'),
        widget=forms.NumberInput(attrs=({'maxlength': 4})),
        min_value=0, required=False
    )

    followup_session_modality = forms.MultipleChoiceField(
        label=_('Please indicate modality'),
        choices=CLM.SESSION_MODALITY,
        widget=forms.CheckboxSelectMultiple,
        required=False
    )
    followup_parent_attended = forms.ChoiceField(
        label=_("Parent who attended the parents meeting"),
        widget=forms.Select, required=False,
        choices=(
            ('', '----------'),
            ('mother', _('Mother')),
            ('father', _('Father')),
            ('other', _('Other')),
        )
    )
    followup_parent_attended_other = forms.CharField(
        label=_('Please specify'),
        widget=forms.TextInput, required=False
    )
    child_health_examed = forms.ChoiceField(
        label=_("Did the child receive health exam"),
        widget=forms.Select, required=False,
        choices=(('yes', _("Yes")), ('no', _("No"))),
        initial='yes'
    )
    child_health_concern = forms.ChoiceField(
        label=_("Anything to worry about"),
        widget=forms.Select, required=False,
        choices=(('yes', _("Yes")), ('no', _("No"))),
        initial='yes'
    )

    registration_level = forms.ChoiceField(
        label=_("Registration level"),
        widget=forms.Select, required=True,
        choices=REGISTRATION_LEVEL
    )

    clm_type = forms.CharField(widget=forms.HiddenInput, required=False)

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(ABLNAssessmentForm, self).__init__(*args, **kwargs)

        post_test = ''
        post_test_button = ' btn-outline-secondary disabled'
        instance = kwargs['instance'] if 'instance' in kwargs else ''
        self.fields['clm_type'].initial = 'ABLN'

        display_assessment = ''
        form_action = reverse('clm:abln_post_assessment', kwargs={'pk': instance.id})

        if instance.post_test:
            post_test_button = ' btn-outline-success '
            post_test = instance.assessment_form(
                stage='post_test',
                assessment_slug='abln_post_test',
                callback=self.request.build_absolute_uri(
                    reverse('clm:abln_post_assessment', kwargs={'pk': instance.id}))
            )

        self.helper = FormHelper()
        self.helper.form_show_labels = True
        self.helper.form_action = form_action
        self.helper.layout = Layout(
            Fieldset(
                None,
                Div(
                    HTML('<h4 id="alternatives-to-hidden-labels">' + _('Assessment data') + '</h4>'),
                ),
            ),
            Fieldset(
                None,
                Div(
                    HTML('<span>A</span>'), css_class='block_tag'),
                Div(
                    HTML('<h4 id="alternatives-to-hidden-labels">' + _('School evaluation') + '</h4>')
                ),

                Div(
                    Div('registration_level', css_class='col-md-3 d-none'),
                    css_class='row',
                ),
                Div(
                    HTML('<span class="badge badge-default">1</span>'),
                    Div('participation', css_class='col-md-2'),
                    HTML('<span class="badge badge-default" id="span_barriers_single">1.1</span>'),
                    Div('barriers_single', css_class='col-md-2'),
                    HTML('<span class="badge badge-default" id="span_barriers_other">1.2</span>'),
                    Div('barriers_other', css_class='col-md-2'),
                    css_class='row',
                ),
                Div(
                    HTML('<span class="badge badge-default">2</span>'),
                    Div('test_done', css_class='col-md-4'),
                    HTML('<span class="badge badge-default" id="span_round_complete">2.1</span>'),
                    Div('round_complete', css_class='col-md-4'),
                    css_class='row',
                ),
                Div(
                    HTML('<span class="badge badge-default">3</span>'),
                    Div('basic_stationery', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">4</span>'),
                    Div('pss_kit', css_class='col-md-3'),
                    css_class='row',
                ),
                Div(
                    HTML('<span class="badge badge-default">5</span>'),
                    Div('learning_result', css_class='col-md-4'),
                    HTML('<span class="badge badge-default">6</span>'),
                    Div('cp_referral', css_class='col-md-4'),
                    css_class='row',
                ),
                Div(
                    HTML('<span class="badge badge-default">6</span>'),
                    Div('attended_arabic', css_class='col-md-2'),
                    HTML('<span class="badge badge-default" id="span_modality_arabic">6.1</span>'),
                    Div('modality_arabic', css_class='col-md-2  multiple-checbkoxes'),
                    HTML('<span class="badge badge-default" id="span_arabic">6.2</span>'),
                    Div('arabic', css_class='col-md-2'),
                    css_class='row grades',
                ),
                # Div(
                #     HTML('<span class="badge badge-default">7</span>'),
                #     Div('attended_english', css_class='col-md-2'),
                #     HTML('<span class="badge badge-default" id="span_modality_english">7.1</span>'),
                #     Div('modality_english', css_class='col-md-2  multiple-checbkoxes'),
                #     HTML('<span class="badge badge-default" id="span_english">7.2</span>'),
                #     Div('english', css_class='col-md-2'),
                #     css_class='row grades',
                # ),
                Div(
                    HTML('<span class="badge badge-default">7</span>'),
                    Div('attended_math', css_class='col-md-2'),
                    HTML('<span class="badge badge-default" id="span_modality_math">7.1</span>'),
                    Div('modality_math', css_class='col-md-2  multiple-checbkoxes'),
                    HTML('<span class="badge badge-default" id="span_math">7.2</span>'),
                    Div('math', css_class='col-md-2'),
                    css_class='row grades',
                ),

                Div(
                    HTML('<span class="badge badge-default">8</span>'),
                    Div('attended_social', css_class='col-md-2'),
                    HTML('<span class="badge badge-default" id="span_modality_social">7.1</span>'),
                    Div('modality_social', css_class='col-md-2  multiple-checbkoxes'),
                    HTML('<span class="badge badge-default" id="span_social_emotional">7.2</span>'),
                    Div('social_emotional', css_class='col-md-2'),
                    css_class='row grades',
                ),

                Div(
                    HTML('<span class="badge badge-default">9</span>'),
                    Div('attended_psychomotor', css_class='col-md-2'),
                    HTML('<span class="badge badge-default" id="span_modality_psychomotor">9.1</span>'),
                    Div('modality_psychomotor', css_class='col-md-2  multiple-checbkoxes'),
                    HTML('<span class="badge badge-default" id="span_psychomotor">9.2</span>'),
                    Div('psychomotor', css_class='col-md-2'),
                    css_class='row grades',
                ),


                css_class='bd-callout bd-callout-warning A_right_border'
            ),
            Fieldset(
                None,
                Div(
                    HTML('<span>B</span>'), css_class='block_tag'),
                Div(
                    HTML('<h4 id="alternatives-to-hidden-labels">' + _('Follow up') + '</h4>')
                ),
                Div(
                    HTML('<span class="badge badge-default">1</span>'),
                    Div('phone_call_number', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">1.1</span>'),
                    Div('phone_call_follow_up_result', css_class='col-md-3'),
                    css_class='row'
                ),
                Div(
                    HTML('<span class="badge badge-default">2</span>'),
                    Div('house_visit_number', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">2.1</span>'),
                    Div('house_visit_follow_up_result', css_class='col-md-3'),
                    css_class='row'
                ),
                Div(
                    HTML('<span class="badge badge-default">3</span>'),
                    Div('family_visit_number', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">3.1</span>'),
                    Div('family_visit_follow_up_result', css_class='col-md-3'),
                    css_class='row'
                ),
                id='follow_up',
                css_class='bd-callout bd-callout-warning B_right_border'
            ),

            Fieldset(
                None,
                Div(
                    HTML('<span>C</span>'), css_class='block_tag'),
                None,
                Div(
                    HTML('<h4 id="alternatives-to-hidden-labels">' + _('Parents Meeting and Health Exam') + '</h4>')
                ),
                Div(
                    HTML('<span class="badge badge-default">1</span>'),
                    Div('parent_attended_visits', css_class='col-md-3'),
                    # HTML('<span class="badge badge-default">2</span>'),
                    # Div('visits_number', css_class='col-md-4'),
                    css_class='row',
                ),

                Div(
                    HTML('<span class="badge badge-default">2</span>'),
                    Div('pss_session_attended', css_class='col-md-2'),
                    HTML('<span class="badge badge-default" id="span_pss_session_modality">2.1</span>'),
                    Div('pss_session_modality', css_class='col-md-2 multiple-checbkoxes'),
                    HTML('<span class="badge badge-default" id="span_pss_session_number">2.2</span>'),
                    Div('pss_session_number', css_class='col-md-2'),
                    HTML('<span class="badge badge-default" id="span_pss_parent_attended">2.3</span>'),
                    Div('pss_parent_attended', css_class='col-md-2'),
                    HTML('<span class="badge badge-default" id="span_pss_parent_attended_other">2.4</span>'),
                    Div('pss_parent_attended_other', css_class='col-md-2'),
                    css_class='row parent_visits',
                ),
                Div(
                    HTML('<span class="badge badge-default">3</span>'),
                    Div('covid_session_attended', css_class='col-md-2'),
                    HTML('<span class="badge badge-default" id="span_covid_session_modality">3.1</span>'),
                    Div('covid_session_modality', css_class='col-md-2 multiple-checbkoxes'),
                    HTML('<span class="badge badge-default" id="span_covid_session_number">3.2</span>'),
                    Div('covid_session_number', css_class='col-md-2'),
                    HTML('<span class="badge badge-default" id="span_covid_parent_attended">3.3</span>'),
                    Div('covid_parent_attended', css_class='col-md-2'),
                    HTML('<span class="badge badge-default" id="span_covid_parent_attended_other">3.4</span>'),
                    Div('covid_parent_attended_other', css_class='col-md-2'),
                    css_class='row parent_visits',
                ),
                Div(
                    HTML('<span class="badge badge-default">4</span>'),
                    Div('followup_session_attended', css_class='col-md-2'),
                    HTML('<span class="badge badge-default" id="span_followup_session_modality">4.1</span>'),
                    Div('followup_session_modality', css_class='col-md-2 multiple-checbkoxes'),
                    HTML('<span class="badge badge-default" id="span_followup_session_number">4.2</span>'),
                    Div('followup_session_number', css_class='col-md-2'),
                    HTML('<span class="badge badge-default" id="span_followup_parent_attended">4.3</span>'),
                    Div('followup_parent_attended', css_class='col-md-2'),
                    HTML('<span class="badge badge-default" id="span_followup_parent_attended_other">4.4</span>'),
                    Div('followup_parent_attended_other', css_class='col-md-2'),
                    css_class='row parent_visits',
                ),

                # Div(
                #     HTML('<span class="badge badge-default">4</span>'),
                #     Div('child_health_examed', css_class='col-md-4'),
                #     HTML('<span class="badge badge-default">5</span>'),
                #     Div('child_health_concern', css_class='col-md-4'),
                #     css_class='row',
                # ),
                id= 'visits',
                css_class='bd-callout bd-callout-warning C_right_border'+ display_assessment,
            ),
            FormActions(
                Submit('save', _('Save'), css_class='col-md-2'),
                HTML('<a class="btn btn-info cancel-button" href="/clm/abln-list/" translation="' +
                     _('Are you sure you want to cancel this registration?') + '">' + _('Back to list') + '</a>'),
            )
        )

    def clean(self):
        cleaned_data = super(ABLNAssessmentForm, self).clean()

        attended_arabic = cleaned_data.get("attended_arabic")
        modality_arabic = cleaned_data.get("modality_arabic")
        arabic = cleaned_data.get("arabic")

        # attended_english = cleaned_data.get("attended_english")
        # modality_english = cleaned_data.get("modality_english")
        # english = cleaned_data.get("english")

        attended_psychomotor = cleaned_data.get("attended_psychomotor")
        modality_psychomotor = cleaned_data.get("modality_psychomotor")
        psychomotor = cleaned_data.get("psychomotor")

        attended_math = cleaned_data.get("attended_math")
        modality_math = cleaned_data.get("modality_math")
        math = cleaned_data.get("math")

        attended_social = cleaned_data.get("attended_social")
        modality_social = cleaned_data.get("modality_social")
        social_emotional = cleaned_data.get("social_emotional")

        learning_result = cleaned_data.get("learning_result")
        barriers_single = cleaned_data.get("barriers_single")
        barriers_other = cleaned_data.get("barriers_other")

        test_done = cleaned_data.get("test_done")
        round_complete = cleaned_data.get("round_complete")

        if test_done == 'yes':
            if not round_complete:
                self.add_error('round_complete', 'This field is required')

        if learning_result != 'no_absence':
            if not barriers_single:
                self.add_error('barriers_single', 'This field is required')

        if barriers_single == 'other':
            if not barriers_other:
                self.add_error('barriers_other', 'This field is required')
        if test_done =='yes':
            if attended_arabic == 'yes':
                if not modality_arabic:
                    self.add_error('modality_arabic', 'This field is required')
                if arabic is None:
                    self.add_error('arabic', 'This field is required')

            # if attended_english == 'yes':
            #     if not modality_english:
            #         self.add_error('modality_english', 'This field is required')
            #     if english is None:
            #         self.add_error('english', 'This field is required')

            if attended_psychomotor == 'yes':
                if not modality_psychomotor:
                    self.add_error('modality_psychomotor', 'This field is required')
                if psychomotor is None:
                    self.add_error('psychomotor', 'This field is required')

            if attended_math == 'yes':
                if not modality_math:
                    self.add_error('modality_math', 'This field is required')
                if math is None:
                    self.add_error('math', 'This field is required')

            if attended_social == 'yes':
                if not modality_social:
                    self.add_error('modality_social', 'This field is required')
                if social_emotional is None:
                    self.add_error('social_emotional', 'This field is required')

            # grades Max Value validation
            registration_level = cleaned_data.get("registration_level")

            if registration_level == 'level_one':
                if arabic > 44:
                    self.add_error('arabic', 'This value is greater that 44')
                # if english > 36:
                #     self.add_error('english', 'This value is greater that 36')
                if math > 18:
                    self.add_error('math', 'This value is greater that 18')
                if social_emotional > 24:
                    self.add_error('social_emotional', 'This value is greater that 24')
                if psychomotor > 8:
                    self.add_error('psychomotor', 'This value is greater that 8')
            else:
                if arabic > 52:
                    self.add_error('arabic', 'This value is greater that 52')
                # if english > 56:
                #     self.add_error('english', 'This value is greater that 56')
                if math > 34:
                    self.add_error('math', 'This value is greater that 34')
                if social_emotional > 24:
                    self.add_error('social_emotional', 'This value is greater that 24')
                if psychomotor > 8:
                    self.add_error('psychomotor', 'This value is greater that 8')


    def save(self, instance=None, request=None):
        instance = super(ABLNAssessmentForm, self).save()
        # instance = super(ABLNAssessmentForm, self).save(request=request, instance=instance, serializer=ABLNSerializer)

        instance.modified_by = request.user
        # instance.pss_session_modality = request.POST.getlist('pss_session_modality')
        # instance.covid_session_modality = request.POST.getlist('covid_session_modality')
        # instance.followup_session_modality = request.POST.getlist('followup_session_modality')

        instance.post_test = {
                "ABLN_ASSESSMENT/attended_arabic": request.POST.get('attended_arabic'),
                "ABLN_ASSESSMENT/modality_arabic": request.POST.getlist('modality_arabic'),
                "ABLN_ASSESSMENT/arabic": request.POST.get('arabic'),

                # "ABLN_ASSESSMENT/attended_english": request.POST.get('attended_english'),
                # "ABLN_ASSESSMENT/modality_english": request.POST.getlist('modality_english'),
                # "ABLN_ASSESSMENT/english": request.POST.get('english'),

                "ABLN_ASSESSMENT/attended_psychomotor": request.POST.get('attended_psychomotor'),
                "ABLN_ASSESSMENT/modality_psychomotor": request.POST.getlist('modality_psychomotor'),
                "ABLN_ASSESSMENT/psychomotor": request.POST.get('psychomotor'),

                "ABLN_ASSESSMENT/attended_math": request.POST.get('attended_math'),
                "ABLN_ASSESSMENT/modality_math": request.POST.getlist('modality_math'),
                "ABLN_ASSESSMENT/math": request.POST.get('math'),

                "ABLN_ASSESSMENT/attended_social": request.POST.get('attended_social'),
                "ABLN_ASSESSMENT/modality_social": request.POST.getlist('modality_social'),
                "ABLN_ASSESSMENT/social_emotional": request.POST.get('social_emotional'),
            }

        instance.save()
        messages.success(request, _('Your data has been sent successfully to the server'))

    class Meta:
        model = ABLN
        fields = (
            'participation',
            'barriers_single',
            'barriers_other',
            'test_done',
            'round_complete',
            'basic_stationery',
            'pss_kit',
            'learning_result',
            'phone_call_number',
            'house_visit_number',
            'family_visit_number',
            'phone_call_follow_up_result' ,
            'house_visit_follow_up_result' ,
            'family_visit_follow_up_result' ,
            'parent_attended_visits',
            'pss_session_attended',
            'pss_session_number',
            'pss_session_modality',
            'pss_parent_attended',
            'pss_parent_attended_other',
            'covid_session_attended',
            'covid_session_number',
            'covid_session_modality',
            'covid_parent_attended',
            'covid_parent_attended_other',
            'followup_session_attended',
            'followup_session_number',
            'followup_session_modality',
            'followup_parent_attended_other',
            'followup_parent_attended',
            'cp_referral',
        )

class BLNAssessmentForm(forms.ModelForm):
    REGISTRATION_LEVEL = (
        ('', '----------'),
        ('level_one', _('Level one')),
        ('level_two', _('Level two')),
        ('level_three', _('Level three'))
    )
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
    learning_result = forms.ChoiceField(
        label=_('Based on the overall score, what is the recommended learning path?'),
        widget=forms.Select, required=True,
        choices=(
            ('', '----------'),
            # ('graduated_to_bln_next_level', _('Graduated to the next level')),
            ('graduated_to_bln_next_round_same_level', _('Graduated to the next round, same level')),
            ('graduated_to_bln_next_round_higher_level', _('Graduated to the next round, higher level')),
            ('referred_to_alp', _('referred to ALP')),
            ('referred_public_school', _('Referred to public school')),
            ('referred_to_tvet', _('Referred to TVET')),
            ('referred_to_ybln', _('Referred to YBLN')),
            ('dropout', _('Dropout, referral not possible')),
        ),
        initial=''
    )
    barriers_single = forms.ChoiceField(
        label=_('The main barriers affecting the daily attendance and performance '
                'of the child or drop out of programme? (Select more than one if applicable)'),
        choices=CLM.BARRIERS,
        widget=forms.Select,
        required=True
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

    basic_stationery = forms.ChoiceField(
        label=_("Did the child receive basic stationery?"),
        widget=forms.Select, required=True,
        choices=CLM.YES_NO
    )
    pss_kit = forms.ChoiceField(
            label=_("Did the child benefit from the PSS kit?"),
            widget=forms.Select, required=True,
            choices=CLM.YES_NO
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
    attended_english = forms.ChoiceField(
        label=_("Attended English test"),
        widget=forms.Select, required=True,
        choices=(('yes', _("Yes")), ('no', _("No"))),
        initial='yes'
    )
    modality_english = forms.MultipleChoiceField(
        label=_('Please indicate modality'),
        choices=CLM.MODALITY,
        widget=forms.CheckboxSelectMultiple,
        required=False
    )
    english = forms.FloatField(
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
    attended_social = forms.ChoiceField(
        label=_("Attended Social test"),
        widget=forms.Select, required=True,
        choices=(('yes', _("Yes")), ('no', _("No"))),
        initial='yes'
    )
    modality_social = forms.MultipleChoiceField(
        label=_('Please indicate modality'),
        choices=CLM.MODALITY,
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    social_emotional = forms.FloatField(
        label=_('Results'),
        widget=forms.NumberInput(attrs=({'maxlength': 4})),
        min_value=0, required=False
    )
    attended_psychomotor = forms.ChoiceField(
        label=_("Attended Psychomotor test"),
        widget=forms.Select, required=True,
        choices=(('yes', _("Yes")), ('no', _("No"))),
        initial='yes'
    )
    modality_psychomotor = forms.MultipleChoiceField(
        label=_('Please indicate modality'),
        choices=CLM.MODALITY,
        widget=forms.CheckboxSelectMultiple,
        required=False
    )
    psychomotor = forms.FloatField(
        label=_('Results'),
        widget=forms.NumberInput(attrs=({'maxlength': 4})),
        min_value=0, required=False
    )

    follow_up_type = forms.ChoiceField(
        label=_('Type of follow up'),
        widget=forms.Select, required=False,
        choices=(
            ('none', _('----------')),
            ('Phone', _('Phone Call')),
            ('House visit', _('House Visit')),
            ('Family Visit', _('Family Visit')),
        ),
        initial=''
    )
    phone_call_number = forms.IntegerField(
        label=_('Please enter the number phone calls'),
        widget=forms.NumberInput(attrs=({'maxlength': 4})),
        min_value=0, required=False
    )
    house_visit_number = forms.IntegerField(
        label=_('Please enter the number of house visits'),
        widget=forms.NumberInput(attrs=({'maxlength': 4})),
        min_value=0, required=False
    )
    family_visit_number = forms.IntegerField(
        label=_('Please enter the number parent visits'),
        widget=forms.NumberInput(attrs=({'maxlength': 4})),
        min_value=0, required=False
    )
    phone_call_follow_up_result = forms.ChoiceField(
        label=_('Result of follow up'),
        widget=forms.Select, required=False,
        choices=(
            ('child back', _('Child returned to Round')),
            ('child transfer to difficulty center', _('Child referred to specialized services')),
            ('child transfer to protection', _('Child referred to protection')),
            ('child transfer to medical', _('Child referred to Health programme')),
            ('Intensive followup', _('Follow-up with parents')),
            ('dropout', _('Dropout/No Interest')),
        ),
        initial=''
    )
    house_visit_follow_up_result = forms.ChoiceField(
        label=_('Result of follow up'),
        widget=forms.Select, required=False,
        choices=(
            ('child back', _('Child returned to Round')),
            ('child transfer to difficulty center', _('Child referred to specialized services')),
            ('child transfer to protection', _('Child referred to protection')),
            ('child transfer to medical', _('Child referred to Health programme')),
            ('Intensive followup', _('Follow-up with parents')),
            ('dropout', _('Dropout/No Interest')),
        ),
        initial=''
    )
    family_visit_follow_up_result = forms.ChoiceField(
        label=_('Result of follow up'),
        widget=forms.Select, required=False,
        choices=(
            ('child back', _('Child returned to Round')),
            ('child transfer to difficulty center', _('Child referred to specialized services')),
            ('child transfer to protection', _('Child referred to protection')),
            ('child transfer to medical', _('Child referred to Health programme')),
            ('Intensive followup', _('Follow-up with parents')),
            ('dropout', _('Dropout/No Interest')),
        ),
        initial=''
    )
    parent_attended_visits = forms.ChoiceField(
        label=_("Parents attended parents meeting"),
        widget=forms.Select, required=False,
        choices=(('yes', _("Yes")), ('no', _("No"))),
        initial='yes'
    )
    cp_referral = forms.ChoiceField(
        label=_("CP Followup"),
        widget=forms.Select, required=True,
        choices=(
            ('', '----------'),
            ('yes', _("Yes")),
            ('no', _("No")))
    )
    pss_session_attended = forms.ChoiceField(
        label=_("Attended PSS Session"),
        widget=forms.Select, required=True,
        choices=(('yes', _("Yes")), ('no', _("No")))
    )
    pss_session_number = forms.IntegerField(
        label=_('Please enter the number of sessions'),
        widget=forms.NumberInput(attrs=({'maxlength': 4})),
        min_value=0, required=False
    )
    pss_session_modality = forms.MultipleChoiceField(
        label=_('Please indicate modality'),
        choices=CLM.SESSION_MODALITY,
        widget=forms.CheckboxSelectMultiple,
        required=False
    )
    pss_parent_attended = forms.ChoiceField(
        label=_("Parent who attended the parents meeting"),
        widget=forms.Select, required=False,
        choices=(
            ('', '----------'),
            ('mother', _('Mother')),
            ('father', _('Father')),
            ('other', _('Other')),
        )
    )
    pss_parent_attended_other = forms.CharField(
        label=_('Please specify'),
        widget=forms.TextInput, required=False
    )
    covid_session_attended = forms.ChoiceField(
        label=_("Attended covid Session"),
        widget=forms.Select, required=True,
        choices=(('yes', _("Yes")), ('no', _("No")))
    )
    covid_session_number = forms.IntegerField(
        label=_('Please enter the number of sessions'),
        widget=forms.NumberInput(attrs=({'maxlength': 4})),
        min_value=0, required=False
    )
    covid_session_modality = forms.MultipleChoiceField(
        label=_('Please indicate modality'),
        choices=CLM.SESSION_MODALITY,
        widget=forms.CheckboxSelectMultiple,
        required=False
    )
    covid_parent_attended = forms.ChoiceField(
        label=_("Parent who attended the parents meeting"),
        widget=forms.Select, required=False,
        choices=(
            ('', '----------'),
            ('mother', _('Mother')),
            ('father', _('Father')),
            ('other', _('Other')),
        )
    )
    covid_parent_attended_other = forms.CharField(
        label=_('Please specify'),
        widget=forms.TextInput, required=False
    )
    followup_session_attended = forms.ChoiceField(
        label=_("Attended followup Session"),
        widget=forms.Select, required=True,
        choices=(('yes', _("Yes")), ('no', _("No")))
    )
    followup_session_number = forms.IntegerField(
        label=_('Please enter the number of sessions'),
        widget=forms.NumberInput(attrs=({'maxlength': 4})),
        min_value=0, required=False
    )

    followup_session_modality = forms.MultipleChoiceField(
        label=_('Please indicate modality'),
        choices=CLM.SESSION_MODALITY,
        widget=forms.CheckboxSelectMultiple,
        required=False
    )
    followup_parent_attended = forms.ChoiceField(
        label=_("Parent who attended the parents meeting"),
        widget=forms.Select, required=False,
        choices=(
            ('', '----------'),
            ('mother', _('Mother')),
            ('father', _('Father')),
            ('other', _('Other')),
        )
    )
    followup_parent_attended_other = forms.CharField(
        label=_('Please specify'),
        widget=forms.TextInput, required=False
    )
    child_health_examed = forms.ChoiceField(
        label=_("Did the child receive health exam"),
        widget=forms.Select, required=False,
        choices=(('yes', _("Yes")), ('no', _("No"))),
        initial='yes'
    )
    child_health_concern = forms.ChoiceField(
        label=_("Anything to worry about"),
        widget=forms.Select, required=False,
        choices=(('yes', _("Yes")), ('no', _("No"))),
        initial='yes'
    )

    registration_level = forms.ChoiceField(
        label=_("Registration level"),
        widget=forms.Select, required=True,
        choices=REGISTRATION_LEVEL
    )

    clm_type = forms.CharField(widget=forms.HiddenInput, required=False)


    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(BLNAssessmentForm, self).__init__(*args, **kwargs)

        post_test = ''
        post_test_button = ' btn-outline-secondary disabled'
        instance = kwargs['instance'] if 'instance' in kwargs else ''
        self.fields['clm_type'].initial = 'BLN'

        display_assessment = ''
        form_action = reverse('clm:bln_post_assessment', kwargs={'pk': instance.id})

        if instance.post_test:
            post_test_button = ' btn-outline-success '
            post_test = instance.assessment_form(
                stage='post_test',
                assessment_slug='bln_post_test',
                callback=self.request.build_absolute_uri(
                    reverse('clm:bln_post_assessment', kwargs={'pk': instance.id}))
            )

        self.helper = FormHelper()
        self.helper.form_show_labels = True
        self.helper.form_action = form_action
        self.helper.layout = Layout(
            Fieldset(
                None,
                Div(
                    HTML('<h4 id="alternatives-to-hidden-labels">' + _('Assessment data') + '</h4>'),
                ),
            ),
            Fieldset(
                None,
                Div(
                    HTML('<span>A</span>'), css_class='block_tag'),
                Div(
                    HTML('<h4 id="alternatives-to-hidden-labels">' + _('School evaluation') + '</h4>')
                ),
                Div(
                    Div('registration_level', css_class='col-md-3 d-none'),
                    css_class='row',
                ),
                Div(
                    HTML('<span class="badge badge-default">1</span>'),
                    Div('participation', css_class='col-md-2'),
                    HTML('<span class="badge badge-default" id="span_barriers_single">1.1</span>'),
                    Div('barriers_single', css_class='col-md-2'),
                    HTML('<span class="badge badge-default" id="span_barriers_other">1.2</span>'),
                    Div('barriers_other', css_class='col-md-2'),
                    css_class='row',
                ),
                Div(
                    HTML('<span class="badge badge-default">2</span>'),
                    Div('test_done', css_class='col-md-4'),
                    HTML('<span class="badge badge-default" id="span_round_complete">2.1</span>'),
                    Div('round_complete', css_class='col-md-4'),
                    css_class='row',
                ),
                Div(
                    HTML('<span class="badge badge-default">3</span>'),
                    Div('basic_stationery', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">4</span>'),
                    Div('pss_kit', css_class='col-md-3'),
                    css_class='row',
                ),
                Div(
                    HTML('<span class="badge badge-default">5</span>'),
                    Div('learning_result', css_class='col-md-4'),
                    HTML('<span class="badge badge-default">6</span>'),
                    Div('cp_referral', css_class='col-md-3'),
                    css_class='row',
                ),
                Div(
                    HTML('<span class="badge badge-default">6</span>'),
                    Div('attended_arabic', css_class='col-md-2'),
                    HTML('<span class="badge badge-default" id="span_modality_arabic">6.1</span>'),
                    Div('modality_arabic', css_class='col-md-2  multiple-checbkoxes'),
                    HTML('<span class="badge badge-default" id="span_arabic">6.2</span>'),
                    Div('arabic', css_class='col-md-2'),
                    css_class='row grades',
                ),
                Div(
                    HTML('<span class="badge badge-default">7</span>'),
                    Div('attended_english', css_class='col-md-2'),
                    HTML('<span class="badge badge-default" id="span_modality_english">7.1</span>'),
                    Div('modality_english', css_class='col-md-2  multiple-checbkoxes'),
                    HTML('<span class="badge badge-default" id="span_english">7.2</span>'),
                    Div('english', css_class='col-md-2'),
                    css_class='row grades',
                ),
                Div(
                    HTML('<span class="badge badge-default">8</span>'),
                    Div('attended_math', css_class='col-md-2'),
                    HTML('<span class="badge badge-default" id="span_modality_math">8.1</span>'),
                    Div('modality_math', css_class='col-md-2  multiple-checbkoxes'),
                    HTML('<span class="badge badge-default" id="span_math">8.2</span>'),
                    Div('math', css_class='col-md-2'),
                    css_class='row grades',
                ),

                Div(
                    HTML('<span class="badge badge-default">9</span>'),
                    Div('attended_social', css_class='col-md-2'),
                    HTML('<span class="badge badge-default" id="span_modality_social">9.1</span>'),
                    Div('modality_social', css_class='col-md-2  multiple-checbkoxes'),
                    HTML('<span class="badge badge-default" id="span_social_emotional">9.2</span>'),
                    Div('social_emotional', css_class='col-md-2'),
                    css_class='row grades',
                ),

                Div(
                    HTML('<span class="badge badge-default">10</span>'),
                    Div('attended_psychomotor', css_class='col-md-2'),
                    HTML('<span class="badge badge-default" id="span_modality_psychomotor">10.1</span>'),
                    Div('modality_psychomotor', css_class='col-md-2  multiple-checbkoxes'),
                    HTML('<span class="badge badge-default" id="span_psychomotor">10.2</span>'),
                    Div('psychomotor', css_class='col-md-2'),
                    css_class='row grades',
                ),


                css_class='bd-callout bd-callout-warning A_right_border'
            ),
            Fieldset(
                None,
                Div(
                    HTML('<span>B</span>'), css_class='block_tag'),
                Div(
                    HTML('<h4 id="alternatives-to-hidden-labels">' + _('Follow up') + '</h4>')
                ),
                Div(
                    HTML('<span class="badge badge-default">1</span>'),
                    Div('phone_call_number', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">1.1</span>'),
                    Div('phone_call_follow_up_result', css_class='col-md-3'),
                    css_class='row'
                ),
                Div(
                    HTML('<span class="badge badge-default">2</span>'),
                    Div('house_visit_number', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">2.1</span>'),
                    Div('house_visit_follow_up_result', css_class='col-md-3'),
                    css_class='row'
                ),
                Div(
                    HTML('<span class="badge badge-default">3</span>'),
                    Div('family_visit_number', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">3.1</span>'),
                    Div('family_visit_follow_up_result', css_class='col-md-3'),
                    css_class='row'
                ),
                id='follow_up',
                css_class='bd-callout bd-callout-warning B_right_border'
            ),

            Fieldset(
                None,
                Div(
                    HTML('<span>C</span>'), css_class='block_tag'),
                None,
                Div(
                    HTML('<h4 id="alternatives-to-hidden-labels">' + _('Parents Meeting and Health Exam') + '</h4>')
                ),
                Div(
                    HTML('<span class="badge badge-default">1</span>'),
                    Div('parent_attended_visits', css_class='col-md-3'),
                    # HTML('<span class="badge badge-default">2</span>'),
                    # Div('visits_number', css_class='col-md-4'),
                    css_class='row',
                ),

                Div(
                    HTML('<span class="badge badge-default">2</span>'),
                    Div('pss_session_attended', css_class='col-md-2'),
                    HTML('<span class="badge badge-default" id="span_pss_session_modality">2.1</span>'),
                    Div('pss_session_modality', css_class='col-md-2 multiple-checbkoxes'),
                    HTML('<span class="badge badge-default" id="span_pss_session_number">2.2</span>'),
                    Div('pss_session_number', css_class='col-md-2'),
                    HTML('<span class="badge badge-default" id="span_pss_parent_attended">2.3</span>'),
                    Div('pss_parent_attended', css_class='col-md-2'),
                    HTML('<span class="badge badge-default" id="span_pss_parent_attended_other">2.4</span>'),
                    Div('pss_parent_attended_other', css_class='col-md-2'),
                    css_class='row parent_visits',
                ),
                Div(
                    HTML('<span class="badge badge-default">3</span>'),
                    Div('covid_session_attended', css_class='col-md-2'),
                    HTML('<span class="badge badge-default" id="span_covid_session_modality">3.1</span>'),
                    Div('covid_session_modality', css_class='col-md-2 multiple-checbkoxes'),
                    HTML('<span class="badge badge-default" id="span_covid_session_number">3.2</span>'),
                    Div('covid_session_number', css_class='col-md-2'),
                    HTML('<span class="badge badge-default" id="span_covid_parent_attended">3.3</span>'),
                    Div('covid_parent_attended', css_class='col-md-2'),
                    HTML('<span class="badge badge-default" id="span_covid_parent_attended_other">3.4</span>'),
                    Div('covid_parent_attended_other', css_class='col-md-2'),
                    css_class='row parent_visits',
                ),
                Div(
                    HTML('<span class="badge badge-default">4</span>'),
                    Div('followup_session_attended', css_class='col-md-2'),
                    HTML('<span class="badge badge-default" id="span_followup_session_modality">4.1</span>'),
                    Div('followup_session_modality', css_class='col-md-2 multiple-checbkoxes'),
                    HTML('<span class="badge badge-default" id="span_followup_session_number">4.2</span>'),
                    Div('followup_session_number', css_class='col-md-2'),
                    HTML('<span class="badge badge-default" id="span_followup_parent_attended">4.3</span>'),
                    Div('followup_parent_attended', css_class='col-md-2'),
                    HTML('<span class="badge badge-default" id="span_followup_parent_attended_other">4.4</span>'),
                    Div('followup_parent_attended_other', css_class='col-md-2'),
                    css_class='row parent_visits',
                ),
                # Div(
                #     HTML('<span class="badge badge-default">4</span>'),
                #     Div('child_health_examed', css_class='col-md-4'),
                #     HTML('<span class="badge badge-default">5</span>'),
                #     Div('child_health_concern', css_class='col-md-4'),
                #     css_class='row',
                # ),
                id= 'visits',
                css_class='bd-callout bd-callout-warning C_right_border'+ display_assessment,
            ),
            FormActions(
                Submit('save', _('Save'), css_class='col-md-2'),
                HTML('<a class="btn btn-info cancel-button" href="/clm/bln-list/" translation="' +
                     _('Are you sure you want to cancel this registration?') + '">' + _('Back to list') + '</a>'),
            )
        )

    def clean(self):
        cleaned_data = super(BLNAssessmentForm, self).clean()

        attended_arabic = cleaned_data.get("attended_arabic")
        modality_arabic = cleaned_data.get("modality_arabic")
        arabic = cleaned_data.get("arabic")

        attended_english = cleaned_data.get("attended_english")
        modality_english = cleaned_data.get("modality_english")
        english = cleaned_data.get("english")

        attended_psychomotor = cleaned_data.get("attended_psychomotor")
        modality_psychomotor = cleaned_data.get("modality_psychomotor")
        psychomotor = cleaned_data.get("psychomotor")

        attended_math = cleaned_data.get("attended_math")
        modality_math = cleaned_data.get("modality_math")
        math = cleaned_data.get("math")

        attended_social = cleaned_data.get("attended_social")
        modality_social = cleaned_data.get("modality_social")
        social_emotional = cleaned_data.get("social_emotional")

        learning_result = cleaned_data.get("learning_result")
        barriers_single = cleaned_data.get("barriers_single")
        barriers_other = cleaned_data.get("barriers_other")

        test_done = cleaned_data.get("test_done")
        round_complete = cleaned_data.get("round_complete")

        if test_done == 'yes':
            if not round_complete:
                self.add_error('round_complete', 'This field is required')

        if learning_result != 'no_absence':
            if not barriers_single:
                self.add_error('barriers_single', 'This field is required')

        if barriers_single == 'other':
            if not barriers_other:
                self.add_error('barriers_other', 'This field is required')

        if test_done == 'yes':
            if attended_arabic == 'yes':
                if not modality_arabic:
                    self.add_error('modality_arabic', 'This field is required')
                if arabic is None:
                    self.add_error('arabic', 'This field is required')

            if attended_english == 'yes':
                if not modality_english:
                    self.add_error('modality_english', 'This field is required')
                if english is None:
                    self.add_error('english', 'This field is required')

            if attended_psychomotor == 'yes':
                if not modality_psychomotor:
                    self.add_error('modality_psychomotor', 'This field is required')
                if psychomotor is None:
                    self.add_error('psychomotor', 'This field is required')

            if attended_math == 'yes':
                if not modality_math:
                    self.add_error('modality_math', 'This field is required')
                if math is None:
                    self.add_error('math', 'This field is required')

            if attended_social == 'yes':
                if not modality_social:
                    self.add_error('modality_social', 'This field is required')
                if social_emotional is None:
                    self.add_error('social_emotional', 'This field is required')

            # grades Max Value validation
            registration_level = cleaned_data.get("registration_level")

            if registration_level == 'level_one':
                if arabic > 44:
                    self.add_error('arabic', 'This value is greater that 44')
                if english > 36:
                    self.add_error('english', 'This value is greater that 36')
                if math > 18:
                    self.add_error('math', 'This value is greater that 18')
                if social_emotional > 24:
                    self.add_error('social_emotional', 'This value is greater that 24')
                if psychomotor > 8:
                    self.add_error('psychomotor', 'This value is greater that 8')
            elif registration_level == 'level_two':
                if arabic > 52:
                    self.add_error('arabic', 'This value is greater that 52')
                if english > 56:
                    self.add_error('english', 'This value is greater that 56')
                if math > 30:
                    self.add_error('math', 'This value is greater that 30')
                if social_emotional > 24:
                    self.add_error('social_emotional', 'This value is greater that 24')
                if psychomotor > 8:
                    self.add_error('psychomotor', 'This value is greater that 8')
            else:
                if arabic > 58:
                    self.add_error('arabic', 'This value is greater that 58')
                if english > 60:
                    self.add_error('english', 'This value is greater that 60')
                if math > 32:
                    self.add_error('math', 'This value is greater that 32')
                if social_emotional > 24:
                    self.add_error('social_emotional', 'This value is greater that 24')
                if psychomotor > 8:
                    self.add_error('psychomotor', 'This value is greater that 8')


    def save(self, instance=None, request=None):
        instance = super(BLNAssessmentForm, self).save()
        # instance = super(BLNAssessmentForm, self).save(request=request, instance=instance, serializer=BLNSerializer)

        instance.modified_by = request.user
        # instance.pss_session_modality = request.POST.getlist('pss_session_modality')
        # instance.covid_session_modality = request.POST.getlist('covid_session_modality')
        # instance.followup_session_modality = request.POST.getlist('followup_session_modality')

        instance.post_test = {
                "BLN_ASSESSMENT/attended_arabic": request.POST.get('attended_arabic'),
                "BLN_ASSESSMENT/modality_arabic": request.POST.getlist('modality_arabic'),
                "BLN_ASSESSMENT/arabic": request.POST.get('arabic'),

                "BLN_ASSESSMENT/attended_english": request.POST.get('attended_english'),
                "BLN_ASSESSMENT/modality_english": request.POST.getlist('modality_english'),
                "BLN_ASSESSMENT/english": request.POST.get('english'),

                "BLN_ASSESSMENT/attended_psychomotor": request.POST.get('attended_psychomotor'),
                "BLN_ASSESSMENT/modality_psychomotor": request.POST.getlist('modality_psychomotor'),
                "BLN_ASSESSMENT/psychomotor": request.POST.get('psychomotor'),

                "BLN_ASSESSMENT/attended_math": request.POST.get('attended_math'),
                "BLN_ASSESSMENT/modality_math": request.POST.getlist('modality_math'),
                "BLN_ASSESSMENT/math": request.POST.get('math'),

                "BLN_ASSESSMENT/attended_social": request.POST.get('attended_social'),
                "BLN_ASSESSMENT/modality_social": request.POST.getlist('modality_social'),
                "BLN_ASSESSMENT/social_emotional": request.POST.get('social_emotional'),
            }

        instance.save()
        messages.success(request, _('Your data has been sent successfully to the server'))

    class Meta:
        model = BLN
        fields = (
            'participation',
            'barriers_single',
            'barriers_other',
            'test_done',
            'round_complete',
            'basic_stationery',
            'pss_kit',
            'learning_result',
            'phone_call_number',
            'house_visit_number',
            'family_visit_number',
            'phone_call_follow_up_result' ,
            'house_visit_follow_up_result' ,
            'family_visit_follow_up_result' ,
            'parent_attended_visits',
            'pss_session_attended',
            'pss_session_number',
            'pss_session_modality',
            'pss_parent_attended',
            'pss_parent_attended_other',
            'covid_session_attended',
            'covid_session_number',
            'covid_session_modality',
            'covid_parent_attended',
            'covid_parent_attended_other',
            'followup_session_attended',
            'followup_session_number',
            'followup_session_modality',
            'followup_parent_attended_other',
            'followup_parent_attended',
            'cp_referral',
            # 'child_health_examed',
            # 'child_health_concern',
        )

class CBECEAssessmentForm(forms.ModelForm):
    REGISTRATION_LEVEL = (
        ('', '----------'),
        ('level_two', _('Level two')),
        ('level_three', _('Level three'))
    )
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
    learning_result = forms.ChoiceField(
        label=_('Based on the overall score, what is the recommended learning path?'),
        widget=forms.Select, required=True,
        choices=(
            ('', '----------'),
            # ('graduated_to_cbece_next_level', _('Graduated to the next level')),
            ('graduated_to_cbece_next_round_same_level', _('Graduated to the next round, same level')),
            ('graduated_to_cbece_next_round_higher_level', _('Graduated to the next round, higher level round 3')),
            # ('referred_to_alp', _('referred to ALP')),
            ('referred_public_school', _('Referred to public school grade 1')),
            # ('referred_to_tvet', _('Referred to TVET')),
            # ('referred_to_ycbece', _('Referred to YCBECE')),
            ('dropout', _('Dropout, referral not possible')),
        ),
        initial=''
    )
    barriers_single = forms.ChoiceField(
        label=_('The main barriers affecting the daily attendance and performance '
                'of the child or drop out of programme? (Select more than one if applicable)'),
        choices= (
            ('Full time job to support family financially', _('Full time job to support family financially')),
            ('seasonal_work', _('Seasonal work')),
            ('availablity_electronic_device', _('Availablity of Electronic Device')),
            ('internet_connectivity', _('Internet Connectivity')),
            ('sickness', _('Sickness')),
            ('security', _('Security')),
            ('family_moved', _('Family moved')),
            ('Moved back to Syria', _('Moved back to Syria')),
            ('Enrolled in formal education', _('Enrolled in formal education')),
            ('violence bullying', _('Violence/Bullying')),
            ('No interest in pursuing the programme/No value', _('No interest in pursuing the programme/No value')),
            ('other', _('Other')),
        ),
        widget=forms.Select,
        required=True
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

    basic_stationery = forms.ChoiceField(
        label=_("Did the child receive basic stationery?"),
        widget=forms.Select, required=True,
        choices=CLM.YES_NO
    )
    # pss_kit = forms.ChoiceField(
    #         label=_("Did the child benefit from the PSS kit?"),
    #         widget=forms.Select, required=True,
    #         choices=CLM.YES_NO
    # )
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
    attended_english = forms.ChoiceField(
        label=_("Attended English test"),
        widget=forms.Select, required=True,
        choices=(('yes', _("Yes")), ('no', _("No"))),
        initial='yes'
    )
    modality_english = forms.MultipleChoiceField(
        label=_('Please indicate modality'),
        choices=CLM.MODALITY,
        widget=forms.CheckboxSelectMultiple,
        required=False
    )
    english = forms.FloatField(
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
    attended_social = forms.ChoiceField(
        label=_("Attended Social test"),
        widget=forms.Select, required=True,
        choices=(('yes', _("Yes")), ('no', _("No"))),
        initial='yes'
    )
    modality_social = forms.MultipleChoiceField(
        label=_('Please indicate modality'),
        choices=CLM.MODALITY,
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    social_emotional = forms.FloatField(
        label=_('Results'),
        widget=forms.NumberInput(attrs=({'maxlength': 4})),
        min_value=0, required=False
    )

    attended_psychomotor = forms.ChoiceField(
        label=_("Attended Psychomotor test"),
        widget=forms.Select, required=True,
        choices=(('yes', _("Yes")), ('no', _("No"))),
        initial='yes'
    )
    modality_psychomotor = forms.MultipleChoiceField(
        label=_('Please indicate modality'),
        choices=CLM.MODALITY,
        widget=forms.CheckboxSelectMultiple,
        required=False
    )
    psychomotor = forms.FloatField(
        label=_('Results'),
        widget=forms.NumberInput(attrs=({'maxlength': 4})),
        min_value=0, required=False
    )
    attended_science = forms.ChoiceField(
        label=_("Attended Science test"),
        widget=forms.Select, required=True,
        choices=(('yes', _("Yes")), ('no', _("No"))),
        initial='yes'
    )
    modality_science = forms.MultipleChoiceField(
        label=_('Please indicate modality'),
        choices=CLM.MODALITY,
        widget=forms.CheckboxSelectMultiple,
        required=False
    )
    science = forms.FloatField(
        label=_('Results'),
        widget=forms.NumberInput(attrs=({'maxlength': 4})),
        min_value=0, required=False
    )
    attended_artistic = forms.ChoiceField(
        label=_("Attended Artistic test"),
        widget=forms.Select, required=True,
        choices=(('yes', _("Yes")), ('no', _("No"))),
        initial='yes'
    )
    modality_artistic = forms.MultipleChoiceField(
        label=_('Please indicate modality'),
        choices=CLM.MODALITY,
        widget=forms.CheckboxSelectMultiple,
        required=False
    )
    artistic = forms.FloatField(
        label=_('Results'),
        widget=forms.NumberInput(attrs=({'maxlength': 4})),
        min_value=0, required=False
    )
    follow_up_type = forms.ChoiceField(
        label=_('Type of follow up'),
        widget=forms.Select, required=False,
        choices=(
            ('none', _('----------')),
            ('Phone', _('Phone Call')),
            ('House visit', _('House Visit')),
            ('Family Visit', _('Family Visit')),
        ),
        initial=''
    )
    phone_call_number = forms.IntegerField(
        label=_('Please enter the number phone calls'),
        widget=forms.NumberInput(attrs=({'maxlength': 4})),
        min_value=0, required=False
    )
    house_visit_number = forms.IntegerField(
        label=_('Please enter the number of house visits'),
        widget=forms.NumberInput(attrs=({'maxlength': 4})),
        min_value=0, required=False
    )
    family_visit_number = forms.IntegerField(
        label=_('Please enter the number parent visits'),
        widget=forms.NumberInput(attrs=({'maxlength': 4})),
        min_value=0, required=False
    )
    phone_call_follow_up_result = forms.ChoiceField(
        label=_('Result of follow up'),
        widget=forms.Select, required=False,
        choices=(
            ('child back', _('Child returned to Round')),
            ('child transfer to difficulty center', _('Child referred to specialized services')),
            ('child transfer to protection', _('Child referred to protection')),
            ('child transfer to medical', _('Child referred to Health programme')),
            ('Intensive followup', _('Follow-up with parents')),
            ('dropout', _('Dropout/No Interest')),
        ),
        initial=''
    )
    house_visit_follow_up_result = forms.ChoiceField(
        label=_('Result of follow up'),
        widget=forms.Select, required=False,
        choices=(
            ('child back', _('Child returned to Round')),
            ('child transfer to difficulty center', _('Child referred to specialized services')),
            ('child transfer to protection', _('Child referred to protection')),
            ('child transfer to medical', _('Child referred to Health programme')),
            ('Intensive followup', _('Follow-up with parents')),
            ('dropout', _('Dropout/No Interest')),
        ),
        initial=''
    )
    family_visit_follow_up_result = forms.ChoiceField(
        label=_('Result of follow up'),
        widget=forms.Select, required=False,
        choices=(
            ('child back', _('Child returned to Round')),
            ('child transfer to difficulty center', _('Child referred to specialized services')),
            ('child transfer to protection', _('Child referred to protection')),
            ('child transfer to medical', _('Child referred to Health programme')),
            ('Intensive followup', _('Follow-up with parents')),
            ('dropout', _('Dropout/No Interest')),
        ),
        initial=''
    )
    parent_attended_visits = forms.ChoiceField(
        label=_("Parents attended parents meeting"),
        widget=forms.Select, required=False,
        choices=(('yes', _("Yes")), ('no', _("No"))),
        initial='yes'
    )
    cp_referral = forms.ChoiceField(
        label=_("CP Followup"),
        widget=forms.Select, required=True,
        choices=(
            ('', '----------'),
            ('yes', _("Yes")),
            ('no', _("No")))
    )
    pss_session_attended = forms.ChoiceField(
        label=_("Attended PSS Session"),
        widget=forms.Select, required=True,
        choices=(('yes', _("Yes")), ('no', _("No")))
    )
    pss_session_number = forms.IntegerField(
        label=_('Please enter the number of sessions'),
        widget=forms.NumberInput(attrs=({'maxlength': 4})),
        min_value=0, required=False
    )
    pss_session_modality = forms.MultipleChoiceField(
        label=_('Please indicate modality'),
        choices=CLM.SESSION_MODALITY,
        widget=forms.CheckboxSelectMultiple,
        required=False
    )
    pss_parent_attended = forms.ChoiceField(
        label=_("Parent who attended the parents meeting"),
        widget=forms.Select, required=False,
        choices=(
            ('', '----------'),
            ('mother', _('Mother')),
            ('father', _('Father')),
            ('other', _('Other')),
        )
    )
    pss_parent_attended_other = forms.CharField(
        label=_('Please specify'),
        widget=forms.TextInput, required=False
    )
    covid_session_attended = forms.ChoiceField(
        label=_("Attended covid Session"),
        widget=forms.Select, required=True,
        choices=(('yes', _("Yes")), ('no', _("No")))
    )
    covid_session_number = forms.IntegerField(
        label=_('Please enter the number of sessions'),
        widget=forms.NumberInput(attrs=({'maxlength': 4})),
        min_value=0, required=False
    )
    covid_session_modality = forms.MultipleChoiceField(
        label=_('Please indicate modality'),
        choices=CLM.SESSION_MODALITY,
        widget=forms.CheckboxSelectMultiple,
        required=False
    )
    covid_parent_attended = forms.ChoiceField(
        label=_("Parent who attended the parents meeting"),
        widget=forms.Select, required=False,
        choices=(
            ('', '----------'),
            ('mother', _('Mother')),
            ('father', _('Father')),
            ('other', _('Other')),
        )
    )
    covid_parent_attended_other = forms.CharField(
        label=_('Please specify'),
        widget=forms.TextInput, required=False
    )
    followup_session_attended = forms.ChoiceField(
        label=_("Attended followup Session"),
        widget=forms.Select, required=True,
        choices=(('yes', _("Yes")), ('no', _("No")))
    )
    followup_session_number = forms.IntegerField(
        label=_('Please enter the number of sessions'),
        widget=forms.NumberInput(attrs=({'maxlength': 4})),
        min_value=0, required=False
    )

    followup_session_modality = forms.MultipleChoiceField(
        label=_('Please indicate modality'),
        choices=CLM.SESSION_MODALITY,
        widget=forms.CheckboxSelectMultiple,
        required=False
    )
    followup_parent_attended = forms.ChoiceField(
        label=_("Parent who attended the parents meeting"),
        widget=forms.Select, required=False,
        choices=(
            ('', '----------'),
            ('mother', _('Mother')),
            ('father', _('Father')),
            ('other', _('Other')),
        )
    )
    followup_parent_attended_other = forms.CharField(
        label=_('Please specify'),
        widget=forms.TextInput, required=False
    )
    child_health_examed = forms.ChoiceField(
        label=_("Did the child receive health exam"),
        widget=forms.Select, required=False,
        choices=(('yes', _("Yes")), ('no', _("No"))),
        initial='yes'
    )
    child_health_concern = forms.ChoiceField(
        label=_("Anything to worry about"),
        widget=forms.Select, required=False,
        choices=(('yes', _("Yes")), ('no', _("No"))),
        initial='yes'
    )

    clm_type = forms.CharField(widget=forms.HiddenInput, required=False)
    registration_level = forms.CharField(widget=forms.HiddenInput, required=False)

    registration_level = forms.ChoiceField(
        label=_("Registration level"),
        widget=forms.Select, required=False,
        choices=REGISTRATION_LEVEL
    )

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(CBECEAssessmentForm, self).__init__(*args, **kwargs)

        post_test = ''
        post_test_button = ' btn-outline-secondary disabled'
        instance = kwargs['instance'] if 'instance' in kwargs else ''
        self.fields['clm_type'].initial = 'CBECE'

        display_assessment = ''
        form_action = reverse('clm:cbece_post_assessment', kwargs={'pk': instance.id})

        if instance.post_test:
            post_test_button = ' btn-outline-success '
            post_test = instance.assessment_form(
                stage='post_test',
                assessment_slug='cbece_post_test',
                callback=self.request.build_absolute_uri(
                    reverse('clm:cbece_post_assessment', kwargs={'pk': instance.id}))
            )

        self.helper = FormHelper()
        self.helper.form_show_labels = True
        self.helper.form_action = form_action
        self.helper.layout = Layout(
            Fieldset(
                None,
                Div(
                    HTML('<h4 id="alternatives-to-hidden-labels">' + _('Assessment data') + '</h4>'),
                ),
            ),
            Fieldset(
                None,
                Div(
                    HTML('<span>A</span>'), css_class='block_tag'),
                Div(
                    HTML('<h4 id="alternatives-to-hidden-labels">' + _('School evaluation') + '</h4>')
                ),
                Div(
                    Div('registration_level', css_class='col-md-3 d-none'),
                    css_class='row',
                ),
                Div(
                    HTML('<span class="badge badge-default">1</span>'),
                    Div('participation', css_class='col-md-2'),
                    HTML('<span class="badge badge-default" id="span_barriers_single">1.1</span>'),
                    Div('barriers_single', css_class='col-md-2'),
                    HTML('<span class="badge badge-default" id="span_barriers_other">1.2</span>'),
                    Div('barriers_other', css_class='col-md-2'),
                    css_class='row',
                ),
                Div(
                    HTML('<span class="badge badge-default">2</span>'),
                    Div('test_done', css_class='col-md-4'),
                    HTML('<span class="badge badge-default" id="span_round_complete">2.1</span>'),
                    Div('round_complete', css_class='col-md-4'),
                    css_class='row',
                ),
                Div(
                    HTML('<span class="badge badge-default">3</span>'),
                    Div('basic_stationery', css_class='col-md-3'),
                    # HTML('<span class="badge badge-default">4</span>'),
                    # Div('pss_kit', css_class='col-md-3'),
                    css_class='row',
                ),
                Div(
                    HTML('<span class="badge badge-default">4</span>'),
                    Div('learning_result', css_class='col-md-4'),
                    HTML('<span class="badge badge-default">5</span>'),
                    Div('cp_referral', css_class='col-md-3'),
                    css_class='row',
                ),
                Div(
                    HTML('<span class="badge badge-default">5</span>'),
                    Div('attended_arabic', css_class='col-md-2'),
                    HTML('<span class="badge badge-default" id="span_modality_arabic">5.1</span>'),
                    Div('modality_arabic', css_class='col-md-2 multiple-checbkoxes'),
                    HTML('<span class="badge badge-default" id="span_arabic">5.2</span>'),
                    Div('arabic', css_class='col-md-2'),
                    css_class='row grades',
                ),
                Div(
                    HTML('<span class="badge badge-default">6</span>'),
                    Div('attended_english', css_class='col-md-2'),
                    HTML('<span class="badge badge-default" id="span_modality_english">6.1</span>'),
                    Div('modality_english', css_class='col-md-2 multiple-checbkoxes'),
                    HTML('<span class="badge badge-default" id="span_english">6.2</span>'),
                    Div('english', css_class='col-md-2'),
                    css_class='row grades',
                ),
                Div(
                    HTML('<span class="badge badge-default">7</span>'),
                    Div('attended_math', css_class='col-md-2'),
                    HTML('<span class="badge badge-default" id="span_modality_math">7.1</span>'),
                    Div('modality_math', css_class='col-md-2 multiple-checbkoxes'),
                    HTML('<span class="badge badge-default" id="span_math">7.2</span>'),
                    Div('math', css_class='col-md-2'),
                    css_class='row grades',
                ),
                Div(
                    HTML('<span class="badge badge-default">8</span>'),
                    Div('attended_science', css_class='col-md-2'),
                    HTML('<span class="badge badge-default" id="span_modality_science">8.1</span>'),
                    Div('modality_science', css_class='col-md-2 multiple-checbkoxes'),
                    HTML('<span class="badge badge-default" id="span_science">8.2</span>'),
                    Div('science', css_class='col-md-2'),
                    css_class='row grades',
                ),

                Div(
                    HTML('<span class="badge badge-default">9</span>'),
                    Div('attended_social', css_class='col-md-2'),
                    HTML('<span class="badge badge-default" id="span_modality_social">9.1</span>'),
                    Div('modality_social', css_class='col-md-2 multiple-checbkoxes'),
                    HTML('<span class="badge badge-default" id="span_social_emotional">9.2</span>'),
                    Div('social_emotional', css_class='col-md-2'),
                    css_class='row grades',
                ),

                Div(
                    HTML('<span class="badge badge-default">10</span>'),
                    Div('attended_psychomotor', css_class='col-md-2'),
                    HTML('<span class="badge badge-default" id="span_modality_psychomotor">10.1</span>'),
                    Div('modality_psychomotor', css_class='col-md-2 multiple-checbkoxes'),
                    HTML('<span class="badge badge-default" id="span_psychomotor">10.2</span>'),
                    Div('psychomotor', css_class='col-md-2'),
                    css_class='row grades',
                ),

                Div(
                    HTML('<span class="badge badge-default">11</span>'),
                    Div('attended_artistic', css_class='col-md-2'),
                    HTML('<span class="badge badge-default" id="span_modality_artistic">11.1</span>'),
                    Div('modality_artistic', css_class='col-md-2 multiple-checbkoxes'),
                    HTML('<span class="badge badge-default" id="span_artistic">11.2</span>'),
                    Div('artistic', css_class='col-md-2'),
                    css_class='row grades',
                ),
                css_class='bd-callout bd-callout-warning A_right_border'
            ),
            Fieldset(
                None,
                Div(
                    HTML('<span>B</span>'), css_class='block_tag'),
                Div(
                    HTML('<h4 id="alternatives-to-hidden-labels">' + _('Follow up') + '</h4>')
                ),
                Div(
                    HTML('<span class="badge badge-default">1</span>'),
                    Div('phone_call_number', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">1.1</span>'),
                    Div('phone_call_follow_up_result', css_class='col-md-3'),
                    css_class='row'
                ),
                Div(
                    HTML('<span class="badge badge-default">2</span>'),
                    Div('house_visit_number', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">2.1</span>'),
                    Div('house_visit_follow_up_result', css_class='col-md-3'),
                    css_class='row'
                ),
                Div(
                    HTML('<span class="badge badge-default">3</span>'),
                    Div('family_visit_number', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">3.1</span>'),
                    Div('family_visit_follow_up_result', css_class='col-md-3'),
                    css_class='row'
                ),
                id='follow_up',
                css_class='bd-callout bd-callout-warning B_right_border'
            ),

            Fieldset(
                None,
                Div(
                    HTML('<span>C</span>'), css_class='block_tag'),
                None,
                Div(
                    HTML('<h4 id="alternatives-to-hidden-labels">' + _('Parents Meeting and Health Exam') + '</h4>')
                ),
                Div(
                    HTML('<span class="badge badge-default">1</span>'),
                    Div('parent_attended_visits', css_class='col-md-3'),
                    # HTML('<span class="badge badge-default">2</span>'),
                    # Div('visits_number', css_class='col-md-4'),
                    css_class='row',
                ),

                Div(
                    HTML('<span class="badge badge-default">2</span>'),
                    Div('pss_session_attended', css_class='col-md-2'),
                    HTML('<span class="badge badge-default" id="span_pss_session_modality">2.1</span>'),
                    Div('pss_session_modality', css_class='col-md-2 multiple-checbkoxes'),
                    HTML('<span class="badge badge-default" id="span_pss_session_number">2.2</span>'),
                    Div('pss_session_number', css_class='col-md-2'),
                    HTML('<span class="badge badge-default" id="span_pss_parent_attended">5</span>'),
                    Div('pss_parent_attended', css_class='col-md-2'),
                    HTML('<span class="badge badge-default" id="span_pss_parent_attended_other">5.1</span>'),
                    Div('pss_parent_attended_other', css_class='col-md-2'),
                    css_class='row parent_visits',
                ),
                Div(
                    HTML('<span class="badge badge-default">3</span>'),
                    Div('covid_session_attended', css_class='col-md-2'),
                    HTML('<span class="badge badge-default" id="span_covid_session_modality">3.1</span>'),
                    Div('covid_session_modality', css_class='col-md-2 multiple-checbkoxes'),
                    HTML('<span class="badge badge-default" id="span_covid_session_number">3.2</span>'),
                    Div('covid_session_number', css_class='col-md-2'),
                    HTML('<span class="badge badge-default" id="span_covid_parent_attended">5</span>'),
                    Div('covid_parent_attended', css_class='col-md-2'),
                    HTML('<span class="badge badge-default" id="span_covid_parent_attended_other">5.1</span>'),
                    Div('covid_parent_attended_other', css_class='col-md-2'),
                    css_class='row parent_visits',
                ),
                Div(
                    HTML('<span class="badge badge-default">4</span>'),
                    Div('followup_session_attended', css_class='col-md-2'),
                    HTML('<span class="badge badge-default" id="span_followup_session_modality">4.1</span>'),
                    Div('followup_session_modality', css_class='col-md-2 multiple-checbkoxes'),
                    HTML('<span class="badge badge-default" id="span_followup_session_number">4.2</span>'),
                    Div('followup_session_number', css_class='col-md-2'),
                    HTML('<span class="badge badge-default" id="span_followup_parent_attended">5</span>'),
                    Div('followup_parent_attended', css_class='col-md-2'),
                    HTML('<span class="badge badge-default" id="span_followup_parent_attended_other">5.1</span>'),
                    Div('followup_parent_attended_other', css_class='col-md-2'),
                    css_class='row parent_visits',
                ),

                # Div(
                #     HTML('<span class="badge badge-default">4</span>'),
                #     Div('child_health_examed', css_class='col-md-4'),
                #     HTML('<span class="badge badge-default">5</span>'),
                #     Div('child_health_concern', css_class='col-md-4'),
                #     css_class='row',
                # ),
                id= 'visits',
                css_class='bd-callout bd-callout-warning C_right_border'+ display_assessment,
            ),
            FormActions(
                Submit('save', _('Save'), css_class='col-md-2'),
                HTML('<a class="btn btn-info cancel-button" href="/clm/cbece-list/" translation="' +
                     _('Are you sure you want to cancel this registration?') + '">' + _('Back to list') + '</a>'),
            )
        )

    def clean(self):
        cleaned_data = super(CBECEAssessmentForm, self).clean()

        attended_arabic = cleaned_data.get("attended_arabic")
        modality_arabic = cleaned_data.get("modality_arabic")
        arabic = cleaned_data.get("arabic")

        attended_english = cleaned_data.get("attended_english")
        modality_english = cleaned_data.get("modality_english")
        english = cleaned_data.get("english")

        attended_psychomotor = cleaned_data.get("attended_psychomotor")
        modality_psychomotor = cleaned_data.get("modality_psychomotor")
        psychomotor = cleaned_data.get("psychomotor")

        attended_math = cleaned_data.get("attended_math")
        modality_math = cleaned_data.get("modality_math")
        math = cleaned_data.get("math")

        attended_social = cleaned_data.get("attended_social")
        modality_social = cleaned_data.get("modality_social")
        social_emotional = cleaned_data.get("social_emotional")

        attended_science = cleaned_data.get("attended_science")
        modality_science = cleaned_data.get("modality_science")
        science = cleaned_data.get("science")

        attended_artistic = cleaned_data.get("attended_artistic")
        modality_artistic = cleaned_data.get("modality_artistic")
        artistic = cleaned_data.get("artistic")

        learning_result = cleaned_data.get("learning_result")
        barriers_single = cleaned_data.get("barriers_single")
        barriers_other = cleaned_data.get("barriers_other")

        test_done = cleaned_data.get("test_done")
        round_complete = cleaned_data.get("round_complete")

        if test_done == 'yes':
            if not round_complete:
                self.add_error('round_complete', 'This field is required')

        if learning_result != 'no_absence':
            if not barriers_single:
                self.add_error('barriers_single', 'This field is required')

        if barriers_single == 'other':
            if not barriers_other:
                self.add_error('barriers_other', 'This field is required')

        if test_done == 'yes':
            if attended_science == 'yes':
                if not modality_science:
                    self.add_error('modality_science', 'This field is required')
                if science is None:
                    self.add_error('science', 'This field is required')

            if attended_artistic == 'yes':
                if not modality_artistic:
                    self.add_error('modality_artistic', 'This field is required')
                if artistic is None:
                    self.add_error('artistic', 'This field is required')

            if attended_arabic == 'yes':
                if not modality_arabic:
                    self.add_error('modality_arabic', 'This field is required')
                if arabic is None:
                    self.add_error('arabic', 'This field is required')

            if attended_english == 'yes':
                if not modality_english:
                    self.add_error('modality_english', 'This field is required')
                if english is None:
                    self.add_error('english', 'This field is required')

            if attended_psychomotor == 'yes':
                if not modality_psychomotor:
                    self.add_error('modality_psychomotor', 'This field is required')
                if psychomotor is None:
                    self.add_error('psychomotor', 'This field is required')

            if attended_math == 'yes':
                if not modality_math:
                    self.add_error('modality_math', 'This field is required')
                if math is None:
                    self.add_error('math', 'This field is required')

            if attended_social == 'yes':
                if not modality_social:
                    self.add_error('modality_social', 'This field is required')
                if social_emotional is None:
                    self.add_error('social_emotional', 'This field is required')

            # grades Max Value validation
            registration_level = cleaned_data.get("registration_level")

            if registration_level == 'level_two':
                if arabic > 48:
                    self.add_error('arabic', 'This value is greater that 48')
                if english > 48:
                    self.add_error('english', 'This value is greater that 48')
                if math > 44:
                    self.add_error('math', 'This value is greater that 44')
                if social_emotional > 40:
                    self.add_error('social_emotional', 'This value is greater that 40')
                if psychomotor > 34:
                    self.add_error('psychomotor', 'This value is greater that 34')
                if science > 36:
                    self.add_error('science', 'This value is greater that 36')
                if artistic > 12:
                    self.add_error('artistic', 'This value is greater that 12')
            else:
                if arabic > 60:
                    self.add_error('arabic', 'This value is greater that 60')
                if english > 60:
                    self.add_error('english', 'This value is greater that 60')
                if math > 46:
                    self.add_error('math', 'This value is greater that 46')
                if social_emotional > 40:
                    self.add_error('social_emotional', 'This value is greater that 40')
                if psychomotor > 36:
                    self.add_error('psychomotor', 'This value is greater that 36')
                if science > 36:
                    self.add_error('science', 'This value is greater that 36')
                if artistic > 12:
                    self.add_error('artistic', 'This value is greater that 12')

    def save(self, instance=None, request=None):
        instance = super(CBECEAssessmentForm, self).save()
        # instance = super(CBECEAssessmentForm, self).save(request=request, instance=instance, serializer=CBECESerializer)

        instance.modified_by = request.user
        # instance.pss_session_modality = request.POST.getlist('pss_session_modality')
        # instance.covid_session_modality = request.POST.getlist('covid_session_modality')
        # instance.followup_session_modality = request.POST.getlist('followup_session_modality')

        instance.post_test = {
                "CBECE_ASSESSMENT/attended_arabic": request.POST.get('attended_arabic'),
                "CBECE_ASSESSMENT/modality_arabic": request.POST.getlist('modality_arabic'),
                "CBECE_ASSESSMENT/arabic": request.POST.get('arabic'),

                "CBECE_ASSESSMENT/attended_english": request.POST.get('attended_english'),
                "CBECE_ASSESSMENT/modality_english": request.POST.getlist('modality_english'),
                "CBECE_ASSESSMENT/english": request.POST.get('english'),

                "CBECE_ASSESSMENT/attended_psychomotor": request.POST.get('attended_psychomotor'),
                "CBECE_ASSESSMENT/modality_psychomotor": request.POST.getlist('modality_psychomotor'),
                "CBECE_ASSESSMENT/psychomotor": request.POST.get('psychomotor'),

                "CBECE_ASSESSMENT/attended_math": request.POST.get('attended_math'),
                "CBECE_ASSESSMENT/modality_math": request.POST.getlist('modality_math'),
                "CBECE_ASSESSMENT/math": request.POST.get('math'),

                "CBECE_ASSESSMENT/attended_social": request.POST.get('attended_social'),
                "CBECE_ASSESSMENT/modality_social": request.POST.getlist('modality_social'),
                "CBECE_ASSESSMENT/social_emotional": request.POST.get('social_emotional'),

                "CBECE_ASSESSMENT/attended_science": request.POST.get('attended_science'),
                "CBECE_ASSESSMENT/modality_science": request.POST.getlist('modality_science'),
                "CBECE_ASSESSMENT/science": request.POST.get('science'),

                "CBECE_ASSESSMENT/attended_artistic": request.POST.get('attended_artistic'),
                "CBECE_ASSESSMENT/modality_artistic": request.POST.getlist('modality_artistic'),
                "CBECE_ASSESSMENT/artistic": request.POST.get('artistic')
            }

        instance.save()
        messages.success(request, _('Your data has been sent successfully to the server'))

    class Meta:
        model = CBECE
        fields = (
            'participation',
            'barriers_single',
            'barriers_other',
            'test_done',
            'round_complete',
            'basic_stationery',
            # 'pss_kit',
            'learning_result',
            'phone_call_number',
            'house_visit_number',
            'family_visit_number',
            'phone_call_follow_up_result' ,
            'house_visit_follow_up_result' ,
            'family_visit_follow_up_result' ,
            'parent_attended_visits',
            'pss_session_attended',
            'pss_session_number',
            'pss_session_modality',
            'pss_parent_attended',
            'pss_parent_attended_other',
            'covid_session_attended',
            'covid_session_number',
            'covid_session_modality',
            'covid_parent_attended',
            'covid_parent_attended_other',
            'followup_session_attended',
            'followup_session_number',
            'followup_session_modality',
            'followup_parent_attended_other',
            'followup_parent_attended',
            'cp_referral',
            # 'child_health_examed',
            # 'child_health_concern',
        )

class CBECEMidAssessmentForm(forms.ModelForm):

    REGISTRATION_LEVEL = (
        ('', '----------'),
        ('level_two', _('Level two')),
        ('level_three', _('Level three'))
    )

    mid_test_done = forms.ChoiceField(
        label=_("Mid test has been done"),
        widget=forms.Select, required=True,
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
    attended_english = forms.ChoiceField(
        label=_("Attended English test"),
        widget=forms.Select, required=True,
        choices=(('yes', _("Yes")), ('no', _("No"))),
        initial='yes'
    )
    modality_english = forms.MultipleChoiceField(
        label=_('Please indicate modality'),
        choices=CLM.MODALITY,
        widget=forms.CheckboxSelectMultiple,
        required=False
    )
    english = forms.FloatField(
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
    attended_social = forms.ChoiceField(
        label=_("Attended Social test"),
        widget=forms.Select, required=True,
        choices=(('yes', _("Yes")), ('no', _("No"))),
        initial='yes'
    )
    modality_social = forms.MultipleChoiceField(
        label=_('Please indicate modality'),
        choices=CLM.MODALITY,
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    social_emotional = forms.FloatField(
        label=_('Results'),
        widget=forms.NumberInput(attrs=({'maxlength': 4})),
        min_value=0, required=False
    )

    attended_psychomotor = forms.ChoiceField(
        label=_("Attended Psychomotor test"),
        widget=forms.Select, required=True,
        choices=(('yes', _("Yes")), ('no', _("No"))),
        initial='yes'
    )
    modality_psychomotor = forms.MultipleChoiceField(
        label=_('Please indicate modality'),
        choices=CLM.MODALITY,
        widget=forms.CheckboxSelectMultiple,
        required=False
    )
    psychomotor = forms.FloatField(
        label=_('Results'),
        widget=forms.NumberInput(attrs=({'maxlength': 4})),
        min_value=0, required=False
    )
    attended_science = forms.ChoiceField(
        label=_("Attended Science test"),
        widget=forms.Select, required=True,
        choices=(('yes', _("Yes")), ('no', _("No"))),
        initial='yes'
    )
    modality_science = forms.MultipleChoiceField(
        label=_('Please indicate modality'),
        choices=CLM.MODALITY,
        widget=forms.CheckboxSelectMultiple,
        required=False
    )
    science = forms.FloatField(
        label=_('Results'),
        widget=forms.NumberInput(attrs=({'maxlength': 4})),
        min_value=0, required=False
    )
    attended_artistic = forms.ChoiceField(
        label=_("Attended Artistic test"),
        widget=forms.Select, required=True,
        choices=(('yes', _("Yes")), ('no', _("No"))),
        initial='yes'
    )
    modality_artistic = forms.MultipleChoiceField(
        label=_('Please indicate modality'),
        choices=CLM.MODALITY,
        widget=forms.CheckboxSelectMultiple,
        required=False
    )
    artistic = forms.FloatField(
        label=_('Results'),
        widget=forms.NumberInput(attrs=({'maxlength': 4})),
        min_value=0, required=False
    )


    clm_type = forms.CharField(widget=forms.HiddenInput, required=False)

    registration_level = forms.ChoiceField(
        label=_("Registration level"),
        widget=forms.Select, required=True,
        choices=REGISTRATION_LEVEL
    )

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(CBECEMidAssessmentForm, self).__init__(*args, **kwargs)

        mid_test = ''
        mid_test_button = ' btn-outline-secondary disabled'
        instance = kwargs['instance'] if 'instance' in kwargs else ''
        self.fields['clm_type'].initial = 'CBECE'

        display_assessment = ''
        form_action = reverse('clm:cbece_mid_assessment', kwargs={'pk': instance.id})

        if instance.mid_test:
            mid_test_button = ' btn-outline-success '
            mid_test = instance.assessment_form(
                stage='mid_test',
                assessment_slug='cbece_mid_test',
                callback=self.request.build_absolute_uri(
                    reverse('clm:cbece_mid_assessment', kwargs={'pk': instance.id}))
            )

        self.helper = FormHelper()
        self.helper.form_show_labels = True
        self.helper.form_action = form_action
        self.helper.layout = Layout(
            Fieldset(
                None,
                Div(
                    HTML('<h4 id="alternatives-to-hidden-labels">' + _('Assessment data') + '</h4>'),
                ),
            ),
            Fieldset(
                None,
                Div(
                    HTML('<span>A</span>'), css_class='block_tag'),
                Div(
                    HTML('<h4 id="alternatives-to-hidden-labels">' + _('School evaluation') + '</h4>')
                ),
                Div(
                    HTML('<span class="badge badge-default">1</span>'),
                    Div('mid_test_done', css_class='col-md-4'),
                    css_class='row',
                ),
                Div(
                    Div('registration_level', css_class='col-md-3 d-none'),
                    css_class='row',
                ),

                Div(
                    HTML('<span class="badge badge-default">5</span>'),
                    Div('attended_arabic', css_class='col-md-2'),
                    HTML('<span class="badge badge-default" id="span_modality_arabic">5.1</span>'),
                    Div('modality_arabic', css_class='col-md-2 multiple-checbkoxes'),
                    HTML('<span class="badge badge-default" id="span_arabic">5.2</span>'),
                    Div('arabic', css_class='col-md-2'),
                    css_class='row grades',
                ),
                Div(
                    HTML('<span class="badge badge-default">6</span>'),
                    Div('attended_english', css_class='col-md-2'),
                    HTML('<span class="badge badge-default" id="span_modality_english">6.1</span>'),
                    Div('modality_english', css_class='col-md-2 multiple-checbkoxes'),
                    HTML('<span class="badge badge-default" id="span_english">6.2</span>'),
                    Div('english', css_class='col-md-2'),
                    css_class='row grades',
                ),
                Div(
                    HTML('<span class="badge badge-default">7</span>'),
                    Div('attended_math', css_class='col-md-2'),
                    HTML('<span class="badge badge-default" id="span_modality_math">7.1</span>'),
                    Div('modality_math', css_class='col-md-2 multiple-checbkoxes'),
                    HTML('<span class="badge badge-default" id="span_math">7.2</span>'),
                    Div('math', css_class='col-md-2'),
                    css_class='row grades',
                ),
                Div(
                    HTML('<span class="badge badge-default">8</span>'),
                    Div('attended_science', css_class='col-md-2'),
                    HTML('<span class="badge badge-default" id="span_modality_science">8.1</span>'),
                    Div('modality_science', css_class='col-md-2 multiple-checbkoxes'),
                    HTML('<span class="badge badge-default" id="span_science">8.2</span>'),
                    Div('science', css_class='col-md-2'),
                    css_class='row grades',
                ),

                Div(
                    HTML('<span class="badge badge-default">9</span>'),
                    Div('attended_social', css_class='col-md-2'),
                    HTML('<span class="badge badge-default" id="span_modality_social">9.1</span>'),
                    Div('modality_social', css_class='col-md-2 multiple-checbkoxes'),
                    HTML('<span class="badge badge-default" id="span_social_emotional">9.2</span>'),
                    Div('social_emotional', css_class='col-md-2'),
                    css_class='row grades',
                ),

                Div(
                    HTML('<span class="badge badge-default">10</span>'),
                    Div('attended_psychomotor', css_class='col-md-2'),
                    HTML('<span class="badge badge-default" id="span_modality_psychomotor">10.1</span>'),
                    Div('modality_psychomotor', css_class='col-md-2 multiple-checbkoxes'),
                    HTML('<span class="badge badge-default" id="span_psychomotor">10.2</span>'),
                    Div('psychomotor', css_class='col-md-2'),
                    css_class='row grades',
                ),
                Div(
                    HTML('<span class="badge badge-default">11</span>'),
                    Div('attended_artistic', css_class='col-md-2'),
                    HTML('<span class="badge badge-default" id="span_modality_artistic">11.1</span>'),
                    Div('modality_artistic', css_class='col-md-2 multiple-checbkoxes'),
                    HTML('<span class="badge badge-default" id="span_artistic">11.2</span>'),
                    Div('artistic', css_class='col-md-2'),
                    css_class='row grades',
                ),
                css_class='bd-callout bd-callout-warning A_right_border'
            ),
            FormActions(
                Submit('save', _('Save'), css_class='col-md-2'),
                HTML('<a class="btn btn-info cancel-button" href="/clm/cbece-list/" translation="' +
                     _('Are you sure you want to cancel this registration?') + '">' + _('Back to list') + '</a>'),
            )
        )

    def clean(self):
        cleaned_data = super(CBECEMidAssessmentForm, self).clean()

        attended_arabic = cleaned_data.get("attended_arabic")
        modality_arabic = cleaned_data.get("modality_arabic")
        arabic = cleaned_data.get("arabic")

        attended_english = cleaned_data.get("attended_english")
        modality_english = cleaned_data.get("modality_english")
        english = cleaned_data.get("english")

        attended_psychomotor = cleaned_data.get("attended_psychomotor")
        modality_psychomotor = cleaned_data.get("modality_psychomotor")
        psychomotor = cleaned_data.get("psychomotor")

        attended_math = cleaned_data.get("attended_math")
        modality_math = cleaned_data.get("modality_math")
        math = cleaned_data.get("math")

        attended_social = cleaned_data.get("attended_social")
        modality_social = cleaned_data.get("modality_social")
        social_emotional = cleaned_data.get("social_emotional")

        attended_science = cleaned_data.get("attended_science")
        modality_science = cleaned_data.get("modality_science")
        science = cleaned_data.get("science")

        attended_artistic = cleaned_data.get("attended_artistic")
        modality_artistic = cleaned_data.get("modality_artistic")
        artistic = cleaned_data.get("artistic")

        test_done = cleaned_data.get("mid_test_done")

        if test_done == 'yes':

            if attended_science == 'yes':
                if not modality_science:
                    self.add_error('modality_science', 'This field is required')
                if science is None:
                    self.add_error('science', 'This field is required')

            if attended_artistic == 'yes':
                if not modality_artistic:
                    self.add_error('modality_artistic', 'This field is required')
                if artistic is None:
                    self.add_error('artistic', 'This field is required')

            if attended_arabic == 'yes':
                if not modality_arabic:
                    self.add_error('modality_arabic', 'This field is required')
                if arabic is None:
                    self.add_error('arabic', 'This field is required')

            if attended_english == 'yes':
                if not modality_english:
                    self.add_error('modality_english', 'This field is required')
                if english is None:
                    self.add_error('english', 'This field is required')

            if attended_psychomotor == 'yes':
                if not modality_psychomotor:
                    self.add_error('modality_psychomotor', 'This field is required')
                if psychomotor is None:
                    self.add_error('psychomotor', 'This field is required')

            if attended_math == 'yes':
                if not modality_math:
                    self.add_error('modality_math', 'This field is required')
                if math is None:
                    self.add_error('math', 'This field is required')

            if attended_social == 'yes':
                if not modality_social:
                    self.add_error('modality_social', 'This field is required')
                if social_emotional is None:
                    self.add_error('social_emotional', 'This field is required')

            # grades Max Value validation
            registration_level = cleaned_data.get("registration_level")

            if registration_level == 'level_two':
                if arabic > 48:
                    self.add_error('arabic', 'This value is greater that 48')
                if english > 48:
                    self.add_error('english', 'This value is greater that 48')
                if math > 44:
                    self.add_error('math', 'This value is greater that 44')
                if social_emotional > 40:
                    self.add_error('social_emotional', 'This value is greater that 40')
                if psychomotor > 34:
                    self.add_error('psychomotor', 'This value is greater that 34')
                if science > 36:
                    self.add_error('science', 'This value is greater that 36')
                if artistic > 12:
                    self.add_error('artistic', 'This value is greater that 12')
            else:
                if arabic > 60:
                    self.add_error('arabic', 'This value is greater that 60')
                if english > 60:
                    self.add_error('english', 'This value is greater that 60')
                if math > 46:
                    self.add_error('math', 'This value is greater that 46')
                if social_emotional > 40:
                    self.add_error('social_emotional', 'This value is greater that 40')
                if psychomotor > 36:
                    self.add_error('psychomotor', 'This value is greater that 36')
                if science > 36:
                    self.add_error('science', 'This value is greater that 36')
                if artistic > 12:
                    self.add_error('artistic', 'This value is greater that 12')

    def save(self, instance=None, request=None):
        instance = super(CBECEMidAssessmentForm, self).save()
        # instance = super(CBECEMidAssessmentForm, self).save(request=request, instance=instance, serializer=CBECESerializer)

        instance.modified_by = request.user
        instance.mid_test = {
                "CBECE_ASSESSMENT/attended_arabic": request.POST.get('attended_arabic'),
                "CBECE_ASSESSMENT/modality_arabic": request.POST.getlist('modality_arabic'),
                "CBECE_ASSESSMENT/arabic": request.POST.get('arabic'),

                "CBECE_ASSESSMENT/attended_english": request.POST.get('attended_english'),
                "CBECE_ASSESSMENT/modality_english": request.POST.getlist('modality_english'),
                "CBECE_ASSESSMENT/english": request.POST.get('english'),

                "CBECE_ASSESSMENT/attended_psychomotor": request.POST.get('attended_psychomotor'),
                "CBECE_ASSESSMENT/modality_psychomotor": request.POST.getlist('modality_psychomotor'),
                "CBECE_ASSESSMENT/psychomotor": request.POST.get('psychomotor'),

                "CBECE_ASSESSMENT/attended_math": request.POST.get('attended_math'),
                "CBECE_ASSESSMENT/modality_math": request.POST.getlist('modality_math'),
                "CBECE_ASSESSMENT/math": request.POST.get('math'),

                "CBECE_ASSESSMENT/attended_social": request.POST.get('attended_social'),
                "CBECE_ASSESSMENT/modality_social": request.POST.getlist('modality_social'),
                "CBECE_ASSESSMENT/social_emotional": request.POST.get('social_emotional'),

                "CBECE_ASSESSMENT/attended_science": request.POST.get('attended_science'),
                "CBECE_ASSESSMENT/modality_science": request.POST.getlist('modality_science'),
                "CBECE_ASSESSMENT/science": request.POST.get('science'),

                "CBECE_ASSESSMENT/attended_artistic": request.POST.get('attended_artistic'),
                "CBECE_ASSESSMENT/modality_artistic": request.POST.getlist('modality_artistic'),
                "CBECE_ASSESSMENT/artistic": request.POST.get('artistic')
            }

        instance.save()
        messages.success(request, _('Your data has been sent successfully to the server'))

    class Meta:
        model = CBECE
        fields = (
            'mid_test_done',
        )

class BLNAdminForm(forms.ModelForm):

    student = forms.ModelChoiceField(
        queryset=Student.objects.all(),
        widget=autocomplete.ModelSelect2(url='student_autocomplete')
    )

    def __init__(self, *args, **kwargs):
        super(BLNAdminForm, self).__init__(*args, **kwargs)

    class Meta:
        model = BLN
        fields = '__all__'

class ABLNAdminForm(forms.ModelForm):

    student = forms.ModelChoiceField(
        queryset=Student.objects.all(),
        widget=autocomplete.ModelSelect2(url='student_autocomplete')
    )

    def __init__(self, *args, **kwargs):
        super(ABLNAdminForm, self).__init__(*args, **kwargs)

    class Meta:
        model = ABLN
        fields = '__all__'

class RSAdminForm(forms.ModelForm):

    student = forms.ModelChoiceField(
        queryset=Student.objects.all(),
        widget=autocomplete.ModelSelect2(url='student_autocomplete')
    )

    def __init__(self, *args, **kwargs):
        super(RSAdminForm, self).__init__(*args, **kwargs)

    class Meta:
        model = RS
        fields = '__all__'

class InclusionAdminForm(forms.ModelForm):

    student = forms.ModelChoiceField(
        queryset=Student.objects.all(),
        widget=autocomplete.ModelSelect2(url='student_autocomplete')
    )

    def __init__(self, *args, **kwargs):
        super(InclusionAdminForm, self).__init__(*args, **kwargs)

    class Meta:
        model = BLN
        fields = '__all__'

class CBECEAdminForm(forms.ModelForm):

    student = forms.ModelChoiceField(
        queryset=Student.objects.all(),
        widget=autocomplete.ModelSelect2(url='student_autocomplete')
    )

    def __init__(self, *args, **kwargs):
        super(CBECEAdminForm, self).__init__(*args, **kwargs)

    class Meta:
        model = CBECE
        fields = '__all__'

class RSAssessmentForm(forms.ModelForm):
    REGISTRATION_LEVEL = (
        ('', '----------'),
        ('level_two', _('Level two')),
        ('level_three', _('Level three'))
    )
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
    learning_result = forms.ChoiceField(
        label=_('Based on the overall score, what is the recommended learning path?'),
        widget=forms.Select, required=True,
        choices=(
            ('', '----------'),
            ('graduated_to_rs_next_round_higher_level', _('Progress to FE higher grade next year')),
            ('graduated_to_rs_next_round_same_level', _('Repeat same grade next year')),
            ('referred_alp', _('Referred to ALP')),
            ('graduated_to_tvet', _('Referred to TVET')),
            ('other', _('Other')),
        ),
        initial=''
    )
    learning_result_other = forms.CharField(
        label=_('Please specify'),
        widget=forms.TextInput, required=False
    )
    barriers_single = forms.ChoiceField(
        label=_('The main barriers affecting the daily attendance and performance '
                'of the child or drop out of programme? (Select more than one if applicable)'),
        choices= (
            ('Full time job to support family financially', _('Full time job to support family financially')),
            ('seasonal_work', _('Seasonal work')),
            ('availablity_electronic_device', _('Availablity of Electronic Device')),
            ('internet_connectivity', _('Internet Connectivity')),
            ('sickness', _('Sickness')),
            ('security', _('Security')),
            ('family_moved', _('Family moved')),
            ('Moved back to Syria', _('Moved back to Syria')),
            ('Enrolled in formal education', _('Enrolled in formal education')),
            ('violence bullying', _('Violence/Bullying')),
            ('No interest in pursuing the programme/No value', _('No interest in pursuing the programme/No value')),
            ('other', _('Other')),
        ),
        widget=forms.Select,
        required=True
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

    basic_stationery = forms.ChoiceField(
        label=_("Did the child receive basic stationery?"),
        widget=forms.Select, required=True,
        choices=CLM.YES_NO
    )
    # pss_kit = forms.ChoiceField(
    #         label=_("Did the child benefit from the PSS kit?"),
    #         widget=forms.Select, required=True,
    #         choices=CLM.YES_NO
    # )
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
    attended_english = forms.ChoiceField(
        label=_("Attended English test"),
        widget=forms.Select, required=True,
        choices=(('yes', _("Yes")), ('no', _("No"))),
        initial='yes'
    )
    modality_english = forms.MultipleChoiceField(
        label=_('Please indicate modality'),
        choices=CLM.MODALITY,
        widget=forms.CheckboxSelectMultiple,
        required=False
    )
    english = forms.FloatField(
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
    attended_biology = forms.ChoiceField(
        label=_("Attended biology test"),
        widget=forms.Select, required=True,
        choices=(('yes', _("Yes")), ('no', _("No"))),
        initial='yes'
    )
    modality_biology = forms.MultipleChoiceField(
        label=_('Please indicate modality'),
        choices=CLM.MODALITY,
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    biology = forms.FloatField(
        label=_('Results'),
        widget=forms.NumberInput(attrs=({'maxlength': 4})),
        min_value=0, required=False
    )
    attended_science = forms.ChoiceField(
        label=_("Attended Science test"),
        widget=forms.Select, required=True,
        choices=(('yes', _("Yes")), ('no', _("No"))),
        initial='yes'
    )
    modality_science = forms.MultipleChoiceField(
        label=_('Please indicate modality'),
        choices=CLM.MODALITY,
        widget=forms.CheckboxSelectMultiple,
        required=False
    )
    science = forms.FloatField(
        label=_('Results'),
        widget=forms.NumberInput(attrs=({'maxlength': 4})),
        min_value=0, required=False
    )
    attended_chemistry = forms.ChoiceField(
        label=_("Attended chemistry test"),
        widget=forms.Select, required=True,
        choices=(('yes', _("Yes")), ('no', _("No"))),
        initial='yes'
    )
    modality_chemistry = forms.MultipleChoiceField(
        label=_('Please indicate modality'),
        choices=CLM.MODALITY,
        widget=forms.CheckboxSelectMultiple,
        required=False
    )
    chemistry = forms.FloatField(
        label=_('Results'),
        widget=forms.NumberInput(attrs=({'maxlength': 4})),
        min_value=0, required=False
    )

    attended_physics = forms.ChoiceField(
        label=_("Attended physics test"),
        widget=forms.Select, required=True,
        choices=(('yes', _("Yes")), ('no', _("No"))),
        initial='yes'
    )
    modality_physics = forms.MultipleChoiceField(
        label=_('Please indicate modality'),
        choices=CLM.MODALITY,
        widget=forms.CheckboxSelectMultiple,
        required=False
    )
    physics = forms.FloatField(
        label=_('Results'),
        widget=forms.NumberInput(attrs=({'maxlength': 4})),
        min_value=0, required=False
    )
    follow_up_type = forms.ChoiceField(
        label=_('Type of follow up'),
        widget=forms.Select, required=False,
        choices=(
            ('none', _('----------')),
            ('Phone', _('Phone Call')),
            ('House visit', _('House Visit')),
            ('Family Visit', _('Family Visit')),
        ),
        initial=''
    )
    phone_call_number = forms.IntegerField(
        label=_('Please enter the number phone calls'),
        widget=forms.NumberInput(attrs=({'maxlength': 4})),
        min_value=0, required=False
    )
    house_visit_number = forms.IntegerField(
        label=_('Please enter the number of house visits'),
        widget=forms.NumberInput(attrs=({'maxlength': 4})),
        min_value=0, required=False
    )
    family_visit_number = forms.IntegerField(
        label=_('Please enter the number parent visits'),
        widget=forms.NumberInput(attrs=({'maxlength': 4})),
        min_value=0, required=False
    )
    phone_call_follow_up_result = forms.ChoiceField(
        label=_('Result of follow up'),
        widget=forms.Select, required=False,
        choices=(
            ('child back', _('Child returned to Round')),
            ('child transfer to difficulty center', _('Child referred to specialized services')),
            ('child transfer to protection', _('Child referred to protection')),
            ('child transfer to medical', _('Child referred to Health programme')),
            ('Intensive followup', _('Follow-up with parents')),
            ('dropout', _('Dropout/No Interest')),
        ),
        initial=''
    )
    house_visit_follow_up_result = forms.ChoiceField(
        label=_('Result of follow up'),
        widget=forms.Select, required=False,
        choices=(
            ('child back', _('Child returned to Round')),
            ('child transfer to difficulty center', _('Child referred to specialized services')),
            ('child transfer to protection', _('Child referred to protection')),
            ('child transfer to medical', _('Child referred to Health programme')),
            ('Intensive followup', _('Follow-up with parents')),
            ('dropout', _('Dropout/No Interest')),
        ),
        initial=''
    )
    family_visit_follow_up_result = forms.ChoiceField(
        label=_('Result of follow up'),
        widget=forms.Select, required=False,
        choices=(
            ('child back', _('Child returned to Round')),
            ('child transfer to difficulty center', _('Child referred to specialized services')),
            ('child transfer to protection', _('Child referred to protection')),
            ('child transfer to medical', _('Child referred to Health programme')),
            ('Intensive followup', _('Follow-up with parents')),
            ('dropout', _('Dropout/No Interest')),
        ),
        initial=''
    )
    parent_attended_visits = forms.ChoiceField(
        label=_("Parents attended parents meeting"),
        widget=forms.Select, required=False,
        choices=(('yes', _("Yes")), ('no', _("No"))),
        initial='yes'
    )
    cp_referral = forms.ChoiceField(
        label=_("CP Followup"),
        widget=forms.Select, required=True,
        choices=(
            ('', '----------'),
            ('yes', _("Yes")),
            ('no', _("No")))
    )
    pss_session_attended = forms.ChoiceField(
        label=_("Attended PSS Session"),
        widget=forms.Select, required=True,
        choices=(('yes', _("Yes")), ('no', _("No")))
    )
    pss_session_number = forms.IntegerField(
        label=_('Please enter the number of sessions'),
        widget=forms.NumberInput(attrs=({'maxlength': 4})),
        min_value=0, required=False
    )
    pss_session_modality = forms.MultipleChoiceField(
        label=_('Please indicate modality'),
        choices=CLM.SESSION_MODALITY,
        widget=forms.CheckboxSelectMultiple,
        required=False
    )
    pss_parent_attended = forms.ChoiceField(
        label=_("Parent who attended the parents meeting"),
        widget=forms.Select, required=False,
        choices=(
            ('', '----------'),
            ('mother', _('Mother')),
            ('father', _('Father')),
            ('other', _('Other')),
        )
    )
    pss_parent_attended_other = forms.CharField(
        label=_('Please specify'),
        widget=forms.TextInput, required=False
    )
    covid_session_attended = forms.ChoiceField(
        label=_("Attended covid Session"),
        widget=forms.Select, required=True,
        choices=(('yes', _("Yes")), ('no', _("No")))
    )
    covid_session_number = forms.IntegerField(
        label=_('Please enter the number of sessions'),
        widget=forms.NumberInput(attrs=({'maxlength': 4})),
        min_value=0, required=False
    )
    covid_session_modality = forms.MultipleChoiceField(
        label=_('Please indicate modality'),
        choices=CLM.SESSION_MODALITY,
        widget=forms.CheckboxSelectMultiple,
        required=False
    )
    covid_parent_attended = forms.ChoiceField(
        label=_("Parent who attended the parents meeting"),
        widget=forms.Select, required=False,
        choices=(
            ('', '----------'),
            ('mother', _('Mother')),
            ('father', _('Father')),
            ('other', _('Other')),
        )
    )
    covid_parent_attended_other = forms.CharField(
        label=_('Please specify'),
        widget=forms.TextInput, required=False
    )
    followup_session_attended = forms.ChoiceField(
        label=_("Attended followup Session"),
        widget=forms.Select, required=True,
        choices=(('yes', _("Yes")), ('no', _("No")))
    )
    followup_session_number = forms.IntegerField(
        label=_('Please enter the number of sessions'),
        widget=forms.NumberInput(attrs=({'maxlength': 4})),
        min_value=0, required=False
    )

    followup_session_modality = forms.MultipleChoiceField(
        label=_('Please indicate modality'),
        choices=CLM.SESSION_MODALITY,
        widget=forms.CheckboxSelectMultiple,
        required=False
    )
    followup_parent_attended = forms.ChoiceField(
        label=_("Parent who attended the parents meeting"),
        widget=forms.Select, required=False,
        choices=(
            ('', '----------'),
            ('mother', _('Mother')),
            ('father', _('Father')),
            ('other', _('Other')),
        )
    )
    followup_parent_attended_other = forms.CharField(
        label=_('Please specify'),
        widget=forms.TextInput, required=False
    )
    child_health_examed = forms.ChoiceField(
        label=_("Did the child receive health exam"),
        widget=forms.Select, required=False,
        choices=(('yes', _("Yes")), ('no', _("No"))),
        initial='yes'
    )
    child_health_concern = forms.ChoiceField(
        label=_("Anything to worry about"),
        widget=forms.Select, required=False,
        choices=(('yes', _("Yes")), ('no', _("No"))),
        initial='yes'
    )

    clm_type = forms.CharField(widget=forms.HiddenInput, required=False)
    registration_level = forms.CharField(widget=forms.HiddenInput, required=False)

    registration_level = forms.ChoiceField(
        label=_("Registration level"),
        widget=forms.Select, required=False,
        choices=REGISTRATION_LEVEL
    )

    grade_registration =  forms.ChoiceField(
        label=_("Grade of registeration"),
        widget=forms.Select, required=True,
        choices=(
            ('', '----------'),
            ('6', _('6')),
            ('7', _('7')),
            ('8', _('8')),
            ('9', _('9')),
        )
    )

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(RSAssessmentForm, self).__init__(*args, **kwargs)

        post_test = ''
        post_test_button = ' btn-outline-secondary disabled'
        instance = kwargs['instance'] if 'instance' in kwargs else ''
        self.fields['clm_type'].initial = 'RS'

        display_assessment = ''
        form_action = reverse('clm:rs_post_assessment', kwargs={'pk': instance.id})

        if instance.post_test:
            post_test_button = ' btn-outline-success '
            post_test = instance.assessment_form(
                stage='post_test',
                assessment_slug='rs_post_test',
                callback=self.request.build_absolute_uri(
                    reverse('clm:rs_post_assessment', kwargs={'pk': instance.id}))
            )

        self.helper = FormHelper()
        self.helper.form_show_labels = True
        self.helper.form_action = form_action
        self.helper.layout = Layout(
            Fieldset(
                None,
                Div(
                    HTML('<h4 id="alternatives-to-hidden-labels">' + _('Assessment data') + '</h4>'),
                ),
            ),
            Fieldset(
                None,
                Div(
                    HTML('<span>A</span>'), css_class='block_tag'),
                Div(
                    HTML('<h4 id="alternatives-to-hidden-labels">' + _('School evaluation') + '</h4>')
                ),
                Div(
                    Div('grade_registration', css_class='col-md-3 d-none'),
                    css_class='row',
                ),
                Div(
                    HTML('<span class="badge badge-default">1</span>'),
                    Div('participation', css_class='col-md-2'),
                    HTML('<span class="badge badge-default" id="span_barriers_single">1.1</span>'),
                    Div('barriers_single', css_class='col-md-2'),
                    HTML('<span class="badge badge-default" id="span_barriers_other">1.2</span>'),
                    Div('barriers_other', css_class='col-md-2'),
                    css_class='row',
                ),
                Div(
                    HTML('<span class="badge badge-default">2</span>'),
                    Div('test_done', css_class='col-md-4'),
                    HTML('<span class="badge badge-default" id="span_round_complete">2.1</span>'),
                    Div('round_complete', css_class='col-md-4'),
                    css_class='row',
                ),
                Div(
                    HTML('<span class="badge badge-default">3</span>'),
                    Div('basic_stationery', css_class='col-md-3'),
                    # HTML('<span class="badge badge-default">4</span>'),
                    # Div('pss_kit', css_class='col-md-3'),
                    css_class='row',
                ),
                Div(
                    HTML('<span class="badge badge-default">4</span>'),
                    Div('learning_result', css_class='col-md-4'),
                    HTML('<span class="badge badge-default" id="span_blearning_result_other">4.1</span>'),
                    Div('learning_result_other', css_class='col-md-2'),
                    css_class='row',
                ),
                Div(
                    HTML('<span class="badge badge-default">5</span>'),
                    Div('cp_referral', css_class='col-md-3'),
                    css_class='row',
                ),
                Div(
                    HTML('<span class="badge badge-default">1</span>'),
                    Div('attended_arabic', css_class='col-md-2'),
                    HTML('<span class="badge badge-default" id="span_modality_arabic">1.1</span>'),
                    Div('modality_arabic', css_class='col-md-2 multiple-checbkoxes'),
                    HTML('<span class="badge badge-default" id="span_arabic">1.2</span>'),
                    Div('arabic', css_class='col-md-2'),
                    css_class='row grades',
                ),
                Div(
                    HTML('<span class="badge badge-default">2</span>'),
                    Div('attended_english', css_class='col-md-2'),
                    HTML('<span class="badge badge-default" id="span_modality_english">2.1</span>'),
                    Div('modality_english', css_class='col-md-2 multiple-checbkoxes'),
                    HTML('<span class="badge badge-default" id="span_english">2.2</span>'),
                    Div('english', css_class='col-md-2'),
                    css_class='row grades',
                ),
                Div(
                    HTML('<span class="badge badge-default">3</span>'),
                    Div('attended_math', css_class='col-md-2'),
                    HTML('<span class="badge badge-default" id="span_modality_math">3.1</span>'),
                    Div('modality_math', css_class='col-md-2 multiple-checbkoxes'),
                    HTML('<span class="badge badge-default" id="span_math">3.2</span>'),
                    Div('math', css_class='col-md-2'),
                    css_class='row grades',
                ),
                Div(
                    HTML('<span class="badge badge-default">4</span>'),
                    Div('attended_science', css_class='col-md-2'),
                    HTML('<span class="badge badge-default" id="span_modality_science">4.1</span>'),
                    Div('modality_science', css_class='col-md-2 multiple-checbkoxes'),
                    HTML('<span class="badge badge-default" id="span_science">4.2</span>'),
                    Div('science', css_class='col-md-2'),
                    css_class='row grd6 grades',
                ),
                Div(
                    HTML('<span class="badge badge-default">4</span>'),
                    Div('attended_biology', css_class='col-md-2'),
                    HTML('<span class="badge badge-default" id="span_modality_biology">4.1</span>'),
                    Div('modality_biology', css_class='col-md-2 multiple-checbkoxes'),
                    HTML('<span class="badge badge-default" id="span_biology">4.2</span>'),
                    Div('biology', css_class='col-md-2'),
                    css_class='row grd7 grades',
                ),

                Div(
                    HTML('<span class="badge badge-default">5</span>'),
                    Div('attended_chemistry', css_class='col-md-2'),
                    HTML('<span class="badge badge-default" id="span_modality_chemistry">5.1</span>'),
                    Div('modality_chemistry', css_class='col-md-2 multiple-checbkoxes'),
                    HTML('<span class="badge badge-default" id="span_chemistry">5.2</span>'),
                    Div('chemistry', css_class='col-md-2'),
                    css_class='row grd7 grades',
                ),

                Div(
                    HTML('<span class="badge badge-default">6</span>'),
                    Div('attended_physics', css_class='col-md-2'),
                    HTML('<span class="badge badge-default" id="span_modality_physics">6.1</span>'),
                    Div('modality_physics', css_class='col-md-2 multiple-checbkoxes'),
                    HTML('<span class="badge badge-default" id="span_physics">6.2</span>'),
                    Div('physics', css_class='col-md-2'),
                    css_class='row grd7 grades',
                ),
                css_class='bd-callout bd-callout-warning A_right_border'
            ),
            Fieldset(
                None,
                Div(
                    HTML('<span>B</span>'), css_class='block_tag'),
                Div(
                    HTML('<h4 id="alternatives-to-hidden-labels">' + _('Follow up') + '</h4>')
                ),
                Div(
                    HTML('<span class="badge badge-default">1</span>'),
                    Div('phone_call_number', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">1.1</span>'),
                    Div('phone_call_follow_up_result', css_class='col-md-3'),
                    css_class='row'
                ),
                Div(
                    HTML('<span class="badge badge-default">2</span>'),
                    Div('house_visit_number', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">2.1</span>'),
                    Div('house_visit_follow_up_result', css_class='col-md-3'),
                    css_class='row'
                ),
                Div(
                    HTML('<span class="badge badge-default">3</span>'),
                    Div('family_visit_number', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">3.1</span>'),
                    Div('family_visit_follow_up_result', css_class='col-md-3'),
                    css_class='row'
                ),
                id='follow_up',
                css_class='bd-callout bd-callout-warning B_right_border'
            ),

            Fieldset(
                None,
                Div(
                    HTML('<span>C</span>'), css_class='block_tag'),
                None,
                Div(
                    HTML('<h4 id="alternatives-to-hidden-labels">' + _('Parents Meeting and Health Exam') + '</h4>')
                ),
                Div(
                    HTML('<span class="badge badge-default">1</span>'),
                    Div('parent_attended_visits', css_class='col-md-3'),
                    # HTML('<span class="badge badge-default">2</span>'),
                    # Div('visits_number', css_class='col-md-4'),
                    css_class='row',
                ),

                Div(
                    HTML('<span class="badge badge-default">2</span>'),
                    Div('pss_session_attended', css_class='col-md-2'),
                    HTML('<span class="badge badge-default" id="span_pss_session_modality">2.1</span>'),
                    Div('pss_session_modality', css_class='col-md-2 multiple-checbkoxes'),
                    HTML('<span class="badge badge-default" id="span_pss_session_number">2.2</span>'),
                    Div('pss_session_number', css_class='col-md-2'),
                    HTML('<span class="badge badge-default" id="span_pss_parent_attended">5</span>'),
                    Div('pss_parent_attended', css_class='col-md-2'),
                    HTML('<span class="badge badge-default" id="span_pss_parent_attended_other">5.1</span>'),
                    Div('pss_parent_attended_other', css_class='col-md-2'),
                    css_class='row parent_visits',
                ),
                Div(
                    HTML('<span class="badge badge-default">3</span>'),
                    Div('covid_session_attended', css_class='col-md-2'),
                    HTML('<span class="badge badge-default" id="span_covid_session_modality">3.1</span>'),
                    Div('covid_session_modality', css_class='col-md-2 multiple-checbkoxes'),
                    HTML('<span class="badge badge-default" id="span_covid_session_number">3.2</span>'),
                    Div('covid_session_number', css_class='col-md-2'),
                    HTML('<span class="badge badge-default" id="span_covid_parent_attended">5</span>'),
                    Div('covid_parent_attended', css_class='col-md-2'),
                    HTML('<span class="badge badge-default" id="span_covid_parent_attended_other">5.1</span>'),
                    Div('covid_parent_attended_other', css_class='col-md-2'),
                    css_class='row parent_visits',
                ),
                Div(
                    HTML('<span class="badge badge-default">4</span>'),
                    Div('followup_session_attended', css_class='col-md-2'),
                    HTML('<span class="badge badge-default" id="span_followup_session_modality">4.1</span>'),
                    Div('followup_session_modality', css_class='col-md-2 multiple-checbkoxes'),
                    HTML('<span class="badge badge-default" id="span_followup_session_number">4.2</span>'),
                    Div('followup_session_number', css_class='col-md-2'),
                    HTML('<span class="badge badge-default" id="span_followup_parent_attended">5</span>'),
                    Div('followup_parent_attended', css_class='col-md-2'),
                    HTML('<span class="badge badge-default" id="span_followup_parent_attended_other">5.1</span>'),
                    Div('followup_parent_attended_other', css_class='col-md-2'),
                    css_class='row parent_visits',
                ),

                # Div(
                #     HTML('<span class="badge badge-default">4</span>'),
                #     Div('child_health_examed', css_class='col-md-4'),
                #     HTML('<span class="badge badge-default">5</span>'),
                #     Div('child_health_concern', css_class='col-md-4'),
                #     css_class='row',
                # ),
                id= 'visits',
                css_class='bd-callout bd-callout-warning C_right_border'+ display_assessment,
            ),
            FormActions(
                Submit('save', _('Save'), css_class='col-md-2'),
                HTML('<a class="btn btn-info cancel-button" href="/clm/rs-list/" translation="' +
                     _('Are you sure you want to cancel this registration?') + '">' + _('Back to list') + '</a>'),
            )
        )

    def clean(self):
        cleaned_data = super(RSAssessmentForm, self).clean()

        attended_arabic = cleaned_data.get("attended_arabic")
        modality_arabic = cleaned_data.get("modality_arabic")
        arabic = cleaned_data.get("arabic")

        attended_english = cleaned_data.get("attended_english")
        modality_english = cleaned_data.get("modality_english")
        english = cleaned_data.get("english")

        attended_math = cleaned_data.get("attended_math")
        modality_math = cleaned_data.get("modality_math")
        math = cleaned_data.get("math")

        attended_science = cleaned_data.get("attended_science")
        modality_science = cleaned_data.get("modality_science")
        science = cleaned_data.get("science")

        attended_biology = cleaned_data.get("attended_biology")
        modality_biology = cleaned_data.get("modality_biology")
        biology = cleaned_data.get("biology")

        attended_chemistry = cleaned_data.get("attended_chemistry")
        modality_chemistry = cleaned_data.get("modality_chemistry")
        chemistry = cleaned_data.get("chemistry")

        attended_physics = cleaned_data.get("attended_physics")
        modality_physics = cleaned_data.get("modality_physics")
        physics = cleaned_data.get("physics")

        learning_result = cleaned_data.get("learning_result")
        learning_result_other = cleaned_data.get("learning_result_other")
        barriers_single = cleaned_data.get("barriers_single")
        barriers_other = cleaned_data.get("barriers_other")

        test_done = cleaned_data.get("test_done")
        round_complete = cleaned_data.get("round_complete")
        grade_registration = cleaned_data.get("grade_registration")


        if test_done == 'yes':
            if not round_complete:
                self.add_error('round_complete', 'This field is required')

        if learning_result != 'no_absence':
            if not barriers_single:
                self.add_error('barriers_single', 'This field is required')

        if learning_result == 'other':
            if not learning_result_other:
                self.add_error('learning_result_other', 'This field is required')

        if barriers_single == 'other':
            if not barriers_other:
                self.add_error('barriers_other', 'This field is required')

        if test_done == 'yes':
            if attended_arabic == 'yes':
                if not modality_arabic:
                    self.add_error('modality_arabic', 'This field is required')
                if arabic is None:
                    self.add_error('arabic', 'This field is required')

            if attended_english == 'yes':
                if not modality_english:
                    self.add_error('modality_english', 'This field is required')
                if english is None:
                    self.add_error('english', 'This field is required')

            if attended_math == 'yes':
                if not modality_math:
                    self.add_error('modality_math', 'This field is required')
                if math is None:
                    self.add_error('math', 'This field is required')

            if grade_registration == '6' :
                if attended_science == 'yes':
                    if not modality_science:
                        self.add_error('modality_science', 'This field is required')
                    if science is None:
                        self.add_error('science', 'This field is required')
            elif grade_registration == '7' or grade_registration == '8' or grade_registration == '9':

                if attended_biology == 'yes':
                    if not modality_biology:
                        self.add_error('modality_biology', 'This field is required')
                    if biology is None:
                        self.add_error('biology', 'This field is required')

                if attended_chemistry == 'yes':
                    if not modality_chemistry:
                        self.add_error('modality_chemistry', 'This field is required')
                    if chemistry is None:
                        self.add_error('chemistry', 'This field is required')

                if attended_physics == 'yes':
                    if not modality_physics:
                        self.add_error('modality_physics', 'This field is required')
                    if physics is None:
                        self.add_error('physics', 'This field is required')

            # grades Max Value validation
            if grade_registration == '6':
                if arabic > 20:
                    self.add_error('arabic', 'This value is greater that 20')
                if english > 20:
                    self.add_error('english', 'This value is greater that 20')
                if math > 20:
                    self.add_error('math', 'This value is greater that 20')
                if science > 20:
                    self.add_error('science', 'This value is greater that 20')
            elif grade_registration == '7' or grade_registration == '8' or grade_registration == '9':

                if arabic > 60:
                    self.add_error('arabic', 'This value is greater that 60')
                if english > 40:
                    self.add_error('english', 'This value is greater that 40')
                if math > 60:
                    self.add_error('math', 'This value is greater that 60')
                if biology > 20:
                    self.add_error('biology', 'This value is greater that 20')
                if chemistry > 20:
                    self.add_error('chemistry', 'This value is greater that 20')
                if physics > 20:
                    self.add_error('physics', 'This value is greater that 20')


    def save(self, instance=None, request=None):
        instance = super(RSAssessmentForm, self).save()
        # instance = super(RSAssessmentForm, self).save(request=request, instance=instance, serializer=RSSerializer)

        instance.modified_by = request.user
        # instance.pss_session_modality = request.POST.getlist('pss_session_modality')
        # instance.covid_session_modality = request.POST.getlist('covid_session_modality')
        # instance.followup_session_modality = request.POST.getlist('followup_session_modality')

        instance.post_test = {
            # arabic, english, math, science, biology, chemistry, physics
            "RS_ASSESSMENT/attended_arabic": request.POST.get('attended_arabic'),
            "RS_ASSESSMENT/modality_arabic": request.POST.getlist('modality_arabic'),
            "RS_ASSESSMENT/arabic": request.POST.get('arabic'),

            "RS_ASSESSMENT/attended_english": request.POST.get('attended_english'),
            "RS_ASSESSMENT/modality_english": request.POST.getlist('modality_english'),
            "RS_ASSESSMENT/english": request.POST.get('english'),

            "RS_ASSESSMENT/attended_math": request.POST.get('attended_math'),
            "RS_ASSESSMENT/modality_math": request.POST.getlist('modality_math'),
            "RS_ASSESSMENT/math": request.POST.get('math'),

            "RS_ASSESSMENT/attended_science": request.POST.get('attended_science'),
            "RS_ASSESSMENT/modality_science": request.POST.getlist('modality_science'),
            "RS_ASSESSMENT/science": request.POST.get('science'),

            "RS_ASSESSMENT/attended_biology": request.POST.get('attended_biology'),
            "RS_ASSESSMENT/modality_biology": request.POST.getlist('modality_biology'),
            "RS_ASSESSMENT/biology": request.POST.get('biology'),

            "RS_ASSESSMENT/attended_chemistry": request.POST.get('attended_chemistry'),
            "RS_ASSESSMENT/modality_chemistry": request.POST.getlist('modality_chemistry'),
            "RS_ASSESSMENT/chemistry": request.POST.get('chemistry'),

            "RS_ASSESSMENT/attended_physics": request.POST.get('attended_physics'),
            "RS_ASSESSMENT/modality_physics": request.POST.getlist('modality_physics'),
            "RS_ASSESSMENT/physics": request.POST.get('physics'),
            }

        instance.save()
        messages.success(request, _('Your data has been sent successfully to the server'))

    class Meta:
        model = RS
        fields = (
            'participation',
            'barriers_single',
            'barriers_other',
            'test_done',
            'round_complete',
            'basic_stationery',
            # 'pss_kit',
            'learning_result',
            'phone_call_number',
            'house_visit_number',
            'family_visit_number',
            'phone_call_follow_up_result' ,
            'house_visit_follow_up_result' ,
            'family_visit_follow_up_result' ,
            'parent_attended_visits',
            'pss_session_attended',
            'pss_session_number',
            'pss_session_modality',
            'pss_parent_attended',
            'pss_parent_attended_other',
            'covid_session_attended',
            'covid_session_number',
            'covid_session_modality',
            'covid_parent_attended',
            'covid_parent_attended_other',
            'followup_session_attended',
            'followup_session_number',
            'followup_session_modality',
            'followup_parent_attended_other',
            'followup_parent_attended',
            'cp_referral',
            'learning_result_other',
            # 'child_health_examed',
            # 'child_health_concern',
        )

class BLNReferralForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(BLNReferralForm, self).__init__(*args, **kwargs)

        instance = kwargs['instance']

        self.helper = FormHelper()
        self.helper.form_show_labels = True
        self.helper.form_action = reverse('clm:bln_referral', kwargs={'pk': instance.id})
        self.helper.layout = Layout(
            Fieldset(
                None,
                Div(css_class='block_tag'),
                Div(
                    Div(HTML('<span>1</span>'), css_class='block_tag'),
                    HTML('<h4 id="alternatives-to-hidden-labels">' + _('Referral 1') + '</h4>'),
                ),
                Div(
                    HTML('<span class="badge badge-default">1</span>'),
                    Div('referral_programme_type_1', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">2</span>'),
                    Div('referral_partner_1', css_class='col-md-3'),
                    css_class='row',
                ),
                Div(
                    HTML('<span class="badge badge-default">3</span>'),
                    Div('referral_date_1', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">4</span>'),
                    Div('confirmation_date_1', css_class='col-md-3'),
                    css_class='row',
                ),
                css_class='bd-callout bd-callout-warning A_right_border'
            ),
            Fieldset(
                None,
                Div(
                    Div(HTML('<span>2</span>'), css_class='block_tag'),
                    HTML('<h4 id="alternatives-to-hidden-labels">' + _('Referral 2') + '</h4>')
                ),
                Div(
                    HTML('<span class="badge badge-default">1</span>'),
                    Div('referral_programme_type_2', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">2</span>'),
                    Div('referral_partner_2', css_class='col-md-3'),
                    css_class='row',
                ),
                Div(
                    HTML('<span class="badge badge-default">3</span>'),
                    Div('referral_date_2', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">4</span>'),
                    Div('confirmation_date_2', css_class='col-md-3'),
                    css_class='row',
                ),
                css_class='bd-callout bd-callout-warning B_right_border'
            ),
            Fieldset(
                None,
                Div(
                    Div(HTML('<span>3</span>'), css_class='block_tag'),
                    HTML('<h4 id="alternatives-to-hidden-labels">' + _('Referral 3') + '</h4>')
                ),
                Div(
                    HTML('<span class="badge badge-default">1</span>'),
                    Div('referral_programme_type_3', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">2</span>'),
                    Div('referral_partner_3', css_class='col-md-3'),
                    css_class='row',
                ),
                Div(
                    HTML('<span class="badge badge-default">3</span>'),
                    Div('referral_date_3', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">4</span>'),
                    Div('confirmation_date_3', css_class='col-md-3'),
                    css_class='row',
                ),
                css_class='bd-callout bd-callout-warning C_right_border'
            ),

            FormActions(
                Submit('save', _('Save')),
                HTML('<a class="btn btn-info" href="/clm/bln-list/">' + _('Back to list') + '</a>'),
            )
        )

    def save(self, instance=None, request=None):
        instance = super(BLNReferralForm, self).save()
        instance.modified_by = request.user
        instance.save()
        messages.success(request, _('Your data has been sent successfully to the server'))

    class Meta:
        model = BLN
        fields = (
            'referral_programme_type_1',
            'referral_partner_1',
            'referral_date_1',
            'confirmation_date_1',
            'referral_programme_type_2',
            'referral_partner_2',
            'referral_date_2',
            'confirmation_date_2',
            'referral_programme_type_3',
            'referral_partner_3',
            'referral_date_3',
            'confirmation_date_3',
        )

    class Media:
        js = (
            # 'js/validator.js',
        )

class BLNFollowupForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(BLNFollowupForm, self).__init__(*args, **kwargs)

        instance = kwargs['instance']

        self.helper = FormHelper()
        self.helper.form_show_labels = True
        self.helper.form_action = reverse('clm:bln_followup', kwargs={'pk': instance.id})
        self.helper.layout = Layout(
            Fieldset(
                None,
                Div(
                    HTML('<h4 id="alternatives-to-hidden-labels">' + _('Follow-up first call') + '</h4>')
                ),
                Div(
                    HTML('<span class="badge badge-default">1</span>'),
                    Div('followup_call_date_1', css_class='col-md-3'),
                    css_class='row',
                ),
                Div(
                    HTML('<span class="badge badge-default">2</span>'),
                    Div('followup_call_reason_1', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">3</span>'),
                    Div('followup_call_result_1', css_class='col-md-3'),
                    css_class='row',
                ),
                css_class='bd-callout bd-callout-warning'
            ),
            Fieldset(
                None,
                Div(
                    HTML('<h4 id="alternatives-to-hidden-labels">' + _('Follow-up second call') + '</h4>')
                ),
                Div(
                    HTML('<span class="badge badge-default">1</span>'),
                    Div('followup_call_date_2', css_class='col-md-3'),
                    css_class='row',
                ),
                Div(
                    HTML('<span class="badge badge-default">2</span>'),
                    Div('followup_call_reason_2', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">3</span>'),
                    Div('followup_call_result_2', css_class='col-md-3'),
                    css_class='row',
                ),
                css_class='bd-callout bd-callout-warning'
            ),
            Fieldset(
                None,
                Div(
                    HTML('<h4 id="alternatives-to-hidden-labels">' + _('Follow-up Household visit') + '</h4>')
                ),
                Div(
                    HTML('<span class="badge badge-default">1</span>'),
                    Div('followup_visit_date_1', css_class='col-md-3'),
                    css_class='row',
                ),
                Div(
                    HTML('<span class="badge badge-default">2</span>'),
                    Div('followup_visit_reason_1', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">3</span>'),
                    Div('followup_visit_result_1', css_class='col-md-3'),
                    css_class='row',
                ),
                css_class='bd-callout bd-callout-warning'
            ),
            FormActions(
                Submit('save', _('Save')),
                HTML('<a class="btn btn-info" href="/clm/bln-list/">' + _('Back to list') + '</a>'),
            )
        )

    def save(self, instance=None, request=None):
        instance = super(BLNFollowupForm, self).save()
        instance.modified_by = request.user
        instance.save()
        messages.success(request, _('Your data has been sent successfully to the server'))

    class Meta:
        model = BLN
        fields = (
            'followup_call_date_1',
            'followup_call_reason_1',
            'followup_call_result_1',
            'followup_call_date_2',
            'followup_call_reason_2',
            'followup_call_result_2',
            'followup_visit_date_1',
            'followup_visit_reason_1',
            'followup_visit_result_1',
        )

    class Media:
        js = (
            # 'js/validator.js',
        )

class ABLNReferralForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(ABLNReferralForm, self).__init__(*args, **kwargs)

        instance = kwargs['instance']

        self.helper = FormHelper()
        self.helper.form_show_labels = True
        self.helper.form_action = reverse('clm:abln_referral', kwargs={'pk': instance.id})
        self.helper.layout = Layout(
            Fieldset(
                None,
                Div(css_class='block_tag'),
                Div(
                    Div(HTML('<span>1</span>'), css_class='block_tag'),
                    HTML('<h4 id="alternatives-to-hidden-labels">' + _('Referral 1') + '</h4>'),
                ),
                Div(
                    HTML('<span class="badge badge-default">1</span>'),
                    Div('referral_programme_type_1', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">2</span>'),
                    Div('referral_partner_1', css_class='col-md-3'),
                    css_class='row',
                ),
                Div(
                    HTML('<span class="badge badge-default">3</span>'),
                    Div('referral_date_1', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">4</span>'),
                    Div('confirmation_date_1', css_class='col-md-3'),
                    css_class='row',
                ),
                css_class='bd-callout bd-callout-warning A_right_border'
            ),
            Fieldset(
                None,
                Div(
                    Div(HTML('<span>2</span>'), css_class='block_tag'),
                    HTML('<h4 id="alternatives-to-hidden-labels">' + _('Referral 2') + '</h4>')
                ),
                Div(
                    HTML('<span class="badge badge-default">1</span>'),
                    Div('referral_programme_type_2', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">2</span>'),
                    Div('referral_partner_2', css_class='col-md-3'),
                    css_class='row',
                ),
                Div(
                    HTML('<span class="badge badge-default">3</span>'),
                    Div('referral_date_2', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">4</span>'),
                    Div('confirmation_date_2', css_class='col-md-3'),
                    css_class='row',
                ),
                css_class='bd-callout bd-callout-warning B_right_border'
            ),
            Fieldset(
                None,
                Div(
                    Div(HTML('<span>3</span>'), css_class='block_tag'),
                    HTML('<h4 id="alternatives-to-hidden-labels">' + _('Referral 3') + '</h4>')
                ),
                Div(
                    HTML('<span class="badge badge-default">1</span>'),
                    Div('referral_programme_type_3', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">2</span>'),
                    Div('referral_partner_3', css_class='col-md-3'),
                    css_class='row',
                ),
                Div(
                    HTML('<span class="badge badge-default">3</span>'),
                    Div('referral_date_3', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">4</span>'),
                    Div('confirmation_date_3', css_class='col-md-3'),
                    css_class='row',
                ),
                css_class='bd-callout bd-callout-warning C_right_border'
            ),
            FormActions(
                Submit('save', _('Save')),
                HTML('<a class="btn btn-info" href="/clm/abln-list/">' + _('Back to list') + '</a>'),
            )
        )

    def save(self, instance=None, request=None):
        instance = super(ABLNReferralForm, self).save()
        instance.modified_by = request.user
        instance.save()
        messages.success(request, _('Your data has been sent successfully to the server'))

    class Meta:
        model = ABLN
        fields = (
            'referral_programme_type_1',
            'referral_partner_1',
            'referral_date_1',
            'confirmation_date_1',
            'referral_programme_type_2',
            'referral_partner_2',
            'referral_date_2',
            'confirmation_date_2',
            'referral_programme_type_3',
            'referral_partner_3',
            'referral_date_3',
            'confirmation_date_3',
        )

    class Media:
        js = (
            # 'js/validator.js',
        )

class ABLNFollowupForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(ABLNFollowupForm, self).__init__(*args, **kwargs)

        instance = kwargs['instance']

        self.helper = FormHelper()
        self.helper.form_show_labels = True
        self.helper.form_action = reverse('clm:abln_followup', kwargs={'pk': instance.id})
        self.helper.layout = Layout(
            Fieldset(
                None,
                Div(
                    HTML('<h4 id="alternatives-to-hidden-labels">' + _('Follow-up first call') + '</h4>')
                ),
                Div(
                    HTML('<span class="badge badge-default">1</span>'),
                    Div('followup_call_date_1', css_class='col-md-3'),
                    css_class='row',
                ),
                Div(
                    HTML('<span class="badge badge-default">2</span>'),
                    Div('followup_call_reason_1', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">3</span>'),
                    Div('followup_call_result_1', css_class='col-md-3'),
                    css_class='row',
                ),
                css_class='bd-callout bd-callout-warning'
            ),
            Fieldset(
                None,
                Div(
                    HTML('<h4 id="alternatives-to-hidden-labels">' + _('Follow-up second call') + '</h4>')
                ),
                Div(
                    HTML('<span class="badge badge-default">1</span>'),
                    Div('followup_call_date_2', css_class='col-md-3'),
                    css_class='row',
                ),
                Div(
                    HTML('<span class="badge badge-default">2</span>'),
                    Div('followup_call_reason_2', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">3</span>'),
                    Div('followup_call_result_2', css_class='col-md-3'),
                    css_class='row',
                ),
                css_class='bd-callout bd-callout-warning'
            ),
            Fieldset(
                None,
                Div(
                    HTML('<h4 id="alternatives-to-hidden-labels">' + _('Follow-up Household visit') + '</h4>')
                ),
                Div(
                    HTML('<span class="badge badge-default">1</span>'),
                    Div('followup_visit_date_1', css_class='col-md-3'),
                    css_class='row',
                ),
                Div(
                    HTML('<span class="badge badge-default">2</span>'),
                    Div('followup_visit_reason_1', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">3</span>'),
                    Div('followup_visit_result_1', css_class='col-md-3'),
                    css_class='row',
                ),
                css_class='bd-callout bd-callout-warning'
            ),
            FormActions(
                Submit('save', _('Save')),
                HTML('<a class="btn btn-info" href="/clm/abln-list/">' + _('Back to list') + '</a>'),
            )
        )

    def save(self, instance=None, request=None):
        instance = super(ABLNFollowupForm, self).save()
        instance.modified_by = request.user
        instance.save()
        messages.success(request, _('Your data has been sent successfully to the server'))

    class Meta:
        model = ABLN
        fields = (
            'followup_call_date_1',
            'followup_call_reason_1',
            'followup_call_result_1',
            'followup_call_date_2',
            'followup_call_reason_2',
            'followup_call_result_2',
            'followup_visit_date_1',
            'followup_visit_reason_1',
            'followup_visit_result_1',
        )

    class Media:
        js = (
            # 'js/validator.js',
        )

class CBECEReferralForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(CBECEReferralForm, self).__init__(*args, **kwargs)

        instance = kwargs['instance']

        self.helper = FormHelper()
        self.helper.form_show_labels = True
        self.helper.form_action = reverse('clm:cbece_referral', kwargs={'pk': instance.id})
        self.helper.layout = Layout(
            Fieldset(
                None,
                Div(
                    HTML('<h4 id="alternatives-to-hidden-labels">' + _('Referral 1') + '</h4>')
                ),
                Div(
                    HTML('<span class="badge badge-default">1</span>'),
                    Div('referral_programme_type_1', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">2</span>'),
                    Div('referral_partner_1', css_class='col-md-3'),
                    css_class='row',
                ),
                Div(
                    HTML('<span class="badge badge-default">3</span>'),
                    Div('referral_date_1', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">4</span>'),
                    Div('confirmation_date_1', css_class='col-md-3'),
                    css_class='row',
                ),
                css_class='bd-callout bd-callout-warning'
            ),
            Fieldset(
                None,
                Div(
                    HTML('<h4 id="alternatives-to-hidden-labels">' + _('Referral 2') + '</h4>')
                ),
                Div(
                    HTML('<span class="badge badge-default">1</span>'),
                    Div('referral_programme_type_2', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">2</span>'),
                    Div('referral_partner_2', css_class='col-md-3'),
                    css_class='row',
                ),
                Div(
                    HTML('<span class="badge badge-default">3</span>'),
                    Div('referral_date_2', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">4</span>'),
                    Div('confirmation_date_2', css_class='col-md-3'),
                    css_class='row',
                ),
                css_class='bd-callout bd-callout-warning'
            ),
            Fieldset(
                None,
                Div(
                    HTML('<h4 id="alternatives-to-hidden-labels">' + _('Referral 3') + '</h4>')
                ),
                Div(
                    HTML('<span class="badge badge-default">1</span>'),
                    Div('referral_programme_type_3', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">2</span>'),
                    Div('referral_partner_3', css_class='col-md-3'),
                    css_class='row',
                ),
                Div(
                    HTML('<span class="badge badge-default">3</span>'),
                    Div('referral_date_3', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">4</span>'),
                    Div('confirmation_date_3', css_class='col-md-3'),
                    css_class='row',
                ),
                css_class='bd-callout bd-callout-warning'
            ),
            FormActions(
                Submit('save', _('Save')),
                HTML('<a class="btn btn-info" href="/clm/cbece-list/">' + _('Back to list') + '</a>'),
            )
        )

    def save(self, instance=None, request=None):
        instance = super(CBECEReferralForm, self).save()
        instance.modified_by = request.user
        instance.save()
        messages.success(request, _('Your data has been sent successfully to the server'))

    class Meta:
        model = CBECE
        fields = (
            'referral_programme_type_1',
            'referral_partner_1',
            'referral_date_1',
            'confirmation_date_1',
            'referral_programme_type_2',
            'referral_partner_2',
            'referral_date_2',
            'confirmation_date_2',
            'referral_programme_type_3',
            'referral_partner_3',
            'referral_date_3',
            'confirmation_date_3',
        )

    class Media:
        js = (
            # 'js/validator.js',
        )

class CBECEFollowupForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(CBECEFollowupForm, self).__init__(*args, **kwargs)

        instance = kwargs['instance']

        self.helper = FormHelper()
        self.helper.form_show_labels = True
        self.helper.form_action = reverse('clm:cbece_followup', kwargs={'pk': instance.id})
        self.helper.layout = Layout(
            Fieldset(
                None,
                Div(
                    HTML('<h4 id="alternatives-to-hidden-labels">' + _('Follow-up first call') + '</h4>')
                ),
                Div(
                    HTML('<span class="badge badge-default">1</span>'),
                    Div('followup_call_date_1', css_class='col-md-3'),
                    css_class='row',
                ),
                Div(
                    HTML('<span class="badge badge-default">2</span>'),
                    Div('followup_call_reason_1', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">3</span>'),
                    Div('followup_call_result_1', css_class='col-md-3'),
                    css_class='row',
                ),
                css_class='bd-callout bd-callout-warning'
            ),
            Fieldset(
                None,
                Div(
                    HTML('<h4 id="alternatives-to-hidden-labels">' + _('Follow-up second call') + '</h4>')
                ),
                Div(
                    HTML('<span class="badge badge-default">1</span>'),
                    Div('followup_call_date_2', css_class='col-md-3'),
                    css_class='row',
                ),
                Div(
                    HTML('<span class="badge badge-default">2</span>'),
                    Div('followup_call_reason_2', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">3</span>'),
                    Div('followup_call_result_2', css_class='col-md-3'),
                    css_class='row',
                ),
                css_class='bd-callout bd-callout-warning'
            ),
            Fieldset(
                None,
                Div(
                    HTML('<h4 id="alternatives-to-hidden-labels">' + _('Follow-up Household visit') + '</h4>')
                ),
                Div(
                    HTML('<span class="badge badge-default">1</span>'),
                    Div('followup_visit_date_1', css_class='col-md-3'),
                    css_class='row',
                ),
                Div(
                    HTML('<span class="badge badge-default">2</span>'),
                    Div('followup_visit_reason_1', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">3</span>'),
                    Div('followup_visit_result_1', css_class='col-md-3'),
                    css_class='row',
                ),
                css_class='bd-callout bd-callout-warning'
            ),
            FormActions(
                Submit('save', _('Save')),
                HTML('<a class="btn btn-info" href="/clm/cbece-list/">' + _('Back to list') + '</a>'),
            )
        )

    def save(self, instance=None, request=None):
        instance = super(CBECEFollowupForm, self).save()
        instance.modified_by = request.user
        instance.save()
        messages.success(request, _('Your data has been sent successfully to the server'))

    class Meta:
        model = CBECE
        fields = (
            'followup_call_date_1',
            'followup_call_reason_1',
            'followup_call_result_1',
            'followup_call_date_2',
            'followup_call_reason_2',
            'followup_call_result_2',
            'followup_visit_date_1',
            'followup_visit_reason_1',
            'followup_visit_result_1',
        )

    class Media:
        js = (
            # 'js/validator.js',
        )

class ABLNPreFCForm(forms.ModelForm):
    facilitator_name = forms.CharField(
        label=_('Facilitator name'),
        widget=forms.TextInput, required=True
    )
    subject_taught = forms.CharField(
        label=_('Subject taught'),
        widget=forms.TextInput, required=True
    )
    date_of_monitoring = forms.DateField(
        label=_("Date of monitoring"),
        required=True
    )
    numbers_child_monitored = forms.IntegerField(
        label=_('Number of times the child has been monitored to date'),
        widget=forms.NumberInput(attrs=({'maxlength': 4})),
        min_value=0, required=False
    )
    topic_covered = forms.CharField(
        label=_('Activities/ topic covered'),
        widget=forms.TextInput, required=True
    )
    materials_needed = forms.CharField(
        label=_('Materials needed for the lesson (teaching/ learning)'),
        widget=forms.TextInput, required=True
    )

    materials_needed_available = forms.ChoiceField(
        widget=forms.Select, required=True,
        choices=ABLN_FC.YES_NO ,
        label=_('Did the child have these learning materials available for the lesson?')
    )
    materials_needed_reason_no = forms.CharField(
        label=_('Reason'),
        widget=forms.TextInput, required=True
    )
    remote_learning = forms.ChoiceField(
        widget=forms.Select, required=True,
        choices=ABLN_FC.YES_NO ,
        label=_('Was the child involved in remote learning?')
    )
    share_expectations_caregiver = forms.ChoiceField(
        widget=forms.Select, required=True,
        choices=ABLN_FC.YES_NO ,
        label=_('Did you share the expectations with their caregiver for the weekly engagement in learning?')
    )
    share_expectations_no_reason = forms.CharField(
        label=_('Reason'),
        widget=forms.TextInput, required=True
    )
    child_engaged_lesson = forms.ChoiceField(
        widget=forms.Select, required=True,
        choices=ABLN_FC.YES_NO ,
        label=_('Was the child engaged in the lesson and understood the content?')
    )
    child_engaged_lesson_explain = forms.CharField(
        label=_('How was this verified?'),
        widget=forms.TextInput, required=True
    )

    child_participate_others = forms.ChoiceField(
        widget=forms.Select, required=True,
        choices=ABLN_FC.YES_NO ,
        label=_('Did the child participate with others on time?')
    )
    child_participate_others_no_explain = forms.CharField(
        label=_('Please explain Why'),
        widget=forms.TextInput, required=True
    )

    child_expected_work_independently = forms.ChoiceField(
        widget=forms.Select, required=True,
        choices=ABLN_FC.YES_NO ,
        label=_('Was the child expected to work independently?')
    )
    child_meet_lesson_objectives = forms.ChoiceField(
        widget=forms.Select, required=True,
        choices=ABLN_FC.YES_NO ,
        label=_('Did the child meet the previous lesson objectives?')
    )
    child_meet_lesson_objectives_verified = forms.CharField(
        label=_('How was this verified?'),
        widget=forms.TextInput, required=True
    )
    homework_after_lesson = forms.ChoiceField(
        widget=forms.Select, required=True,
        choices=ABLN_FC.YES_NO ,
        label=_('Was there any homework given after the lesson?')
    )
    homework_after_lesson_explain = forms.CharField(
        label=_('Please explain'),
        widget=forms.TextInput, required=True
    )
    homework_score = forms.IntegerField(
        label=_('(if applicable) What score did the child receive on the homework?'),
        widget=forms.NumberInput(attrs=({'maxlength': 4})),
        min_value=0, required=False
    )
    homework_score_explain = forms.CharField(
        label=_('How was the Grading and Feedback on the homework given?'),
        widget=forms.TextInput, required=True
    )

    parents_supporting_student = forms.ChoiceField(
        widget=forms.Select, required=True,
        choices=ABLN_FC.YES_NO ,
        label=_('Were parents supporting the student through this lesson?')
    )
    parents_supporting_student_explain = forms.CharField(
        label=_('Please explain'),
        widget=forms.TextInput, required=True
    )
    child_complete_printed_package = forms.ChoiceField(
        widget=forms.Select, required=True,
        choices=ABLN_FC.YES_NO ,
        label=_('(if applicable) Did the child complete the printed package for the week?')
    )
    number_child_participate_online = forms.IntegerField(
        label=_('How many times did this child participate in online classes this week?'),
        widget=forms.NumberInput(attrs=({'maxlength': 4})),
        min_value=0, required=False
    )
    how_make_sure_child_access_online = forms.CharField(
        label=_('How did you make sure that the child was able to login/access the online lessons?'),
        widget=forms.TextInput, required=True
    )
    followup_not_join_online = forms.CharField(
        label=_('How do you follow up if the child does not join / engage in online learning?'),
        widget=forms.TextInput, required=True
    )
    times_voice_contact_child_caregiver = forms.IntegerField(
        label=_('How many times do you have voice contact with the child/caregiver per week?'),
        widget=forms.NumberInput(attrs=({'maxlength': 4})),
        min_value=0, required=False
    )
    child_coping_home_learning = forms.ChoiceField(
        widget=forms.Select, required=True,
        choices=ABLN_FC.YES_NO ,
        label=_('Is the child coping with home-based learning? ')
    )
    child_caregiver_challenges = forms.CharField(
        label=_('What challenges does this child face? child/caregiver?'),
        widget=forms.TextInput, required=True
    )
    actions_before_next_class = forms.CharField(
        label=_('What specific actions need to be taken with this child before the next class?'),
        widget=forms.TextInput, required=True
    )
    actions_before_next_class_how = forms.CharField(
        label=_('Please explain'),
        widget=forms.TextInput, required=True
    )
    girls_boys_participate_access_device = forms.ChoiceField(
        widget=forms.Select, required=True,
        choices=ABLN_FC.YES_NO ,
        label=_(
            '(if applicable) Did both girls and boys in the same family participate in the class and have access to the phone/ device?')
    )
    girls_boys_participate_explain = forms.CharField(
        label=_('Please explain'),
        widget=forms.TextInput, required=True
    )

    how_often_contact_caregivers = forms.ChoiceField(
        widget=forms.Select, required=True,
        choices=ABLN_FC.CONTACT_LEARNING_CLOSED ,
        label=_('How often do you keep in touch with parents /caregivers of this child since the learning center closed?')
    )
    how_contact_caregivers = forms.MultipleChoiceField(
        label=_('How do you keep in touch with parents / caregivers?'),
        choices=ABLN_FC.CONTACT_CAREGIVER,
        widget=forms.CheckboxSelectMultiple,
        required=False
    )
    how_keep_touch_caregivers_specify = forms.CharField(
        label=_('Please Specify'),
        widget=forms.TextInput, required=True
    )
    child_awareness_prevention_covid19 = forms.ChoiceField(
        widget=forms.Select, required=True,
        choices=ABLN_FC.YES_NO ,
        label=_('Has the child been reached with awareness messaging on Covid-19 and prevention measures?')
    )
    followup_done_messages = forms.ChoiceField(
        widget=forms.Select, required=True,
        choices=ABLN_FC.YES_NO ,
        label=_('Was any follow-up done with the child to ensure message(s) received and understood?')
    )
    followup_explain = forms.CharField(
        label=_('Please Specify'),
        widget=forms.TextInput, required=True
    )
    child_practice_basic_handwashing = forms.ChoiceField(
        widget=forms.Select, required=True,
        choices=ABLN_FC.YES_NO ,
        label=_('Does this child practice basic handwashing? ')
    )
    child_practice_basic_handwashing_explain = forms.CharField(
        label=_('Please Specify'),
        widget=forms.TextInput, required=True
    )
    child_have_pss_wellbeing = forms.ChoiceField(
        widget=forms.Select, required=True,
        choices=ABLN_FC.YES_NO ,
        label=_('Does the child have any PSS/ wellbeing needs?')
    )
    child_have_pss_wellbeing_explain = forms.CharField(
        label=_('Please Specify'),
        widget=forms.TextInput, required=True
    )
    additional_notes = forms.CharField(
        label=_('Additional notes/ specific challenges/ follow up action/ referrals etc.'),
        widget=forms.TextInput, required=True
    )

    abln_id = forms.CharField(widget=forms.HiddenInput, required=False)
    fc_type = forms.CharField(widget=forms.HiddenInput, required=False)

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(ABLNPreFCForm, self).__init__(*args, **kwargs)

        instance = kwargs['instance'] if 'instance' in kwargs else ''
        data = kwargs['initial'] if 'initial' in kwargs else ''
        abln_id= data.get('abln_id')
        fc_type= data.get('fc_type')

        print('------------------------------------------------------------------------')
        print('------------------------------------------------------------------------')
        print('------------------------------------------------------------------------')

        print (abln_id)
        print (fc_type)

        print('------------------------------------------------------------------------')
        print('------------------------------------------------------------------------')
        print('------------------------------------------------------------------------')
        form_action = reverse('clm:abln_pre_fc_add', kwargs = {'abln_id': abln_id, 'fc_type': fc_type})
        self.fields['abln_id'].initial = abln_id
        self.fields['fc_type'].initial = fc_type

        if instance:
            form_action = reverse('clm:abln_pre_fc_edit', kwargs = {'abln_id': abln_id, 'fc_type': fc_type})
            # form_action = reverse('clm:abln_pre_fc_edit', kwargs={'pk': instance.id})

        self.helper = FormHelper()
        self.helper.form_show_labels = True
        self.helper.form_action = form_action
        self.helper.layout = Layout(
            Fieldset(
                None,
                Div(
                    HTML('<span>A</span>'), css_class='block_tag'),
                Div(
                    HTML('<h4 id="alternatives-to-hidden-labels">' + _('FE Partner & Facilitator details') + '</h4>')
                ),
                Div(
                    'enrollment_id',
                    'abln_id',
                    'fc_type',
                    css_class='row',
                ),
                Div(
                    HTML('<span class="badge badge-default">1</span>'),
                    Div('facilitator_name', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">2</span>'),
                    Div('subject_taught', css_class='col-md-3'),
                    css_class='row',
                ),
                css_class='bd-callout bd-callout-warning  A_right_border'
            ),
            Fieldset(
                None,
                Div(
                    HTML('<span>B</span>'), css_class='block_tag'),
                Div(
                    HTML('<h4 id="alternatives-to-hidden-labels">' + _('Individual child details') + '</h4>')
                ),

                Div(
                    HTML('<span class="badge badge-default">1</span>'),
                    Div('date_of_monitoring', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">2</span>'),
                    Div('numbers_child_monitored', css_class='col-md-3'),
                    css_class='row',
                ),
                css_class='bd-callout bd-callout-warning  B_right_border'
            ),
            Fieldset(
                None,
                Div(HTML('<span>C</span>'), css_class='block_tag'),
                Div(
                    HTML('<h4 id="alternatives-to-hidden-labels">' + _('Lesson details') + '</h4>')
                ),
                Div(
                    HTML('<span class="badge badge-default">1</span>'),
                    Div('topic_covered', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">2</span>'),
                    Div('materials_needed', css_class='col-md-3'),
                    css_class='row',
                ),
                Div(
                    HTML('<span class="badge badge-default">3</span>'),
                    Div('materials_needed_available', css_class='col-md-3'),
                    HTML('<span class="badge badge-default" id="span_materials_needed_reason_no">3.1</span>'),
                    Div('materials_needed_reason_no', css_class='col-md-3'),
                    css_class='row',
                ),
                css_class='bd-callout bd-callout-warning  C_right_border'
            ),
            Fieldset(
                None,
                Div(
                    HTML('<span>D</span>'), css_class='block_tag'),
                Div(
                    HTML('<h4 id="alternatives-to-hidden-labels">' + _('Content shared this week (subject)') + '</h4>')
                ),

                Div(
                    HTML('<span class="badge badge-default">1</span>'),
                    Div('remote_learning', css_class='col-md-3'),
                    css_class='row',
                ),
                css_class='bd-callout bd-callout-warning  D_right_border'
            ),

            Fieldset(
                None,
                Div(HTML('<span>E</span>'), css_class='block_tag'),
                Div(
                    HTML('<h4 id="alternatives-to-hidden-labels">' + _('Modality & preparation:') + '</h4>')
                ),
                Div(
                    HTML('<span class="badge badge-default">1</span>'),
                    Div('share_expectations_caregiver', css_class='col-md-3'),
                    HTML('<span class="badge badge-default" id="span_share_expectations_no_reason">1.1</span>'),
                    Div('share_expectations_no_reason', css_class='col-md-3', css_id='student_have_children'),
                    css_class='row',
                ),
                css_class='bd-callout bd-callout-warning child_data D_right_border'
            ),
            Fieldset(

                None,
                Div(
                    HTML('<span>F</span>'), css_class='block_tag'),
                Div(
                    HTML('<h4 id="alternatives-to-hidden-labels">' + _('Weekly lesson') + '</h4>')
                ),
                Div(
                    HTML('<span class="badge badge-default">1</span>'),
                    Div('child_engaged_lesson', css_class='col-md-3'),
                    HTML('<span class="badge badge-default" id="span_child_engaged_lesson_explain">1.1</span>'),
                    Div('child_engaged_lesson_explain', css_class='col-md-3 '),
                    css_class='row',
                ),
                Div(
                    HTML('<span class="badge badge-default">2</span>'),
                    Div('child_participate_others', css_class='col-md-3'),
                    HTML('<span class="badge badge-default" id="span_child_participate_others_no_explain">2.1</span>'),
                    Div('child_participate_others_no_explain', css_class='col-md-3 '),
                    css_class='row',
                ),
                Div(
                    HTML('<span class="badge badge-default">3</span>'),
                    Div('child_expected_work_independently', css_class='col-md-3'),
                    css_class='row',
                ),
                Div(
                    HTML('<span class="badge badge-default">4</span>'),
                    Div('child_meet_lesson_objectives', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">4.1</span>'),
                    Div('child_meet_lesson_objectives_verified', css_class='col-md-3 '),
                    css_class='row',
                ),
                Div(
                    HTML('<span class="badge badge-default">5</span>'),
                    Div('homework_after_lesson', css_class='col-md-3'),
                    HTML('<span class="badge badge-default" id="span_homework_after_lesson_explain">5.1</span>'),
                    Div('homework_after_lesson_explain', css_class='col-md-3 '),
                    css_class='row',
                ),
                Div(
                    HTML('<span class="badge badge-default">6</span>'),
                    Div('homework_score', css_class='col-md-3'),
                    HTML('<span class="badge badge-default" id="span_homework_score_explain">6.1</span>'),
                    Div('homework_score_explain', css_class='col-md-3 '),
                    css_class='row',
                ),
                Div(
                    HTML('<span class="badge badge-default">6</span>'),
                    Div('parents_supporting_student', css_class='col-md-3'),
                    HTML('<span class="badge badge-default" id="span_parents_supporting_student_explain">6.1</span>'),
                    Div('parents_supporting_student_explain', css_class='col-md-3 '),
                    css_class='row',
                ),
                css_class='bd-callout bd-callout-warning F_right_border'
            ),

            Fieldset(

                None,
                Div(
                    HTML('<span>G</span>'), css_class='block_tag'),
                Div(
                    HTML('<h4 id="alternatives-to-hidden-labels">' + _('Feedback about home-based/distance learning from this child/caregiver') + '</h4>')
                ),
                Div(
                    HTML('<span class="badge badge-default">1</span>'),
                    Div('child_complete_printed_package', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">2</span>'),
                    Div('number_child_participate_online', css_class='col-md-3 '),
                    css_class='row',
                ),
                Div(
                    HTML('<span class="badge badge-default">3</span>'),
                    Div('how_make_sure_child_access_online', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">4</span>'),
                    Div('followup_not_join_online', css_class='col-md-3 '),
                    css_class='row',
                ),
                Div(
                    HTML('<span class="badge badge-default">5</span>'),
                    Div('times_voice_contact_child_caregiver', css_class='col-md-3'),
                    css_class='row',
                ),
                css_class='bd-callout bd-callout-warning A_right_border'
            ),
            Fieldset(

                None,
                Div(
                    HTML('<span>H</span>'), css_class='block_tag'),
                Div(
                    HTML('<h4 id="alternatives-to-hidden-labels">' + _('Follow up actions') + '</h4>')
                ),
                Div(
                    HTML('<span class="badge badge-default">1</span>'),
                    Div('child_coping_home_learning', css_class='col-md-3'),
                    HTML('<span class="badge badge-default" id="span_child_engaged_lesson_explain">2</span>'),
                    Div('child_caregiver_challenges', css_class='col-md-3 '),
                    css_class='row',
                ),
                Div(
                    HTML('<span class="badge badge-default">3</span>'),
                    Div('actions_before_next_class', css_class='col-md-3'),
                    HTML('<span class="badge badge-default" id="span_actions_before_next_class_how">3.1</span>'),
                    Div('actions_before_next_class_how', css_class='col-md-3 '),
                    css_class='row',
                ),
                css_class='bd-callout bd-callout-warning B_right_border'
            ),
            Fieldset(

                None,
                Div(
                    HTML('<span>H</span>'), css_class='block_tag'),
                Div(
                    HTML('<h4 id="alternatives-to-hidden-labels">' + _('Gender considerations') + '</h4>')
                ),
                Div(
                    HTML('<span class="badge badge-default">1</span>'),
                    Div('girls_boys_participate_access_device', css_class='col-md-3'),
                    HTML('<span class="badge badge-default" id="span_girls_boys_participate_explain">1.1</span>'),
                    Div('girls_boys_participate_explain', css_class='col-md-3 '),
                    css_class='row',
                ),
                css_class='bd-callout bd-callout-warning C_right_border'
            ),
            Fieldset(

                None,
                Div(
                    HTML('<span>I</span>'), css_class='block_tag'),
                Div(
                    HTML('<h4 id="alternatives-to-hidden-labels">' + _('Covid-19 PSS/ Wellbeing') + '</h4>')
                ),
                Div(
                    HTML('<span class="badge badge-default">1</span>'),
                    Div('how_often_contact_caregivers', css_class='col-md-3'),

                    HTML('<span class="badge badge-default">2</span>'),
                    Div('how_contact_caregivers', css_class='col-md-2 multiple-checbkoxes'),
                    HTML('<span class="badge badge-default" id="span_how_keep_touch_caregivers_specify">2.1</span>'),
                    Div('how_keep_touch_caregivers_specify', css_class='col-md-3 '),
                    css_class='row',
                ),
                Div(
                    HTML('<span class="badge badge-default">3</span>'),
                    Div('child_awareness_prevention_covid19', css_class='col-md-3'),
                    css_class='row',
                ),
                Div(
                    HTML('<span class="badge badge-default">4</span>'),
                    Div('followup_done_messages', css_class='col-md-3'),
                    HTML('<span class="badge badge-default" id="span_followup_explain">4.1</span>'),
                    Div('followup_explain', css_class='col-md-3 '),
                    css_class='row',
                ),
                Div(
                    HTML('<span class="badge badge-default">4</span>'),
                    Div('child_practice_basic_handwashing', css_class='col-md-3'),
                    HTML('<span class="badge badge-default" id="span_child_practice_basic_handwashing_explain">4.1</span>'),
                    Div('child_practice_basic_handwashing_explain', css_class='col-md-3 '),
                    css_class='row',
                ),
                Div(
                    HTML('<span class="badge badge-default">4</span>'),
                    Div('child_have_pss_wellbeing', css_class='col-md-3'),
                    HTML('<span class="badge badge-default" id="span_child_have_pss_wellbeing_explain">4.1</span>'),
                    Div('child_have_pss_wellbeing_explain', css_class='col-md-3 '),
                    css_class='row',
                ),
                Div(
                    HTML('<span class="badge badge-default">4</span>'),
                    Div('additional_notes', css_class='col-md-3'),
                    css_class='row',
                ),
                # ''
                css_class='bd-callout bd-callout-warning D_right_border'
            ),
            FormActions(
                Submit('save', _('Save'), css_class='col-md-2'),
                Submit('save_add_another', _('Save and add another'), css_class='col-md-2 child_data col-md-2'),
                HTML('<a class="btn btn-info cancel-button" href="/clm/abln-list/" translation="' + _(
                    'Are you sure you want to cancel this registration?') + '">' + _('Back to list') + '</a>'),
                css_class='button-group'
            )
        )

    def clean(self):
        cleaned_data = super(ABLNPreFCForm, self).clean()

    def save(self, instance=None, request=None):
        instance = super(ABLNPreFCForm, self).save()
        instance.modified_by = request.user
        instance.save()
        messages.success(request, _('Your data has been sent successfully to the server'))

    class Meta:
        model = ABLN_FC
        fields = (
            'abln_id',
            'fc_type',
            'facilitator_name',
            'subject_taught',
            'date_of_monitoring',
            'numbers_child_monitored',
            'topic_covered',
            'materials_needed_available',
            'materials_needed_reason_no',
            'remote_learning',
            'share_expectations_caregiver',
            'share_expectations_no_reason',
            'child_engaged_lesson',
            'child_engaged_lesson_explain',
            'child_participate_others',
            'child_participate_others_no_explain',
            'child_expected_work_independently',
            'child_meet_lesson_objectives',
            'child_meet_lesson_objectives_verified',
            'homework_after_lesson',
            'homework_after_lesson_explain',
            'homework_score',
            'homework_score_explain',
            'parents_supporting_student',
            'parents_supporting_student_explain',
            'child_complete_printed_package',
            'number_child_participate_online',
            'how_make_sure_child_access_online',
            'followup_not_join_online',
            'times_voice_contact_child_caregiver',
            'child_coping_home_learning',
            'child_caregiver_challenges',
            'actions_before_next_class',
            'actions_before_next_class_how',
            'girls_boys_participate_access_device',
            'girls_boys_participate_explain',
            'how_often_contact_caregivers',
            'how_contact_caregivers',
            'how_keep_touch_caregivers_specify',
            'child_awareness_prevention_covid19',
            'followup_done_messages',
            'followup_explain',
            'child_practice_basic_handwashing',
            'child_practice_basic_handwashing_explain',
            'child_have_pss_wellbeing',
            'child_have_pss_wellbeing_explain',
            'additional_notes'
        )
