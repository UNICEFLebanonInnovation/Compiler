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
from django.contrib.auth.forms import (
    AdminPasswordChangeForm, UserChangeForm, UserCreationForm,
)
from student_registration.users.models import (
    User
)
from student_registration.schools.models import (
    School,
)
from collections import OrderedDict
from django.template.loader import render_to_string

from django.core.exceptions import ValidationError

class UserAdminForm(UserChangeForm):

    school = forms.ModelChoiceField(
        queryset=School.objects.filter(is_closed=False),
        widget=autocomplete.ModelSelect2(url='school_autocomplete'),
        required=False
    )

    def __init__(self, *args, **kwargs):
        super(UserAdminForm, self).__init__(*args, **kwargs)

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if username:
            qs = User.objects.filter(username__iexact=username)
            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise ValidationError("A user with this username already exists.")
        return username

    class Meta:
        model = User
        fields = '__all__'
