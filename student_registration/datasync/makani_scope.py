"""One eligibility policy for previews, saves, backfills and delivery.

Blank package types are historical Makani records (the Makani list includes
them). TLS and unknown package types must never travel through this channel.
Shared centres remain eligible when they have a Makani registration or staff.
"""
from django.db.models import Exists, OuterRef, Q

from .constants import (
    RESOURCE_ATTENDANCE, RESOURCE_CENTER, RESOURCE_REGISTRATION,
    RESOURCE_ROUND, RESOURCE_TEACHER,
)

MAKANI_TYPES = ('', 'Core-Package', 'Walk-in', 'Walk-in-OOSC', 'Walk-in-In-School')
MAKANI_PROGRAMS = ('BLN', 'ABLN', 'RS', 'CBECE', 'YBLN', 'YFS')
REGISTRATION_FILTER = Q(type__in=MAKANI_TYPES) | Q(type__isnull=True)


class MakaniScopeError(ValueError):
    """A record cannot be sent through the Makani channel."""


def registrations():
    from student_registration.mscc.models import Registration
    return Registration.objects.filter(REGISTRATION_FILTER)


def staff():
    from student_registration.locations.models import ProgramStaff
    # ProgramStaff is the Makani source, independent of Dirasa's Teacher.
    # On a TLS centre require an explicit Makani programme, allowing centres
    # which provide both programmes without publishing TLS-only staff.
    return ProgramStaff.objects.filter(center__isnull=False).filter(
        ~Q(center__is_tls__iexact='yes') | Q(programs__overlap=MAKANI_PROGRAMS),
    ).filter(Q(programs__contained_by=MAKANI_PROGRAMS) | Q(programs__isnull=True))


def centers():
    from student_registration.locations.models import Center
    return Center.objects.filter(
        ~Q(is_tls__iexact='yes') |
        Q(Exists(registrations().filter(center_id=OuterRef('pk')))) |
        Q(Exists(staff().filter(center_id=OuterRef('pk')))),
    )


def scoped_queryset(resource):
    from .serializers import MODEL_FOR_RESOURCE
    if resource == RESOURCE_REGISTRATION:
        return registrations()
    if resource == RESOURCE_TEACHER:
        return staff()
    if resource == RESOURCE_CENTER:
        return centers()
    if resource not in MODEL_FOR_RESOURCE:
        raise MakaniScopeError('Legacy Dirasa teacher sync is disabled. Start a new Makani ProgramStaff request.')
    query = MODEL_FOR_RESOURCE[resource].objects.all()
    if resource == RESOURCE_ROUND:
        return query  # Shared metadata; no registrations or staff embedded.
    if resource == RESOURCE_ATTENDANCE:
        from student_registration.attendances.models import MSCCAttendanceChild
        # Inspect only the children of each candidate day via its indexed FK.
        # A global NOT IN materializes every non-Makani attendance row and
        # can rescan that result for every child when it exceeds work_mem.
        non_makani = MSCCAttendanceChild.objects.filter(
            attendance_day_id=OuterRef('pk'),
        ).exclude(Q(registration__type__in=MAKANI_TYPES) |
                  Q(registration__type__isnull=True, registration__isnull=False))
        # Attendance is replaced as one unit. Never strip TLS child rows out
        # of a mixed day, which would hide a data issue or delete other rows.
        return query.filter(Exists(centers().filter(pk=OuterRef('center_id')))).filter(
            ~Exists(non_makani),
        ).exclude(education_program__in=['TLS', 'Dirasa'])
    return query.filter(Q(registration__type__in=MAKANI_TYPES) |
                        Q(registration__type__isnull=True, registration__isnull=False))


def validate_registration_links(registration):
    from .partner_scope import PartnerScopeError
    if registration.center_id and registration.center.partner_id != registration.partner_id:
        raise PartnerScopeError('Registration centre belongs to a different partner. Correct its links before syncing.')


def validate_relationships(resource, instance):
    """Apply data consistency checks to automatic and bulk delivery alike."""
    from .partner_scope import PartnerScopeError
    if resource == RESOURCE_REGISTRATION:
        validate_registration_links(instance)
    elif resource == RESOURCE_ATTENDANCE:
        from student_registration.attendances.models import MSCCAttendanceChild
        for row in MSCCAttendanceChild.objects.filter(attendance_day=instance).select_related(
                'registration__center', 'child'):
            registration = row.registration
            if registration is None:
                raise PartnerScopeError('Attendance row has no registration.')
            validate_registration_links(registration)
            if row.child_id != registration.child_id:
                raise PartnerScopeError('Attendance child differs from its registration.')
            if registration.center_id != instance.center_id:
                raise PartnerScopeError('Attendance registration belongs to a different centre or partner.')
            if registration.round_id != instance.round_id:
                raise PartnerScopeError('Attendance registration belongs to a different round.')
    elif resource not in (RESOURCE_ROUND, RESOURCE_CENTER, RESOURCE_TEACHER):
        if instance.registration_id:
            validate_registration_links(instance.registration)
            if resource == 'mscc.education_service' and instance.round_id and instance.round_id != instance.registration.round_id:
                raise PartnerScopeError('Education service round differs from its registration.')


def validate_delivery(resource, instance, check_relationships=True):
    if not scoped_queryset(resource).filter(pk=instance.pk).exists():
        raise MakaniScopeError('Record is outside Makani scope (TLS, Dirasa, unknown package type or mixed attendance).')
    if check_relationships:
        validate_relationships(resource, instance)


def eligible_instance(resource, instance):
    """Check deletions without relying on a row which has already gone."""
    if resource == RESOURCE_REGISTRATION:
        return instance.type is None or instance.type in MAKANI_TYPES
    if resource == RESOURCE_TEACHER:
        return bool(instance.center_id and set(instance.programs or []).issubset(MAKANI_PROGRAMS) and (
            (instance.center.is_tls or '').lower() != 'yes' or
            set(instance.programs or []).intersection(MAKANI_PROGRAMS)))
    if resource == RESOURCE_CENTER:
        from .models import SyncEvent
        return (instance.is_tls or '').lower() != 'yes' or SyncEvent.objects.filter(
                resource=resource, source_id=str(instance.pk), status='sent').exists()
    if resource == RESOURCE_ROUND:
        return True
    if resource == RESOURCE_ATTENDANCE:
        # Deleting a day removes its rows before post_delete. Only send a
        # tombstone if it was previously checked and published as Makani.
        from .models import SyncEvent
        return SyncEvent.objects.filter(resource=resource, source_id=str(instance.pk), status='sent').exists()
    return bool(instance.registration_id and (
        instance.registration.type is None or instance.registration.type in MAKANI_TYPES))
