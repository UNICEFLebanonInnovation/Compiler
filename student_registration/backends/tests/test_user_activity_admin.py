from types import SimpleNamespace
from unittest.mock import Mock

from django.contrib import admin
from django.db.models import Q
from django.test import RequestFactory, SimpleTestCase

from student_registration.backends.admin import UserActivityAdmin
from student_registration.backends.models import UserActivity


class TestUserActivityAdminSearch(SimpleTestCase):
    def setUp(self):
        self.model_admin = UserActivityAdmin(UserActivity, admin.site)
        self.request = RequestFactory().get('/admin/backends/useractivity/')

    def test_email_search_matches_username_exactly(self):
        queryset = Mock()
        filtered_queryset = Mock()
        queryset.filter.return_value = filtered_queryset

        result, may_have_duplicates = self.model_admin.get_search_results(
            self.request,
            queryset,
            'jhanna@unicef.org',
        )

        self.assertIs(result, filtered_queryset)
        self.assertFalse(may_have_duplicates)
        queryset.filter.assert_called_once_with(username='jhanna@unicef.org')

    def test_path_search_requires_leading_slash(self):
        queryset = Mock()
        filtered_queryset = Mock()
        queryset.filter.return_value = filtered_queryset

        result, may_have_duplicates = self.model_admin.get_search_results(
            self.request,
            queryset,
            '/admin/backends/useractivity/',
        )

        self.assertIs(result, filtered_queryset)
        self.assertFalse(may_have_duplicates)
        queryset.filter.assert_called_once_with(
            Q(username__icontains='/admin/backends/useractivity/')
            | Q(path__icontains='/admin/backends/useractivity/')
        )

    def test_non_path_search_does_not_scan_path(self):
        queryset = Mock()
        filtered_queryset = Mock()
        queryset.filter.return_value = filtered_queryset

        result, may_have_duplicates = self.model_admin.get_search_results(
            self.request,
            queryset,
            'admin',
        )

        self.assertIs(result, filtered_queryset)
        self.assertFalse(may_have_duplicates)
        queryset.filter.assert_called_once_with(Q(username__icontains='admin'))

    def test_list_display_uses_annotated_previews(self):
        obj = SimpleNamespace(path_preview='/admin/', data_preview='payload=ok')

        self.assertEqual(self.model_admin.path_preview(obj), '/admin/')
        self.assertEqual(self.model_admin.data_preview(obj), 'payload=ok')
