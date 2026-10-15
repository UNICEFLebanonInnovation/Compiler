"""Shared access and filtering rules for MSCC registration exports."""

from django.core.exceptions import ValidationError

from student_registration.child.models import Child
from student_registration.users.templatetags.custom_tags import has_group

from .models import Registration


def _is_world_learning(user):
    partner = getattr(user, 'partner', None)
    return bool(partner and partner.is_world_learning)


def user_can_export(user):
    """Whether a user has an MSCC export scope: UNICEF, a partner or a centre."""
    if not user or not user.is_authenticated or not user.is_active:
        return False
    return bool(
        has_group(user, 'MSCC_UNICEF')
        or _is_world_learning(user)
        or (has_group(user, 'MSCC_PARTNER') and user.partner_id)
        or (has_group(user, 'MSCC_CENTER') and user.center_id)
    )


def scoped_registrations(user):
    """Return all nondeleted registrations within the user's MSCC scope.

    The scope matches the list page and profile views: UNICEF and World
    Learning users see every registration, partner users their partner's and
    centre users their centre's. All forward relationships used by the
    document snapshot are loaded together with the registration and child.
    """
    related = [
        field.name for field in Registration._meta.fields
        if field.many_to_one
    ]
    related.extend(
        'child__' + field.name for field in Child._meta.fields
        if field.many_to_one
    )
    queryset = Registration.objects.filter(deleted=False).select_related(
        *related
    ).order_by('pk')
    if not user_can_export(user):
        return queryset.none()
    if has_group(user, 'MSCC_UNICEF') or _is_world_learning(user):
        return queryset
    if has_group(user, 'MSCC_PARTNER') and user.partner_id:
        return queryset.filter(partner_id=user.partner_id)
    if has_group(user, 'MSCC_CENTER') and user.center_id:
        return queryset.filter(center_id=user.center_id)
    return queryset.none()


def _integer_filter(value, name):
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        raise ValidationError('Invalid %s filter.' % name)
    if parsed <= 0:
        raise ValidationError('Invalid %s filter.' % name)
    return parsed


def filter_registrations(queryset, filters=None):
    """Apply the list export filters without widening an access scope.

    A cycle is always required: ``no_round`` selects registrations without a
    cycle and any other value must be a cycle ID.
    """
    filters = filters or {}
    round_id = filters.get('round')
    if not round_id:
        return queryset.none()
    if round_id == 'no_round':
        queryset = queryset.filter(round__isnull=True)
    else:
        queryset = queryset.filter(round_id=_integer_filter(round_id, 'round'))

    nationality = filters.get('nationality')
    if nationality:
        queryset = queryset.filter(
            child__nationality_id=_integer_filter(nationality, 'nationality')
        )

    for name in ('first_name', 'last_name', 'father_name', 'mother_fullname'):
        value = filters.get(name)
        if value:
            queryset = queryset.filter(**{'child__' + name + '__icontains': value})
    return queryset
