"""Diagnose staging from the portal without exporting records or revealing secrets."""
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.test import Client, SimpleTestCase, TestCase, override_settings

from . import test_bulk_sync as fixture
from .. import health
from ..bulk_sync import prepare_run, schedule_bulk_sweep
from ..client import SyncTransportError
from ..models import BulkSyncRun, SyncEvent


@override_settings(DATASYNC_ENABLED=True, DATASYNC_TARGET_URL='https://nfe.test/api/sync/events/',
                   DATASYNC_TARGET_TOKEN='private-service-token')
class HealthChecksTests(SimpleTestCase):
    def setUp(self):
        self.app_patch = patch.object(health, 'current_app')
        self.app = self.app_patch.start()
        self.addCleanup(self.app_patch.stop)
        self.connection = self.app.connection_for_write.return_value.__enter__.return_value
        self.connection.transport.driver_type = 'redis'
        self.inspector = self.app.control.inspect.return_value
        self.inspector.active_queues.return_value = {'sync@one': [{'name': 'datasync'}]}
        self.inspector.registered.return_value = {
            'sync@one': ['datasync.flush_sync_outbox', 'datasync.worker_health']}
        self.client_patch = patch.object(health, 'SyncClient')
        self.client = self.client_patch.start()
        self.addCleanup(self.client_patch.stop)
        self.client.return_value.ping.return_value = {'enabled': True}

    def component(self, name):
        return next(row for row in health.check_sync_health()['checks'] if row['component'] == name)

    def test_healthy_worker_is_confirmed_on_correct_queue_with_current_tasks(self):
        result = health.check_sync_health()
        self.assertTrue(all(row['status'] == 'ok' for row in result['checks'][:-1]))
        self.connection.ensure_connection.assert_called_once_with(max_retries=0, timeout=3)
        self.app.control.inspect.assert_called_once_with(timeout=2, connection=self.connection)
        self.app.send_task.assert_not_called()
        self.client.assert_called_once()
        self.assertEqual(self.client.call_args.kwargs['timeout'], 4)

    def test_unreachable_broker_still_checks_receiver_independently(self):
        self.connection.ensure_connection.side_effect = ConnectionError('broker unavailable')
        result = health.check_sync_health()
        states = {row['component']: row['status'] for row in result['checks']}
        self.assertEqual(states['Message broker'], 'error')
        self.assertEqual(states['BMA-NFE receiver'], 'ok')
        self.app.control.inspect.assert_not_called()

    def test_export_worker_does_not_count_as_a_sync_worker(self):
        self.inspector.active_queues.return_value = {'export@one': [{'name': 'mscc_export'}]}
        result = self.component('Sync worker')
        self.assertEqual(result['status'], 'warning')
        self.assertIn('No responding worker consumes the datasync queue', result['detail'])

    def test_no_reply_is_reported_without_claiming_that_worker_is_definitely_down(self):
        self.inspector.active_queues.return_value = None
        self.assertIn('busy workers or disabled remote control', self.component('Sync worker')['detail'])

    def test_older_or_unconfirmed_worker_tasks_are_visible(self):
        self.inspector.registered.return_value = {'sync@one': ['datasync.flush_sync_outbox']}
        self.assertIn('Restart or update', self.component('Sync worker')['detail'])

    def test_non_inspectable_transport_does_not_get_a_false_failure(self):
        self.connection.transport.driver_type = 'filesystem'
        self.assertEqual(self.component('Sync worker')['status'], 'warning')
        self.app.control.inspect.assert_not_called()

    def test_inspect_failure_is_contained(self):
        self.inspector.active_queues.side_effect = RuntimeError('remote control unavailable')
        self.assertEqual(self.component('Sync worker')['status'], 'warning')

    def test_receiver_503_is_readable_without_dumping_its_html(self):
        self.client.return_value.ping.side_effect = SyncTransportError(
            'BMA-NFE replied 503: <!DOCTYPE html><style>secret-page-content</style>')
        result = self.component('BMA-NFE receiver')
        self.assertEqual(result['status'], 'error')
        self.assertIn('HTTP 503', result['detail'])
        self.assertNotIn('secret-page-content', result['detail'])

    def test_receiver_disabled_ingest_is_not_reported_healthy(self):
        self.client.return_value.ping.return_value = {'enabled': False}
        self.assertEqual(self.component('BMA-NFE receiver')['status'], 'error')

    @override_settings(DATASYNC_ENABLED=False)
    def test_disabled_web_sync_is_visible(self):
        self.assertEqual(self.component('Compiler sync')['status'], 'error')

    @override_settings(CELERY_BROKER_URL='rediss://broker-user:broker-secret@broker.test:6380/0')
    def test_errors_redact_credentials_urls_and_service_tokens(self):
        text = health.safe_error(RuntimeError(
            'rediss://broker-user:broker-secret@broker.test:6380/0 '
            'https://someone:other-secret@example.test/?token=other-token '
            'private-service-token password=another-secret Bearer other-bearer'))
        for secret in ('broker-user', 'broker-secret', 'other-secret', 'private-service-token',
                       'another-secret', 'other-bearer', 'other-token'):
            self.assertNotIn(secret, text)

    @override_settings(DATASYNC_TARGET_URL='https://user:password@nfe.test/api/sync/events/?token=private')
    def test_displayed_destination_excludes_credentials_and_query(self):
        self.assertEqual(health.safe_target(), 'https://nfe.test/api/sync/events/')

    def test_worker_probe_reports_loaded_capability_and_current_switch(self):
        from ..tasks import worker_health
        self.assertEqual(worker_health(), {'bulk_sync_diagnostics': 1, 'sync_enabled': True})


