from django import forms
from student_registration.attendances.models import AttendanceDt
import datetime
from .widgets import DatePickerInput
from django.utils.translation import ugettext as _
from django.forms import inlineformset_factory,HiddenInput
from django.core.urlresolvers import reverse
from django.contrib import messages
from crispy_forms.helper import FormHelper
from crispy_forms.bootstrap import (
    FormActions,
    InlineCheckboxes
)
from crispy_forms.layout import Layout, Fieldset, Button, Submit, Div, Field, HTML
from dal import autocomplete
from .models import CLMAttendance,CLMAttendanceStudent
from student_registration.clm.models import Bridging
from student_registration.schools.models import (
    School,
)

from collections import OrderedDict
from django.template.loader import render_to_string

class AttendanceDtdAdminForm(forms.ModelForm):
    class Meta:
        model = AttendanceDt
        fields = '__all__'


class AttendanceForm(forms.Form):
    CLOSE_REASON = (
        ('', '----------'),
        ('public_holiday', _('Public Holiday')),
        ('school_holiday', _('School Holiday')),
        ('strike', _('Strike')),
        ('weekly_holiday', _('Weekly Holiday')),
        ('roads_closed', _('Roads Closed')),
    )
    attendance_date = forms.DateField(initial=datetime.date.today,widget=DatePickerInput)

    day_off = forms.ChoiceField(
        label=_("Day Off"),
        widget=forms.Select, required=True,
        choices=Bridging.YES_NO,
        initial=1
    )
    close_reason = forms.ChoiceField(
        label=_("Day off reason"),
        widget=forms.Select, required=True,
        choices=CLOSE_REASON,
        initial=1
    )


class MainAttendanceForm(forms.ModelForm):
    school = forms.ModelChoiceField(
        queryset=School.objects.filter(is_first_shift='yes'), widget=forms.Select,
        label=_('School Name'),
        empty_label='-------',
        required=True, to_field_name='id',
        initial=0
    )
    attendance_date = forms.DateField(
        initial=datetime.date.today,
        widget=DatePickerInput,
        label=_('Attendance date')
    )
    registration_level = forms.ChoiceField(
        label=_("Registration level"),
        widget=forms.Select, required=True,
        choices=CLMAttendance.REGISTRATION_LEVEL
    )
    day_off = forms.ChoiceField(
        label=_("Day off ?"),
        widget=forms.Select, required=True,
        choices=CLMAttendance.YES_NO
    )
    close_reason = forms.ChoiceField(
        label=_("Day off reason"),
        widget=forms.Select, required=False,
        choices=CLMAttendance.CLOSE_REASON
    )

    def render_attendance_students(self, request, context):
        template_name = "attendances/attendance_students.html"
        return render_to_string(template_name, context)

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)

        attendance_student_formset = kwargs.pop('attendance_student_formset', None)
        saveStage = kwargs.pop('saveStage', None)

        # if attendance_student_formset:
        #     print('loaded....')

        if saveStage:

            load_students_button = Button('LoadStudentsButton', _('Load'), css_class='col-md-2 btn btn-info ', disabled=True)
            submit_button = Submit('save', _('Save'), css_class='col-md-2')

        else:

            load_students_button = Button('LoadStudentsButton', _('Load'), css_class='col-md-2 btn btn-info ')
            submit_button = Submit('save', _('Save'), css_class='col-md-2', disabled=True)

        attendance_students_context = {}
        if attendance_student_formset:
            attendance_students_context['attendance_student_formset'] = attendance_student_formset

        super(MainAttendanceForm, self).__init__(*args, **kwargs)
        form_action = reverse('attendances:main_attendance')
        self.helper = FormHelper()
        self.helper.form_show_labels = True
        self.helper.form_action = form_action
        self.helper.layout = Layout(
            Fieldset(
                None,
                Div(
                    HTML('<h4 id="alternatives-to-hidden-labels">' + _('Attendance') + '</h4>')

                ),
                Div(
                    Div('attendance_date', css_class='col-md-3 form-group'),
                    Div('school', css_class='col-md-3 form-group'),
                    Div('registration_level', css_class='col-md-3 form-group'),
                    css_class='row',
                ),
                Div(
                    Div('day_off', css_class='col-md-3 form-group'),
                    Div('close_reason', css_class='col-md-3 form-group'),
                    css_class='row',
                ),
                css_class='bd-callout bd-callout-warning'
            ),
            HTML(self.render_attendance_students(self.request, attendance_students_context)),
            FormActions(
                        load_students_button,
                        submit_button,
                        css_class='button-group'
                    )
        )

    def clean(self):
        cleaned_data = super(MainAttendanceForm, self).clean()
        if cleaned_data.get('day_off') == 'yes' and cleaned_data.get('close_reason') == '':
            self.add_error('close_reason', "The reason should be specified.")
        # Make sure filters are provided

        if self.instance is None:
            if cleaned_data.get('school') != '' and cleaned_data.get('registration_level') != '' and cleaned_data.get('attendance_date') != '' and cleaned_data.get('day_off') != '':
                num_results = CLMAttendance.objects.filter(school=cleaned_data['school'],
                                                           registration_level=cleaned_data['registration_level'],
                                                           attendance_date=cleaned_data['attendance_date'],
                                                           ).count()
                if num_results > 0:
                    self.add_error('attendance_date', "There is already an attendance record for this date." )

    class Meta:
        model = CLMAttendance
        fields = (
            'attendance_date',
            'school',
            'registration_level',
            'day_off',
            'close_reason')


class AttendanceStudentForm(forms.ModelForm):

    id = forms.IntegerField(widget=HiddenInput(), required=False)
    student_id = forms.IntegerField(widget=HiddenInput(), required=False)
    student_name = forms.CharField(label=_('Student name'))
    attended = forms.ChoiceField(
        label=_("Student Attended?"),
        widget=forms.Select, required=True,
        choices=CLMAttendanceStudent.YES_NO,
        initial=0
    )
    absence_reason = forms.ChoiceField(
        label=_("Absence reason"),
        widget=forms.Select, required=False,
        choices=CLMAttendanceStudent.ABSENCE_REASON,
        initial=0
    )

    def __init__(self, *args, **kwargs):
        super(AttendanceStudentForm, self).__init__(*args, **kwargs)
        self.fields['student_name'].widget.attrs['readonly'] = True
        fields_keyorder = ['id','student_name', 'attended', 'absence_reason', 'student_id']
        if self.fields.has_key('keyOrder'):
            self.fields.keyOrder = fields_keyorder
        else:
            self.fields = OrderedDict((k, self.fields[k]) for k in fields_keyorder)

    def clean(self):
        cleaned_data = super(AttendanceStudentForm, self).clean()
        if cleaned_data.get('attended') == 'no' and cleaned_data.get('absence_reason') == '':
            self.add_error('absence_reason', "The reason should be specified for " + cleaned_data.get('student_name'))

    class Meta:
        model = CLMAttendanceStudent
        fields = ('id','absence_reason', 'attended', 'student_id')
        widgets = {'tag': forms.HiddenInput()}




