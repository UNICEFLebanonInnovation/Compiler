from __future__ import unicode_literals, absolute_import, division

from django.utils.translation import ugettext as _
from django import forms
from dal import autocomplete
from .models import Outreach
from student_registration.students.models import Student


class OutreachForm(forms.ModelForm):

    student = forms.ModelChoiceField(
        queryset=Student.objects.all(),
        widget=autocomplete.ModelSelect2(url='student_autocomplete')
    )

    pre_test_total = forms.CharField(widget=forms.TextInput(attrs=({'readonly': 'readonly'})),
                                     required=False)

    post_test_total = forms.CharField(widget=forms.TextInput(attrs=({'readonly': 'readonly'})),
                                      required=False)

    def __init__(self, *args, **kwargs):
        super(OutreachForm, self).__init__(*args, **kwargs)
        if 'instance' in kwargs:
            instance = kwargs['instance']
            self.fields['pre_test_total'].initial = instance.exam_total
            self.fields['post_test_total'].initial = instance.post_exam_total

    class Meta:
        model = Outreach
        fields = '__all__'
        exclude = (
            'partner',
            'location',
            'preferred_language',
            'last_class_level',
            'average_distance',
            'exam_year',
            'exam_month',
            'exam_day',
            'grade',
            'classroom',
            'alp_year',
            'exam_school',
            'enrolled_in_this_school',
            'not_enrolled_in_this_school',
            'exam_not_exist_in_school',
            'registered_in_school',
            'exam_corrector_arabic',
            'exam_corrector_language',
            'exam_corrector_math',
            'exam_corrector_science',
            'post_exam_corrector_arabic',
            'post_exam_corrector_language',
            'post_exam_corrector_math',
            'post_exam_corrector_science',
            'last_year_result',
            'last_informal_edu_result',
            'last_informal_edu_year',
        )


