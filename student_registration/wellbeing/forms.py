from django import forms

from .models import Flag, today

FOLLOW_UP_TYPES = (
    ('Phone call', 'Phone call'),
    ('Home visit', 'Home visit'),
    ('Caregiver visited the center', 'Caregiver visited the center'),
    ('Talked with the child at the center', 'Talked with the child at the center'),
    ('Checked the records', 'Checked the records'),
)


class FollowUpForm(forms.Form):
    follow_up_type = forms.ChoiceField(choices=FOLLOW_UP_TYPES, label='How')
    result = forms.ChoiceField(choices=Flag.RESULTS, label='Result')
    followed_up_on = forms.DateField(label='Date', widget=forms.DateInput(attrs={'type': 'date'}))
    note = forms.CharField(label='Note (optional, no sensitive details)', required=False,
                           widget=forms.Textarea(attrs={'rows': 3}), max_length=2000)

    def __init__(self, *args, flag=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.flag = flag
        self.fields['followed_up_on'].initial = today()
        for field in self.fields.values():
            field.widget.attrs.setdefault('class', 'form-control')

    def clean_followed_up_on(self):
        day = self.cleaned_data['followed_up_on']
        if day > today():
            raise forms.ValidationError('The date is in the future.')
        if self.flag is not None and day < self.flag.opened_on:
            raise forms.ValidationError('The date is before the flag was raised.')
        return day
