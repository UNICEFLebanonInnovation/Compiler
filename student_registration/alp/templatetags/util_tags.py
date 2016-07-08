import json
from django import template
from django.utils.safestring import mark_safe

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


@register.simple_tag
def json_load_value(data, key):
    list = json.loads(data)
    return list[key]
