"""Partner boundaries shared by bulk selection and last-moment delivery checks."""
from django.db.models import F

from student_registration.schools.models import PartnerOrganization

from .constants import (
    RESOURCE_ATTENDANCE, RESOURCE_CENTER, RESOURCE_REGISTRATION,
    RESOURCE_ROUND, RESOURCE_TEACHER,
)


class PartnerScopeError(ValueError):
    """Sending this record would exceed the saved partner selection."""


def available_partners(user):
    query = PartnerOrganization.objects.order_by('name', 'pk')
    if not user.is_active or not user.is_staff:
        return query.none()
    if user.is_superuser:
        return query
    meta = PartnerOrganization._meta
    if not (user.has_perm('{}.view_{}'.format(meta.app_label, meta.model_name)) or
            user.has_perm('{}.change_{}'.format(meta.app_label, meta.model_name))):
        return query.none()
    if user.partner_id:
        query = query.filter(pk=user.partner_id)
    if user.center_id:
        query = query.filter(pk=user.center.partner_id)
    return query


def validate_registration_partner(registration, partner_id):
    if registration.partner_id != partner_id:
        raise PartnerScopeError('Registration is outside the selected partner. Preview a new request after correcting its links.')
    if registration.center_id and registration.center.partner_id != partner_id:
        raise PartnerScopeError('Registration centre belongs to a different partner. Correct its links before syncing.')


def validate_record_partner(resource, instance, partner_id):
    if not partner_id:
        raise PartnerScopeError('This legacy bulk request has no partner. Start a new request and choose a partner.')
    if resource == RESOURCE_ROUND:
        return  # A shared round contains metadata, not other partners' records.
    if resource == RESOURCE_CENTER:
        if instance.partner_id != partner_id:
            raise PartnerScopeError('Centre is outside the selected partner. Preview a new request.')
    elif resource == RESOURCE_TEACHER:
        if not instance.center_id or instance.center.partner_id != partner_id:
            raise PartnerScopeError('Program staff centre is outside the selected partner.')
    elif resource == RESOURCE_REGISTRATION:
        validate_registration_partner(instance, partner_id)
    elif resource == RESOURCE_ATTENDANCE:
        from student_registration.attendances.models import MSCCAttendanceChild
        if not instance.center_id or instance.center.partner_id != partner_id:
            raise PartnerScopeError('Attendance centre is outside the selected partner.')
        rows = MSCCAttendanceChild.objects.filter(attendance_day=instance).exclude(registration__isnull=True)
        if rows.exclude(registration__partner_id=partner_id).exists():
            raise PartnerScopeError('Attendance includes registrations from another partner. Correct those links first.')
        if rows.exclude(registration__center__isnull=True).exclude(registration__center__partner_id=partner_id).exists():
            raise PartnerScopeError('Attendance includes a registration centre from another partner. Correct those links first.')
        if rows.exclude(child_id=F('registration__child_id')).exists():
            raise PartnerScopeError('Attendance child differs from its registration. Correct those links first.')
    else:
        if not instance.registration_id:
            raise PartnerScopeError('Record has no registration for the selected partner.')
        validate_registration_partner(instance.registration, partner_id)


def validate_bulk_delivery(event, instance, payload):
    if not event.bulk_run_id:
        return
    run = event.bulk_run
    if not run.partner_id:
        raise PartnerScopeError('This legacy bulk request has no partner. Start a new request and choose a partner.')
    if run.requested_by_id:
        from django.contrib.auth import get_user_model
        # Related objects can be cached by a reverse manager or a long-running
        # worker; fetch current account assignments/permissions for this push.
        requester = get_user_model().objects.select_related('center').get(pk=run.requested_by_id)
        if not available_partners(requester).filter(pk=run.partner_id).exists():
            raise PartnerScopeError('The requesting operator no longer has access to this partner. Start a new authorized request.')
    validate_record_partner(event.resource, instance, run.partner_id)
    # Validate the actual serialized references as well: mappings/attendance
    # rows can change while the dispatcher builds a payload.
    if event.resource in (RESOURCE_CENTER, RESOURCE_TEACHER, RESOURCE_REGISTRATION, RESOURCE_ATTENDANCE):
        center = payload if event.resource == RESOURCE_CENTER else payload.get('center')
        if center and (center.get('partner') or {}).get('source_id') != run.partner_id:
            raise PartnerScopeError('Serialized centre reference is outside the selected partner.')
    if event.resource == RESOURCE_REGISTRATION:
        if (payload.get('partner') or {}).get('source_id') != run.partner_id:
            raise PartnerScopeError('Serialized registration is outside the selected partner.')
    if event.resource == RESOURCE_ATTENDANCE:
        from student_registration.mscc.models import Registration
        children = payload.get('children') or []
        references = {str(row['registration']['source_id']): str(row['child']['source_id'])
                      for row in children if row.get('registration') and row.get('child')}
        actual = {str(pk): str(child_id) for pk,child_id in Registration.objects.filter(
            pk__in=references, partner_id=run.partner_id,
        ).values_list('pk','child_id')}
        if actual != references:
            raise PartnerScopeError('Serialized attendance includes a registration or child outside the selected partner.')
    if run.round_id and event.resource not in (RESOURCE_ROUND, RESOURCE_CENTER, RESOURCE_TEACHER):
        record_round = instance.round_id if event.resource in (RESOURCE_REGISTRATION, RESOURCE_ATTENDANCE) else instance.registration.round_id
        if record_round != run.round_id:
            raise PartnerScopeError('Record moved outside the selected round. Preview a new request.')
