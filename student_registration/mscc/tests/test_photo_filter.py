"""Filter Makani and Dirasa lists and exports by whether a photo is saved."""

from types import SimpleNamespace
from unittest.mock import Mock, patch

from django.core.exceptions import ValidationError
from django.test import RequestFactory, SimpleTestCase

from student_registration.mscc import export_access
from student_registration.mscc.export_access import filter_by_photo
from student_registration.mscc.models import Round

# The list filters read the current cycles from the database when the views
# module is first imported. Stub that lookup so these tests need no database.
with patch.object(Round, 'objects') as _rounds:
    _rounds.filter.return_value.values_list.return_value.order_by.return_value.distinct.return_value = []
    from student_registration.clm.filters import BridgingFullFilter, BridgingPartnerFilter
    from student_registration.mscc import views
    from student_registration.mscc.filters import FullFilter, MainFilter


def mock_queryset():
    qs = Mock()
    qs.filter.return_value = qs
    qs.exclude.return_value = qs
    return qs


class PhotoFilterTests(SimpleTestCase):
    def test_with_photo_excludes_empty_and_missing_pictures(self):
        qs = mock_queryset()
        self.assertIs(filter_by_photo(qs, 'yes'), qs)
        self.assertEqual(
            [call.kwargs for call in qs.exclude.call_args_list],
            [{'profile_picture': ''}, {'profile_picture__isnull': True}],
        )
        qs.filter.assert_not_called()

    def test_without_photo_keeps_empty_or_missing_pictures(self):
        qs = mock_queryset()
        filter_by_photo(qs, 'no')
        condition = qs.filter.call_args.args[0]
        self.assertEqual(condition.connector, 'OR')
        self.assertEqual(
            sorted(condition.children), [('profile_picture', ''), ('profile_picture__isnull', True)],
        )
        qs.exclude.assert_not_called()

    def test_blank_value_leaves_the_queryset_alone_and_other_values_are_rejected(self):
        qs = mock_queryset()
        self.assertIs(filter_by_photo(qs, ''), qs)
        self.assertIs(filter_by_photo(qs, None), qs)
        qs.filter.assert_not_called()
        qs.exclude.assert_not_called()
        with self.assertRaises(ValidationError):
            filter_by_photo(qs, 'maybe')

    def test_list_filters_offer_the_photo_choice_on_both_programmes(self):
        for filterset in (MainFilter, FullFilter, BridgingFullFilter, BridgingPartnerFilter):
            photo_filter = filterset.base_filters['has_photo']
            self.assertEqual(
                [choice[0] for choice in photo_filter.extra['choices']], ['yes', 'no'], filterset,
            )
            qs = mock_queryset()
            filterset.filter_has_photo(None, qs, 'has_photo', 'yes')
            self.assertEqual(qs.exclude.call_count, 2, filterset)


class ExcelScopePhotoFilterTests(SimpleTestCase):
    def test_excel_scope_applies_the_photo_filter_after_the_role_scope(self):
        user = SimpleNamespace(
            is_authenticated=True, is_active=True, is_staff=True, is_superuser=False,
            partner=None, partner_id=None, center_id=None,
        )
        qs = mock_queryset()
        qs.select_related.return_value = qs
        qs.order_by.return_value = qs
        with patch.object(export_access.Registration, 'objects') as manager, \
                patch.object(export_access, 'has_group', return_value=False):
            manager.filter.return_value.exclude.return_value = qs
            export_access.excel_export_registrations(user, round='4', has_photo='yes')
            with self.assertRaises(ValidationError):
                export_access.excel_export_registrations(user, round='4', has_photo='maybe')
        self.assertEqual(qs.filter.call_args_list[0].kwargs, {'round_id': 4})
        self.assertEqual(
            [call.kwargs for call in qs.exclude.call_args_list],
            [{'profile_picture': ''}, {'profile_picture__isnull': True}],
        )


class ExportViewPhotoFilterTests(SimpleTestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = SimpleNamespace(is_authenticated=True, is_active=True, partner=None)

    def start(self, params):
        request = self.factory.get('/mscc/export-list-background/', params)
        request.user = self.user
        with patch.object(views, 'user_can_export', return_value=True), \
                patch.object(views, 'excel_export_registrations') as scope, \
                patch.object(views.ExportHistory.objects, 'create') as create, \
                patch.object(views, 'queue_filtered_mscc_export') as queue:
            create.return_value = SimpleNamespace(id=55)
            response = views.export_list_background(request)
        return response, scope, queue

    def test_photo_filter_is_validated_and_passed_to_the_export_job(self):
        response, scope, queue = self.start({'round': '4', 'format': 'xlsx', 'has_photo': 'yes'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(scope.call_args.kwargs['has_photo'], 'yes')
        self.assertEqual(queue.call_args.kwargs['has_photo'], 'yes')
        self.assertEqual(queue.call_args.args[1:], ('', '', '', '', '', '4'))

        response, scope, queue = self.start({'round': '4', 'format': 'csv'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(queue.call_args.kwargs['has_photo'], '')

        response, scope, queue = self.start({'round': '4', 'format': 'xlsx', 'has_photo': 'maybe'})
        self.assertEqual(response.status_code, 400)
        queue.assert_not_called()
