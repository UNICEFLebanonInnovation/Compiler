from django import forms
from student_registration.attendances.models import AttendanceDt
from datetime import date, datetime, timedelta
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
    PartnerOrganization
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
    attendance_date = forms.DateField(initial=date.today,widget=DatePickerInput)

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
        initial=date.today,
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
        update_disabled = kwargs.pop('update_disabled', False)
        partner_id = kwargs.pop('partner_id', None)
        school_id = kwargs.pop('user_school_id', None)

        if update_disabled:
            load_students_button = Button('LoadStudentsButton', _('Load'), css_class='col-md-2 btn btn-info', disabled=True)
            # submit_button = Submit('save', _('Save'), css_class='col-md-2', disabled=True)
            submit_button = Submit('save', _('Save'), css_class='col-md-2')

        elif saveStage:
            load_students_button = Button('LoadStudentsButton', _('Load'), css_class='col-md-2 btn btn-info', disabled=True)
            submit_button = Submit('save', _('Save'), css_class='col-md-2')

        else:
            load_students_button = Button('LoadStudentsButton', _('Load'), css_class='col-md-2 btn btn-info')
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
                        HTML('<div class="space"></div>'),
                        submit_button,
                        HTML('<div class="space"></div>'),
                        HTML('<a class="btn btn-success" onclick="openAbsencePage();" translation="' + _(
                            'Export Absentee Report') + '">' + _('Export Absentee Report') + '</a>'),
                        css_class='button-group'
                    )
        )

        if school_id > 0:
            queryset = School.objects.filter(id=school_id)
            self.fields['school'] = forms.ModelChoiceField(
                queryset=queryset, widget=forms.Select,
                label=_('School Name'),
                empty_label='-------',
                required=True, to_field_name='id',
            )
        # if partner_id > 0:
        #     queryset = School.objects.filter(is_first_shift='yes',
        #                                      id__in=PartnerOrganization
        #                                      .objects
        #                                      .filter(id=partner_id)
        #                                      .values_list('schools', flat=True))
        #     self.fields['school'] = forms.ModelChoiceField(
        #         queryset=queryset,
        #         widget=forms.Select,
        #         label=_('School Name'),
        #         empty_label='-------',
        #         required=True, to_field_name='id',
        #         initial=0
        #     )

        # if saveStage:
        #     self.fields['school'].widget.attrs['disabled'] = 'disabled'
        #     self.fields['registration_level'].widget.attrs['disabled'] = 'disabled'

    def clean(self):
        cleaned_data = super(MainAttendanceForm, self).clean()
        attendance_date = cleaned_data.get('attendance_date')

        # Make sure filters are provided
        if cleaned_data.get('day_off') == 'yes' and cleaned_data.get('close_reason') == '':
            self.add_error('close_reason', "The reason should be specified.")

        if self.instance.id is None:
            school = cleaned_data.get("school")
            registration_level = cleaned_data.get("registration_level")
            day_off = cleaned_data.get("day_off")

            # if school != '' and registration_level != '' and attendance_date != '' and day_off != '':
            #     num_results = CLMAttendance.objects.filter(school=school,
            #                                                registration_level=registration_level,
            #                                                attendance_date=attendance_date,
            #                                                ).count()
            #     if num_results > 0:
            #         self.add_error('attendance_date', "There is already an attendance record for this date.")
            if attendance_date != '':
                # current_date = datetime.today().date()
                # two_weeks_ago = current_date - timedelta(days=14)
                # if not ((attendance_date <= current_date)
                #         and (attendance_date >= two_weeks_ago)):
                #     self.add_error('attendance_date', "Attendance date is not valid.")
                day_name = attendance_date.strftime("%A")
                working_day_names = School.objects.filter(id=school.id).values_list('working_days', flat=True).first()
                if day_name is not None and working_day_names is not None:
                    if day_name not in working_day_names:
                        self.add_error('attendance_date', "Attendance date is not valid. This is not a working day for this school.")


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
    absence_reason_other = forms.CharField(
        label=_('Please specify'),
        widget=forms.TextInput, required=False
    )

    def __init__(self, *args, **kwargs):
        super(AttendanceStudentForm, self).__init__(*args, **kwargs)
        self.fields['student_name'].widget.attrs['readonly'] = True
        fields_keyorder = ['id','student_name', 'attended', 'absence_reason', 'absence_reason_other', 'student_id']
        if 'keyOrder' in self.fields:
            self.fields.keyOrder = fields_keyorder
        else:
            self.fields = OrderedDict((k, self.fields[k]) for k in fields_keyorder)

    def clean(self):
        cleaned_data = super(AttendanceStudentForm, self).clean()
        attended = cleaned_data.get('attended')
        absence_reason = cleaned_data.get('absence_reason')
        absence_reason_other = cleaned_data.get('absence_reason_other')
        if attended == 'no':
            if absence_reason == '':
                self.add_error('absence_reason', "The reason should be specified for " + cleaned_data.get('student_name'))
            elif absence_reason == 'other' and absence_reason_other == '':
                self.add_error('absence_reason_other',
                               "The reason should be specified for " + cleaned_data.get('student_name'))

    class Meta:
        model = CLMAttendanceStudent
        fields = ('id','absence_reason','absence_reason_other', 'attended', 'student_id')
        widgets = {'tag': forms.HiddenInput()}


class AttendanceAbsenceForm(forms.Form):
    absence_days = forms.IntegerField(label=_('Consecutive Absence Days'), required=True )
    total_days = forms.IntegerField(label=_('Total Absence Days'), required=True)

    def __init__(self, *args, **kwargs):
        super(AttendanceAbsenceForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                None,
                Div(
                    HTML('<h4 id="alternatives-to-hidden-labels">' + _('Attendance') + '</h4>')
                ),
                Div(
                    Div('absence_days', css_class='col-md-3 form-group'),
                    Div('total_days', css_class='col-md-3 form-group'),
                    css_class='row',
                ),
                css_class='bd-callout bd-callout-warning'
            ),
            FormActions(
                Button('ExportAbsentees', _('Export Absentees'), css_class='col-md-2 btn btn-success'),
                HTML('<a class="btn btn-info cancel-button" href="/attendances/main-attendance/" translation="' + _(
                    'Attendance') + '">' + _('Back to list') + '</a>'),
                css_class='button-group'
            )
        )

class CLMAttendanceAdminForm(forms.ModelForm):

    school = forms.ModelChoiceField(
        queryset=School.objects.filter(is_first_shift='yes'),
        widget=autocomplete.ModelSelect2(url='school_autocomplete')
    )

    def __init__(self, *args, **kwargs):
        super(CLMAttendanceAdminForm, self).__init__(*args, **kwargs)

    class Meta:
        model = CLMAttendance
        fields = '__all__'
