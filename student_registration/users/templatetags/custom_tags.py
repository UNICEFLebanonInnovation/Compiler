from django import template
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

register = template.Library()


@register.filter(name='has_group')
def has_group(user, group_name):
    """Return True if the user belongs to the specified group.

    Superusers are considered members of all groups to ensure they can
    access every module without having explicit group assignments.
    """
    if not user:
        return False
    if getattr(user, "is_superuser", False):
        return True
    return user.groups.filter(name=group_name).exists()


@register.filter(name='have_edit_right')
def have_edit_right(user, name):
    if user:
        return user.groups.filter(name=name).exists()
    return False


@register.simple_tag
def allow_admin_login():
    return settings.ADMIN_ALLOW_LOGIN


@register.simple_tag
def get_list_parameters(request):

    url_parameters = '?fake=true'
    for key in request.GET:
        url_parameters += '&{}={}'.format(key, request.GET.get(key))

    return url_parameters


@register.simple_tag
def check_field_value(record, field):
    try:
        if record.new_fields and field in record.new_fields:
            return 'badge-success'
        if record.updated_fields and field in record.updated_fields:
            return 'badge-primary'
        if record.removed_fields and field in record.removed_fields:
            return 'badge-danger'
    except Exception as ex:
        logger.exception(ex)
    return ''


@register.simple_tag(takes_context=True)
def recent_export_history(context, count=5):
    """Return the latest export history entries for the current user."""
    from student_registration.backends.models import ExportHistory

    request = context.get('request')
    if not request or not request.user.is_authenticated:
        return ExportHistory.objects.none()
    return ExportHistory.objects.filter(created_by=request.user).order_by('-created')[:count]
