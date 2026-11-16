"""MSCC assessment tags, named uniquely to avoid other apps' tag libraries."""
from django import template

register = template.Library()

@register.simple_tag
def wl_programme_sections(programme, provide_french_language=None):
    """Use the same components and maxima as the WL add/edit forms."""
    from student_registration.mscc.education_form import WL_BLN_PROGRAMME_CONFIG

    excluded_prefix = 'english_' if provide_french_language == 'Yes' else 'french_'
    return [(field, config)
            for field, config in WL_BLN_PROGRAMME_CONFIG.get(programme, {}).items()
            if not field.startswith(excluded_prefix)]
