"""Test fixtures providing light-weight stand-ins for pytest-django helpers."""

import pytest


@pytest.fixture
def db():  # noqa: D401 - mimic pytest-django fixture name
    """Provide a no-op database fixture so tests can depend on it."""

    yield
