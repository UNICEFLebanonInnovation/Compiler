"""Generate the MSCC Excel export with each registration's profile photograph.

Each workbook row represents one registration. Child and registration IDs
remain in every export so a child registered in several cycles can still be
identified without losing the cycle or type of a particular record.
"""

import datetime
import io
import json
import logging
import re
from collections import Counter, OrderedDict
from dataclasses import dataclass

import xlsxwriter
from django.db import models
from PIL import Image, ImageOps

from student_registration.child.models import Child
from student_registration.mscc.models import Registration


logger = logging.getLogger(__name__)

PHOTO_INCLUDED = 'Photograph included'
PHOTO_MISSING = 'No photograph uploaded'
PHOTO_UNAVAILABLE = 'Photograph unavailable'

# XML 1.0 cannot represent these characters in XLSX documents.
_INVALID_XML_CHARACTERS = re.compile(
    '[\x00-\x08\x0b\x0c\x0e-\x1f\ud800-\udfff￾￿]'
)

_CHILD_EXCLUDED = frozenset({'id'})
# The photograph has its own column, so the stored file name is not repeated.
_REGISTRATION_EXCLUDED = frozenset({'id', 'child', 'profile_picture'})


@dataclass(frozen=True)
class ExportColumn:
    key: str
    label: str
    aliases: tuple = ()


@dataclass(frozen=True)
class RegistrationSnapshot:
    values: OrderedDict
    photo_data: bytes | None
    photo_status: str


_REQUIRED_COLUMNS = (
    ExportColumn('registration_id', 'Registration ID', ('id',)),
    ExportColumn('child_id', 'Child ID'),
    ExportColumn('photograph', 'Photograph', ('photo', 'profile_picture')),
    ExportColumn('photograph_status', 'Photograph status', ('photo_status',)),
)


def _text(value):
    """Return literal, XML-safe text without inventing values for empty data."""
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
        # Several legacy fields have the same verbose name. Keep each value
        # identifiable while still displaying the familiar registration label.
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
    """Return stable, unambiguous headers, retaining identity and photo columns.

    Optional selectors accept field names, ``child__field`` /
    ``registration__field`` names, or the visible header. Unknown selectors
    do not accidentally fall back to exporting every stored field.
    """
    child_columns = _model_columns(Child, 'child', _CHILD_EXCLUDED)
    registration_columns = _model_columns(Registration, 'registration', _REGISTRATION_EXCLUDED)
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
    if fields:
        if isinstance(fields, str):
            fields = [fields]
        selected = set(fields)
        optional = [column for column in optional if selected.intersection(
            (column.key, column.label) + column.aliases
        )]
    return list(_REQUIRED_COLUMNS) + optional


def _choice_label(field, value):
    if value is None:
        return None
    labels = dict(field.flatchoices)
    return labels.get(value, value)


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
            # Storage names are permanent references; signed storage URLs are
            # neither necessary nor appropriate to retain in a document.
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


def _date_of_birth(child):
    """Use the saved birthday components, including incomplete legacy dates."""
    if child is None:
        return ''
    year = _text(getattr(child, 'birthday_year', None))
    month = _text(getattr(child, 'birthday_month', None))
    day = _text(getattr(child, 'birthday_day', None))
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
    """Load the registration's saved profile picture as a normalised PNG."""
    picture = getattr(registration, 'profile_picture', None)
    if not picture:
        return None, PHOTO_MISSING
    try:
        with picture.open('rb') as source:
            data = source.read()
    except Exception:
        # A storage backend may raise its own network or missing-object errors,
        # rather than OSError. Report this registration's image as unavailable
        # without leaking storage URLs or replacing it with another picture.
        logger.warning('Photograph unavailable for registration ID %s', registration.pk)
        return None, PHOTO_UNAVAILABLE
    try:
        with Image.open(io.BytesIO(data)) as image:
            # Apply camera orientation before removing metadata so the same
            # PNG can be embedded in the workbook.
            image = ImageOps.exif_transpose(image).convert('RGB')
            image.thumbnail((384, 480), Image.Resampling.LANCZOS)
            destination = io.BytesIO()
            image.save(destination, format='PNG')
            return destination.getvalue(), PHOTO_INCLUDED
    except (OSError, ValueError, SyntaxError, Image.DecompressionBombError):
        logger.warning('Photograph unavailable for registration ID %s', registration.pk)
        return None, PHOTO_UNAVAILABLE


def registration_snapshot(registration):
    """Read one registration's values and its profile photograph once."""
    child = registration.child
    photo_data, photo_status = load_registration_photo(registration)
    picture = getattr(registration, 'profile_picture', None)
    values = OrderedDict((
        ('registration_id', _text(registration.pk)),
        ('child_id', _text(registration.child_id)),
        ('photograph', _text(picture.name if picture else None)),
        ('photograph_status', photo_status),
        ('child_full_name', ' '.join(
            _text(getattr(child, name, None)).strip()
            for name in ('first_name', 'father_name', 'last_name')
            if child is not None and getattr(child, name, None)
        ) if child is not None else 'Child record unavailable'),
        ('date_of_birth', _date_of_birth(child)),
    ))
    values.update(_field_values(child, Child, 'child', _CHILD_EXCLUDED))
    values.update(_field_values(registration, Registration, 'registration', _REGISTRATION_EXCLUDED))
    return RegistrationSnapshot(values, photo_data, photo_status)


def build_children_workbook(registrations, fields=None):
    """Return an XLSX with each photograph contained in its registration row."""
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
            # write_string keeps names beginning with '=' or URLs as literal
            # registered values instead of executing formulas or hyperlinks.
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
                # Move and size the image with its own row when users sort or
                # filter the workbook. Its full anchor stays inside the row.
                'positioning': 1,
            })
    sheet.autofilter(0, 0, last_row, len(columns) - 1)
    workbook.close()
    return destination.getvalue()
