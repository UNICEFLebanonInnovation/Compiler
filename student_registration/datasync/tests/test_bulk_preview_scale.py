"""Production-size attendance and cancellation while validation is in progress."""
from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta
import threading
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.db import connection, connections
from django.test import TestCase, TransactionTestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from student_registration.attendances.models import MSCCAttendance, MSCCAttendanceChild
from student_registration.child.models import Child
from student_registration.locations.models import Center
from student_registration.mscc.models import Registration, Round
from student_registration.schools.models import PartnerOrganization
from ..bulk_sync import RoundSyncPlan, prepare_run
from ..constants import RESOURCE_ATTENDANCE, RESOURCE_ROUND
from ..models import BulkSyncRun, SyncEvent
from ..pending_cleanup import remove_pending
from . import test_bulk_sync as fixture


@override_settings(DATASYNC_ENABLED=False)
class BulkAttendanceScaleTests(TransactionTestCase):
    def test_large_unrelated_attendance_preview_has_bounded_database_work(self):
        if connection.vendor != 'postgresql':
            self.skipTest('PostgreSQL planner and statement budget regression')
        partner = PartnerOrganization.objects.create(name='Scale selected partner')
        foreign = PartnerOrganization.objects.create(name='Scale foreign partner')
        center = Center.objects.create(name='Selected centre', partner=partner)
        other = Center.objects.create(name='Foreign centre', partner=foreign)
        round_object = Round.objects.create(name='Scale selected round')
        other_round = Round.objects.create(name='Scale foreign round')
        child = Child.objects.create(first_name='Synthetic scale child')
        registration = Registration.objects.create(child=child, center=center, round=round_object,
                                                    partner=partner, type='Core-Package')
        tls = Registration.objects.create(child=child, center=other, round=other_round,
                                            partner=foreign, type='TLS')
        day = MSCCAttendance.objects.create(center=center, round_id=round_object.pk)
        MSCCAttendanceChild.objects.bulk_create([MSCCAttendanceChild(
            attendance_day=day, registration=registration, child=child) for _ in range(100)])
        selected_days = MSCCAttendance.objects.bulk_create([MSCCAttendance(center=center, round_id=round_object.pk)
                                                           for _ in range(2000)])
        MSCCAttendanceChild.objects.bulk_create([MSCCAttendanceChild(attendance_day=d,
            registration=registration, child=child) for d in selected_days], batch_size=1000)
        days = MSCCAttendance.objects.bulk_create([MSCCAttendance(center=other, round_id=other_round.pk)
                                                   for _ in range(1200)])
        MSCCAttendanceChild.objects.bulk_create([MSCCAttendanceChild(attendance_day=d, registration=tls,
            child=child) for d in days for _ in range(50)], batch_size=1000)
        with connection.cursor() as cursor:
            for table in ('attendances_msccattendance', 'attendances_msccattendancechild', 'mscc_registration'):
                cursor.execute('ANALYZE ' + table)
            cursor.execute("SET work_mem = '64kB'")
            cursor.execute("SET statement_timeout = '1500ms'")
        try:
            plan = RoundSyncPlan(round_object, 'all', partner)
            self.assertEqual(plan.errors(), [])
            self.assertEqual(set(plan.queries[RESOURCE_ATTENDANCE].values_list('pk', flat=True)),
                             {day.pk, *(d.pk for d in selected_days)})
            self.assertEqual(len(plan.summary()), 9)
            self.assertLessEqual(len(plan.preview(0, 50)), 50)
        finally:
            with connection.cursor() as cursor:
                cursor.execute('RESET statement_timeout')
                cursor.execute('RESET work_mem')


@override_settings(DATASYNC_ENABLED=True)
class PreparationCancellationTests(TransactionTestCase):
    def setUp(self):
        with override_settings(DATASYNC_ENABLED=False):
            self.partner = PartnerOrganization.objects.create(name='Validation cancellation partner')
            self.round = Round.objects.create(name='Validation cancellation round')
        self.user = get_user_model().objects.create_superuser(username='validation-cancel',
                            password='test-password', email='qa@example.test')
        self.run = BulkSyncRun.objects.create(partner=self.partner, round=self.round,
                                               category=RESOURCE_ROUND, requested_by=self.user)
        BulkSyncRun.objects.filter(pk=self.run.pk).update(created=timezone.now() - timedelta(days=1))

    def test_yesterdays_waiting_request_can_be_removed_during_slow_validation(self):
        entered, release = threading.Event(), threading.Event()
        real_errors = RoundSyncPlan.errors

        def slow_validation(plan):
            entered.set()
            if not release.wait(15):
                raise RuntimeError('Validation test did not release')
            return real_errors(plan)

        def worker():
            try:
                prepare_run(self.run.pk)
            finally:
                connections.close_all()

        with patch.object(RoundSyncPlan, 'errors', slow_validation):
            with ThreadPoolExecutor(max_workers=1) as pool:
                task = pool.submit(worker)
                try:
                    self.assertTrue(entered.wait(10))
                    self.assertEqual(remove_pending(self.user, self.partner, [self.run.pk]), (1, 0))
                finally:
                    release.set()
                task.result(timeout=20)
        self.assertFalse(BulkSyncRun.objects.filter(pk=self.run.pk).exists())
        self.assertFalse(SyncEvent.objects.exists())
        self.assertTrue(Round.objects.filter(pk=self.round.pk).exists())

    def test_two_workers_validating_together_queue_exactly_once(self):
        barrier = threading.Barrier(2)
        real_errors = RoundSyncPlan.errors

        def concurrent_validation(plan):
            barrier.wait(timeout=15)
            return real_errors(plan)

        def worker():
            try:
                prepare_run(self.run.pk)
            finally:
                connections.close_all()

        with patch.object(RoundSyncPlan, 'errors', concurrent_validation):
            with ThreadPoolExecutor(max_workers=2) as pool:
                tasks = [pool.submit(worker) for _ in range(2)]
                for task in tasks:
                    task.result(timeout=25)
        self.run.refresh_from_db()
        self.assertEqual(self.run.preparation, 'ready')
        self.assertEqual(self.run.events.count(), 1)


