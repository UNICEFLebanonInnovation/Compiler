"""Direct submission and one unfinished bulk job, including worker races."""
from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta
import threading
import uuid
from unittest.mock import patch

from django.db import connection, connections
from django.test import TestCase, TransactionTestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from . import test_bulk_sync as fixture
from ..bulk_jobs import BulkBusy, current_run, retire_stopped_events, retry_run, stop_run, submit_run
from ..bulk_sync import prepare_run, prepare_waiting_runs
from ..constants import RESOURCE_CENTER, RESOURCE_ROUND, RESOURCE_TEACHER
from ..delivery import guard_events
from ..dispatch import due_events
from ..models import BulkSyncRun, SyncEvent


@override_settings(DATASYNC_ENABLED=True, DATASYNC_TARGET_URL='https://nfe.test/api/sync/events/',
                   DATASYNC_TARGET_TOKEN='isolated-single-job-test')
class SingleBulkTests(TestCase):
    setUp = fixture.BulkRoundTests.setUp
    post_data = fixture.BulkRoundTests.post_data
    new_run = fixture.BulkRoundTests.new_run

    def test_page_has_one_start_form_and_no_preview_or_queue_controls(self):
        response = self.client.get(self.url)
        self.assertContains(response, 'Start sync')
        self.assertContains(response, 'id="bulk-sync-selection"', count=1)
        for text in ('Preview records', 'Sync this selection', 'Record preview', 'Remove pending bulk syncs',
                     'Retry queue notification', 'Recent bulk requests'):
            self.assertNotContains(response, text)

    def test_get_and_post_never_plan_or_count_source_records(self):
        with patch('student_registration.datasync.bulk_sync.RoundSyncPlan', side_effect=AssertionError('Web planning forbidden')):
            self.assertEqual(self.client.get(self.url, self.post_data()).status_code, 200)
            response = self.client.post(self.url, self.post_data())
            self.assertEqual(response.status_code, 302)
        self.assertEqual(BulkSyncRun.objects.count(), 1)
        self.assertFalse(SyncEvent.objects.exists())

    def test_two_different_request_ids_cannot_create_two_jobs(self):
        self.assertEqual(self.client.post(self.url, self.post_data()).status_code, 302)
        response = self.client.post(self.url, self.post_data())
        self.assertContains(response, 'A sync is already in progress')
        self.assertEqual(BulkSyncRun.objects.count(), 1)

    def test_double_click_reuses_same_job(self):
        data = self.post_data()
        self.assertEqual(self.client.post(self.url, data).status_code, 302)
        self.assertEqual(self.client.post(self.url, data).status_code, 302)
        self.assertEqual(BulkSyncRun.objects.count(), 1)

    def test_completed_job_allows_next_selection(self):
        run = self.new_run(RESOURCE_ROUND)
        prepare_run(run.pk)
        run.events.update(status='sent')
        self.assertEqual(self.client.post(self.url, self.post_data()).status_code, 302)
        self.assertEqual(BulkSyncRun.objects.count(), 2)

    def test_retryable_failure_blocks_next_job_even_before_its_retry_time(self):
        run = self.new_run(RESOURCE_ROUND)
        prepare_run(run.pk)
        run.events.update(status='failed', next_attempt=timezone.now() + timedelta(hours=1))
        self.assertContains(self.client.post(self.url, self.post_data()), 'already in progress')
        self.assertEqual(BulkSyncRun.objects.count(), 1)

    def test_preparation_failure_can_retry_same_request(self):
        run = self.new_run(RESOURCE_ROUND)
        run.preparation = 'failed'; run.save()
        retry_run(run.pk)
        prepare_run(run.pk)
        self.assertEqual(run.events.count(), 1)
        self.assertEqual(BulkSyncRun.objects.count(), 1)

    def test_stopping_before_preparation_keeps_history_and_creates_no_events(self):
        run = self.new_run(RESOURCE_ROUND)
        stop_run(run.pk)
        prepare_run(run.pk)
        run.refresh_from_db()
        self.assertEqual(run.preparation, 'cancelled')
        self.assertFalse(run.events.exists())
        self.assertIsNone(current_run())

    def test_stopping_delivery_preserves_sent_records_and_releases_next_job(self):
        run = self.new_run()
        prepare_run(run.pk)
        first = run.events.first(); first.status = 'sent'; first.save()
        stop_run(run.pk)
        first.refresh_from_db(); self.assertEqual(first.status, 'sent')
        self.assertFalse(run.events.filter(status__in=('pending', 'failed')).exists())
        self.assertEqual(run.events.filter(status='abandoned').count(), 3)
        self.assertIsNone(current_run())
        self.assertEqual(self.client.post(self.url, self.post_data()).status_code, 302)

    def test_older_backlog_is_prepared_one_job_at_a_time(self):
        first = self.new_run(RESOURCE_ROUND); second = self.new_run(RESOURCE_ROUND)
        prepare_waiting_runs(limit=10)
        self.assertEqual(first.events.count(), 1)
        self.assertFalse(second.events.exists())
        prepare_run(second.pk)
        self.assertFalse(second.events.exists())
        first.events.update(status='sent')
        prepare_waiting_runs()
        self.assertEqual(second.events.count(), 1)

    def test_delivery_limits_bulk_jobs_and_allows_ordinary_saves(self):
        first = self.new_run(RESOURCE_ROUND); second = self.new_run(RESOURCE_ROUND)
        prepare_run(first.pk)
        second.preparation = 'ready'; second.save()
        later = SyncEvent.objects.create(bulk_run=second, resource=RESOURCE_ROUND, source_id='222')
        automatic = SyncEvent.objects.create(resource=RESOURCE_ROUND, source_id='333')
        ids = {event.pk for event in due_events()}
        self.assertIn(automatic.pk, ids)
        self.assertNotIn(later.pk, ids)
        first.events.update(status='sent')
        self.assertIn(later.pk, {event.pk for event in due_events()})

    def test_source_master_categories_need_no_round(self):
        data = self.post_data(); data['category'] = [RESOURCE_CENTER, RESOURCE_TEACHER]; data.pop('round')
        self.assertEqual(self.client.post(self.url, data).status_code, 302)
        run = BulkSyncRun.objects.get(); self.assertIsNone(run.round_id)
        prepare_run(run.pk)
        self.assertEqual(run.events.count(), 4)

    def test_stop_is_post_only_and_stopped_job_cannot_be_retried(self):
        run = self.new_run(RESOURCE_ROUND)
        self.assertEqual(self.client.get(self.url, {'run': run.pk, 'sync_action': 'stop'}).status_code, 405)
        stop_run(run.pk)
        with self.assertRaises(BulkBusy):
            retry_run(run.pk)

    def test_other_operator_cannot_stop_or_retry_a_job(self):
        from django.contrib.auth import get_user_model
        from django.contrib.auth.models import Permission
        run = self.new_run(RESOURCE_ROUND)
        other = get_user_model().objects.create_user(username='other-single-operator', is_staff=True,
                                                     partner=self.partner)
        other.user_permissions.add(*Permission.objects.filter(codename__in=(
            'view_bulksyncrun', 'add_bulksyncrun', 'view_partnerorganization', 'view_round')))
        self.client.force_login(other)
        for action in ('stop', 'retry'):
            self.assertEqual(self.client.post(self.url + '?run=' + str(run.pk),
                {'sync_action': action}).status_code, 404)
        run.refresh_from_db(); self.assertEqual(run.preparation, 'waiting')

    def test_no_records_is_reported_by_worker_and_does_not_block_next_job(self):
        from student_registration.schools.models import PartnerOrganization
        with override_settings(DATASYNC_ENABLED=False):
            empty = PartnerOrganization.objects.create(name='Empty single-job partner')
        run, _ = submit_run(self.user, empty, None, [RESOURCE_CENTER], uuid.uuid4())
        prepare_run(run.pk); run.refresh_from_db()
        self.assertEqual(run.preparation, 'failed')
        self.assertIn('No records', run.last_error)
        self.assertFalse(run.events.exists())
        self.assertIsNone(current_run())

    def test_retry_wakes_failed_events_without_duplicate_outbox_rows(self):
        run = self.new_run(RESOURCE_ROUND); prepare_run(run.pk)
        event = run.events.get(); event.status = 'failed'; event.next_attempt = timezone.now() + timedelta(hours=1)
        event.save()
        response = self.client.post(self.url + '?run=' + str(run.pk), {'sync_action': 'retry'})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(run.events.count(), 1)
        event.refresh_from_db(); self.assertIsNone(event.next_attempt)

    def test_stopped_choice_migration_has_no_schema_ddl(self):
        from importlib import import_module
        from django.apps import apps
        from django.db.migrations.state import ProjectState
        migration = import_module('student_registration.datasync.migrations.0010_bulk_sync_stopped').Migration(
            '0010_bulk_sync_stopped', 'datasync')
        before = ProjectState.from_apps(apps)
        field = before.models['datasync', 'bulksyncrun'].fields['preparation'].clone()
        field.choices = [('waiting', 'Waiting to queue'), ('ready', 'Queued'), ('failed', 'Queueing failed')]
        before.models['datasync', 'bulksyncrun'].fields['preparation'] = field
        with connection.schema_editor(collect_sql=True) as editor:
            after = migration.apply(before, editor)
        self.assertEqual(editor.collected_sql, [])
        choices = after.apps.get_model('datasync', 'BulkSyncRun')._meta.get_field('preparation').choices
        self.assertIn(('cancelled', 'Stopped'), choices)

    def test_stop_after_completion_preserves_completed_audit(self):
        run = self.new_run(RESOURCE_ROUND); prepare_run(run.pk)
        run.events.update(status='sent')
        self.assertFalse(stop_run(run.pk))
        response = self.client.post(self.url + '?run=' + str(run.pk), {'sync_action': 'stop'}, follow=True)
        self.assertContains(response, 'already finished')
        run.refresh_from_db(); self.assertEqual(run.preparation, 'ready')
        self.assertEqual(run.events.get().status, 'sent')


