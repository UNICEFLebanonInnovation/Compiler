from django import template
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

register = template.Library()


def _get_user_group_names(user):
    """Return a cached set of group names for ``user``.

    The first time this helper is called for a given user instance we hit
    the database to fetch all group names. The result is stored on the user
    object so subsequent checks during the same request are served from
    memory, avoiding repetitive ``SELECT`` queries to ``auth_group`` and
    eliminating the N+1 query pattern.
    """
    if not hasattr(user, "_group_names_cache"):
        user._group_names_cache = set(
            user.groups.values_list("name", flat=True)
        )
    return user._group_names_cache


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
    return group_name in _get_user_group_names(user)


@register.filter(name='have_edit_right')
def have_edit_right(user, name):
    """Return True if the user may edit a given object.

    Superusers automatically have edit rights for all objects so they
    are not limited by specific group assignments.
    """
    if not user:
        return False
    if getattr(user, "is_superuser", False):
        return True
    return name in _get_user_group_names(user)


@register.simple_tag
def allow_admin_login():
    return settings.ADMIN_ALLOW_LOGIN


@register.simple_tag
def idle_logout_minutes():
    """Minutes of inactivity after which AutoLogout ends the session (0 = never).

    base.html hands this to redesign.js, which warns two minutes before and
    keeps the session alive while the user is typing.
    """
    return getattr(settings, 'AUTO_LOGOUT_DELAY', 0) or 0


@register.simple_tag
def get_list_parameters(request):

    url_parameters = '?fake=true'
    for key in request.GET:
        url_parameters += '&{}={}'.format(key, request.GET.get(key))

    return url_parameters


@register.simple_tag
def active_filters(filterset):
    """Return the filters currently applied, ready to render as chips.

    The list FilterSets deliberately blank out field labels and lean on
    placeholders (see ``PlaceholderFilterSet``), so a human-readable name has
    to be recovered per field: the placeholder for text inputs, the empty
    choice for selects, and a prettified field name as a last resort.

    Each entry is ``{'name', 'label', 'value'}`` where ``value`` is the
    display text of the selection rather than the submitted key.
    """
    applied = []
    form = getattr(filterset, 'form', None)
    if form is None:
        return applied

    data = getattr(form, 'data', None)
    if not data:
        return applied

    for name, field in form.fields.items():
        try:
            value = data.get(name)
        except (AttributeError, TypeError):
            continue

        if value in (None, '', []):
            continue

        choices = list(getattr(field, 'choices', None) or [])

        label = field.widget.attrs.get('placeholder') or field.label
        if not label and choices and str(choices[0][0]) == '':
            # Selects carry their name in the empty option ("Governorate").
            label = choices[0][1]
        if not label:
            label = name.replace('__', ' ').replace('_', ' ').strip().title()

        display = value
        for key, text in choices:
            if str(key) == str(value):
                display = text
                break

        applied.append({'name': name, 'label': label, 'value': display})

    return applied


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
