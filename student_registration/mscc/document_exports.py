"""Export saved MSCC registrations and their own profile photographs to Excel.

Each row represents one registration. Both identity columns are always present
so registrations for the same child in different rounds remain distinguishable.
Compiler stores the profile photograph on Registration, rather than Child.
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
    '[\x00-\x08\x0b\x0c\x0e-\x1f\ud800-\udfff\ufffe\uffff]'
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


_REQUIRED_COLUMNS = (
    ExportColumn('registration_id', 'Registration ID', ('id',)),
    ExportColumn('child_id', 'Child ID'),
    ExportColumn('photograph', 'Photograph', ('photo',)),
    ExportColumn('photograph_status', 'Photograph status', ('photo_status',)),
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


def export_columns(fields=None):
    """Return headers with permanent identity and photograph columns.

    Optional selectors accept field names, ``child__field`` /
    ``registration__field`` names, dotted names or visible headers. Unknown
    selectors return only the mandatory columns rather than all stored fields.
    """
    child_columns = _model_columns(Child, 'child', {'id'})
    registration_columns = _model_columns(Registration, 'registration', {'id', 'child'})
    used_labels = {column.label for column in _REQUIRED_COLUMNS + tuple(child_columns)}
    registration_columns = [
        ExportColumn(
            column.key,
            'Registration {}'.format(column.label) if column.label in used_labels else column.label,
            column.aliases,
        ) for column in registration_columns
    ]
    optional = [
        ExportColumn('child_full_name', 'Child full name', ('child_fullname',)),
        ExportColumn('date_of_birth', 'Date of birth', ('birthday',)),
    ] + child_columns + registration_columns

    # Include every concrete field even if its verbose name clashes with an
    # identity column, an FK identifier or a generated convenience column.
    unique_optional = []
    used_labels = {column.label for column in _REQUIRED_COLUMNS}
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
    return list(_REQUIRED_COLUMNS) + unique_optional


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
        elif field.choices and instance is not None:
            values[key] = _text(getattr(instance, 'get_{}_display'.format(field.name))())
        elif hasattr(field, 'base_field') and field.base_field.choices and value is not None:
            labels = dict(field.base_field.flatchoices)
            values[key] = '; '.join(_text(labels.get(item, item)) for item in value)
        else:
            values[key] = _text(value)
    return values


def _date_of_birth(child):
    """Use saved birthday components without inventing missing legacy values."""
    if child is None:
        return ''
    year = _text(child.birthday_year)
    month = _text(child.birthday_month)
    day = _text(child.birthday_day)
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


def load_registration_photo(registration):
    """Read the registration's saved profile image through its storage backend."""
    if registration is None or not registration.profile_picture:
        return None, PHOTO_MISSING
    try:
        with registration.profile_picture.open('rb') as source:
            data = source.read()
    except Exception:
        # Remote backends can raise their own connection or missing-object
        # exceptions. Keep this row and report the unavailable photo explicitly.
        logger.warning('Photograph unavailable for registration ID %s', registration.pk)
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
    except (OSError, ValueError, SyntaxError, Image.DecompressionBombError):
        logger.warning('Photograph unavailable for registration ID %s', registration.pk)
        return None, PHOTO_UNAVAILABLE


def registration_snapshot(registration):
    """Read a registration's values and its own profile photograph once."""
    child = registration.child
    photo_data, photo_status = load_registration_photo(registration)
    values = OrderedDict((
        ('registration_id', _text(registration.pk)),
        ('child_id', _text(registration.child_id)),
        ('photograph', _text(
            registration.profile_picture.name if registration.profile_picture else None
        )),
        ('photograph_status', photo_status),
        ('child_full_name', ' '.join(
            _text(getattr(child, name, None)).strip()
            for name in ('first_name', 'father_name', 'last_name')
            if child is not None and getattr(child, name, None)
        ) if child is not None else 'Child record unavailable'),
        ('date_of_birth', _date_of_birth(child)),
    ))
    values.update(_field_values(child, Child, 'child', {'id'}))
    values.update(_field_values(registration, Registration, 'registration', {'id', 'child'}))
    return RegistrationSnapshot(values, photo_data, photo_status)


def build_children_workbook(registrations, fields=None):
    """Return XLSX bytes with each photo anchored inside its registration row."""
    columns = export_columns(fields)
    destination = io.BytesIO()
    workbook = xlsxwriter.Workbook(destination, {
        'in_memory': True,
        'strings_to_formulas': False,
        'strings_to_urls': False,
    })
    sheet = workbook.add_worksheet('Registered children')
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
        snapshot = registration_snapshot(registration)
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
            sheet.insert_image(row, 2, 'child_{}_registration_{}.png'.format(
                registration.child_id, registration.pk,
            ), {
                'image_data': image_data,
                'x_offset': 4, 'y_offset': 4,
                'x_scale': scale, 'y_scale': scale,
                'positioning': 1,
            })
    sheet.autofilter(0, 0, last_row, len(columns) - 1)
    workbook.close()
    return destination.getvalue()
