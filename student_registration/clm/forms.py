from __future__ import unicode_literals, absolute_import, division

from django.utils.translation import ugettext as _
from django import forms
from django.core.urlresolvers import reverse

from crispy_forms.helper import FormHelper
from crispy_forms.bootstrap import FormActions, Accordion, PrependedText, InlineCheckboxes, InlineRadios
from crispy_forms.layout import Layout, Fieldset, Button, Submit, Div, Field, HTML
from dal import autocomplete

from student_registration.students.models import (
    Student,
    Nationality,
)
from student_registration.schools.models import (
    School,
    ClassRoom,
    EducationalLevel,
)
from student_registration.locations.models import Location
from .models import (
    CLM,
    BLN,
    RS,
    CBECE,
    Cycle,
    Disability,
    Assessment
)
from .serializers import BLNSerializer, RSSerializer, CBECESerializer

YES_NO_CHOICE = ((1, _("Yes")), (0, _("No")))

YEARS = list(((str(x), x) for x in range(1990, 2050)))
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
    ('more_than_15days', _('More than 15 absence days'))
)

LEARNING_RESULT = (
    ('', '----------'),
    ('repeat_level', _('Repeat level')),
    ('graduated_next_level', _('Graduated to the next level')),
    ('graduated_to_formal_kg', _('Graduated to formal education - KG')),
    ('graduated_to_formal_level1', _('Graduated to formal education - Level 1')),
    ('referred_to_another_program', _('Referred to another program')),
    ('dropout', _('Dropout from school'))
)


