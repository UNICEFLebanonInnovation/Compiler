from __future__ import unicode_literals, absolute_import, division

from django.utils.translation import ugettext as _
from django import forms
from .models import Enrollment


class EnrollmentForm(forms.Form):

    def __init__(self, *args, **kwargs):
        super(EnrollmentForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Enrollment
        fields = '__all__'


