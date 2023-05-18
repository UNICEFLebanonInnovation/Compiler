from django import forms
from student_registration.attendances.models import AttendanceDt
from datetime import date, datetime, timedelta
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
from student_registration.users.models import (
    User
)
from student_registration.schools.models import (
    School,
)

from collections import OrderedDict
from django.template.loader import render_to_string


class UserAdminForm(forms.ModelForm):

    school = forms.ModelChoiceField(
        queryset=School.objects.filter(is_first_shift='yes'),
        widget=autocomplete.ModelSelect2(url='school_autocomplete')
    )

    def __init__(self, *args, **kwargs):
        super(UserAdminForm, self).__init__(*args, **kwargs)

    class Meta:
        model = User
        fields = '__all__'
