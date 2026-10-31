"""Shared access rules for the Dirasa list and exports."""

from django.db.models import Q

from student_registration.users.templatetags.custom_tags import has_group

TEMPORARY_BRIDGING_GOVERNORATES = {7: (7,), 107: (1,), 29: (3, 5)}


def unrestricted_bridging_access(user):
    return bool(user.is_superuser or user.is_staff or has_group(user, 'CLM_BRIDGING_ALL'))


def user_can_access_bridging(user):
    return bool(
        user and user.is_authenticated and user.is_active
        and (unrestricted_bridging_access(user)
             or getattr(user, 'school_id', None) or getattr(user, 'partner_id', None))
    )


def temporary_bridging_governorates(user):
    if getattr(user, 'school_id', None):
        return ()
    return TEMPORARY_BRIDGING_GOVERNORATES.get(getattr(user, 'partner_id', None), ())


def has_temporary_bridging_access(user, registration):
    return bool(
        registration and registration.partner_id == 3
        and registration.governorate_id in temporary_bridging_governorates(user)
    )


def scope_bridging_queryset(queryset, user):
    if not user_can_access_bridging(user):
        return queryset.none()
    if unrestricted_bridging_access(user):
        return queryset
    if getattr(user, 'school_id', None):
        return queryset.filter(school_id=user.school_id)
    own_records = Q(partner_id=user.partner_id)
    governorates = temporary_bridging_governorates(user)
    if governorates:
        own_records |= Q(partner_id=3, governorate_id__in=governorates)
    return queryset.filter(own_records)