@override_settings(DATASYNC_ENABLED=True, DATASYNC_TARGET_URL='https://nfe.test/api/sync/events/',
                   DATASYNC_TARGET_TOKEN='private-service-token')
class DiagnosticsPortalTests(TestCase):
    setUp = fixture.BulkRoundTests.setUp
    new_run = fixture.BulkRoundTests.new_run
    post_data = fixture.BulkRoundTests.post_data

    def test_diagnostics_are_post_only_and_require_csrf(self):
        run = self.new_run()
        url = '{}?run={}'.format(self.url, run.pk)
        self.assertEqual(self.client.get(url + '&sync_action=diagnose').status_code, 405)
        client = Client(enforce_csrf_checks=True)
        client.force_login(self.user)
        with patch('student_registration.datasync.bulk_admin.check_sync_health') as check:
            self.assertEqual(client.post(url, {'sync_action': 'diagnose'}).status_code, 403)
            check.assert_not_called()

    def test_diagnostics_do_not_prepare_or_deliver_records(self):
        run = self.new_run()
        before = (BulkSyncRun.objects.count(), SyncEvent.objects.count())
        with patch('student_registration.datasync.bulk_admin.check_sync_health', return_value={
                'target': 'https://nfe.test/api/sync/events/',
                'checks': [{'component': 'Message broker', 'status': 'error', 'detail': 'Connection refused'}],
        }), patch('student_registration.datasync.tasks.flush_sync_outbox.apply_async') as send:
            response = self.client.post('{}?run={}'.format(self.url, run.pk), {'sync_action': 'diagnose'})
        self.assertContains(response, 'Connection refused')
        self.assertContains(response, 'Retry sync')
        self.assertEqual((BulkSyncRun.objects.count(), SyncEvent.objects.count()), before)
        send.assert_not_called()

    def test_queue_error_is_saved_without_discarding_waiting_request(self):
        run = self.new_run()
        with patch('student_registration.datasync.tasks.flush_sync_outbox.apply_async',
                   side_effect=ConnectionError('failed private-service-token')):
            self.assertFalse(schedule_bulk_sweep(run.pk))
        run.refresh_from_db()
        self.assertEqual(run.preparation, 'waiting')
        self.assertIn('Could not notify the sync queue', run.last_error)
        self.assertNotIn('private-service-token', run.last_error)
        self.assertFalse(run.events.exists())

    def test_retry_notifies_existing_request_and_keeps_one_set_of_events(self):
        run = self.new_run()
        run.last_error = 'Previous notification failed'
        run.save(update_fields=['last_error'])
        with patch('student_registration.datasync.tasks.flush_sync_outbox.apply_async') as send:
            response = self.client.post('{}?run={}'.format(self.url, run.pk), {'sync_action': 'notify_queue'})
        self.assertRedirects(response, '{}?run={}'.format(self.url, run.pk))
        send.assert_called_once_with(retry=False, timeout=3)
        self.assertEqual(BulkSyncRun.objects.count(), 1)
        run.refresh_from_db()
        self.assertEqual(run.last_error, '')
        prepare_run(run.pk)
        first = list(run.events.values_list('pk', flat=True))
        prepare_run(run.pk)
        self.assertEqual(list(run.events.values_list('pk', flat=True)), first)

    def test_retry_failure_remains_visible_on_same_request(self):
        run = self.new_run()
        with patch('student_registration.datasync.tasks.flush_sync_outbox.apply_async',
                   side_effect=ConnectionError('broker unavailable')):
            self.client.post('{}?run={}'.format(self.url, run.pk), {'sync_action': 'notify_queue'})
        response = self.client.get(self.url, {'run': run.pk})
        self.assertContains(response, 'broker unavailable')
        self.assertEqual(BulkSyncRun.objects.count(), 1)

    def test_initial_notification_passes_run_identity_for_durable_errors(self):
        with patch('student_registration.datasync.bulk_admin.schedule_bulk_sweep') as schedule, \
                self.captureOnCommitCallbacks(execute=True):
            self.client.post(self.url, self.post_data())
        schedule.assert_called_once_with(BulkSyncRun.objects.get().pk)

    def test_another_operators_request_cannot_be_diagnosed_or_notified(self):
        run = self.new_run()
        user = get_user_model().objects.create_user(username='other-diagnostic-user', is_staff=True)
        user.user_permissions.add(*Permission.objects.filter(codename__in=[
            'view_bulksyncrun', 'add_bulksyncrun', 'view_round', 'view_partnerorganization']))
        self.client.force_login(user)
        for action in ('diagnose', 'notify_queue'):
            with self.subTest(action=action), patch('student_registration.datasync.bulk_admin.check_sync_health') as check, \
                    patch('student_registration.datasync.bulk_admin.schedule_bulk_sweep') as notify:
                self.assertEqual(self.client.post('{}?run={}'.format(self.url, run.pk),
                                                 {'sync_action': action}).status_code, 404)
                check.assert_not_called()
                notify.assert_not_called()

    def test_view_only_operator_cannot_invoke_actions(self):
        user = get_user_model().objects.create_user(username='diagnostic-viewer', is_staff=True)
        user.user_permissions.add(*Permission.objects.filter(codename__in=[
            'view_bulksyncrun', 'view_round', 'view_partnerorganization']))
        run = BulkSyncRun.objects.create(partner=self.partner, round=self.round, requested_by=user,
                                         category='mscc.round')
        self.client.force_login(user)
        for action in ('diagnose', 'notify_queue'):
            self.assertEqual(self.client.post('{}?run={}'.format(self.url, run.pk),
                                             {'sync_action': action}).status_code, 403)

    def test_ready_request_cannot_be_prepared_again_from_retry_action(self):
        run = self.new_run()
        prepare_run(run.pk)
        event_ids = list(run.events.values_list('pk', flat=True))
        with patch('student_registration.datasync.bulk_admin.schedule_bulk_sweep') as notify:
            self.client.post('{}?run={}'.format(self.url, run.pk), {'sync_action': 'notify_queue'})
        notify.assert_called_once_with(run.pk)
        prepare_run(run.pk)
        self.assertEqual(list(run.events.values_list('pk', flat=True)), event_ids)

    def test_disabled_sync_does_not_publish_a_retry_notification(self):
        run = self.new_run()
        with override_settings(DATASYNC_ENABLED=False), \
                patch('student_registration.datasync.bulk_admin.schedule_bulk_sweep') as notify:
            self.client.post('{}?run={}'.format(self.url, run.pk), {'sync_action': 'notify_queue'})
        notify.assert_not_called()
