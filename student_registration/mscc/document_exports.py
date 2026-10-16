"""Export saved registrations and their own profile photographs to Excel.

Each row represents one registration. Both identity columns are always present
so registrations for the same person in different rounds remain distinguishable.
Compiler stores the profile photograph on the registration, rather than on the
child or student. The MSCC profile is the default; other programmes (for
example Dirasa) describe their own registration and person models with an
``ExportProfile``.
"""

import datetime
import io
import json
import logging
import re
from collections import Counter, OrderedDict
from dataclasses import dataclass
from typing import Optional

import xlsxwriter
from django.db import models
from PIL import Image, ImageOps

from student_registration.child.models import Child
from student_registration.mscc.models import Registration


logger = logging.getLogger(__name__)

PHOTO_INCLUDED = 'Photograph included'
PHOTO_MISSING = 'No photograph uploaded'
PHOTO_UNAVAILABLE = 'Photograph unavailable'

# These characters cannot be represented in XML 1.0 spreadsheet documents.
_INVALID_XML_CHARACTERS = re.compile(
    '[\x00-\x08\x0b\x0c\x0e-\x1f\ud800-\udfff￾￿]'
)


@dataclass(frozen=True)
class ExportColumn:
    key: str
    label: str
    aliases: tuple = ()


@dataclass(frozen=True)
class RegistrationSnapshot:
    values: OrderedDict
    photo_data: Optional[bytes]
    photo_status: str


@dataclass(frozen=True)
class ExportProfile:
    """Describe which registration model, person relation and picture to export."""

    registration_model: type
    person_model: type
    person_field: str
    person_label: str
    sheet_name: str
    picture_field: str = 'profile_picture'

    @property
    def person_excluded(self):
        return frozenset({'id'})

    @property
    def registration_excluded(self):
        return frozenset({'id', self.person_field})

    @property
    def person_id_key(self):
        return '{}_id'.format(self.person_field)

    @property
    def required_columns(self):
        return (
            ExportColumn('registration_id', 'Registration ID', ('id',)),
            ExportColumn(self.person_id_key, '{} ID'.format(self.person_label)),
            ExportColumn('photograph', 'Photograph', ('photo',)),
            ExportColumn('photograph_status', 'Photograph status', ('photo_status',)),
        )

    @property
    def full_name_column(self):
        return ExportColumn(
            '{}_full_name'.format(self.person_field),
            '{} full name'.format(self.person_label),
            ('{}_fullname'.format(self.person_field),),
        )


MSCC_PROFILE = ExportProfile(
    registration_model=Registration, person_model=Child, person_field='child',
    person_label='Child', sheet_name='Registered children',
)


def _text(value):
    """Return literal, XML-safe text, preserving empty and incomplete data."""
    if value is None:
        return ''
    if isinstance(value, bool):
        value = 'Yes' if value else 'No'
    elif isinstance(value, (datetime.datetime, datetime.date, datetime.time)):
        value = value.isoformat()
    elif isinstance(value, (dict, list, tuple)):
        value = json.dumps(value, ensure_ascii=False, sort_keys=True, default=str)
    return _INVALID_XML_CHARACTERS.sub('', str(value))


def _model_columns(model, prefix, excluded):
    fields = [field for field in model._meta.concrete_fields if field.name not in excluded]
    labels = [_text(field.verbose_name) for field in fields]
    duplicates = Counter(labels)
    columns = []
    for field, label in zip(fields, labels):
        if duplicates[label] > 1:
            label = '{} ({})'.format(label, field.name)
        columns.append(ExportColumn(
            '{}__{}'.format(prefix, field.name), label,
            (field.name, '{}.{}'.format(prefix, field.name)),
        ))
        if isinstance(field, models.ForeignKey):
            columns.append(ExportColumn(
                '{}__{}_id'.format(prefix, field.name), '{} ID'.format(label),
                ('{}_id'.format(field.name), '{}.{}_id'.format(prefix, field.name)),
            ))
    return columns


