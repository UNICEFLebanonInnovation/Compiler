
from __future__ import unicode_literals, absolute_import, division

from django.utils.translation import ugettext as _
from django import forms
from django.core.urlresolvers import reverse
from django.contrib import messages

from dal import autocomplete
from crispy_forms.helper import FormHelper
from crispy_forms.bootstrap import FormActions
from crispy_forms.layout import Layout, Fieldset, Button, Submit, Div, Field, HTML

from student_registration.students.models import (
    Person,
    Student,
    IDType,
    Nationality,
    SpecialNeeds,
    SpecialNeedsDt,
    FinancialSupport,
)
from student_registration.schools.models import (
    School,
    Section,
    ClassRoom,
    EducationLevel,
    ClassLevel,
)
from student_registration.alp.models import ALPRound
from .models import Enrollment, LoggingStudentMove, EducationYear
from .serializers import EnrollmentSerializer
from .utils import initiate_grading
from student_registration.enrollments.models import DuplicateStd

YES_NO_CHOICE = ((1, _("Yes")), (0, _("No")))

EDUCATION_YEARS = list((str(x-1)+'/'+str(x), str(x-1)+'/'+str(x)) for x in range(2001, Person.CURRENT_YEAR+1))
EDUCATION_YEARS.append(('na', 'n/a'))

YEARS = list(((str(x), x) for x in range(Person.CURRENT_YEAR-20, Person.CURRENT_YEAR-2)))
YEARS.insert(0, ('', '---------'))

DAYS = list(((str(x), x) for x in range(1, 32)))
DAYS.insert(0, ('', '---------'))


class DuplicateStdAdminForm(forms.ModelForm):

    class Meta:
        model = DuplicateStd
        fields = '__all__'