@override_settings(DATASYNC_ENABLED=True)
class SingleBulkRaces(TransactionTestCase):
    setUp = fixture.BulkRoundTests.setUp

    def test_concurrent_start_attempts_admit_exactly_one(self):
        barrier = threading.Barrier(2)

        def start():
            try:
                barrier.wait(timeout=10)
                try:
                    submit_run(self.user, self.partner, self.round, [RESOURCE_ROUND], uuid.uuid4())
                    return 'started'
                except BulkBusy:
                    return 'busy'
            finally:
                connections.close_all()
        with ThreadPoolExecutor(max_workers=2) as pool:
            results = list(pool.map(lambda _: start(), range(2)))
        self.assertEqual(sorted(results), ['busy', 'started'])
        self.assertEqual(BulkSyncRun.objects.count(), 1)

    def test_stop_waits_for_inflight_event_before_admitting_next_job(self):
        run = BulkSyncRun.objects.create(partner=self.partner, round=self.round, category=RESOURCE_ROUND,
                                        requested_by=self.user)
        prepare_run(run.pk)
        event = run.events.get()
        entered, release = threading.Event(), threading.Event()

        def in_flight():
            try:
                with guard_events([event]) as ready:
                    self.assertEqual(len(ready), 1)
                    entered.set()
                    if not release.wait(15):
                        raise RuntimeError('In-flight test did not release')
                    event.mark_sent()
            finally:
                connections.close_all()
        with ThreadPoolExecutor(max_workers=1) as pool:
            task = pool.submit(in_flight)
            try:
                self.assertTrue(entered.wait(10))
                stop_run(run.pk)
                self.assertEqual(current_run().pk, run.pk)
                with self.assertRaises(BulkBusy):
                    submit_run(self.user, self.partner, self.round, [RESOURCE_ROUND], uuid.uuid4())
            finally:
                release.set()
            task.result(timeout=20)
        retire_stopped_events()
        self.assertIsNone(current_run())
        event.refresh_from_db(); self.assertEqual(event.status, 'sent')
