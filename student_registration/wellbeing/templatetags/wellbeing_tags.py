from django import template

register = template.Library()


@register.simple_tag
def percent(part, whole):
    try:
        return '{:.0f}%'.format(100.0 * part / whole) if whole else '—'
    except (TypeError, ValueError):
        return '—'
