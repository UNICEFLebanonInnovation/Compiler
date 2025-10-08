"""Compatibility helpers for encoding utilities."""


def force_str(value):
    """Return ``value`` coerced to ``str``."""

    if isinstance(value, bytes):
        return value.decode('utf-8')
    return str(value)
