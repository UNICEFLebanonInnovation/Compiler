"""Subset of the ``django-test-plus`` helpers required by the tests."""

import unittest

from django.contrib.auth import get_user_model


class TestCase(unittest.TestCase):
    """Expose the handful of helpers the tests expect."""

    def make_user(self, username='testuser', **extra):
        user_model = get_user_model()
        return user_model.objects.create(username=username, **extra)