def export_columns(fields=None, profile=MSCC_PROFILE):
    """Return headers with permanent identity and photograph columns.

    Optional selectors accept field names, ``child__field`` /
    ``registration__field`` names, dotted names or visible headers. Unknown
    selectors return only the mandatory columns rather than all stored fields.
    """
    required = profile.required_columns
    person_columns = _model_columns(
        profile.person_model, profile.person_field, profile.person_excluded,
    )
    registration_columns = _model_columns(
        profile.registration_model, 'registration', profile.registration_excluded,
    )
    used_labels = {column.label for column in required + tuple(person_columns)}
    registration_columns = [
        ExportColumn(
            column.key,
            'Registration {}'.format(column.label) if column.label in used_labels else column.label,
            column.aliases,
        ) for column in registration_columns
    ]
    optional = [
        profile.full_name_column,
        ExportColumn('date_of_birth', 'Date of birth', ('birthday',)),
    ] + person_columns + registration_columns

    # Include every concrete field even if its verbose name clashes with an
    # identity column, an FK identifier or a generated convenience column.
    unique_optional = []
    used_labels = {column.label for column in required}
    for column in optional:
        label = column.label
        if label in used_labels:
            label = '{} ({})'.format(label, column.key)
        used_labels.add(label)
        aliases = column.aliases + ((column.label,) if label != column.label else ())
        unique_optional.append(ExportColumn(column.key, label, aliases))
    if fields:
        if isinstance(fields, str):
            fields = [fields]
        selected = set(fields)
        unique_optional = [column for column in unique_optional if selected.intersection(
            (column.key, column.label) + column.aliases
        )]
    return list(required) + unique_optional


def _choice_label(field, value):
    if value is None:
        return None
    return dict(field.flatchoices).get(value, value)


def _field_values(instance, model, prefix, excluded):
    values = OrderedDict()
    for field in model._meta.concrete_fields:
        if field.name in excluded:
            continue
        key = '{}__{}'.format(prefix, field.name)
        value = getattr(instance, field.name, None) if instance is not None else None
        if isinstance(field, models.ForeignKey):
            values[key] = _text(value)
            values['{}__{}_id'.format(prefix, field.name)] = _text(
                getattr(instance, field.attname, None) if instance is not None else None
            )
        elif isinstance(field, models.FileField):
            # Retain the saved storage name, never an expiring or private URL.
            values[key] = _text(value.name if value else None)
        elif field.choices:
            values[key] = _text(_choice_label(field, value))
        elif hasattr(field, 'base_field') and field.base_field.choices and value is not None:
            values[key] = '; '.join(
                _text(_choice_label(field.base_field, item)) for item in value
            )
        else:
            values[key] = _text(value)
    return values


def _date_of_birth(person):
    """Use saved birthday components without inventing missing legacy values."""
    if person is None:
        return ''
    year = _text(getattr(person, 'birthday_year', None))
    month = _text(getattr(person, 'birthday_month', None))
    day = _text(getattr(person, 'birthday_day', None))
    try:
        return datetime.date(int(year), int(month), int(day)).isoformat()
    except (ValueError, TypeError):
        parts = []
        if year and year != '0':
            parts.append(year)
        if month and month != '0':
            parts.append('month: {}'.format(month))
        if day and day != '0':
            parts.append('day: {}'.format(day))
        return ', '.join(parts)


def load_registration_photo(registration, picture_field='profile_picture'):
    """Read the registration's saved profile image through its storage backend."""
    picture = getattr(registration, picture_field, None) if registration is not None else None
    if not picture:
        return None, PHOTO_MISSING
    try:
        with picture.open('rb') as source:
            data = source.read()
    except Exception as exc:
        # Remote backends can raise their own connection or missing-object
        # exceptions. Keep this row and report the unavailable photo explicitly,
        # naming the error type so a storage misconfiguration is easy to spot.
        logger.warning(
            'Photograph unavailable for registration ID %s: %s while opening %s via %s',
            registration.pk, type(exc).__name__, picture.name,
            type(getattr(picture, 'storage', None)).__name__,
        )
        return None, PHOTO_UNAVAILABLE
    try:
        with Image.open(io.BytesIO(data)) as source:
            image = ImageOps.exif_transpose(source).convert('RGB')
            image.thumbnail((384, 480), Image.Resampling.LANCZOS)
            # A new pixel-only image strips EXIF, comments and colour profiles,
            # including metadata Pillow otherwise carries into a saved PNG.
            clean_image = Image.new('RGB', image.size)
            clean_image.paste(image)
            destination = io.BytesIO()
            clean_image.save(destination, format='PNG')
            return destination.getvalue(), PHOTO_INCLUDED
    except (OSError, ValueError, SyntaxError, Image.DecompressionBombError) as exc:
        logger.warning(
            'Photograph unavailable for registration ID %s: %s while decoding %s',
            registration.pk, type(exc).__name__, picture.name,
        )
        return None, PHOTO_UNAVAILABLE