@override_settings(DATASYNC_ENABLED=True, DATASYNC_TARGET_URL='https://nfe.test/api/sync/events/',
                   DATASYNC_TARGET_TOKEN='isolated-preview-test')
class PreviewBudgetTests(TestCase):
    setUp = fixture.BulkRoundTests.setUp
    post_data = fixture.BulkRoundTests.post_data

    def timeout(self):
        from ..query_budget import preview_budget
        return preview_budget(.05)

    def slow_errors(self):
        with connection.cursor() as cursor:
            cursor.execute('SELECT pg_sleep(0.2)')
        return []

    def test_slow_preview_returns_a_useful_page_instead_of_a_500(self):
        with patch('student_registration.datasync.bulk_admin.preview_budget', self.timeout), \
                patch.object(RoundSyncPlan, 'errors', side_effect=self.slow_errors):
            response = self.client.get(self.url, self.post_data())
        self.assertContains(response, 'Preview took too long')
        self.assertNotContains(response, 'Sync this selection')
        self.assertEqual(BulkSyncRun.objects.count(), 0)
        self.assertEqual(SyncEvent.objects.count(), 0)
        with connection.cursor() as cursor:
            cursor.execute('SELECT 1')
            self.assertEqual(cursor.fetchone()[0], 1)

    def test_timed_out_post_never_creates_a_request_or_events(self):
        with patch('student_registration.datasync.bulk_admin.preview_budget', self.timeout), \
                patch.object(RoundSyncPlan, 'errors', side_effect=self.slow_errors):
            response = self.client.post(self.url, self.post_data())
        self.assertContains(response, 'No new sync request was created')
        self.assertFalse(BulkSyncRun.objects.exists())
        self.assertFalse(SyncEvent.objects.exists())

    def test_timeout_setting_is_restored_on_success_and_after_cancellation(self):
        from ..query_budget import preview_budget, PreviewTimeout
        with connection.cursor() as cursor:
            cursor.execute('SHOW statement_timeout')
            before = cursor.fetchone()[0]
        with preview_budget(.2):
            with connection.cursor() as cursor:
                cursor.execute('SELECT 1')
        with self.assertRaises(PreviewTimeout):
            with preview_budget(.05):
                self.slow_errors()
        with connection.cursor() as cursor:
            cursor.execute('SHOW statement_timeout')
            self.assertEqual(cursor.fetchone()[0], before)

    def test_budget_covers_multiple_queries_not_just_each_query(self):
        from ..query_budget import preview_budget, PreviewTimeout
        with self.assertRaises(PreviewTimeout):
            with preview_budget(.15):
                with connection.cursor() as cursor:
                    cursor.execute('SELECT pg_sleep(0.1)')
                    cursor.execute('SELECT pg_sleep(0.1)')

    def test_null_registration_does_not_leak_a_day_or_poison_other_days(self):
        from ..makani_scope import scoped_queryset
        with override_settings(DATASYNC_ENABLED=False):
            invalid = MSCCAttendance.objects.create(center=self.center, round_id=self.round.pk)
            MSCCAttendanceChild.objects.create(attendance_day=invalid, child=self.child)
        days = scoped_queryset(RESOURCE_ATTENDANCE)
        self.assertFalse(days.filter(pk=invalid.pk).exists())
        self.assertTrue(days.filter(pk=self.day.pk).exists())

    def test_null_package_type_remains_makani_for_days_and_related_records(self):
        from ..makani_scope import scoped_queryset
        Registration.objects.filter(pk=self.registration.pk).update(type=None)
        self.assertTrue(scoped_queryset(RESOURCE_ATTENDANCE).filter(pk=self.day.pk).exists())
        self.assertTrue(scoped_queryset('mscc.education_assessment').filter(pk=self.assessment.pk).exists())

    def test_multiple_preview_pages_reuse_counts_and_preserve_scope(self):
        plan = RoundSyncPlan(self.round, 'all', self.partner)
        summary = plan.summary()
        total = sum(row['count'] for row in summary)
        rows = [row for offset in range(0, total, 2) for row in plan.preview(offset, 2)]
        self.assertEqual(len(rows), total)
        self.assertEqual(len({(row['label'], row['source_id']) for row in rows}), total)
