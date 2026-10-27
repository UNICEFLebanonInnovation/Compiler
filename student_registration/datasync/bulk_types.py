"""Categories exposed by the round bulk-sync screen."""
from .constants import (
    RESOURCE_ATTENDANCE, RESOURCE_CENTER, RESOURCE_EDUCATION_ASSESSMENT,
    RESOURCE_EDUCATION_SERVICE, RESOURCE_GRADING, RESOURCE_REFERRAL,
    RESOURCE_REGISTRATION, RESOURCE_ROUND, RESOURCE_TEACHER,
)

ALL_CATEGORIES = 'all'
SELECTED_CATEGORIES = 'selected'
GLOBAL_CATEGORIES = frozenset((RESOURCE_CENTER, RESOURCE_TEACHER))
CATEGORY_CHOICES = (
    (ALL_CATEGORIES, 'All categories'),
    (RESOURCE_ROUND, 'Round'),
    (RESOURCE_CENTER, 'Centres (including partners)'),
    (RESOURCE_TEACHER, 'Teachers (Makani program staff)'),
    (RESOURCE_REGISTRATION, 'Registrations (including children and photos)'),
    (RESOURCE_EDUCATION_SERVICE, 'Education services'),
    (RESOURCE_EDUCATION_ASSESSMENT, 'Education assessments'),
    (RESOURCE_GRADING, 'Education grading'),
    (RESOURCE_REFERRAL, 'Referrals'),
    (RESOURCE_ATTENDANCE, 'Attendance (including child rows)'),
)
CATEGORY_LABELS = dict(CATEGORY_CHOICES)
RUN_CATEGORY_CHOICES = CATEGORY_CHOICES + ((SELECTED_CATEGORIES, 'Selected categories'),)


def normalize_categories(categories):
    """Keep request identity stable across order, duplicates and All selections."""
    from .constants import RESOURCE_ORDER

    if isinstance(categories, str):
        categories = [categories]
    if not isinstance(categories, (list, tuple)) or not categories:
        raise ValueError('Select at least one category.')
    if any(not isinstance(key, str) or key not in CATEGORY_LABELS for key in categories):
        raise ValueError('Choose valid categories.')
    selected = set(categories)
    if ALL_CATEGORIES in selected or set(RESOURCE_ORDER).issubset(selected):
        return [ALL_CATEGORIES]
    return [key for key in RESOURCE_ORDER if key in selected]


def selection_kind(categories):
    return categories[0] if len(categories) == 1 else SELECTED_CATEGORIES


def requires_round(categories):
    selected = normalize_categories(categories)
    return ALL_CATEGORIES in selected or any(key not in GLOBAL_CATEGORIES for key in selected)
