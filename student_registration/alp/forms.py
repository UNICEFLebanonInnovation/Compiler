
from django import forms
from django.forms import ModelForm
from django.forms.formsets import BaseFormSet
from .models import Outreach
from student_registration.students.models import (
    School
)


class OutreachForm(ModelForm):

    class Meta:
        model = Outreach
        fields = '__all__'


class OutreachFormSet(BaseFormSet):

    def __init__(self, *args, **kwargs):
        super(OutreachFormSet, self).__init__(*args, **kwargs)
        self.queryset = Outreach.objects.all()

    def clean(self):
        if any(self.errors):
            return
