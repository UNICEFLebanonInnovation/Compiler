import json
from django import template
from django.utils.safestring import mark_safe
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import Group
from django.core.urlresolvers import resolve

register = template.Library()


@register.assignment_tag
def get_range(start, end):
    return (str(x) for x in range(start, end))


@register.assignment_tag
def get_range_int(start, end):
    return (x for x in range(start, end))


@register.assignment_tag
def get_range_str(start, end):
    return (str(x-1)+'/'+str(x) for x in range(start, end))


@register.assignment_tag
def get_range_years(start=1990, end=2051):
    return (str(x) for x in range(start, end))


@register.assignment_tag
def get_range_months(start=1, end=13):
    return (str(x) for x in range(start, end))


@register.assignment_tag
def get_range_days(start=1, end=31):
    return (str(x) for x in range(start, end))


@register.filter
def json_loads(data):
    return json.loads(data)


@register.assignment_tag
def json_load_value(data, key):
    key = key.replace("column", "field")
    list = json.loads(data)
    if key in list:
        return list[key]
    return ''


@register.assignment_tag
def get_user_token(user_id):
    # token = Token.objects.get_or_create(user_id=user_id)
    try:
        token = Token.objects.get(user_id=user_id)
    except Token.DoesNotExist:
        token = Token.objects.create(user_id=user_id)
    return token.key


@register.filter(name='has_group')
def has_group(user, group_name):
    try:
        group = Group.objects.get(name=group_name)
        return True if user and group in user.groups.all() else False
    except Group.DoesNotExist:
        return False


@register.filter(name='user_main_role')
def user_main_role(user):
    groups = user.groups.all()
    if 'PMU' in groups:
        return 'pmu'
    if 'COORDINATOR' in groups:
        return 'coordinator'
    if 'DIRECTOR' in groups:
        return 'director'
    if 'SCHOOL' in groups:
        return 'school'
    return 'mehe'


@register.filter(name='is_current_page')
def is_current_page(request, url_name):
    # path_info = request.META.get('PATH_INFO', '')
    # current_url = resolve(path_info).url_name
    # if url_name == current_url:
    #     return True
    return False


@register.filter(name='multiply')
def multiply(value, arg):
    return value*arg


@register.filter(name='percentage')
def percentage(number, total):
    if number:
        return round((number*100)/total)
    return 0
