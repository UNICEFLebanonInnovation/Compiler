import json
from django import template
from django.utils.safestring import mark_safe
from rest_framework.authtoken.models import Token

register = template.Library()


@register.assignment_tag
def get_range(start, end):
    return (str(x) for x in range(start, end))


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
    try:
        token = Token.objects.get(user_id=user_id)
    except Token.DoesNotExist:
        token = Token.objects.create(user_id=user_id)
    return token.key
