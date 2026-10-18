"""Source storage reads, explicit child links and authenticated HTTP contract."""

import hashlib
import io
import uuid
from types import SimpleNamespace
from unittest.mock import Mock, patch

from django.test import SimpleTestCase, override_settings
from django.utils import timezone

from .. import photos
from ..client import SyncClient, SyncConfigurationError, SyncTransportError


@override_settings(DATASYNC_ENABLED=True)
class PhotoSenderTests(SimpleTestCase):
    @override_settings(USE_TZ=False, TIME_ZONE='Asia/Beirut')
    def test_naive_project_timestamp_is_sent_with_timezone(self):
        from datetime import datetime
        from ..serializers import wire_timestamp
        self.assertEqual(wire_timestamp(datetime(2026, 10, 18, 12)),
                         '2026-10-18T12:00:00+03:00')
        descriptor, _ = self.deliver(self.student())
        from django.utils.dateparse import parse_datetime
        self.assertTrue(timezone.is_aware(parse_datetime(descriptor['source_modified'])))

    def event(self):
        return SimpleNamespace(payload={'student_id': 7}, source_id='900',
                               event_id=uuid.uuid4(), created=timezone.now())

    def student(self, data=b'image bytes'):
        image = Mock()
        image.open.return_value = io.BytesIO(data)
        return SimpleNamespace(std_image=image)

    def deliver(self, student, client=None):
        Student = Mock()
        Student.objects.filter.return_value.first.return_value = student
        with patch.object(photos.apps, 'get_model', return_value=Student), \
                patch.object(photos, 'linked_student_id', return_value=7):
            return photos.prepare_photo(self.event().source_id, self.event())

    def test_source_file_is_prepared_without_azure_url_or_credential(self):
        descriptor, stream = self.deliver(self.student(b'picture'))
        self.assertEqual(stream.read(), b'picture')
        self.assertEqual(descriptor['sha256'], hashlib.sha256(b'picture').hexdigest())
        self.assertNotIn('url', descriptor)

    def test_cleared_source_photo_prepares_explicit_remove(self):
        descriptor, stream = self.deliver(SimpleNamespace(std_image=''))
        self.assertEqual(descriptor['action'], 'remove')
        self.assertIsNone(stream)

    def test_storage_outage_is_retryable_and_does_not_leak_storage_error(self):
        student = self.student()
        student.std_image.open.side_effect = OSError('sensitive-storage-url')
        with self.assertRaisesRegex(SyncTransportError, '^Cannot read source photo storage$'):
            self.deliver(student)

    def test_oversized_photo_is_not_uploaded(self):
        with self.settings(DATASYNC_PHOTO_MAX_BYTES=1), self.assertRaises(photos.PhotoSourceError):
            self.deliver(self.student(b'large'))

    def test_missing_student_is_not_guessed(self):
        with self.assertRaises(photos.PhotoSourceError):
            self.deliver(None)

    def test_missing_and_ambiguous_links(self):
        Registration = Mock()
        query = Registration.objects.filter.return_value.exclude.return_value.exclude.return_value
        for ids, expected in (([], None), ([7], 7)):
            query.values_list.return_value.distinct.return_value = ids
            with patch.object(photos.apps, 'get_model', return_value=Registration):
                self.assertEqual(photos.linked_student_id(900), expected)
        query.values_list.return_value.distinct.return_value = [7, 8]
        with patch.object(photos.apps, 'get_model', return_value=Registration), \
                self.assertRaises(photos.PhotoSourceError):
            photos.linked_student_id(900)

    def test_missing_link_reports_unavailable_without_guessing(self):
        with patch.object(photos, 'linked_student_id', return_value=None):
            descriptor, stream = photos.prepare_photo(900, self.event())
        self.assertEqual(descriptor['action'], 'unavailable')
        self.assertIsNone(stream)

    def test_disabled_sync_prepares_no_photo(self):
        with self.settings(DATASYNC_ENABLED=False):
            self.assertEqual(photos.prepare_photo(900, self.event()), (None, None))

    def test_client_sends_metadata_and_photo_to_same_events_endpoint(self):
        client = SyncClient(url='https://nfe.example/api/sync/events/', token='test-token')
        response = Mock(status_code=200)
        response.json.return_value = {'results': []}
        with patch.object(__import__(SyncClient.__module__, fromlist=['requests']).requests,
                          'post', return_value=response) as post:
            client.push([{'event_id': 'test'}], attachments={'photo_test': io.BytesIO(b'image')})
        self.assertEqual(post.call_args.args[0], 'https://nfe.example/api/sync/events/')
        self.assertIn('envelope', post.call_args.kwargs['data'])
        self.assertIn('photo_test', post.call_args.kwargs['files'])
        self.assertFalse(post.call_args.kwargs['allow_redirects'])
        self.assertNotIn('Content-Type', post.call_args.kwargs['headers'])
        self.assertEqual(post.call_args.kwargs['headers']['Authorization'], 'Token test-token')

    def test_photo_queue_callback_never_uploads_inline(self):
        from .. import outbox
        callbacks = []
        event = SimpleNamespace(pk=42, resource='child.photo')
        with patch.object(outbox.transaction, 'on_commit', side_effect=callbacks.append):
            outbox._schedule(event)
        with patch.object(outbox, '_deliver_now') as deliver:
            callbacks[0]()
        deliver.assert_called_once_with(42, allow_inline=False)

    def test_initialization_rejects_a_receiver_without_combined_photo_support(self):
        client = SyncClient(url='https://nfe.example/api/sync/events/', token='test-token')
        with patch.object(client, 'ping', return_value={'enabled': True}), \
                self.assertRaisesRegex(SyncConfigurationError, 'unified record/photo'):
            client.check_ready()

    def test_initialization_accepts_the_unified_receiver(self):
        client = SyncClient(url='https://nfe.example/api/sync/events/', token='test-token')
        capabilities = {'enabled': True, 'child_photo_sync': {'atomic_with_registration': True}}
        with patch.object(client, 'ping', return_value=capabilities):
            self.assertEqual(client.check_ready(), capabilities)

    @override_settings(DATASYNC_ENABLED=False)
    def test_disabled_sync_keeps_non_photo_callback_compatibility(self):
        from .. import outbox
        callbacks = []
        event = SimpleNamespace(pk=43, resource='mscc.registration')
        with patch.object(outbox.transaction, 'on_commit', side_effect=callbacks.append):
            outbox._schedule(event)
        with patch.object(outbox, '_deliver_now') as deliver:
            callbacks[0]()
        deliver.assert_called_once_with(43)