def registration_snapshot(registration, profile=MSCC_PROFILE):
    """Read a registration's values and its own profile photograph once."""
    person = getattr(registration, profile.person_field, None)
    photo_data, photo_status = load_registration_photo(registration, profile.picture_field)
    picture = getattr(registration, profile.picture_field, None)
    values = OrderedDict((
        ('registration_id', _text(registration.pk)),
        (profile.person_id_key, _text(getattr(registration, profile.person_id_key, None))),
        ('photograph', _text(picture.name if picture else None)),
        ('photograph_status', photo_status),
        (profile.full_name_column.key, ' '.join(
            _text(getattr(person, name, None)).strip()
            for name in ('first_name', 'father_name', 'last_name')
            if person is not None and getattr(person, name, None)
        ) if person is not None else '{} record unavailable'.format(profile.person_label)),
        ('date_of_birth', _date_of_birth(person)),
    ))
    values.update(_field_values(
        person, profile.person_model, profile.person_field, profile.person_excluded,
    ))
    values.update(_field_values(
        registration, profile.registration_model, 'registration', profile.registration_excluded,
    ))
    return RegistrationSnapshot(values, photo_data, photo_status)


def build_children_workbook(registrations, fields=None, profile=MSCC_PROFILE):
    """Return XLSX bytes with each photo anchored inside its registration row."""
    columns = export_columns(fields, profile)
    destination = io.BytesIO()
    workbook = xlsxwriter.Workbook(destination, {
        'in_memory': True,
        'strings_to_formulas': False,
        'strings_to_urls': False,
    })
    sheet = workbook.add_worksheet(profile.sheet_name)
    heading = workbook.add_format({
        'bold': True, 'bg_color': '#164A68', 'font_color': '#FFFFFF',
        'text_wrap': True, 'valign': 'vcenter', 'border': 1,
    })
    body = workbook.add_format({'text_wrap': True, 'valign': 'top'})
    sheet.freeze_panes(1, 2)
    sheet.set_row(0, 42)
    sheet.set_column(0, len(columns) - 1, 24)
    sheet.set_column(0, 1, 15)
    sheet.set_column(2, 2, 20)
    for index, column in enumerate(columns):
        sheet.write_string(0, index, column.label, heading)

    last_row = 0
    for row, registration in enumerate(registrations, start=1):
        if row >= 1048576:
            raise ValueError('The export exceeds the Excel worksheet row limit.')
        last_row = row
        snapshot = registration_snapshot(registration, profile)
        sheet.set_row(row, 108)
        for index, column in enumerate(columns):
            value = snapshot.values.get(column.key, '')
            if column.key == 'photograph':
                value = '' if snapshot.photo_data else snapshot.photo_status
            if len(value) > 32767:
                raise ValueError('A registered value exceeds the Excel cell text limit.')
            # Explicit strings preserve saved text starting with '=' and URLs
            # without turning it into formulas or clickable external links.
            sheet.write_string(row, index, value, body)
        if snapshot.photo_data:
            image_data = io.BytesIO(snapshot.photo_data)
            with Image.open(image_data) as image:
                scale = min(112 / image.width, 136 / image.height, 1)
            sheet.insert_image(row, 2, '{}_{}_registration_{}.png'.format(
                profile.person_field, snapshot.values[profile.person_id_key], registration.pk,
            ), {
                'image_data': image_data,
                'x_offset': 4, 'y_offset': 4,
                'x_scale': scale, 'y_scale': scale,
                'positioning': 1,
            })
    sheet.autofilter(0, 0, last_row, len(columns) - 1)
    workbook.close()
    return destination.getvalue()