class CommonForm(forms.ModelForm):

    new_registry = forms.ChoiceField(
        label=_("First time registered?"),
        widget=forms.Select, required=True,
        choices=(('yes', _("Yes")), ('no', _("No"))),
        initial='yes'
    )
    student_outreached = forms.ChoiceField(
        label=_("Student outreached?"),
        widget=forms.Select, required=True,
        choices=(('yes', _("Yes")), ('no', _("No"))),
        initial='yes'
    )
    have_barcode = forms.ChoiceField(
        label=_("Have barcode with him?"),
        widget=forms.Select, required=True,
        choices=(('yes', _("Yes")), ('no', _("No"))),
        initial='yes'
    )
    search_student = forms.CharField(
        label=_("Search a student"),
        widget=forms.TextInput,
        required=False
    )
    search_barcode = forms.CharField(
        label=_("Search a barcode"),
        widget=forms.TextInput,
        required=False
    )

    governorate = forms.ModelChoiceField(
        queryset=Location.objects.filter(parent__isnull=True), widget=forms.Select,
        label=_('Governorate'),
        empty_label='-------',
        required=True, to_field_name='id',
        initial=0
    )
    district = forms.ModelChoiceField(
        queryset=Location.objects.filter(parent__isnull=False), widget=forms.Select,
        label=_('District'),
        empty_label='-------',
        required=True, to_field_name='id',
        initial=0
    )
    # location = forms.CharField(
    #     label=_('Location'),
    #     widget=forms.TextInput,
    #     required=True
    # )
    language = forms.MultipleChoiceField(
        label=_('The language supported in the program'),
        choices=CLM.LANGUAGES,
        widget=forms.CheckboxSelectMultiple,
        required=True,
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
    student_birthday_year = forms.ChoiceField(
        label=_("Birthday year"),
        widget=forms.Select, required=True,
        choices=YEARS
    )
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
        queryset=Nationality.objects.all(), widget=forms.Select,
        required=True, to_field_name='id',
    )
    student_mother_fullname = forms.CharField(
        label=_("Mother fullname"),
        widget=forms.TextInput, required=True
    )
    # student_address = forms.CharField(
    #     label=_("The area where the child resides"),
    #     widget=forms.TextInput, required=True
    # )
    student_p_code = forms.CharField(
        label=_('P-Code If a child lives in a tent / Brax in a random camp'),
        widget=forms.TextInput, required=False
    )

    disability = forms.ModelChoiceField(
        queryset=Disability.objects.all(), widget=forms.Select,
        label=_('Does the child have any disability or special need?'),
        required=True, to_field_name='id',
        initial=1
    )

    have_labour = forms.MultipleChoiceField(
        label=_('Does the child participate in work?'),
        choices=CLM.HAVE_LABOUR,
        widget=forms.CheckboxSelectMultiple,
        required=False, initial='no'
    )
    labours = forms.MultipleChoiceField(
        label=_('What is the type of work ?'),
        choices=CLM.LABOURS,
        widget=forms.CheckboxSelectMultiple,
        required=False
    )
    labour_hours = forms.CharField(
        label=_('How many hours does this child work in a day?'),
        widget=forms.TextInput, required=False
    )
    hh_educational_level = forms.ModelChoiceField(
        queryset=EducationalLevel.objects.all(), widget=forms.Select,
        label=_('What is the educational level of a person who is valuable to the child?'),
        required=False, to_field_name='id',
    )

    student_id = forms.CharField(widget=forms.HiddenInput, required=False)
    enrollment_id = forms.CharField(widget=forms.HiddenInput, required=False)
    student_outreach_child = forms.CharField(widget=forms.HiddenInput, required=False)

    participation = forms.ChoiceField(
        label=_('How was the level of child participation in the program?'),
        widget=forms.Select, required=False,
        choices=PARTICIPATION,
        initial=''
    )
    barriers = forms.MultipleChoiceField(
        label=_('The main barriers affecting the daily attendance and performance of the child or drop out of school?'),
        choices=CLM.BARRIERS,
        widget=forms.CheckboxSelectMultiple,
        required=False
    )
    learning_result = forms.ChoiceField(
        label=_('Based on the overall score, what is the recommended learning path?'),
        widget=forms.Select, required=False,
        choices=(
            ('', '----------'),
            ('repeat_level', _('Repeat level')),
            ('graduated_next_level', _('Graduated to the next level')),
            ('graduated_to_formal_kg', _('Graduated to formal education - KG')),
            ('graduated_to_formal_level1', _('Graduated to formal education - Level 1')),
            ('referred_to_another_program', _('Referred to another program')),
            ('dropout', _('Dropout from school'))
        ),
        initial=''
    )

    def __init__(self, *args, **kwargs):
        super(CommonForm, self).__init__(*args, **kwargs)

    def save(self, request=None, instance=None, serializer=None, clm_round=None):
        if instance:
            serializer = serializer(instance, data=request.POST)
            if serializer.is_valid():
                serializer.update(validated_data=serializer.validated_data, instance=instance)
        else:
            serializer = serializer(data=request.POST)
            if serializer.is_valid():
                instance = serializer.create(validated_data=serializer.validated_data)
                instance.owner = request.user
                instance.partner = request.user.partner
                instance.round = clm_round
                instance.save()
            else:
                print(serializer.errors)
                return False

        return True

    class Meta:
        model = CLM
        fields = (
            'new_registry',
            'student_outreached',
            'have_barcode',
            'governorate',
            'district',
            'location',
            'language',
            'student_first_name',
            'student_father_name',
            'student_last_name',
            'student_sex',
            'student_birthday_year',
            'student_birthday_month',
            'student_birthday_day',
            'student_nationality',
            'student_mother_fullname',
            # 'student_address',
            'student_p_code',
            'disability',
            'have_labour',
            'labours',
            'labour_hours',
            'hh_educational_level',
            'participation',
            'barriers',
            'learning_result',
            'student_id',
            'enrollment_id',
            'student_outreach_child',
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

    cycle = forms.ModelChoiceField(
        empty_label='----------',
        queryset=Cycle.objects.all(), widget=forms.Select,
        label=_('In which cycle is this child registered?'),
        required=True, to_field_name='id',
        initial=0
    )
    # referral = forms.MultipleChoiceField(
    #     label=_('Where was the child referred?'),
    #     choices=CLM.REFERRAL,
    #     widget=forms.CheckboxSelectMultiple,
    #     required=True,
    # )
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
        required=False,
    )
    learning_result = forms.ChoiceField(
        label=_('Based on the overall score, what is the recommended learning path?'),
        widget=forms.Select, required=False,
        choices=(
            ('', '----------'),
            ('repeat_level', _('Repeat level')),
            ('attended_public_school', _('Attended public school')),
            ('referred_to_alp', _('referred to ALP')),
            ('ready_to_alp_but_not_possible', _('Ready for ALP but referral is not possible')),
            ('reenrolled_in_alp', _('Re-register on another round of BLN')),
            ('not_enrolled_any_program', _('Not enrolled in any educational program')),
            ('dropout', _('Dropout from school'))
        ),
        initial=''
    )

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(BLNForm, self).__init__(*args, **kwargs)

        pre_test = ''
        post_test = ''
        post_test_permission = 'disabled'
        display_assessment = ' d-none'
        display_registry = ''
        instance = kwargs['instance'] if 'instance' in kwargs else ''
        form_action = reverse('clm:bln_add')

        if instance:
            display_assessment = ''
            display_registry = ' d-none'
            form_action = reverse('clm:bln_edit', kwargs={'pk': instance.id})
            if instance.pre_test:
                post_test_permission = ''

            pre_test = instance.assessment_form(
                stage='pre_test',
                assessment_slug='bln_pre_test',
                callback=self.request.build_absolute_uri(reverse('clm:bln_edit', kwargs={'pk': instance.id}))
             )
            post_test = instance.assessment_form(
                stage='post_test',
                assessment_slug='bln_post_test',
                callback=self.request.build_absolute_uri(reverse('clm:bln_edit', kwargs={'pk': instance.id}))
             )

        self.helper = FormHelper()
        self.helper.form_show_labels = True
        self.helper.form_action = form_action
        self.helper.layout = Layout(
            Fieldset(
                None,
                Div(
                    HTML('<h4 id="alternatives-to-hidden-labels">' + _('Registry') + '</h4>')
                ),
                Div(
                    'student_id',
                    'enrollment_id',
                    'student_outreach_child',
                    HTML('<span class="badge badge-default">1</span>'),
                    Div('new_registry', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">2</span>'),
                    Div('student_outreached', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">3</span>'),
                    Div('have_barcode', css_class='col-md-3', css_id='have_barcode_option'),
                    css_class='row',
                ),
                css_class='bd-callout bd-callout-warning'+display_registry, css_id='registry_block'
            ),
            Fieldset(
                None,
                Div(
                    HTML('<h4 id="alternatives-to-hidden-labels">'+_('Register by Barcode')+'</h4>')
                ),
                Div(
                    Div('search_barcode', css_class='col-md-4'),
                    css_class='row',
                ),
                css_id='register_by_barcode', css_class='bd-callout bd-callout-warning'+display_registry
            ),
            Fieldset(
                None,
                Div(
                    HTML('<h4 id="alternatives-to-hidden-labels">' + _(
                        'Search old student') + '</h4>')
                ),
                Div(
                    HTML('<span class="badge badge-default">1</span>'),
                    Div('search_student', css_class='col-md-3'),
                    css_class='row',
                ),
                css_id='search_options', css_class='bd-callout bd-callout-warning' + display_registry
            ),
            Fieldset(
                None,
                Div(
                    HTML('<h4 id="alternatives-to-hidden-labels">' + _('Program Information') + '</h4>')
                ),
                Div(
                    HTML('<span class="badge badge-default">1</span>'),
                    Div('cycle', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">2</span>'),
                    Div('governorate', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">3</span>'),
                    Div('district', css_class='col-md-3'),
                    css_class='row',
                ),
                Div(
                    HTML('<span class="badge badge-default">4</span>'),
                    Div('location', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">5</span>'),
                    Div('language', css_class='col-md-3'),
                    css_class='row',
                ),
                css_class='bd-callout bd-callout-warning child_data'
            ),
            Fieldset(
                None,
                Div(
                    HTML('<h4 id="alternatives-to-hidden-labels">' + _('Child Information') + '</h4>')
                ),
                # Div(
                #     HTML('<span class="badge badge-default">1</span>'),
                #     Div('referral', css_class='col-md-9'),
                #     css_class='row',
                # ),
                Div(
                    HTML('<span class="badge badge-default">2</span>'),
                    Div('student_first_name', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">3</span>'),
                    Div('student_father_name', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">4</span>'),
                    Div('student_mother_fullname', css_class='col-md-3'),
                    css_class='row',
                ),
                Div(
                    HTML('<span class="badge badge-default">5</span>'),
                    Div('student_last_name', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">6</span>'),
                    Div('student_sex', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">7</span>'),
                    Div('student_nationality', css_class='col-md-3'),
                    css_class='row',
                ),
                Div(
                    HTML('<span class="badge badge-default">8</span>'),
                    Div('student_birthday_year', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">9</span>'),
                    Div('student_birthday_month', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">10</span>'),
                    Div('student_birthday_day', css_class='col-md-3'),
                    css_class='row',
                ),
                Div(
                    # HTML('<span class="badge badge-default">11</span>'),
                    # Div('student_address', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">11</span>'),
                    Div('student_p_code', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">12</span>'),
                    Div('disability', css_class='col-md-3'),
                    css_class='row',
                ),
                css_class='bd-callout bd-callout-warning child_data'
            ),
            Fieldset(
                None,
                Div(
                    HTML('<h4 id="alternatives-to-hidden-labels">' + _('Family Status') + '</h4>')
                ),
                Div(
                    HTML('<span class="badge badge-default">1</span>'),
                    Div('hh_educational_level', css_class='col-md-4'),
                    HTML('<span class="badge badge-default">2</span>'),
                    Div('student_family_status', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">3</span>'),
                    Div('student_have_children', css_class='col-md-3', css_id='student_have_children'),
                    css_class='row',
                ),
                Div(
                    HTML('<span class="badge badge-default">4</span>'),
                    Div('have_labour', css_class='col-md-4'),
                    HTML('<span class="badge badge-default">5</span>'),
                    Div('labours', css_class='col-md-3', css_id='labours'),
                    HTML('<span class="badge badge-default">6</span>'),
                    Div('labour_hours', css_class='col-md-3', css_id='labour_hours'),
                    css_class='row',
                ),
                css_class='bd-callout bd-callout-warning child_data'
            ),
            Fieldset(
                None,
                Div(
                    HTML('<h4 id="alternatives-to-hidden-labels">' + _('Strategy Evaluation') + '</h4>')
                ),
                Div(
                    HTML('<div class="col-md-3"><a class="btn btn-success" href="' + pre_test + '">' + _(
                        'Pre-assessment') + '</a></div>'),
                    HTML(
                        '<div class="col-md-3"><a class="btn btn-success ' + post_test_permission + '" href="' + post_test + '">' + _(
                            'Post-assessment') + '</a></div>'),
                    css_class='row',
                ),
                Div(
                    HTML('<div class="p-3"></div>'),
                    css_class='row'
                ),
                css_class='bd-callout bd-callout-warning' + display_assessment
            ),
            Fieldset(
                None,
                Div(
                    HTML('<h4 id="alternatives-to-hidden-labels">' + _('School evaluation') + '</h4>')
                ),
                Div(
                    HTML('<span class="badge badge-default">1</span>'),
                    Div('participation', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">2</span>'),
                    Div('barriers', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">3</span>'),
                    Div('learning_result', css_class='col-md-3'),
                    css_class='row',
                ),
                css_class='bd-callout bd-callout-warning'+display_assessment
            ),
            FormActions(
                Submit('save', _('Save')),
                HTML('<a class="btn btn-info cancel-button" href="/clm/bln-list/" translation="' + _('Are you sure you want to cancel this registration?') + '">' + _('Back to list') + '</a>'),
            )
        )

    def save(self, request=None, instance=None, serializer=None, clm_round=None):
        clm_round = request.user.partner.bln_round
        super(BLNForm, self).save(request=request, instance=instance, serializer=BLNSerializer, clm_round=clm_round)

    class Meta:
        model = BLN
        fields = CommonForm.Meta.fields + (
            'cycle',
            # 'referral',
            'student_family_status',
            'student_have_children',
        )

    class Media:
        js = (
            'js/jquery-1.12.3.min.js',
            'js/jquery-ui-1.12.1.js',
            'js/validator.js',
            'js/registrations.js',
        )


class RSForm(CommonForm):

    type = forms.ChoiceField(
        widget=forms.Select, required=True,
        label=_('Select the program type'),
        choices=RS.TYPES
    )
    site = forms.ChoiceField(
        widget=forms.Select, required=True,
        label=_('Where is the program?'),
        choices=RS.SITES
    )
    school = forms.ModelChoiceField(
        queryset=School.objects.all(), widget=forms.Select,
        label=_('The school where the child is attending the program'),
        required=True, to_field_name='id',
        initial=0
    )
    registered_in_school = forms.ModelChoiceField(
        queryset=School.objects.all(), widget=forms.Select,
        label=_('The school where the child is registered'),
        required=True, to_field_name='id',
        initial=0
    )
    shift = forms.ChoiceField(
        label=_('Shift'),
        widget=forms.Select, required=True,
        choices=RS.SCHOOL_SHIFTS
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
        required=False,
    )
    grade = forms.ModelChoiceField(
        queryset=ClassRoom.objects.all(), widget=forms.Select,
        label=_('Class'),
        required=True, to_field_name='id',
        initial=0
    )
    referral = forms.MultipleChoiceField(
        label=_('Reason for referral of the child'),
        choices=RS.REFER_SEASON,
        widget=forms.CheckboxSelectMultiple,
        required=True,
        initial='academic'
    )
    learning_result = forms.ChoiceField(
        label=_('Based on the overall score, what is the recommended learning path?'),
        widget=forms.Select, required=False,
        choices=(
            ('', '----------'),
            ('repeat_level', _('Repeat level')),
            ('dropout', _('Dropout from school'))
        ),
        initial=''
    )

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(RSForm, self).__init__(*args, **kwargs)

        pre_test = ''
        post_test = ''
        pre_motivation = ''
        post_motivation = ''
        pre_self_assessment = ''
        post_self_assessment = ''
        post_test_permission = 'disabled'
        post_self_permission = 'disabled'
        post_motivation_permission = 'disabled'
        display_assessment = ' d-none'
        display_registry = ''
        instance = kwargs['instance'] if 'instance' in kwargs else ''
        form_action = reverse('clm:rs_add')

        if instance:
            display_assessment = ''
            display_registry = ' d-none'
            form_action = reverse('clm:rs_edit', kwargs={'pk': instance.id})
            if instance.pre_test:
                post_test_permission = ''
            if instance.pre_self_assessment:
                post_self_permission = ''
            if instance.pre_motivation:
                post_motivation_permission = ''

            #  Strategy Evaluation
            pre_test = instance.assessment_form(
                stage='pre_test',
                assessment_slug='rs_pre_test',
                callback=self.request.build_absolute_uri(reverse('clm:rs_edit', kwargs={'pk': instance.id}))
             )
            post_test = instance.assessment_form(
                stage='post_test',
                assessment_slug='rs_post_test',
                callback=self.request.build_absolute_uri(reverse('clm:rs_edit', kwargs={'pk': instance.id}))
             )

            #  Motivation Assessment
            pre_motivation = instance.assessment_form(
                stage='pre_motivation',
                assessment_slug='rs_pre_motivation',
                callback=self.request.build_absolute_uri(reverse('clm:rs_edit', kwargs={'pk': instance.id}))
             )
            post_motivation = instance.assessment_form(
                stage='post_motivation',
                assessment_slug='rs_post_motivation',
                callback=self.request.build_absolute_uri(reverse('clm:rs_edit', kwargs={'pk': instance.id}))
             )

            #  Self-Assessment
            pre_self_assessment = instance.assessment_form(
                stage='pre_self_assessment',
                assessment_slug='rs_self_assessment_pre',
                callback=self.request.build_absolute_uri(reverse('clm:rs_edit', kwargs={'pk': instance.id}))
             )
            post_self_assessment = instance.assessment_form(
                stage='post_self_assessment',
                assessment_slug='rs_post_self_assessment',
                callback=self.request.build_absolute_uri(reverse('clm:rs_edit', kwargs={'pk': instance.id}))
             )

        self.helper = FormHelper()
        self.helper.form_show_labels = True
        self.helper.form_action = form_action
        self.helper.layout = Layout(
            Fieldset(
                None,
                Div(
                    HTML('<h4 id="alternatives-to-hidden-labels">' + _('Registry') + '</h4>')
                ),
                Div(
                    'student_id',
                    'enrollment_id',
                    'student_outreach_child',
                    HTML('<span class="badge badge-default">1</span>'),
                    Div('new_registry', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">2</span>'),
                    Div('student_outreached', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">3</span>'),
                    Div('have_barcode', css_class='col-md-3', css_id='have_barcode_option'),
                    css_class='row',
                ),
                css_class='bd-callout bd-callout-warning'+display_registry, css_id='registry_block'
            ),
            Fieldset(
                None,
                Div(
                    HTML('<h4 id="alternatives-to-hidden-labels">'+_('Register by Barcode')+'</h4>')
                ),
                Div(
                    Div('search_barcode', css_class='col-md-4'),
                    css_class='row',
                ),
                css_id='register_by_barcode', css_class='bd-callout bd-callout-warning'+display_registry
            ),
            Fieldset(
                None,
                Div(
                    HTML('<h4 id="alternatives-to-hidden-labels">' + _(
                        'Search old student') + '</h4>')
                ),
                Div(
                    HTML('<span class="badge badge-default">1</span>'),
                    Div('search_student', css_class='col-md-3'),
                    css_class='row',
                ),
                css_id='search_options', css_class='bd-callout bd-callout-warning' + display_registry
            ),
            Fieldset(
                None,
                Div(
                    HTML('<h4 id="alternatives-to-hidden-labels">' + _('Program Information') + '</h4>')
                ),
                Div(
                    HTML('<span class="badge badge-default">1</span>'),
                    Div('type', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">2</span>'),
                    Div('site', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">3</span>'),
                    Div('school', css_class='col-md-3'),
                    css_class='row',
                ),
                Div(
                    HTML('<span class="badge badge-default">4</span>'),
                    Div('governorate', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">5</span>'),
                    Div('district', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">6</span>'),
                    Div('location', css_class='col-md-3'),
                    css_class='row',
                ),
                Div(
                    HTML('<span class="badge badge-default">7</span>'),
                    Div('language', css_class='col-md-3'),
                    css_class='row',
                ),
                css_class='bd-callout bd-callout-warning child_data'
            ),
            Fieldset(
                None,
                Div(
                    HTML('<h4 id="alternatives-to-hidden-labels">' + _('Child Information') + '</h4>')
                ),
                Div(
                    HTML('<span class="badge badge-default">3</span>'),
                    Div('student_first_name', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">4</span>'),
                    Div('student_father_name', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">5</span>'),
                    Div('student_mother_fullname', css_class='col-md-3'),
                    css_class='row',
                ),
                Div(
                    HTML('<span class="badge badge-default">6</span>'),
                    Div('student_last_name', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">7</span>'),
                    Div('student_sex', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">8</span>'),
                    Div('student_nationality', css_class='col-md-3'),
                    css_class='row',
                ),
                Div(
                    HTML('<span class="badge badge-default">9</span>'),
                    Div('student_birthday_year', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">10</span>'),
                    Div('student_birthday_month', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">11</span>'),
                    Div('student_birthday_day', css_class='col-md-3'),
                    css_class='row',
                ),
                Div(
                    # HTML('<span class="badge badge-default">12</span>'),
                    # Div('student_address', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">11</span>'),
                    Div('student_p_code', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">12</span>'),
                    Div('disability', css_class='col-md-3'),
                    css_class='row',
                ),
                css_class='bd-callout bd-callout-warning child_data'
            ),
            Fieldset(
                None,
                Div(
                    HTML('<h4 id="alternatives-to-hidden-labels">' + _('Family Status') + '</h4>')
                ),
                Div(
                    HTML('<span class="badge badge-default">1</span>'),
                    Div('hh_educational_level', css_class='col-md-4'),
                    HTML('<span class="badge badge-default">2</span>'),
                    Div('student_family_status', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">3</span>'),
                    Div('student_have_children', css_class='col-md-3', css_id='student_have_children'),
                    css_class='row',
                ),
                Div(
                    HTML('<span class="badge badge-default">4</span>'),
                    Div('have_labour', css_class='col-md-4'),
                    HTML('<span class="badge badge-default">5</span>'),
                    Div('labours', css_class='col-md-3', css_id='labours'),
                    HTML('<span class="badge badge-default">6</span>'),
                    Div('labour_hours', css_class='col-md-3', css_id='labour_hours'),
                    css_class='row',
                ),
                css_class='bd-callout bd-callout-warning child_data'
            ),
            Fieldset(
                None,
                Div(
                    HTML('<h4 id="alternatives-to-hidden-labels">' + _('Academic data') + '</h4>')
                ),
                Div(
                    HTML('<span class="badge badge-default">1</span>'),
                    Div('registered_in_school', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">2</span>'),
                    Div('shift', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">3</span>'),
                    Div('grade', css_class='col-md-3'),
                    css_class='row',
                ),
                Div(
                    HTML('<span class="badge badge-default">4</span>'),
                    Div('referral', css_class='col-md-3'),
                    css_class='row',
                ),
                Div(
                    HTML('<div class="p-3"></div>'),
                    css_class='row'
                ),
                css_class='bd-callout bd-callout-warning child_data'
            ),
            Fieldset(
                None,
                Div(
                    HTML('<h4 id="alternatives-to-hidden-labels">' + _(
                        'Academic data when entering the program') + '</h4>')
                ),
                Div(
                    HTML('<span class="badge badge-default">1</span>'),
                    Div('pre_test_arabic', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">2</span>'),
                    Div('pre_test_language', css_class='col-md-3'),
                    css_class='row',
                ),
                Div(
                    HTML('<span class="badge badge-default">3</span>'),
                    Div('pre_test_math', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">4</span>'),
                    Div('pre_test_science', css_class='col-md-3'),
                    css_class='row',
                ),
                css_class='bd-callout bd-callout-warning child_data'
            ),
            Fieldset(
                None,
                Div(
                    HTML('<h4 id="alternatives-to-hidden-labels">' + _(
                        'Academic data in the end of the program') + '</h4>')
                ),
                Div(
                    HTML('<span class="badge badge-default">1</span>'),
                    Div('post_test_arabic', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">2</span>'),
                    Div('post_test_language', css_class='col-md-3'),
                    css_class='row',
                ),
                Div(
                    HTML('<span class="badge badge-default">3</span>'),
                    Div('post_test_math', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">4</span>'),
                    Div('post_test_science', css_class='col-md-3'),
                    css_class='row',
                ),
                css_class='bd-callout bd-callout-warning'+display_assessment
            ),
            Fieldset(
                None,
                Div(
                    HTML('<h4 id="alternatives-to-hidden-labels">' + _('Assessment') + '</h4>')
                ),
                Div(
                    HTML('<div class="col-md-3"><a class="btn btn-success" href="'+pre_test+'">' +
                         _('Pre-assessment')+'</a></div>'),
                    HTML('<div class="col-md-3"><a class="btn btn-success '+post_test_permission+'" href="' +
                         post_test + '">'+_('Post-assessment')+'</a></div>'),
                    css_class='row',
                ),
                Div(
                    HTML('<div class="p-3"></div>'),
                    css_class='row'
                ),
                css_class='bd-callout bd-callout-warning'+display_assessment
            ),
            Fieldset(
                None,
                Div(
                    HTML('<h4 id="alternatives-to-hidden-labels">' + _('Motivation') + '</h4>')
                ),
                Div(
                    HTML('<div class="col-md-3"><a class="btn btn-success" href="' + pre_motivation + '">' +
                         _('Pre-assessment') + '</a></div>'),
                    HTML('<div class="col-md-3"><a class="btn btn-success ' + post_motivation_permission + '" href="' +
                         post_motivation + '">' + _('Post-assessment') + '</a></div>'),
                    css_class='row',
                ),
                Div(
                    HTML('<div class="p-3"></div>'),
                    css_class='row'
                ),
                css_class='bd-callout bd-callout-warning' + display_assessment
            ),
            Fieldset(
                None,
                Div(
                    HTML('<h4 id="alternatives-to-hidden-labels">' + _('Self-Perception') + '</h4>')
                ),
                Div(
                    HTML('<div class="col-md-3"><a class="btn btn-success" href="' + pre_self_assessment + '">' + _(
                        'Pre-assessment') + '</a></div>'),
                    HTML(
                        '<div class="col-md-3"><a class="btn btn-success ' + post_self_permission + '" href="' +
                        post_self_assessment + '">' + _('Post-assessment') + '</a></div>'),
                    css_class='row',
                ),
                Div(
                    HTML('<div class="p-3"></div>'),
                    css_class='row'
                ),
                css_class='bd-callout bd-callout-warning' + display_assessment
            ),
            Fieldset(
                None,
                Div(
                    HTML('<h4 id="alternatives-to-hidden-labels">' + _('School evaluation') + '</h4>')
                ),
                Div(
                    HTML('<span class="badge badge-default">1</span>'),
                    Div('participation', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">2</span>'),
                    Div('barriers', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">3</span>'),
                    Div('learning_result', css_class='col-md-3'),
                    css_class='row',
                ),
                css_class='bd-callout bd-callout-warning'+display_assessment
            ),
            FormActions(
                Submit('save', _('Save')),
                HTML('<a class="btn btn-info cancel-button" href="/clm/rs-list/" translation="' + _('Are you sure you want to cancel this registration?') + '">' + _('Back to list') + '</a>'),
            )
        )

    def save(self, request=None, instance=None, serializer=None, clm_round=None):
        clm_round = request.user.partner.rs_round
        super(RSForm, self).save(request=request, instance=instance, serializer=RSSerializer, clm_round=clm_round)

    class Meta:
        model = RS
        fields = CommonForm.Meta.fields + (
            'type',
            'site',
            'school',
            'shift',
            'grade',
            'referral',
            'registered_in_school',
            'student_family_status',
            'student_have_children',
            'pre_test_arabic',
            'pre_test_language',
            'pre_test_math',
            'pre_test_science',
            'post_test_arabic',
            'post_test_language',
            'post_test_math',
            'post_test_science',
        )


class CBECEForm(CommonForm):

    cycle = forms.ModelChoiceField(
        queryset=Cycle.objects.all(), widget=forms.Select,
        label=_('In which cycle is this child registered?'),
        required=False, to_field_name='id',
        initial=0
    )
    site = forms.ChoiceField(
        widget=forms.Select, required=True,
        label=_('Where is the program?'),
        choices=(
            ('', '--------'),
            ('in_school', _('Inside the school')),
            ('out_school', _('Outside the school')),
        )
    )
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
        required=True,
    )
    child_muac = forms.ChoiceField(
        label=_("What is the measurement of the child's arm circumference? (Centimeter)"),
        widget=forms.Select, required=True,
        choices=(
            ('', '-------'),
            ('1', _('< 11.5 CM (severe malnutrition)')),
            ('2', _('< 12.5 CM (moderate malnutrition)')),
        )
    )

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(CBECEForm, self).__init__(*args, **kwargs)

        pre_test = ''
        post_test = ''
        display_assessment = ' d-none'
        display_registry = ''
        post_test_permission = 'disabled'
        instance = kwargs['instance'] if 'instance' in kwargs else ''
        form_action = reverse('clm:cbece_add')

        if instance:
            display_assessment = ''
            display_registry = ' d-none'
            form_action = reverse('clm:cbece_edit', kwargs={'pk': instance.id})
            if instance.pre_test:
                post_test_permission = ''

            pre_test = instance.assessment_form(
                stage='pre_test',
                assessment_slug='cbece_pre_test',
                callback=self.request.build_absolute_uri(reverse('clm:cbece_edit', kwargs={'pk': instance.id}))
             )
            post_test = instance.assessment_form(
                stage='post_test',
                assessment_slug='cbece_post_test',
                callback=self.request.build_absolute_uri(reverse('clm:cbece_edit', kwargs={'pk': instance.id}))
             )

        self.helper = FormHelper()
        self.helper.form_show_labels = True
        self.helper.form_action = form_action
        self.helper.layout = Layout(
            Fieldset(
                None,
                Div(
                    HTML('<h4 id="alternatives-to-hidden-labels">' + _('Registry') + '</h4>')
                ),
                Div(
                    'student_id',
                    'enrollment_id',
                    'student_outreach_child',
                    HTML('<span class="badge badge-default">1</span>'),
                    Div('new_registry', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">2</span>'),
                    Div('student_outreached', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">3</span>'),
                    Div('have_barcode', css_class='col-md-3', css_id='have_barcode_option'),
                    css_class='row',
                ),
                css_class='bd-callout bd-callout-warning'+display_registry, css_id='registry_block'
            ),
            Fieldset(
                None,
                Div(
                    HTML('<h4 id="alternatives-to-hidden-labels">'+_('Register by Barcode')+'</h4>')
                ),
                Div(
                    Div('search_barcode', css_class='col-md-4'),
                    css_class='row',
                ),
                css_id='register_by_barcode', css_class='bd-callout bd-callout-warning'+display_registry
            ),
            Fieldset(
                None,
                Div(
                    HTML('<h4 id="alternatives-to-hidden-labels">' + _(
                        'Search old student') + '</h4>')
                ),
                Div(
                    HTML('<span class="badge badge-default">1</span>'),
                    Div('search_student', css_class='col-md-3'),
                    css_class='row',
                ),
                css_id='search_options', css_class='bd-callout bd-callout-warning' + display_registry
            ),
            Fieldset(
                None,
                Div(
                    HTML('<h4 id="alternatives-to-hidden-labels">' + _('Program Information') + '</h4>')
                ),
                Div(
                    HTML('<span class="badge badge-default">1</span>'),
                    Div('cycle', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">2</span>'),
                    Div('site', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">3</span>'),
                    Div('school', css_class='col-md-3'),
                    css_class='row',
                ),
                Div(
                    HTML('<span class="badge badge-default">4</span>'),
                    Div('governorate', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">5</span>'),
                    Div('district', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">6</span>'),
                    Div('location', css_class='col-md-3'),
                    css_class='row',
                ),
                Div(
                    HTML('<span class="badge badge-default">7</span>'),
                    Div('language', css_class='col-md-3'),
                    css_class='row',
                ),
                css_class='bd-callout bd-callout-warning child_data'
            ),
            Fieldset(
                None,
                Div(
                    HTML('<h4 id="alternatives-to-hidden-labels">' + _('Child Information') + '</h4>')
                ),
                Div(
                    HTML('<span class="badge badge-default">1</span>'),
                    Div('referral', css_class='col-md-9'),
                    css_class='row',
                ),
                Div(
                    HTML('<span class="badge badge-default">2</span>'),
                    Div('student_first_name', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">3</span>'),
                    Div('student_father_name', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">4</span>'),
                    Div('student_mother_fullname', css_class='col-md-3'),
                    css_class='row',
                ),
                Div(
                    HTML('<span class="badge badge-default">5</span>'),
                    Div('student_last_name', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">6</span>'),
                    Div('student_sex', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">7</span>'),
                    Div('student_nationality', css_class='col-md-3'),
                    css_class='row',
                ),
                Div(
                    HTML('<span class="badge badge-default">8</span>'),
                    Div('student_birthday_year', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">9</span>'),
                    Div('student_birthday_month', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">10</span>'),
                    Div('student_birthday_day', css_class='col-md-3'),
                    css_class='row',
                ),
                Div(
                    # HTML('<span class="badge badge-default">11</span>'),
                    # Div('student_address', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">11</span>'),
                    Div('student_p_code', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">12</span>'),
                    Div('disability', css_class='col-md-3'),
                    css_class='row',
                ),
                Div(
                    HTML('<span class="badge badge-default">14</span>'),
                    Div('child_muac', css_class='col-md-3'),
                    css_class='row',
                ),
                css_class='bd-callout bd-callout-warning child_data'
            ),
            Fieldset(
                None,
                Div(
                    HTML('<h4 id="alternatives-to-hidden-labels">' + _('Family Status') + '</h4>')
                ),
                Div(
                    HTML('<span class="badge badge-default">1</span>'),
                    Div('hh_educational_level', css_class='col-md-3'),
                    css_class='row',
                ),
                Div(
                    HTML('<span class="badge badge-default">2</span>'),
                    Div('have_labour', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">3</span>'),
                    Div('labours', css_class='col-md-3', css_id='labours'),
                    HTML('<span class="badge badge-default">4</span>'),
                    Div('labour_hours', css_class='col-md-3', css_id='labour_hours'),
                    css_class='row',
                ),
                css_class='bd-callout bd-callout-warning child_data'
            ),
            Fieldset(
                None,
                Div(
                    HTML('<h4 id="alternatives-to-hidden-labels">' + _('Assessment') + '</h4>')
                ),
                Div(
                    HTML('<div class="col-md-3"><a class="btn btn-success" href="'+pre_test+'">'+_('Pre-assessment')+'</a></div>'),
                    HTML('<div class="col-md-3"><a class="btn btn-success '+post_test_permission+'" href="'+post_test+'">'+_('Post-assessment')+'</a></div>'),
                    css_class='row',
                ),
                Div(
                    HTML('<div class="p-3"></div>'),
                    css_class='row'
                ),
                css_class='bd-callout bd-callout-warning'+display_assessment
            ),
            Fieldset(
                None,
                Div(
                    HTML('<h4 id="alternatives-to-hidden-labels">' + _('School evaluation') + '</h4>')
                ),
                Div(
                    HTML('<span class="badge badge-default">1</span>'),
                    Div('participation', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">2</span>'),
                    Div('barriers', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">3</span>'),
                    Div('learning_result', css_class='col-md-3'),
                    css_class='row',
                ),
                css_class='bd-callout bd-callout-warning'+display_assessment
            ),
            FormActions(
                Submit('save', _('Save')),
                HTML('<a class="btn btn-info cancel-button" href="/clm/cbece-list/" translation="' + _('Are you sure you want to cancel this registration?') + '">' + _('Back to list') + '</a>'),
            )
        )

    def save(self, request=None, instance=None, serializer=None, clm_round=None):
        clm_round = request.user.partner.cbece_round
        super(CBECEForm, self).save(request=request, instance=instance, serializer=CBECESerializer, clm_round=clm_round)

    class Meta:
        model = CBECE
        fields = CommonForm.Meta.fields + (
            'cycle',
            'site',
            'school',
            'referral',
            'child_muac',
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
