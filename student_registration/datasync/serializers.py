# -*- coding: utf-8 -*-
"""Turn Compiler records into the natural-keyed payloads BMA-NFE expects.

The two databases do not share primary keys, so nothing that crosses the wire
may carry a local foreign key. Every relation is described by the columns that
mean the same thing in both systems -- a round's name, a centre's P-code, a
school's CERD number, a child's UNICEF unique id -- and BMA-NFE resolves those
back into its own rows.

Plain columns are copied verbatim. BMA-NFE runs a subset of this schema and
simply reports back the columns it does not have, so a Compiler-only field
never breaks a push.
"""

from __future__ import unicode_literals, absolute_import, division

import datetime
import decimal
import logging
import uuid

from django.db import models as django_models

from student_registration.attendances.models import (
    MSCCAttendance,
    MSCCAttendanceChild,
)
from student_registration.locations.models import Center
from student_registration.mscc.models import (
    EducationProgrammeAssessment,
    EducationService,
    Referral,
    Registration,
    Round,
)
from student_registration.students.models import Teacher

from .constants import (
    RESOURCE_ATTENDANCE,
    RESOURCE_CENTER,
    RESOURCE_EDUCATION_SERVICE,
    RESOURCE_GRADING,
    RESOURCE_REFERRAL,
    RESOURCE_REGISTRATION,
    RESOURCE_ROUND,
    RESOURCE_TEACHER,
)

logger = logging.getLogger(__name__)

#: Columns that are meaningless in the other database and are never sent.
NEVER_SENT = frozenset({
    'id', 'created', 'modified',
    'owner', 'modified_by', 'deleted_by',
})

#: Uploaded files are not replicated over this channel; only the description
#: and type of each attachment travel.
FILE_FIELD_TYPES = (django_models.FileField, django_models.ImageField)

#: ``students.Teacher`` speaks Dirasa; ``mscc.Teacher`` speaks Makani.
TEACHER_ASSIGNMENT_MAP = {
    'Dirasa only': 'Makani only',
    'Private and Dirasa': 'Private and Makani',
}


def jsonable(value):
    """Return a JSON-serialisable version of a model attribute value."""
    if value is None or isinstance(value, (bool, int, float, str)):
        return value
    if isinstance(value, decimal.Decimal):
        return float(value)
    if isinstance(value, (datetime.datetime, datetime.date, datetime.time)):
        return value.isoformat()
    if isinstance(value, uuid.UUID):
        return str(value)
    if isinstance(value, (list, tuple)):
        return [jsonable(item) for item in value]
    if isinstance(value, dict):
        return {str(key): jsonable(item) for key, item in value.items()}
    return str(value)


def plain_fields(instance, exclude=()):
    """Return the instance's non-relational columns as a JSON-ready dict.

    Args:
        instance: Any Django model instance.
        exclude (iterable): Extra column names to leave out.

    Returns:
        dict: ``{column: value}`` for every concrete, non-relational,
        non-file column that is not excluded.
    """
    skip = NEVER_SENT.union(exclude)
    values = {}
    for field in instance._meta.get_fields():
        if not getattr(field, 'concrete', False):
            continue
        if field.is_relation or field.auto_created:
            continue
        if field.name in skip or isinstance(field, FILE_FIELD_TYPES):
            continue
        values[field.name] = jsonable(getattr(instance, field.name, None))
    return values


# --------------------------------------------------------------------------
# Natural keys
# --------------------------------------------------------------------------

def key_named(obj):
    """Return the natural key of a simple ``name``-keyed lookup row."""
    if obj is None:
        return None
    key = {'source_id': obj.pk, 'name': getattr(obj, 'name', None)}
    name_en = getattr(obj, 'name_en', None)
    if name_en:
        key['name_en'] = name_en
    return key


def key_partner(partner):
    """Return the natural key of a partner organization."""
    return key_named(partner)


def key_round(round_object):
    """Return the natural key of a round, including enough to recreate it."""
    if round_object is None:
        return None
    return {
        'source_id': round_object.pk,
        'name': round_object.name,
        'year': getattr(round_object, 'year', None),
        'current_year': bool(getattr(round_object, 'current_year', False)),
    }


