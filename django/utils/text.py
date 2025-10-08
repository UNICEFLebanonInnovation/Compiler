"""Utility helpers mirroring a tiny subset of Django's text helpers."""

import re
import unicodedata

_slugify_strip_re = re.compile(r'[^-a-zA-Z0-9]+')
_slugify_hyphenate_re = re.compile(r'[-\s]+')


def slugify(value):
    """Return a basic ASCII slug for ``value``.

    The implementation purposefully mirrors Django's behaviour closely enough
    for the code under test and intentionally keeps the logic simple.
    """

    value = str(value)
    value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
    value = _slugify_strip_re.sub(' ', value).strip().lower()
    return _slugify_hyphenate_re.sub('-', value)
