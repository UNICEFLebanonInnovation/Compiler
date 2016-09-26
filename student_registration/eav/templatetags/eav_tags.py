import json
from django import template
from django.utils.safestring import mark_safe
from rest_framework.authtoken.models import Token
from student_registration.eav.models import Value

register = template.Library()


@register.filter
def eav_values(entity, entity_ct):
    try:
        return Value.objects.filter(entity_id=entity, entity_ct=entity_ct)
    except Value.DoesNotExist:
        return []


@register.assignment_tag
def eav_column_value(entity, entity_ct, column):
    try:
        value = Value.objects.get(entity_id=entity, entity_ct=entity_ct, attribute=column)
        return value.value_text
    except Value.DoesNotExist:
        return None