def key_location(location):
    """Return the natural key of an administrative location."""
    if location is None:
        return None
    return {
        'source_id': location.pk,
        'p_code': location.p_code,
        'name': location.name,
        'name_en': location.name_en,
    }


def key_center(center):
    """Return the natural key of a centre."""
    if center is None:
        return None
    return {
        'source_id': center.pk,
        'p_code': center.p_code,
        'name': center.name,
        'partner': key_partner(center.partner),
    }


def key_school(school):
    """Return the natural key of a school, led by its CERD number."""
    if school is None:
        return None
    return {
        'source_id': school.pk,
        'number': school.number,
        'name': school.name,
    }


def key_child(child):
    """Return the natural key of a child."""
    if child is None:
        return None
    return {'source_id': child.pk, 'unicef_id': child.unicef_id}


def key_registration(registration):
    """Return the natural key of a registration.

    Registrations have no business key, so BMA-NFE resolves them purely
    through the mapping built by earlier pushes.
    """
    if registration is None:
        return None
    return {'source_id': registration.pk}


# --------------------------------------------------------------------------
# Resource payloads
# --------------------------------------------------------------------------

def serialize_round(instance):
    """Serialize a programme round."""
    return {'fields': plain_fields(instance)}


def serialize_center(instance):
    """Serialize a centre with its partner and geography."""
    return {
        'fields': plain_fields(instance),
        'partner': key_partner(instance.partner),
        'governorate': key_location(instance.governorate),
        'caza': key_location(instance.caza),
        'cadaster': key_location(instance.cadaster),
    }


def serialize_child(instance):
    """Serialize a child record for embedding in its registration."""
    return {
        'source_id': instance.pk,
        'fields': plain_fields(instance),
        'nationality': key_named(instance.nationality),
        'main_caregiver_nationality': key_named(instance.main_caregiver_nationality),
        'id_type': key_named(instance.id_type),
        'disability': key_named(instance.disability),
        'father_educational_level': key_named(instance.father_educational_level),
        'mother_educational_level': key_named(instance.mother_educational_level),
    }


def _teacher_birthdate(instance):
    """Assemble a birth date from the Compiler's three-part birthday columns.

    ``students.Teacher`` stores the year, month and day separately while
    ``mscc.Teacher`` stores a single date.

    Returns:
        str | None: An ISO date, or ``None`` when the parts are incomplete or
        do not form a real date.
    """
    year = instance.birthday_year
    month = instance.birthday_month
    day = instance.birthday_day
    if not (year and month and day):
        return None
    try:
        return datetime.date(int(year), int(month), int(day)).isoformat()
    except (TypeError, ValueError):
        logger.info(
            'datasync: teacher %s has an unusable birthday (%s-%s-%s)',
            instance.pk, year, month, day,
        )
        return None


def serialize_teacher(instance):
    """Translate a Compiler (Dirasa) teacher into BMA-NFE's centre teacher.

    The two models describe different programmes, so the mapping is explicit
    rather than a field-by-field copy:

    * the three birthday columns become a single ``birthdate``;
    * ``teaching_hours_dirasa`` becomes ``teaching_hours_mscc``;
    * the Dirasa assignment wording becomes the Makani wording;
    * the Dirasa round name is matched against BMA-NFE's own rounds.

    Two things have no direct counterpart. BMA-NFE teachers belong to a centre
    rather than a school, so the centre comes from the operator-maintained
    :class:`~student_registration.datasync.models.SchoolCenterLink` table and
    is left empty until that school has been mapped. Uploaded attachment files
    are not replicated either -- only each attachment's description and type.
    """
    from .center_links import center_for_school

    fields = {
        'first_name': instance.first_name,
        'father_name': instance.father_name,
        'last_name': instance.last_name,
        'mother_fullname': instance.mother_fullname,
        'sex': instance.sex,
        'birthdate': _teacher_birthdate(instance),
        'id_number': instance.id_number,
        'unicef_id': instance.unicef_id,
        'email': instance.email,
        'primary_phone_number': instance.primary_phone_number,
        'subjects_provided': jsonable(instance.subjects_provided),
        'registration_level': jsonable(instance.registration_level),
        'teacher_assignment': TEACHER_ASSIGNMENT_MAP.get(
            instance.teacher_assignment, instance.teacher_assignment
        ),
        'teaching_hours_private_school': instance.teaching_hours_private_school,
        'teaching_hours_mscc': instance.teaching_hours_dirasa,
        'training_sessions_attended': instance.training_sessions_attended,
        'extra_coaching': instance.extra_coaching,
        'extra_coaching_specify': instance.extra_coaching_specify,
    }
    for index in range(1, 6):
        description = 'attach_short_description_{}'.format(index)
        fields[description] = getattr(instance, description, None)

    payload = {
        'fields': {name: jsonable(value) for name, value in fields.items()},
        'round': key_round(instance.round) if instance.round else None,
        'center': key_center(center_for_school(instance.school)),
        'id_type': key_named(instance.id_type),
        'nationality': key_named(instance.nationality),
        'trainings': [key_named(training) for training in instance.trainings.all()],
    }
    for index in range(1, 6):
        name = 'attach_type_{}'.format(index)
        payload[name] = key_named(getattr(instance, name, None))
    return payload