class EnrollmentAdminForm(forms.ModelForm):

    student = forms.ModelChoiceField(
        queryset=Student.objects.all(),
        widget=autocomplete.ModelSelect2(url='student_autocomplete')
    )

    def __init__(self, *args, **kwargs):
        super(EnrollmentAdminForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Enrollment
        fields = '__all__'
        exclude = (
            'registered_in_unhcr',
        )


class EnrollmentForm(forms.ModelForm):

    new_registry = forms.ChoiceField(
        label=_("First time registered?"),
        widget=forms.Select, required=True,
        choices=(('yes', _("Yes")), ('no', _("No"))),
        initial='no'
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
    search_barcode = forms.CharField(
        label=_("Search a barcode"),
        widget=forms.TextInput,
        required=False
    )
    search_student = forms.CharField(
        label=_("Search a student"),
        widget=forms.TextInput,
        required=False
    )
    search_school = forms.ModelChoiceField(
        label=_("Search by School"),
        queryset=School.objects.all(), widget=forms.Select,
        required=False, to_field_name='id',
        initial=0
    )
    # search_school = forms.ModelChoiceField(
    #     label=_("Search by School"),
    #     queryset=School.objects.all(),
    #     widget=autocomplete.ModelSelect2(url='schools:autocomplete'),
    #     required=False, to_field_name='id',
    #     initial=0
    # )
    school_type = forms.ChoiceField(
        label=_("School type"),
        widget=forms.Select, required=False,
        choices=(
            ('', '----------'),
            ('alp', _('ALP')),
            ('2ndshift', _('2nd Shift')),
        )
    )

    outreach_barcode = forms.RegexField(
        label=_('Outreach barcode'),
        regex=r'^([A-Z]{2})(\d{8})|(-(\d{1}))$',
        widget=forms.TextInput(attrs={'placeholder': 'Format: AA11111111'}),
        required=False
    )

    registration_date = forms.DateField(
        label=_("Registration date"),
        required=True
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
    student_mother_nationality = forms.ModelChoiceField(
        label=_("Mother nationality"),
        queryset=Nationality.objects.all(), widget=forms.Select,
        required=True, to_field_name='id',
    )
    student_registered_in_unhcr = forms.ChoiceField(
        label=_("Registered in UNHCR"),
        widget=forms.Select, required=True,
        choices=(
            ('', '-----------'),
            (1, _("Yes")),
            (0, _("No"))
        )
    )
    student_id_type = forms.ModelChoiceField(
        label=_("ID type"),
        queryset=IDType.objects.all(), widget=forms.Select,
        required=True, to_field_name='id'
    )
    student_id_number = forms.CharField(
        label=_("ID number - Cell 14"),
        widget=forms.TextInput, required=True
    )
    student_phone_prefix = forms.CharField(
        label=_("Phone prefix"),
        widget=forms.TextInput(attrs=({'maxlength': 2})), required=True
    )
    student_phone = forms.CharField(
        label=_("Phone number"),
        widget=forms.TextInput(attrs=({'maxlength': 6})), required=True
    )
    student_address = forms.CharField(
        label=_("Address"),
        widget=forms.TextInput, required=True
    )

    classroom = forms.ModelChoiceField(
        label=_("Current Class"),
        queryset=ClassRoom.objects.exclude(name='n/a'), widget=forms.Select,
        required=True, to_field_name='id',
    )
    section = forms.ModelChoiceField(
        label=_("Current Section"),
        queryset=Section.objects.all(), widget=forms.Select,
        required=True, to_field_name='id',
        initial=1
    )

    student_place_of_birth = forms.CharField(
        label=_("Place of birth"),
        widget=forms.TextInput, required=False
    )
    student_recordnumber = forms.CharField(
        label=_('Identity record number'),
        widget=forms.TextInput, required=False
    )
    number_in_previous_school = forms.CharField(
        label=_("Serial number in previous school"),
        widget=forms.TextInput, required=False
    )

    last_education_level = forms.ModelChoiceField(
        label=_('Last education level'),
        queryset=ClassRoom.objects.all(), widget=forms.Select,
        required=True, to_field_name='id',
        initial=11
    )
    last_school_type = forms.ChoiceField(
        label=_("Last school type"),
        widget=forms.Select, required=True,
        choices=Enrollment.SCHOOL_TYPE,
        initial='na'
    )
    last_school_shift = forms.ChoiceField(
        label=_("Last school shift"),
        widget=forms.Select, required=True,
        choices=Enrollment.SCHOOL_SHIFT,
        initial='na'
    )
    last_school = forms.ModelChoiceField(
        queryset=School.objects.all(), widget=forms.Select,
        label=_('Last school'),
        required=True, to_field_name='id',
    )
    last_education_year = forms.ChoiceField(
        label=_("Last Education year"),
        widget=forms.Select, required=True,
        choices=EDUCATION_YEARS,
        initial='na',
    )
    last_year_result = forms.ChoiceField(
        label=_("Last Education result"),
        widget=forms.Select, required=True,
        choices=(
            ('na', _('n/a')),
            ('graduated', _('Graduated')),
            ('failed', _('Failed'))
        ),
        initial='na'
    )
    participated_in_alp = forms.ChoiceField(
        label=_("Participated in ALP"),
        widget=forms.Select, required=True,
        choices=(
            ('na', _('n/a')),
            ('yes', _('Yes')),
            ('no', _('No')),
        ),
        initial='na'
    )
    # last_informal_edu_level = forms.ModelChoiceField(
    #     label=_("Last informal education level"),
    #     queryset=EducationLevel.objects.all(), widget=forms.Select,
    #     required=True, to_field_name='id',
    #     initial=13
    # )
    last_informal_edu_round = forms.ModelChoiceField(
        label=_("Last informal education round"),
        queryset=ALPRound.objects.all(), widget=forms.Select,
        required=True, to_field_name='id',
        initial=8
    )
    last_informal_edu_final_result = forms.ModelChoiceField(
        label=_("Last informal education status"),
        queryset=ClassLevel.objects.all(), widget=forms.Select,
        required=True, to_field_name='id',
        initial=27
    )
    student_is_justified = forms.BooleanField(required=False, label=_('Justified'))
    student_is_specialneeds = forms.BooleanField(required=False, label=_('Special Needs'))
    student_specialneeds = forms.ModelChoiceField(
        label=_('Special needs program'),
        queryset=SpecialNeeds.objects.all(),
        widget=forms.Select,
        required=False, to_field_name='id'
    )
    student_specialneedsdt = forms.ModelChoiceField(
        label=_('Details Special needs'),
        queryset=SpecialNeedsDt.objects.all(),
        widget=forms.Select,
        required=False, to_field_name='id'
    )
    student_is_financialsupport = forms.BooleanField(required=False, label=_('Is Financial Support'))
    student_Financialsupport_number = forms.CharField(
        label=_('Financial Support Nb'),
        required=False,
        widget=forms.TextInput,
    )
    student_financialsupport = forms.ModelChoiceField(
        label=_('Financial Support Program'),
        queryset=FinancialSupport.objects.all(),
        widget=forms.Select,
        required=False, to_field_name='id'
    )
    student_unhcr_family = forms.RegexField(
        regex=r'^((245)|(380)|(568)|(705)|(781)|(909)|(947)|(954)|(LEB)|(leb))-[0-9][0-9][C]\d{5}$',
        widget=forms.TextInput(attrs={'placeholder': 'Format: XXX-XXCXXXXX'}),
        required=False,
        label=_('UNHCR Family Nb.'),
    )
    student_unhcr_personal = forms.RegexField(
        label=_('UNHCR Personal Nb.'),
        regex=r'^((245)|(380)|(568)|(705)|(781)|(909)|(947)|(954)|(LEB)|(leb))-[0-9]{8}$',
        widget=forms.TextInput(attrs={'placeholder': 'Format: XXX-XXXXXXXX'}),
        required=False,
    )
 #   student_id_image = forms.ImageField(
     #   required=False,
     #   label='_(ID Picture)')
    student_id = forms.CharField(widget=forms.HiddenInput, required=False)
    enrollment_id = forms.CharField(widget=forms.HiddenInput, required=False)
    student_outreach_child = forms.CharField(widget=forms.HiddenInput, required=False)
    age_min_restricted = forms.BooleanField(widget=forms.HiddenInput, required=False)
    age_max_restricted = forms.BooleanField(widget=forms.HiddenInput, required=False)

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(EnrollmentForm, self).__init__(*args, **kwargs)

        instance = kwargs['instance'] if 'instance' in kwargs else ''

        display_registry = ''
        self.helper = FormHelper()
        self.helper.form_show_labels = True
        str_image = ''
        str_id = '-1'
        if instance:
            display_registry = ' d-none'
            form_action = reverse('enrollments:edit', kwargs={'pk': instance.id})
            if instance.student.std_image:
                str_image = instance.student.std_image.url

            if instance.student.id:
                str_id = str(instance.student.id)
        else:
            form_action = reverse('enrollments:add')
            try:
                na_school = School.objects.get(name='n/a').id
            except School.DoesNotExist:
                na_school = 0
            self.fields['last_school'].initial = na_school

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
                    'age_min_restricted',
                    'age_max_restricted',
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
                    HTML('<span class="badge badge-default">1</span>'),
                    Div('search_barcode', css_class='col-md-4'),
                    css_class='row',
                ),
                css_id='register_by_barcode', css_class='bd-callout bd-callout-warning'+display_registry
            ),
            Fieldset(
                None,
                Div(
                    HTML('<h4 id="alternatives-to-hidden-labels">'+_('Search old student (fullname Or ID number)')+'</h4>')
                ),
                Div(
                    HTML('<span class="badge badge-default">1</span>'),
                    Div('school_type', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">2</span>'),
                    Div('search_school', css_class='col-md-4'),
                    HTML('<span class="badge badge-default">3</span>'),
                    Div('search_student', css_class='col-md-3'),
                    css_class='row',
                ),
                css_id='search_options', css_class='bd-callout bd-callout-warning'+display_registry
            ),
            Fieldset(
                None,
                Div(
                    HTML('<h4 id="alternatives-to-hidden-labels">'+_('Basic Data')+'</h4>')
                ),

                Div(

                    HTML('<img src= '+str_image+' enctype=multipart/form-data  height="100" width="100">'),

                    #Div('student_std_image', css_class='col-md-3'),
                ),

                Div(
                    HTML('<span class="badge badge-default">1</span>'),
                    Div('registration_date', css_class='col-md-3'),
                    HTML('<span class="badge badge-default '+display_registry+'">2</span>'),
                    Div('outreach_barcode', css_class='col-md-3'),
                    HTML('<span style="padding-top: 25px;">' +
                         _('The barcode is not required, enter a valid one or leave it empty') +
                         '. <br/><a href="/static/images/barcode_example.png" target="_blank">' +
                         _('Click to see the barcode') + '</a></span>'),
                    css_class='row',
                ),
                Div(
                    HTML('<span class="badge badge-default">3</span>'),
                    Div('student_first_name', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">4</span>'),
                    Div('student_father_name', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">5</span>'),
                    Div('student_last_name', css_class='col-md-3'),
                    css_class='row',
                ),
                Div(
                    HTML('<span class="badge badge-default">6</span>'),
                    Div('student_birthday_year', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">7</span>'),
                    Div('student_birthday_month', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">8</span>'),
                    Div('student_birthday_day', css_class='col-md-3'),
                    css_class='row',
                ),
                Div(
                    HTML('<span class="badge badge-default">9</span>'),
                    Div('student_sex', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">10</span>'),
                    Div('student_nationality', css_class='col-md-3'),
                    css_class='row',
                ),
                Div(
                    HTML('<span class="badge badge-default">11</span>'),
                    Div('student_mother_fullname', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">12</span>'),
                    Div('student_mother_nationality', css_class='col-md-3'),
                    css_class='row',
                ),
                Div(
                    HTML('<span class="badge badge-default">13</span>'),
                    Div('student_registered_in_unhcr', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">14</span>'),
                    Div('student_id_type', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">15</span>'),
                    Div('student_id_number', css_class='col-md-3'),
                    css_class='row',
                ),
                Div(
                    HTML('<span class="badge badge-default">15.1</span>'),
                    Div('student_unhcr_family', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">15.2</span>'),
                    Div('student_unhcr_personal', css_class='col-md-3'),
                    css_class='row',
                ),
                Div(
                    HTML('<span class="badge badge-default">16</span>'),
                    Div('student_phone_prefix', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">17</span>'),
                    Div('student_phone', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">18</span>'),
                    Div('student_address', css_class='col-md-3'),
                    css_class='row',
                ),
                Div(
                    HTML('<span class="badge badge-default">19</span>'),
                    Div('student_place_of_birth', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">20</span>'),
                    Div('student_recordnumber', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">21</span>'),
                    Div('number_in_previous_school', css_class='col-md-3'),
                    css_class='row',
                ),
                css_class='bd-callout bd-callout-warning child_data'
            ),
            Fieldset(
                None,
                Div(
                   # HTML('<div style="background-color:#e6f7ff"> '),
                    Div(
                        HTML('<h4 id="alternatives-to-hidden-labels">' + _('Special needs') + '</h4>')
                        ),
                    Div(
                        HTML('<font color="red"><b>'),
                        Div('student_is_justified', css_class='col-md-3'),
                        HTML('</b></font>'),
                        ),
                        Div(
                        HTML('<font color="green"><b>'),
                        Div('student_is_specialneeds', css_class='col-md-3'),
                        HTML('</b></font>'),
                        ),
                        Div(
                        Div('student_specialneeds', css_class='col-md-3'),
                        Div('student_specialneedsdt', css_class='col-md-3'),
                        css_class='row',
                        ),
                     ),
                     css_class='bd-callout bd-callout-warning child_data'
               # HTML('</div>'),
            ),
            Fieldset(
                None,
                Div(
                    # HTML('<div style="background-color:#e6f7ff"> '),
                    Div(
                        HTML('<h4 id="alternatives-to-hidden-labels">' + _('Financial support') + '</h4>')
                    ),

                    Div(
                        HTML('<font color="navy"><b>'),
                        Div('student_is_financialsupport', css_class='col-md-3'),
                        HTML('</b></font>'),
                    ),
                    Div(
                        Div('student_financialsupport', css_class='col-md-3'),
                        Div('student_Financialsupport_number', css_class='col-md-3'),
                        css_class='row',
                    ),
                    css_class='bd-callout bd-callout-warning child_data'
                ),
                # HTML('</div>'),
            ),

            Fieldset(
                None,
                Div(
                    HTML('<h4 id="alternatives-to-hidden-labels">' + _('Current situation') + '</h4>')
                ),
                Div(
                    HTML('<span class="badge badge-default">1</span>'),
                    Div('classroom', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">2</span>'),
                    Div('section', css_class='col-md-3'),
                    css_class='row',
                ),
                css_class='bd-callout bd-callout-warning child_data'
            ),
            Fieldset(
                None,
                Div(
                    HTML('<h4 id="alternatives-to-hidden-labels">'+_('Last student formal education')+'</h4>')
                ),
                Div(
                    HTML('<span class="badge badge-default">1</span>'),
                    Div('last_education_level', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">2</span>'),
                    Div('last_school_type', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">3</span>'),
                    Div('last_school_shift', css_class='col-md-3'),
                    css_class='row',
                ),
                Div(
                    HTML('<span class="badge badge-default">4</span>'),
                    Div('last_school', css_class='col-md-4'),
                    HTML('<span class="badge badge-default">5</span>'),
                    Div('last_education_year', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">6</span>'),
                    Div('last_year_result', css_class='col-md-3'),
                    css_class='row',
                ),
                css_class='bd-callout bd-callout-warning child_data'
            ),
            Fieldset(
                None,
                Div(
                    HTML('<h4 id="alternatives-to-hidden-labels">'+_('Last student informal education')+'</h4>')
                ),
                Div(
                    HTML('<span class="badge badge-default">1</span>'),
                    Div('participated_in_alp', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">2</span>'),
                    Div('last_informal_edu_round', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">3</span>'),
                    Div('last_informal_edu_final_result', css_class='col-md-3'),
                    css_class='row',
                ),
                css_class='bd-callout bd-callout-warning child_data'
            ),
            FormActions(
                Submit('save', _('Save'), css_class='child_data'),
                Submit('save_add_another', _('Save and add another'), css_class='child_data'),
                # Submit('save_continue_editing', _('Save and continue editing')),
                HTML('<a class="btn btn-info cancel-button" href="/enrollments/list/" translation="' +
                     _('Are you sure you want to cancel this registration?') + '">' + _('Back to list') + '</a>'),
            ),
        Fieldset(
            None,
            Div(
                HTML('<a class="btn btn-success" href={% url "enrollments:saveimage" pk=' + str_id + ' %}>' + _('Upload Pictures') + '  </a>')

            )
        )

        )

    # def clean(self):
    #     super(EnrollmentForm, self).clean()
        # print self.cleaned_data
        # cc_myself = self.cleaned_data.get("cc_myself")

    def save(self, request=None, instance=None):
        if instance:
            serializer = EnrollmentSerializer(instance, data=request.POST)
            if serializer.is_valid():
                serializer.update(validated_data=serializer.validated_data, instance=instance)
                messages.success(request, _('Your data has been sent successfully to the server'))
            else:
                messages.warning(request, serializer.errors)
        else:
            serializer = EnrollmentSerializer(data=request.POST)
            if serializer.is_valid():
                instance = serializer.create(validated_data=serializer.validated_data)
                instance.school = request.user.school
                instance.owner = request.user
                instance.education_year = EducationYear.objects.get(current_year=True)
                initiate_grading(enrollment=instance, term=1)
                initiate_grading(enrollment=instance, term=2)
                initiate_grading(enrollment=instance, term=3)
                initiate_grading(enrollment=instance, term=4)
                messages.success(request, _('Your data has been sent successfully to the server'))
            else:
                messages.warning(request, serializer.errors)
        if instance.id:
            from django.db.models import Q
            std = Student.objects.filter(id=instance.student_id)
            for st in std:
                q_students = Student.objects.filter(
                    Q(first_name=st.first_name, father_name=st.father_name, last_name=st.last_name,
                      mother_fullname=st.mother_fullname, birthday_year=st.birthday_year, birthday_month=
                        st.birthday_month, birthday_day=st.birthday_day)
                    | Q(first_name=st.first_name, father_name=st.father_name, last_name=st.last_name,
                        mother_fullname=st.mother_fullname, id_number=st.id_number)
                    | Q(first_name=st.first_name, father_name=st.father_name, last_name=st.last_name,
                        id_number=st.id_number, birthday_year=st.birthday_year,
                        birthday_month=st.birthday_month,
                        birthday_day=st.birthday_day)
                    | Q(first_name=st.first_name, father_name=st.father_name, last_name=st.last_name,
                        id_number=st.id_number, birthday_year=st.birthday_year)).exclude(id=st.id)
            q_enr = Enrollment.objects.filter(education_year=EducationYear.objects.get(current_year=True), student__in=q_students)
            if q_enr:
                try:
                    DuplicateStd.objects.get(enrollment_id=instance.id, is_solved=False)
                except DuplicateStd.DoesNotExist:
                    # SAVING THE CURRENT ROW
                    q_coordinator = School.objects.get(id=instance.last_school_id)
                    model_duplicatestd = DuplicateStd.objects.create(
                        enrollment_id=instance.id,
                        is_solved=False,
                        school_type='2ndshift',
                        owner=request.user,
                        coordinator_id=q_coordinator.coordinator_id,
                        Level_id=instance.last_education_level_id,
                        section_id=instance.section_id,
                        classroom_id=instance.classroom_id,
                    )
                    model_duplicatestd.save()
                    # SAVING THE SAME AS IT
                    for enr in q_enr:
                        try:
                            DuplicateStd.objects.get(enrollment_id=enr.id, is_solved=False)
                        except DuplicateStd.DoesNotExist:
                            # SAVING THE CURRENT ROW
                            print (enr.school_id)
                            q_coordinator = School.objects.get(id=enr.last_school_id)
                            model_duplicatestd = DuplicateStd.objects.create(
                                enrollment_id=enr.id,
                                is_solved=False,
                                school_type='2ndshift',
                                owner=enr.owner,
                                coordinator_id=q_coordinator.coordinator_id,
                                Level_id=enr.last_education_level_id,
                                section_id=enr.section_id,
                                classroom_id=enr.classroom_id,
                            )
                            model_duplicatestd.save()


    class Meta:
        model = Enrollment
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
            'student_place_of_birth',
            'student_recordnumber',
            'student_phone',
            'student_phone_prefix',
            'student_id_number',
            'student_id_type',
            'student_nationality',
            'student_mother_nationality',
            'student_registered_in_unhcr',
            'participated_in_alp',
            'number_in_previous_school',
            # 'last_informal_edu_level',
            'last_informal_edu_round',
            'last_informal_edu_final_result',
            'student_address',
            'section',
            'classroom',
            'last_year_result',
            'last_school_type',
            'last_school_shift',
            'last_school',
            'last_education_level',
            'last_education_year',
            'outreach_barcode',
            'new_registry',
            'student_outreached',
            'have_barcode',
            'age_min_restricted',
            'age_max_restricted',
            'student_is_justified',
            'student_is_specialneeds',
            'student_specialneeds',
            'student_specialneedsdt',
            'student_is_financialsupport',
            'student_Financialsupport_number',
            'student_financialsupport',
            'student_unhcr_family',
            'student_unhcr_personal',

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


class GradingTermForm(forms.ModelForm):

    exam_result = forms.ChoiceField(
        label=_("Student status"),
        widget=forms.Select, required=False,
        choices=(
            ('', '------------'),
            ('graduated', _('Graduated')),
            ('failed', _('Failed')),
        ),
    )

    def __init__(self, *args, **kwargs):
        super(GradingTermForm, self).__init__(*args, **kwargs)
        instance = kwargs['instance']

        display_exam_result = ''
        self.helper = FormHelper()
        self.helper.form_show_labels = True
        self.helper.form_action = reverse('enrollments:grading', kwargs={'pk': instance.id, 'term': instance.exam_term})
        enrollment_classroom = instance.enrollment.classroom_id

        grades = (
            ('', '------------'),
            (_('A'), _('A')),
            (_('B'), _('B')),
            (_('C'), _('C')),
            (_('D'), _('D')),
            (_('E'), _('E')),
            (_('F'), _('F')),
            (_('G'), _('G')),
        )

        if instance.exam_term in ['3', '4']:
            self.fields['exam_total'].label = _('Final Grade')

        if instance.exam_term in ['1', '2']:
            display_exam_result = ' d-none '
            self.fields['exam_result'].required = False

        if enrollment_classroom in [2, 3, 4]:
            self.fields['exam_result'].choices = (
                ('', '------------'),
                ('graduated', _('Graduated')),
                ('failed', _('Failed')),
                ('uncompleted', _('Uncompleted'))
            )
            self.fields['exam_result_arabic'] = forms.ChoiceField(
                label=_('Arabic') + _('Cycle 1 max grade'), required=True,
                widget=forms.Select, choices=grades
            )

            self.fields['exam_result_language'] = forms.ChoiceField(
                label=_('Foreign language') + _('Cycle 1 max grade'), required=True,
                widget=forms.Select, choices=grades
            )

            self.fields['exam_result_education'] = forms.ChoiceField(
                label=_('Education') + _('Cycle 1 max grade'), required=True,
                widget=forms.Select, choices=grades
            )

            self.fields['exam_result_geo'] = forms.ChoiceField(
                label=_('Geography') + _('Cycle 1 max grade'), required=True,
                widget=forms.Select, choices=grades
            )

            self.fields['exam_result_math'] = forms.ChoiceField(
                label=_('Math') + _('Cycle 1 max grade'), required=True,
                widget=forms.Select, choices=grades
            )

            self.fields['exam_result_science'] = forms.ChoiceField(
                label=_('Science') + _('Cycle 1 max grade'), required=True,
                widget=forms.Select, choices=grades
            )

            self.fields['exam_total'] = forms.ChoiceField(
                label=_('Total Grade') + _('Cycle 1 max grade'), required=True,
                widget=forms.Select, choices=grades
            )

            self.helper.layout = Layout(
                Fieldset(
                    None,
                    Div(
                        HTML('<span class="badge badge-default">1</span>'),
                        Div('exam_result_arabic', css_class='col-md-2'),
                        HTML('<span class="badge badge-default">2</span>'),
                        Div('exam_result_language', css_class='col-md-2'),
                        HTML('<span class="badge badge-default">3</span>'),
                        Div('exam_result_education', css_class='col-md-2'),
                        HTML('<span class="badge badge-default">4</span>'),
                        Div('exam_result_geo', css_class='col-md-2'),
                        css_class='row',
                    ),
                    Div(
                        HTML('<span class="badge badge-default">5</span>'),
                        Div('exam_result_math', css_class='col-md-2'),
                        HTML('<span class="badge badge-default">6</span>'),
                        Div('exam_result_science', css_class='col-md-2'),
                        HTML('<span class="badge badge-default">7</span>'),
                        Div('exam_total', css_class='col-md-4'),
                        css_class='row',
                    ),
                    Div(
                        HTML('<span class="badge badge-default">8</span>'),
                        Div('exam_result', css_class='col-md-2'),
                        css_class='row'+display_exam_result,
                    ),
                    Div(
                        'exam_result_history',
                        'exam_result_physic',
                        'exam_result_chemistry',
                        'exam_result_bio',
                        'exam_result_linguistic_ar',
                        'exam_result_linguistic_en',
                        'exam_result_sociology',
                        'exam_result_physical',
                        'exam_result_artistic',
                        'exam_result_mathematics',
                        'exam_result_sciences',
                        # 'exam_total',
                        css_class='d-none'
                    ),
                    css_class='bd-callout bd-callout-warning'
                ),
                FormActions(
                    Submit('save', _('Save')),
                    HTML('<a class="btn btn-info cancel-button" href="/enrollments/list/" translation="' +
                         _('Are you sure you want to cancel this registration?') + '">' + _('Back to list') + '</a>'),
                )
            )

        if enrollment_classroom in [5, 6, 7]:
            self.fields['exam_result_arabic'] = forms.FloatField(
                label=_('Arabic') + ' (/20)', required=True,
                widget=forms.NumberInput(attrs=({'maxlength': 5})),
                min_value=0, max_value=20
            )

            self.fields['exam_result_language'] = forms.FloatField(
                label=_('Foreign language') + ' (/20)', required=True,
                widget=forms.NumberInput(attrs=({'maxlength': 5})),
                min_value=0, max_value=20
            )

            self.fields['exam_result_education'] = forms.FloatField(
                label=_('Education') + ' (/20)', required=True,
                widget=forms.NumberInput(attrs=({'maxlength': 5})),
                min_value=0, max_value=20
            )

            self.fields['exam_result_geo'] = forms.FloatField(
                label=_('Geography') + ' (/20)', required=True,
                widget=forms.NumberInput(attrs=({'maxlength': 5})),
                min_value=0, max_value=20
            )

            self.fields['exam_result_math'] = forms.FloatField(
                label=_('Math') + ' (/20)', required=True,
                widget=forms.NumberInput(attrs=({'maxlength': 5})),
                min_value=0, max_value=20
            )

            self.fields['exam_result_science'] = forms.FloatField(
                label=_('Science') + ' (/20)', required=True,
                widget=forms.NumberInput(attrs=({'maxlength': 5})),
                min_value=0, max_value=20
            )

            self.fields['exam_total'] = forms.FloatField(
                label=_('Total Grade') + ' (/120)', required=True,
                widget=forms.NumberInput(attrs=({'maxlength': 6})),
                min_value=0, max_value=120
            )

            self.helper.layout = Layout(
                Fieldset(
                    None,
                    Div(
                        HTML('<span class="badge badge-default">1</span>'),
                        Div('exam_result_arabic', css_class='col-md-2'),
                        HTML('<span class="badge badge-default">2</span>'),
                        Div('exam_result_language', css_class='col-md-2'),
                        HTML('<span class="badge badge-default">3</span>'),
                        Div('exam_result_education', css_class='col-md-2'),
                        HTML('<span class="badge badge-default">4</span>'),
                        Div('exam_result_geo', css_class='col-md-2'),
                        css_class='row',
                    ),
                    Div(
                        HTML('<span class="badge badge-default">5</span>'),
                        Div('exam_result_math', css_class='col-md-2'),
                        HTML('<span class="badge badge-default">6</span>'),
                        Div('exam_result_science', css_class='col-md-2'),
                        HTML('<span class="badge badge-default">7</span>'),
                        Div('exam_total', css_class='col-md-2'),
                        css_class='row',
                    ),
                    Div(
                        HTML('<span class="badge badge-default">8</span>'),
                        Div('exam_result', css_class='col-md-2'),
                        css_class='row' + display_exam_result,
                    ),
                    Div(
                        'exam_result_history',
                        'exam_result_physic',
                        'exam_result_chemistry',
                        'exam_result_bio',
                        'exam_result_linguistic_ar',
                        'exam_result_linguistic_en',
                        'exam_result_sociology',
                        'exam_result_physical',
                        'exam_result_artistic',
                        'exam_result_mathematics',
                        'exam_result_sciences',
                        css_class='d-none'
                    ),
                    css_class='bd-callout bd-callout-warning'
                ),
                FormActions(
                    Submit('save', _('Save')),
                    HTML('<a class="btn btn-info cancel-button" href="/enrollments/list/" translation="' +
                         _('Are you sure you want to cancel this registration?') + '">' + _('Back to list') + '</a>'),
                )
            )

        if enrollment_classroom in [8, 9, 10]:
            self.fields['exam_result_arabic'] = forms.FloatField(
                label=_('Arabic') + ' (/60)', required=True,
                widget=forms.NumberInput(attrs=({'maxlength': 5})),
                min_value=0, max_value=60
            )

            self.fields['exam_result_language'] = forms.FloatField(
                label=_('Foreign language') + ' (/40)', required=True,
                widget=forms.NumberInput(attrs=({'maxlength': 5})),
                min_value=0, max_value=40
            )

            self.fields['exam_result_education'] = forms.FloatField(
                label=_('Education') + ' (/20)', required=True,
                widget=forms.NumberInput(attrs=({'maxlength': 5})),
                min_value=0, max_value=20
            )

            self.fields['exam_result_geo'] = forms.FloatField(
                label=_('Geography') + ' (/20)', required=True,
                widget=forms.NumberInput(attrs=({'maxlength': 5})),
                min_value=0, max_value=20
            )

            self.fields['exam_result_history'] = forms.FloatField(
                label=_('History') + ' (/20)', required=True,
                widget=forms.NumberInput(attrs=({'maxlength': 5})),
                min_value=0, max_value=20
            )

            self.fields['exam_result_math'] = forms.FloatField(
                label=_('Math') + ' (/60)', required=True,
                widget=forms.NumberInput(attrs=({'maxlength': 5})),
                min_value=0, max_value=60
              )

            self.fields['exam_result_physic'] = forms.FloatField(
                label=_('Physic') + ' (/20)', required=True,
                widget=forms.NumberInput(attrs=({'maxlength': 5})),
                min_value=0, max_value=20
            )

            self.fields['exam_result_chemistry'] = forms.FloatField(
                label=_('Chemistry') + ' (/20)', required=True,
                widget=forms.NumberInput(attrs=({'maxlength': 5})),
                min_value=0, max_value=20
            )

            self.fields['exam_result_bio'] = forms.FloatField(
                label=_('Biology') + ' (/20)', required=True,
                widget=forms.NumberInput(attrs=({'maxlength': 5})),
                min_value=0, max_value=20
            )

            self.fields['exam_total'] = forms.FloatField(
                label=_('Total Grade') + ' (/280)', required=True,
                widget=forms.NumberInput(attrs=({'maxlength': 6})),
                min_value=0, max_value=280
            )

            self.helper.layout = Layout(
                Fieldset(
                    None,
                    Div(
                        HTML('<span class="badge badge-default">1</span>'),
                        Div('exam_result_arabic', css_class='col-md-2'),
                        HTML('<span class="badge badge-default">2</span>'),
                        Div('exam_result_language', css_class='col-md-2'),
                        HTML('<span class="badge badge-default">3</span>'),
                        Div('exam_result_education', css_class='col-md-2'),
                        HTML('<span class="badge badge-default">4</span>'),
                        Div('exam_result_geo', css_class='col-md-2'),
                        css_class='row',
                    ),
                    Div(
                        HTML('<span class="badge badge-default">5</span>'),
                        Div('exam_result_history', css_class='col-md-2'),
                        HTML('<span class="badge badge-default">6</span>'),
                        Div('exam_result_math', css_class='col-md-2'),
                        HTML('<span class="badge badge-default">7</span>'),
                        Div('exam_result_physic', css_class='col-md-2'),
                        HTML('<span class="badge badge-default">8</span>'),
                        Div('exam_result_chemistry', css_class='col-md-2'),
                        css_class='row',
                    ),
                    Div(
                        HTML('<span class="badge badge-default">9</span>'),
                        Div('exam_result_bio', css_class='col-md-2'),
                        HTML('<span class="badge badge-default">10</span>'),
                        Div('exam_total', css_class='col-md-2'),
                        css_class='row',
                    ),
                    Div(
                        HTML('<span class="badge badge-default">11</span>'),
                        Div('exam_result', css_class='col-md-2'),
                        css_class='row' + display_exam_result,
                    ),
                    Div(
                        'exam_result_science',
                        'exam_result_linguistic_ar',
                        'exam_result_linguistic_en',
                        'exam_result_sociology',
                        'exam_result_physical',
                        'exam_result_artistic',
                        'exam_result_mathematics',
                        'exam_result_sciences',
                        css_class='d-none'
                    ),
                    css_class='bd-callout bd-callout-warning'
                ),
                FormActions(
                    Submit('save', _('Save')),
                    HTML('<a class="btn btn-info cancel-button" href="/enrollments/list/" translation="' +
                         _('Are you sure you want to cancel this registration?') + '">' + _('Back to list') + '</a>'),
                )
            )

        if enrollment_classroom == 1:
            self.fields['exam_result_linguistic_ar'] = forms.FloatField(
                label=_('Linguistic field/Arabic') + ' (/6)', required=True,
                widget=forms.NumberInput,
                min_value=0, max_value=6
            )

            self.fields['exam_result_linguistic_en'] = forms.FloatField(
                label=_('Linguistic field/Foreign language') + ' (/6)', required=True,
                widget=forms.NumberInput,
                min_value=0, max_value=6
            )

            self.fields['exam_result_sociology'] = forms.FloatField(
                label=_('Sociology field') + ' (/6)', required=True,
                widget=forms.NumberInput,
                min_value=0, max_value=6
            )

            self.fields['exam_result_physical'] = forms.FloatField(
                label=_('Physical field') + ' (/6)', required=True,
                widget=forms.NumberInput,
                min_value=0, max_value=6
            )

            self.fields['exam_result_artistic'] = forms.FloatField(
                label=_('Artistic field') + ' (/6)', required=True,
                widget=forms.NumberInput,
                min_value=0, max_value=6
            )

            self.fields['exam_result_mathematics'] = forms.FloatField(
                label=_('Scientific domain/Mathematics') + ' (/6)', required=True,
                widget=forms.NumberInput,
                min_value=0, max_value=6
            )

            self.fields['exam_result_sciences'] = forms.FloatField(
                label=_('Scientific domain/Sciences') + ' (/6)', required=True,
                widget=forms.NumberInput,
                min_value=0, max_value=6
            )

            self.fields['exam_total'] = forms.FloatField(
                label=_('Total Grade') + ' (/6)', required=True,
                widget=forms.NumberInput,
                min_value=0, max_value=6
            )

            self.helper.layout = Layout(
                Fieldset(
                    None,
                    Div(
                        HTML('<span class="badge badge-default">1</span>'),
                        Div('exam_result_linguistic_ar', css_class='col-md-2'),
                        HTML('<span class="badge badge-default">2</span>'),
                        Div('exam_result_linguistic_en', css_class='col-md-2'),
                        HTML('<span class="badge badge-default">3</span>'),
                        Div('exam_result_sociology', css_class='col-md-2'),
                        HTML('<span class="badge badge-default">4</span>'),
                        Div('exam_result_physical', css_class='col-md-2'),
                        css_class='row',
                    ),
                    Div(

                        HTML('<span class="badge badge-default">5</span>'),
                        Div('exam_result_artistic', css_class='col-md-2'),
                        HTML('<span class="badge badge-default">6</span>'),
                        Div('exam_result_mathematics', css_class='col-md-2'),
                        HTML('<span class="badge badge-default">7</span>'),
                        Div('exam_result_sciences', css_class='col-md-2'),
                        css_class='row',
                    ),
                    Div(
                        HTML('<span class="badge badge-default">8</span>'),
                        Div('exam_total', css_class='col-md-2'),
                        css_class='row',
                    ),
                    Div(
                        HTML('<span class="badge badge-default">8</span>'),
                        Div('exam_result', css_class='col-md-2'),
                        css_class='row' + display_exam_result,
                    ),
                    Div(
                        'exam_result_arabic',
                        'exam_result_language',
                        'exam_result_education',
                        'exam_result_geo',
                        'exam_result_history',
                        'exam_result_math',
                        'exam_result_science',
                        'exam_result_physic',
                        'exam_result_chemistry',
                        'exam_result_bio',
                        css_class='d-none'
                    ),
                    css_class='bd-callout bd-callout-warning'
                ),
                FormActions(
                    Submit('save', _('Save')),
                    HTML('<a class="btn btn-info cancel-button" href="/enrollments/list/" translation="' +
                         _('Are you sure you want to cancel this registration?') + '">' + _('Back to list') + '</a>'),
                )
            )

    def save(self, instance=None, request=None):
        instance = super(GradingTermForm, self).save()
        messages.success(request, _('Your data has been sent successfully to the server'))

    class Meta:
        model = Enrollment
        fields = (
            'exam_result_arabic',
            'exam_result_language',
            'exam_result_education',
            'exam_result_geo',
            'exam_result_history',
            'exam_result_math',
            'exam_result_science',
            'exam_result_physic',
            'exam_result_chemistry',
            'exam_result_bio',
            'exam_result_linguistic_ar',
            'exam_result_linguistic_en',
            'exam_result_sociology',
            'exam_result_physical',
            'exam_result_artistic',
            'exam_result_mathematics',
            'exam_result_sciences',
            'exam_total',
            'exam_result',
        )
        initial_fields = fields
        widgets = {}

    class Media:
        js = ()


class GradingIncompleteForm(forms.ModelForm):

    exam_result = forms.ChoiceField(
        label=_("Student status"),
        widget=forms.Select, required=True,
        choices=(
            ('', '------------'),
            ('graduated', _('Graduated')),
            ('failed', _('Failed')),
        )
    )

    def __init__(self, *args, **kwargs):
        super(GradingIncompleteForm, self).__init__(*args, **kwargs)
        instance = kwargs['instance']

        self.helper = FormHelper()
        self.helper.form_show_labels = True
        self.helper.form_action = reverse('enrollments:grading', kwargs={'pk': instance.id, 'term': 4})
        enrollment_classroom = instance.enrollment.classroom_id
        if enrollment_classroom == 1:
            pass

        self.helper.layout = Layout(
            Fieldset(
                None,
                Div(
                    HTML('<span class="badge badge-default">1</span>'),
                    Div('exam_result_arabic', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">2</span>'),
                    Div('exam_result_language', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">3</span>'),
                    Div('exam_result_math', css_class='col-md-3'),
                    css_class='row',
                ),
                Div(
                    HTML('<span class="badge badge-default">4</span>'),
                    Div('exam_total', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">5</span>'),
                    Div('exam_result', css_class='col-md-3'),
                    css_class='row',
                ),
                css_class='bd-callout bd-callout-warning'
            ),
            FormActions(
                Submit('save', _('Save')),
                HTML('<a class="btn btn-info cancel-button" href="/enrollments/list/" translation="' +
                     _('Are you sure you want to cancel this registration?') + '">' + _('Back to list') + '</a>'),
            )
        )

    def save(self, instance=None, request=None):
        instance = super(GradingIncompleteForm, self).save()
        messages.success(request, _('Your data has been sent successfully to the server'))

    class Meta:
        model = Enrollment
        fields = (
            'exam_result_arabic',
            'exam_result_language',
            'exam_result_math',
            'exam_total',
            'exam_result',
        )
        initial_fields = fields
        widgets = {}

    class Media:
        js = ()


class StudentMovedForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        moved = kwargs.pop('moved', None)
        super(StudentMovedForm, self).__init__(*args, **kwargs)
        instance = kwargs['instance']

        self.helper = FormHelper()
        self.helper.form_show_labels = True
        self.helper.form_action = reverse('enrollments:moved',
                                          kwargs={'pk': instance.id, 'moved': moved}
                                          )
        self.helper.layout = Layout(
            Fieldset(
                None,
                Div(
                    HTML('<h4 id="alternatives-to-hidden-labels">' + _('Current situation') + '</h4>')
                ),
                Div(
                    HTML('<span class="badge badge-default">1</span>'),
                    Div('classroom', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">2</span>'),
                    Div('section', css_class='col-md-3'),
                    css_class='row',
                ),
                css_class='bd-callout bd-callout-warning'
            ),
            FormActions(
                Submit('save', _('Save')),
                HTML('<a class="btn btn-info cancel-button" href="/enrollments/list/" translation="' + _('Are you sure you want to cancel this registration?') + '">' + _('Back to list') + '</a>'),
            )
        )

    def save(self, instance=None, request=None):
        instance = super(StudentMovedForm, self).save()
        instance.owner = request.user
        instance.school = request.user.school
        instance.education_year = EducationYear.objects.get(current_year=True)
        instance.moved = False
        instance.save()
        messages.success(request, _('Your data has been sent successfully to the server'))

    class Meta:
        model = Enrollment
        fields = (
            'classroom',
            'section',
        )
        initial_fields = fields
        widgets = {}

    class Media:
        js = ()


class LoggingStudentMoveForm(forms.ModelForm):

    student = forms.ModelChoiceField(
        queryset=Student.objects.all(),
        widget=autocomplete.ModelSelect2(url='student_autocomplete')
    )

    def __init__(self, *args, **kwargs):
        super(LoggingStudentMoveForm, self).__init__(*args, **kwargs)

    class Meta:
        model = LoggingStudentMove
        fields = (
            'education_year',
            'student',
            'school_from',
            'school_to',
        )


class EditOldDataForm(forms.ModelForm):

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
    student_birthday_day = forms.ChoiceField(
        label=_("Birthday day"),
        widget=forms.Select, required=True,
        choices=DAYS
    )
    student_mother_fullname = forms.CharField(
        label=_("Mother fullname"),
        widget=forms.TextInput, required=True
    )
    classroom = forms.ModelChoiceField(
        label=_("Current Class"),
        queryset=ClassRoom.objects.exclude(name='n/a'), widget=forms.Select,
        required=True, to_field_name='id',
    )
    section = forms.ModelChoiceField(
        label=_("Current Section"),
        queryset=Section.objects.all(), widget=forms.Select,
        required=True, to_field_name='id',
        initial=1
    )

    def __init__(self, *args, **kwargs):
        super(EditOldDataForm, self).__init__(*args, **kwargs)

        instance = kwargs['instance'] if 'instance' in kwargs else ''

        self.helper = FormHelper()
        self.helper.form_show_labels = True
        self.helper.form_action = reverse('enrollments:edit_old_data', kwargs={'pk': instance.id})

        self.helper.layout = Layout(
            Fieldset(
                None,
                Div(
                    HTML('<h4 id="alternatives-to-hidden-labels">'+_('Basic Data')+'</h4>')
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
                    Div('student_birthday_year', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">5</span>'),
                    Div('student_birthday_month', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">6</span>'),
                    Div('student_birthday_day', css_class='col-md-3'),
                    css_class='row',
                ),
                Div(
                    HTML('<span class="badge badge-default">7</span>'),
                    Div('student_sex', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">8</span>'),
                    Div('student_mother_fullname', css_class='col-md-3'),
                    css_class='row',
                ),
                css_class='bd-callout bd-callout-warning child_data'
            ),
            Fieldset(
                None,
                Div(
                    HTML('<h4 id="alternatives-to-hidden-labels">' + _('Current situation') + '</h4>')
                ),
                Div(
                    HTML('<span class="badge badge-default">1</span>'),
                    Div('classroom', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">2</span>'),
                    Div('section', css_class='col-md-3'),
                    css_class='row',
                ),
                css_class='bd-callout bd-callout-warning child_data'
            ),
            FormActions(
                Submit('save', _('Save'), css_class='child_data'),
                HTML('<a class="btn btn-info cancel-button" href="/enrollments/list-old-data/" translation="' +
                     _('Are you sure you want to cancel this registration?') + '">' + _('Back to list') + '</a>'),
            )
        )

    def save(self, request=None, instance=None):
        if instance:
            serializer = EnrollmentSerializer(instance, data=request.POST)
            if serializer.is_valid():
                serializer.update(validated_data=serializer.validated_data, instance=instance)
                messages.success(request, _('Your data has been sent successfully to the server'))

            else:
                messages.warning(request, serializer.errors)

    class Meta:
        model = Enrollment
        fields = (
            'student_first_name',
            'student_father_name',
            'student_last_name',
            'student_mother_fullname',
            'student_sex',
            'student_birthday_year',
            'student_birthday_month',
            'student_birthday_day',
            'section',
            'classroom',
        )
        initial_fields = fields
        widgets = {}

    class Media:
        js = (
            'js/jquery-3.3.1.min.js',
            'js/jquery-ui-1.12.1.js',
            'js/validator.js',
            'js/registrations.js',
        )


class ImageStudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = [
            # 'std_image',
            # 'std_image',
            # 'unhcr_image',
            # 'birthdoc_image',
            'id',
        ]
