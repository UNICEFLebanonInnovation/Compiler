"""Visible labels for the list-page filter forms.

Every module's ``PlaceholderFilterSet`` used to blank each field's label and
move the text into the placeholder (text inputs) or the empty ``<option>``
(selects). Once a value was typed or chosen, the control had no name left on
screen, which the accessibility audit ranked as the top usability defect for
low-literacy users. This helper restores a visible label for every control
without touching the individual filter definitions.
"""
import re

from django import forms
from django.utils.translation import gettext_lazy as _

# django-filter derives labels such as "Child first name contains"; the
# lookup suffix adds nothing for the person filtering a list.
_LOOKUP_SUFFIX = re.compile(
    r"\s+(contains|is in|starts with|ends with|is greater than|is less than)$",
    re.IGNORECASE,
)

# Empty-option texts that already read as a value rather than a name.
_VALUE_LIKE = {"", "all", "any", "---------", "--------", "-"}

ALL_LABEL = _("All")


def _fallback_label(name):
    return name.replace("__", " ").replace("_", " ").strip().capitalize()


def label_filter_fields(form):
    """Give every field on ``form`` a visible label.

    * Choice filters whose ``empty_label`` was written as the field's name
      ("Gender", "Governorate", "Package type") use that text as the label,
      and their empty option becomes "All" so it reads as a choice.
    * Other fields keep django-filter's derived label, minus the lookup
      suffix, or fall back to a prettified field name.
    * Text inputs lose the placeholder-as-label; a placeholder that
      disappears on the first keystroke is not a label.
    """
    for name, field in form.fields.items():
        empty_label = getattr(field, "empty_label", None)
        empty_text = str(empty_label).strip() if empty_label is not None else ""

        if empty_text and empty_text.lower() not in _VALUE_LIKE:
            field.label = empty_text
            field.empty_label = ALL_LABEL
        else:
            label = _LOOKUP_SUFFIX.sub("", str(field.label or "").strip())
            field.label = label or _fallback_label(name)

        if isinstance(field.widget, (forms.TextInput, forms.NumberInput)):
            field.widget.attrs.pop("placeholder", None)
