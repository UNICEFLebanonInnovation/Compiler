"""Simplified transaction helpers."""

from contextlib import contextmanager


@contextmanager
def atomic():  # noqa: D401 - mimic Django signature
    yield


def commit():  # pragma: no cover - provided for completeness
    return None


def rollback():  # pragma: no cover - provided for completeness
    return None
