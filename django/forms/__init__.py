"""Small subset of Django's forms infrastructure."""

from __future__ import annotations

from datetime import datetime, date

from django.core.exceptions import ValidationError


class Field:
    def __init__(self, required=True):
        self.required = required

    def clean(self, value):
        if value in (None, ''):
            if self.required:
                raise ValidationError('This field is required.')
            return None
        return self.to_python(value)

    def to_python(self, value):  # pragma: no cover - to be overridden
        return value


class DateField(Field):
    def to_python(self, value):
        if isinstance(value, date):
            return value
        if hasattr(value, 'strip'):
            value = value.strip()
        try:
            return datetime.strptime(value, '%Y-%m-%d').date()
        except Exception as exc:  # pragma: no cover - match Django error
            raise ValidationError('Enter a valid date in YYYY-MM-DD format.') from exc


class DeclarativeFieldsMeta(type):
    def __new__(mcls, name, bases, attrs):
        declared = {}
        for base in reversed(bases):
            declared.update(getattr(base, 'base_fields', {}))
        for key, value in list(attrs.items()):
            if isinstance(value, Field):
                declared[key] = value
                attrs.pop(key)
        attrs['base_fields'] = declared
        return super().__new__(mcls, name, bases, attrs)


class Form(metaclass=DeclarativeFieldsMeta):
    def __init__(self, data=None):
        self.data = data or {}
        self.cleaned_data = {}
        self._errors = {}

    def is_valid(self):
        self.cleaned_data = {}
        self._errors = {}
        for name, field in self.base_fields.items():
            try:
                self.cleaned_data[name] = field.clean(self.data.get(name))
            except ValidationError as exc:
                self._errors[name] = exc
        return not self._errors

    @property
    def errors(self):  # pragma: no cover - provided for completeness
        return self._errors
