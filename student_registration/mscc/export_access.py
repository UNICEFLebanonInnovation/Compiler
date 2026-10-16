"""Scope photograph exports to the registrations the requester may read."""

from django.core.exceptions import ValidationError

from student_registration.child.models import Child
from student_registration.users.templatetags.custom_tags import has_group

from .models import Registration


def user_can_export(user):
    if not user or not user.is_authenticated or not user.is_active:
        return False
    return bool(
        user.is_staff or user.is_superuser
        or has_group(user, 'MSCC_UNICEF')
        or (user.partner and user.partner.is_world_learning)
        or (has_group(user, 'MSCC_PARTNER') and user.partner_id)
        or (has_group(user, 'MSCC_CENTER') and user.center_id)
    )


def _positive_id(value, label):
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        raise ValidationError('Invalid {} filter.'.format(label))
    if parsed <= 0:
        raise ValidationError('Invalid {} filter.'.format(label))
    return parsed


def excel_export_registrations(user, nationality='', first_name='', last_name='',
                               father_name='', mother_fullname='', round=None):
    """Return all matching rows within the existing MSCC partner/centre scope.

    Workbooks are independent of list pagination. An omitted cycle is used by
    the full-export endpoint; the filtered endpoint requires a cycle before
    queueing a job. TLS registrations are handled by their own module.
    """
    related = [field.name for field in Registration._meta.fields if field.many_to_one]
    related += [
        'child__' + field.name for field in Child._meta.fields if field.many_to_one
    ]
    queryset = Registration.objects.filter(
        deleted=False, child__isnull=False,
    ).exclude(type='TLS').select_related(*related).order_by('pk')
    if not user_can_export(user):
        return queryset.none()
    if not (
        user.is_staff or user.is_superuser or has_group(user, 'MSCC_UNICEF')
        or (user.partner and user.partner.is_world_learning)
    ):
        if has_group(user, 'MSCC_PARTNER') and user.partner_id:
            queryset = queryset.filter(partner_id=user.partner_id)
        elif has_group(user, 'MSCC_CENTER') and user.center_id:
            queryset = queryset.filter(center_id=user.center_id)
        else:
            return queryset.none()

    if round == 'no_round':
        queryset = queryset.filter(round__isnull=True)
    elif round not in (None, ''):
        queryset = queryset.filter(round_id=_positive_id(round, 'cycle'))
    if nationality and str(nationality).lower() != 'all':
        queryset = queryset.filter(child__nationality_id=_positive_id(nationality, 'nationality'))
    for field, value in (
        ('first_name', first_name), ('last_name', last_name),
        ('father_name', father_name), ('mother_fullname', mother_fullname),
    ):
        if value:
            queryset = queryset.filter(**{'child__' + field + '__icontains': value})
    return queryset
