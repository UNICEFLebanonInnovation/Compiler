from __future__ import absolute_import, unicode_literals

from django.contrib import admin
from import_export import fields, resources, widgets
from import_export.admin import ImportExportModelAdmin

from .models import HouseHold, OutreachCaregiver, OutreachChild


class HouseHoldResource(resources.ModelResource):
    class Meta:
        model = HouseHold


class HouseHoldAdmin(ImportExportModelAdmin):
    resource_class = HouseHoldResource
    list_display = (
        'form_id',
        'name',
        'phone_number',
        'residence_type',
        'p_code',
        'number_of_children',
        'barcode_number'
    )
    search_fields = (
        'form_id',
        'name',
        'barcode_number',
    )
    list_filter = (
        'p_code',
        'residence_type',
        'governorate',
        'district'
    )

    def get_export_formats(self):
        from student_registration.users.utils import get_default_export_formats
        return get_default_export_formats()

class OutreachChildImportResource(resources.ModelResource):
    CAREGIVER_COLUMNS = {
        'father_name': "Child's Father Name*",
        'last_name': "Child's Family Name*",
        'mother_full_name': "Mother Full Name*",
        'primary_phone': 'Primary phone number',
        'secondary_phone': 'Confirm primary phone number',
        'nationality': "Child's Nationality*",
        'address': 'Registered child Home Address (Village, Street, Building/Camp, Cadaster)',
        'main_caregiver': "Who is the Child's primary caregiver?",
        'other_caregiver': 'if Other, Please specify',
        'cash_assistance': 'Cash support programmes that the child is already benefiting from',
        'number_of_children': 'Number of children under 18',
        'interview_comment': 'Who will be answering the phone?',
    }

    child_notes = fields.Field(column_name='child_notes', attribute='child_notes')
    outreach_caregiver = fields.Field(
        column_name='outreach_caregiver',
        attribute='outreach_caregiver',
        widget=widgets.ForeignKeyWidget(OutreachCaregiver, 'id'),
    )
    first_name = fields.Field(column_name="Child's First Name*", attribute='first_name')
    birthday_year = fields.Field(column_name='Birthday year*', attribute='birthday_year')
    birthday_month = fields.Field(column_name='Birthday month*', attribute='birthday_month')
    birthday_day = fields.Field(column_name='Birthday day*', attribute='birthday_day')
    gender = fields.Field(column_name="Child's Gender*", attribute='gender')
    nationality = fields.Field(column_name="Child's Nationality*", attribute='nationality')
    family_status = fields.Field(column_name="Child's Marital Status *", attribute='family_status')
    disability = fields.Field(
        column_name='Does the child have any disability or special need?*',
        attribute='disability',
    )
    disability_other = fields.Field(column_name='Specify the Disability', attribute='disability_other')
    working_status = fields.Field(
        column_name='Does the child participate in work?',
        attribute='working_status',
    )
    child_referral = fields.Field(
        column_name='Source of referral of the child to Makani*',
        attribute='child_referral',
    )

    MONTH_MAPPING = {
        '1': '1',
        '01': '1',
        'jan': '1',
        'january': '1',
        '2': '2',
        '02': '2',
        'feb': '2',
        'february': '2',
        '3': '3',
        '03': '3',
        'mar': '3',
        'march': '3',
        '4': '4',
        '04': '4',
        'apr': '4',
        'april': '4',
        '5': '5',
        '05': '5',
        'may': '5',
        '6': '6',
        '06': '6',
        'jun': '6',
        'june': '6',
        '7': '7',
        '07': '7',
        'jul': '7',
        'july': '7',
        '8': '8',
        '08': '8',
        'aug': '8',
        'august': '8',
        '9': '9',
        '09': '9',
        'sep': '9',
        'sept': '9',
        'september': '9',
        '10': '10',
        'oct': '10',
        'october': '10',
        '11': '11',
        'nov': '11',
        'november': '11',
        '12': '12',
        'dec': '12',
        'december': '12',
    }

    NOTE_FIELDS = (
        ('Living Arrangement', 'Living arrangement'),
        ("Does the child have children*", 'Child has children'),
        ("Does the child have siblings?*", 'Child has siblings'),
        ("Does any the Sibilings Have a disability", 'Siblings with disability'),
        ('if Other, Please specify', 'Other caregiver details'),
        ("Is the mother pregnant or expecting?*", 'Mother pregnant or expecting'),
        ('Who will be answering the phone?', 'Phone will be answered by'),
        ('Cash support programmes that the child is already benefiting from', 'Cash support'),
    )

    class Meta:
        model = OutreachChild
        import_id_fields = ('outreach_caregiver', 'first_name')
        fields = (
            'outreach_caregiver',
            'first_name',
            'birthday_year',
            'birthday_month',
            'birthday_day',
            'gender',
            'nationality',
            'family_status',
            'disability',
            'disability_other',
            'working_status',
            'child_referral',
            'child_notes',
        )
        clean_model_instances = True

    def before_import_row(self, row, **kwargs):
        caregiver_values = self._extract_caregiver_values(row)
        caregiver = self._get_or_update_caregiver(caregiver_values)
        self._set_value(row, 'outreach_caregiver', caregiver.id)

        month_value = self._normalize_month(self._get_value(row, 'Birthday month*'))
        self._set_value(row, 'Birthday month*', month_value)

        day_value = self._normalize_integer(self._get_value(row, 'Birthday day*'))
        self._set_value(row, 'Birthday day*', day_value)

        year_value = self._normalize_integer(self._get_value(row, 'Birthday year*'))
        self._set_value(row, 'Birthday year*', year_value)

        disability = self._clean(self._get_value(row, 'Does the child have any disability or special need?*'))
        if not disability or disability.lower() == 'no':
            disability = 'No'
            self._set_value(row, 'Specify the Disability', '')
        self._set_value(row, 'Does the child have any disability or special need?*', disability)

        notes = self._build_notes(row)
        self._set_value(row, 'child_notes', notes)

        working_status = self._clean(self._get_value(row, 'Does the child participate in work?'))
        self._set_value(row, 'Does the child participate in work?', working_status or 'No')

        for key in (
            "Child's First Name*",
            "Child's Father Name*",
            "Child's Family Name*",
            "Child's Gender*",
            "Child's Nationality*",
            "Child's Marital Status *",
            "Does the child have siblings?*",
            "Does the child have children*",
            'Living Arrangement',
            "Does any the Sibilings Have a disability",
            "Is the mother pregnant or expecting?*",
            'Source of referral of the child to Makani*',
        ):
            value = self._clean(self._get_value(row, key))
            self._set_value(row, key, value)

    def _extract_caregiver_values(self, row):
        values = {}
        for field, column in self.CAREGIVER_COLUMNS.items():
            values[field] = self._clean(self._get_value(row, column))
        return values

    def _get_or_update_caregiver(self, values):
        lookup = {
            'father_name': values.get('father_name'),
            'mother_full_name': values.get('mother_full_name'),
            'last_name': values.get('last_name'),
        }
        caregiver, _ = OutreachCaregiver.objects.get_or_create(**lookup)

        primary_phone = values.get('primary_phone')
        secondary_phone = values.get('secondary_phone')
        caregiver.primary_phone = primary_phone or caregiver.primary_phone
        caregiver.secondary_phone = secondary_phone or caregiver.secondary_phone
        caregiver.caregiver_nationality = values.get('nationality') or caregiver.caregiver_nationality
        caregiver.address = values.get('address') or caregiver.address
        caregiver.main_caregiver = values.get('main_caregiver') or caregiver.main_caregiver
        caregiver.number_of_children = values.get('number_of_children') or caregiver.number_of_children
        caregiver.cash_assistance = values.get('cash_assistance') or caregiver.cash_assistance
        interview_comment = self._format_interview_comment(values)
        if interview_comment:
            caregiver.interview_comment = interview_comment
        caregiver.save()
        return caregiver

    def _format_interview_comment(self, values):
        contact_person = values.get('interview_comment')
        if not contact_person:
            return None
        formatted = f"Phone will be answered by: {contact_person}"
        other_caregiver = values.get('other_caregiver')
        if other_caregiver:
            formatted = f"{formatted}\nOther caregiver details: {other_caregiver}"
        return formatted

    def _build_notes(self, row):
        notes = []
        for column, label in self.NOTE_FIELDS:
            value = self._clean(self._get_value(row, column))
            if not value:
                continue
            if column == 'Cash support programmes that the child is already benefiting from' and value.lower() == 'none':
                continue
            notes.append(f"{label}: {value}")
        return '\n'.join(notes)

    def _normalize_month(self, value):
        if value is None:
            return ''
        key = self._clean(value).lower()
        key = key.replace('.', '')
        return self.MONTH_MAPPING.get(key, key)

    def _normalize_integer(self, value):
        cleaned = self._clean(value)
        if not cleaned:
            return ''
        try:
            numeric = float(cleaned)
        except ValueError:
            return cleaned
        if numeric.is_integer():
            return str(int(numeric))
        return str(numeric)

    def _get_value(self, row, key):
        normalized_key = self._normalize_key(key)
        for existing_key in row.keys():
            if self._normalize_key(existing_key) == normalized_key:
                return row[existing_key]
        return ''

    def _set_value(self, row, key, value):
        normalized_key = self._normalize_key(key)
        for existing_key in row.keys():
            if self._normalize_key(existing_key) == normalized_key:
                row[existing_key] = value
                return
        row[key] = value

    def _clean(self, value):
        if value is None:
            return ''
        if isinstance(value, str):
            cleaned = value.strip()
            if cleaned.lower() == 'none':
                return ''
            return cleaned
        return str(value).strip()

    def _normalize_key(self, key):
        import re
        import unicodedata

        if key is None:
            return ''
        normalized = unicodedata.normalize('NFKC', str(key))
        normalized = normalized.replace("’", "'")
        normalized = normalized.replace('*', '')
        normalized = normalized.replace('?', '')
        normalized = normalized.replace('’', "'")
        normalized = normalized.replace('–', '-')
        normalized = normalized.replace('-', ' ')
        normalized = normalized.replace("'", '')
        normalized = re.sub(r'\s+', ' ', normalized)
        normalized = normalized.strip().lower()
        return normalized


class OutreachChildAdmin(ImportExportModelAdmin):
    resource_class = OutreachChildImportResource
    list_display = (
        'full_name',
        'date_of_birth',
        'nationality',
    )
    list_filter = (
        'outreach_caregiver__form_id',
    )
    search_fields = (
        'first_name',
        'outreach_caregiver__father_name',
        'outreach_caregiver__last_name',
    )


admin.site.register(HouseHold, HouseHoldAdmin)
admin.site.register(OutreachChild, OutreachChildAdmin)