def serialize_registration(instance):
    """Serialize an MSCC registration with its child record inline."""
    return {
        'fields': plain_fields(instance),
        'child': serialize_child(instance.child) if instance.child else None,
        'center': key_center(instance.center),
        'round': key_round(instance.round),
        'partner': key_partner(instance.partner),
    }


def serialize_education_service(instance):
    """Serialize a child's education situation."""
    return {
        'fields': plain_fields(instance),
        'registration': key_registration(instance.registration),
        'round': key_round(instance.round),
    }


def serialize_grading(instance):
    """Serialize a programme grading sheet."""
    return {
        'fields': plain_fields(instance),
        'registration': key_registration(instance.registration),
    }


def serialize_referral(instance):
    """Serialize a referral."""
    return {
        'fields': plain_fields(instance),
        'registration': key_registration(instance.registration),
        'referred_school': key_school(instance.referred_school),
    }


def serialize_attendance(instance):
    """Serialize an attendance day together with all of its child rows.

    The day and its rows travel as one event so BMA-NFE can replace the whole
    day atomically; a row removed in the Compiler disappears there too.
    """
    fields = plain_fields(instance, exclude=('round_id',))
    round_object = Round.objects.filter(pk=instance.round_id).first()

    children = []
    rows = (
        MSCCAttendanceChild.objects
        .filter(attendance_day=instance)
        .select_related('registration', 'child')
    )
    for row in rows:
        if row.registration_id is None:
            continue
        children.append({
            'source_id': row.pk,
            'fields': plain_fields(row),
            'registration': key_registration(row.registration),
            'child': key_child(row.child),
        })

    return {
        'fields': fields,
        'center': key_center(instance.center),
        'round': key_round(round_object),
        'children': children,
    }


#: Maps each replicated model to its resource name and payload builder.
REGISTRY = (
    (Round, RESOURCE_ROUND, serialize_round),
    (Center, RESOURCE_CENTER, serialize_center),
    (Teacher, RESOURCE_TEACHER, serialize_teacher),
    (Registration, RESOURCE_REGISTRATION, serialize_registration),
    (EducationService, RESOURCE_EDUCATION_SERVICE, serialize_education_service),
    (EducationProgrammeAssessment, RESOURCE_GRADING, serialize_grading),
    (Referral, RESOURCE_REFERRAL, serialize_referral),
    (MSCCAttendance, RESOURCE_ATTENDANCE, serialize_attendance),
)

RESOURCE_FOR_MODEL = {model: resource for model, resource, _ in REGISTRY}
SERIALIZER_FOR_RESOURCE = {resource: builder for _, resource, builder in REGISTRY}
MODEL_FOR_RESOURCE = {resource: model for model, resource, _ in REGISTRY}


def serialize(resource, instance):
    """Return the payload for ``instance`` under ``resource``.

    Args:
        resource (str): One of the ``RESOURCE_*`` constants.
        instance: The model instance to serialize.

    Returns:
        dict: The payload to send.

    Raises:
        KeyError: If ``resource`` is not a replicated resource.
    """
    return SERIALIZER_FOR_RESOURCE[resource](instance)


__all__ = [
    'MODEL_FOR_RESOURCE',
    'REGISTRY',
    'RESOURCE_FOR_MODEL',
    'SERIALIZER_FOR_RESOURCE',
    'jsonable',
    'plain_fields',
    'serialize',
]
