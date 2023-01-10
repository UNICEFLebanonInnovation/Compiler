from django import template
from django.conf import settings

register = template.Library()


@register.filter(name='has_group')
def has_group(user, group_name):
    if user:
        return user.groups.filter(name=group_name).exists()
    return False


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
        # pass
        print(ex)
    return ''
