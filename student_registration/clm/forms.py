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
    Nationality,
)
from student_registration.schools.models import (
    School,
    EducationalLevel,
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
    Assessment
)
from .serializers import BLNSerializer, RSSerializer, CBECESerializer

YES_NO_CHOICE = ((1, "Yes"), (0, "No"))

YEARS = list(((str(x), x) for x in range(1930, 2051)))
YEARS.append(('', _('---------')))

DAYS = list(((str(x), x) for x in range(1, 32)))
DAYS.append(('', _('---------')))


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
    outreach_barcode = forms.CharField(widget=forms.TextInput, required=False)

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
    language = forms.MultipleChoiceField(
        choices=(
            ('english_arabic', _('English/Arabic')),
            ('french_arabic', _('French/Arabic'))
        ),
        widget=forms.CheckboxSelectMultiple,
        required=True
    )

    student_first_name = forms.CharField(widget=forms.TextInput, required=True)
    student_father_name = forms.CharField(widget=forms.TextInput, required=True)
    student_last_name = forms.CharField(widget=forms.TextInput, required=True)
    student_sex = forms.ChoiceField(
        widget=forms.Select, required=True,
        choices=(
            ('', '-----------'),
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
            ('', '-----------'),
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
    student_address = forms.CharField(widget=forms.TextInput, required=True)
    student_p_code = forms.CharField(widget=forms.TextInput, required=True)

    disability = forms.ModelChoiceField(
        queryset=Disability.objects.all(), widget=forms.Select,
        empty_label=_('Disability'),
        required=True, to_field_name='id',
    )
    student_family_status = forms.ChoiceField(
        widget=forms.Select, required=True,
        choices=(
            ('', '-----------'),
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
        choices=((str(x.id), x.name) for x in Labour.objects.all()),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )
    labour_hours = forms.CharField(widget=forms.TextInput, required=True)
    hh_educational_level = forms.ModelChoiceField(
        queryset=EducationalLevel.objects.all(), widget=forms.Select,
        empty_label=_('HH educational level'),
        required=False, to_field_name='id',
    )

    student_id = forms.CharField(widget=forms.HiddenInput, required=False)
    enrollment_id = forms.CharField(widget=forms.HiddenInput, required=False)
    student_outreach_child = forms.CharField(widget=forms.HiddenInput, required=False)

    participation = forms.ChoiceField(
        widget=forms.Select, required=True,
        choices=(
            ('', '-----------'),
            ('less_than_5days', _('Less than 5 absence days')),
            ('5_10_days', _('5 to 10 absence days')),
            ('10_15_days', _('10 to 15 absence days')),
            ('more_than_15days', _('More than 15 absence days'))
        )
    )
    barriers = forms.MultipleChoiceField(
        choices=(
            ('seasonal_work', _('Seasonal work')),
            ('transportation', 'Transportation'),
            ('weather', _('Weather')),
            ('sickness', _('Sickness')),
            ('security', _('Security')),
            ('other', _('Other'))
        ),
        widget=forms.CheckboxSelectMultiple,
        required=True
    )
    learning_result = forms.ChoiceField(
        widget=forms.Select, required=True,
        choices=(
            ('', '-----------'),
            ('graduated_next_level', _('Graduated to the next level')),
            ('graduated_to_formal_kg', _('Graduated to formal education - KG')),
            ('graduated_to_formal_level1', _('Graduated to formal education - Level 1')),
            ('referred_to_another_program', _('Referred to another program')),
            ('dropout', _('Dropout from school'))
        )
    )

    def save(self, request=None, instance=None, serializer=None):
        if instance:
            serializer = serializer(instance, data=request.POST)
            if serializer.is_valid():
                serializer.update(validated_data=serializer.validated_data)
        else:
            serializer = serializer(data=request.POST)
            if serializer.is_valid():
                instance = serializer.create(validated_data=serializer.validated_data)
                instance.owner = request.user
                instance.save()

    class Meta:
        model = CLM
        fields = (
            'new_registry',
            'student_outreached',
            'have_barcode',
            'search_barcode',
            'search_student',
            'outreach_barcode',
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
            'student_address',
            'student_p_code',
            'disability',
            'student_family_status',
            'student_have_children',
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
        queryset=Cycle.objects.all(), widget=forms.Select,
        empty_label=_('Programme Cycle'),
        required=False, to_field_name='id',
        initial=0
    )
    referral = forms.ModelChoiceField(
        queryset=Referral.objects.all(), widget=forms.Select,
        empty_label=_('Referral'),
        required=False, to_field_name='id',
        initial=0
    )
    child_muac = forms.ChoiceField(
        widget=forms.Select, required=True,
        choices=(
            ('', _('Child MUAC')),
            ('1', _('< 11.5 CM (severe malnutrition)')),
            ('2', _('< 12.5 CM (moderate malnutrition)')),
        )
    )

    def __init__(self, *args, **kwargs):
        super(BLNForm, self).__init__(*args, **kwargs)

        pre_test = ''
        post_test = ''
        display_assessment = ' d-none'
        display_registry = ''
        instance = kwargs['instance'] if 'instance' in kwargs else ''
        if instance:
            assessment_pre = Assessment.objects.get(slug='bln_pre_test')
            assessment_post = Assessment.objects.get(slug='bln_post_test')
            display_assessment = ''
            display_registry = ' d-none'
            pre_test = '{form}?d[youth_id]={id}&d[status]={status}&returnURL={callback}'.format(
                form=assessment_pre.assessment_form,
                id=instance.student.id,
                type='pre_test',
                # status=instance.STATUS.pre_test if instance.status == instance.STATUS.enrolled
                # else instance.STATUS.post_test,
                callback=self.request.build_absolute_uri(
                    reverse('clm:bln_edit', kwargs={'id': instance.student.id})
                )
            )
            post_test = '{form}?d[youth_id]={id}&d[status]={status}&returnURL={callback}'.format(
                form=assessment_post.assessment_form,
                id=instance.student.id,
                type='post_test',
                # status=instance.STATUS.pre_test if instance.status == instance.STATUS.enrolled
                # else instance.STATUS.post_test,
                callback=self.request.build_absolute_uri(
                    reverse('clm:bln_edit', kwargs={'id': instance.student.id})
                )
            )

        self.helper = FormHelper()
        self.helper.form_show_labels = True
        self.helper.form_action = reverse('clm:bln_add')
        self.helper.layout = Layout(
            Fieldset(
                None,
                Div(
                    HTML('<h4 id="alternatives-to-hidden-labels">Registry</h4>')
                ),
                Div(
                    'student_id',
                    'enrollment_id',
                    'student_outreach_child',
                    HTML('<span class="badge badge-default">1</span>'),
                    Div(InlineRadios('new_registry'), css_class='col-md-3'),
                    HTML('<span class="badge badge-default">2</span>'),
                    Div(InlineRadios('student_outreached'), css_class='col-md-3'),
                    HTML('<span class="badge badge-default">3</span>'),
                    Div(InlineRadios('have_barcode'), css_class='col-md-3'),
                    css_class='row',
                ),
                css_class='bd-callout bd-callout-warning'+display_registry
            ),
            Fieldset(
                None,
                Div(
                    HTML('<h4 id="alternatives-to-hidden-labels">Register by Barcode</h4>')
                ),
                Div(
                    Div('search_barcode', css_class='col-md-6'),
                    css_class='row',
                ),
                css_id='register_by_barcode', css_class='bd-callout bd-callout-warning'+display_registry
            ),
            Fieldset(
                None,
                Div(
                    HTML('<h4 id="alternatives-to-hidden-labels">Search old student (fullname Or ID number)</h4>')
                ),
                Div(
                    Div('search_student', css_class='col-md-6'),
                    css_class='row',
                ),
                css_id='search_options', css_class='bd-callout bd-callout-warning'+display_registry
            ),
            Fieldset(
                None,
                Div(
                    HTML('<h4 id="alternatives-to-hidden-labels">Program Information</h4>')
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
                css_class='bd-callout bd-callout-warning'
            ),
            Fieldset(
                None,
                Div(
                    HTML('<h4 id="alternatives-to-hidden-labels">Child Information</h4>')
                ),
                Div(
                    HTML('<span class="badge badge-default">1</span>'),
                    Div('referral', css_class='col-md-3'),
                    css_class='row',
                ),
                Div(
                    HTML('<span class="badge badge-default">2</span>'),
                    Div('student_first_name', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">3</span>'),
                    Div('student_father_name', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">4</span>'),
                    Div('student_last_name', css_class='col-md-3'),
                    css_class='row',
                ),
                Div(
                    HTML('<span class="badge badge-default">5</span>'),
                    Div('student_birthday_year', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">6</span>'),
                    Div('student_birthday_month', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">7</span>'),
                    Div('student_birthday_day', css_class='col-md-3'),
                    css_class='row',
                ),
                Div(
                    HTML('<span class="badge badge-default">8</span>'),
                    Div('student_sex', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">9</span>'),
                    Div('student_nationality', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">10</span>'),
                    Div('student_mother_fullname', css_class='col-md-3'),
                    css_class='row',
                ),
                Div(
                    HTML('<span class="badge badge-default">11</span>'),
                    Div('outreach_barcode', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">12</span>'),
                    Div('student_address', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">13</span>'),
                    Div('student_p_code', css_class='col-md-3'),
                    css_class='row',
                ),
                Div(
                    HTML('<span class="badge badge-default">14</span>'),
                    Div('child_muac', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">15</span>'),
                    Div('disability', css_class='col-md-3'),
                    css_class='row',
                ),
                css_class='child_data bd-callout bd-callout-warning'
            ),
            Fieldset(
                None,
                Div(
                    HTML('<h4 id="alternatives-to-hidden-labels">Family Status</h4>')
                ),
                Div(
                    HTML('<span class="badge badge-default">1</span>'),
                    Div('hh_educational_level', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">2</span>'),
                    Div('student_family_status', css_class='col-md-3'),
                    css_class='row',
                ),
                Div(
                    HTML('<span class="badge badge-default">3</span>'),
                    Div('student_have_children', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">4</span>'),
                    Div('have_labour', css_class='col-md-3'),
                    css_class='row',
                ),
                Div(
                    HTML('<span class="badge badge-default">5</span>'),
                    Div('labours', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">6</span>'),
                    Div('labour_hours', css_class='col-md-3'),
                    css_class='row',
                ),
                css_class='child_data bd-callout bd-callout-warning'
            ),
            Fieldset(
                None,
                Div(
                    HTML('<h4 id="alternatives-to-hidden-labels">Assessment</h4>')
                ),
                Div(
                    HTML('<div class="col-md-3"><a class="btn btn-success" href="'+pre_test+'">Pre-Assessment</a></div>'),
                    HTML('<div class="col-md-3"><a class="btn btn-success" href="'+post_test+'">Post-Assessment</a></div>'),
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
                    HTML('<h4 id="alternatives-to-hidden-labels">School Readiness</h4>')
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
                Button('cancel', _('Cancel'))
            )
        )

    def save(self, request=None, instance=None, serializer=None):
        super(BLNForm, self).save()

    class Meta:
        model = BLN
        fields = CommonForm.Meta.fields + (
            'cycle',
            'referral',
            'child_muac',
        )

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

    site = forms.ModelChoiceField(
        queryset=Site.objects.all(), widget=forms.Select,
        empty_label=_('Programme Site'),
        required=False, to_field_name='id',
        initial=0
    )
    school = forms.ModelChoiceField(
        queryset=School.objects.all(), widget=forms.Select,
        empty_label=_('School'),
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
    child_muac = forms.ChoiceField(
        widget=forms.Select, required=True,
        choices=(
            ('', _('Child MUAC')),
            ('1', _('< 11.5 CM (severe malnutrition)')),
            ('2', _('< 12.5 CM (moderate malnutrition)')),
        )
    )

    def save(self, request=None, instance=None, serializer=None):
        super(RSForm, self).save()

    class Meta:
        model = RS
        fields = CommonForm.Meta.fields + (
            'cycle',
            'site',
            'school',
            'shift',
            'child_muac',
        )


class CBECEForm(CommonForm):

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
    school = forms.ModelChoiceField(
        queryset=School.objects.all(), widget=forms.Select,
        empty_label=_('School'),
        required=False, to_field_name='id',
        initial=0
    )
    referral = forms.ModelChoiceField(
        queryset=Referral.objects.all(), widget=forms.Select,
        empty_label=_('Referral'),
        required=False, to_field_name='id',
        initial=0
    )

    def save(self, request=None, instance=None, serializer=None):
        super(CBECEForm, self).save()

    class Meta:
        model = CBECE
        fields = CommonForm.Meta.fields + (
            'cycle',
            'site',
            'school',
            'referral',
        )
