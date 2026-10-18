"""Pooled HTTP transport and cross-connection PostgreSQL delivery exclusion."""
from contextlib import contextmanager
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import io
import threading
import time
from types import SimpleNamespace
import uuid
from unittest.mock import Mock, patch

from django.db import connections
from django.test import SimpleTestCase, TransactionTestCase, override_settings
from django.utils import timezone

from .. import client as transport, delivery, dispatch, photos


class ConnectionReuseTests(SimpleTestCase):
    def test_multiple_posts_reuse_the_same_tcp_connection(self):
        ports = []

        class Handler(BaseHTTPRequestHandler):
            protocol_version = 'HTTP/1.1'

            def do_POST(self):
                self.rfile.read(int(self.headers['Content-Length']))
                ports.append(self.client_address[1])
                body = b'{"results": []}'
                self.send_response(200)
                self.send_header('Content-Length', str(len(body)))
                self.end_headers()
                self.wfile.write(body)

            def log_message(self, *args):
                pass

        server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        client = transport.SyncClient(url='http://127.0.0.1:{}/events/'.format(server.server_port),
                                      token='isolated-test', session=transport._new_session())
        try:
            client.push([{'event_id': 'one'}])
            client.push([{'event_id': 'two'}])
            self.assertEqual(len(ports), 2)
            self.assertEqual(ports[0], ports[1])
        finally:
            client.close()
            server.shutdown()
            server.server_close()
            thread.join()

    def test_capabilities_are_cached_and_worker_sessions_are_separate(self):
        client = transport.SyncClient(url='https://nfe.invalid/events/', token='isolated-test', session=Mock())
        with patch.object(client, 'ping', return_value={'child_photo_sync': {'verified_reuse': True}}) as ping:
            client.session._datasync_capabilities = {}
            self.assertTrue(client.photo_reuse_supported())
            self.assertTrue(client.photo_reuse_supported())
            ping.assert_called_once()
        worker = client.worker_copy()
        self.assertIsNot(worker.session, client.session)
        worker.close()


class FingerprintTests(SimpleTestCase):
    def test_cached_version_avoids_source_image_read_and_force_read_refreshes_hash(self):
        from ..models import SourcePhotoFingerprint
        Student = Mock()
        field = SimpleNamespace(name='profiles/one.png', storage=Mock(), open=Mock(
            side_effect=lambda mode: io.BytesIO(b'source photo')))
        field.storage.get_modified_time.return_value = timezone.now()
        student = SimpleNamespace(pk=7, std_image=field, modified=timezone.now())
        Student.objects.filter.return_value.first.return_value = student
        event = SimpleNamespace(event_id=uuid.uuid4(), created=timezone.now())
        manager = Mock()
        manager.filter.return_value.first.return_value = None
        with patch.object(photos.apps, 'get_model', return_value=Student), \
                patch.object(photos, 'linked_student_id', return_value=7), \
                patch.object(SourcePhotoFingerprint, 'objects', manager):
            descriptor, stream = photos.prepare_photo(900, event, allow_reuse=True)
            stream.close()
            self.assertEqual(descriptor['action'], 'put')
            cached = manager.update_or_create.call_args.kwargs['defaults']
            manager.filter.return_value.first.return_value = SimpleNamespace(**cached)
            descriptor, stream = photos.prepare_photo(900, event, allow_reuse=True)
            self.assertEqual(descriptor['action'], 'verify')
            self.assertIsNone(stream)
            self.assertEqual(field.open.call_count, 1)
            descriptor, stream = photos.prepare_photo(900, event, allow_reuse=True, force_read=True)
            stream.close()
            self.assertEqual(descriptor['action'], 'put')
            self.assertEqual(field.open.call_count, 2)
            # Student changes invalidate a fingerprint even if the backend's
            # modification time has coarse precision and stays the same.
            from datetime import timedelta
            student.modified += timedelta(microseconds=1)
            descriptor, stream = photos.prepare_photo(900, event, allow_reuse=True)
            self.assertEqual(descriptor['action'], 'verify')
            self.assertIsNone(stream)
            self.assertEqual(field.open.call_count, 3)
            student.modified += timedelta(microseconds=1)
            field.open.side_effect = lambda mode: io.BytesIO(b'changed source photo')
            descriptor, stream = photos.prepare_photo(900, event, allow_reuse=True)
            self.assertEqual(descriptor['action'], 'put')
            self.assertEqual(stream.read(), b'changed source photo')
            stream.close()


@override_settings(DATASYNC_ENABLED=True, DATASYNC_PARALLEL_UPLOADS=3)
class DeliveryConcurrencyTests(TransactionTestCase):
    def event(self, index, resource='mscc.registration'):
        return SimpleNamespace(pk=index, event_id=uuid.uuid4(), resource=resource,
                               source_id=str(index), status='pending', next_attempt=None,
                               attempts=0, refresh_from_db=Mock())

    def test_parallel_lanes_are_bounded_and_complete_each_event_once(self):
        lock = threading.Lock()
        active, peak, seen = 0, 0, []

        class Client(transport.SyncClient):
            def __init__(self):
                pass

            def worker_copy(self):
                return Client()

            def close(self):
                pass

        def push(events, client):
            nonlocal active, peak
            with lock:
                active += 1
                peak = max(peak, active)
                seen.extend(event.pk for event in events)
            time.sleep(0.02)
            with lock:
                active -= 1
            return {'sent': len(events), 'failed': 0, 'abandoned': 0}

        with patch.object(delivery, 'entity_key', side_effect=lambda event: event.source_id), \
                patch.object(dispatch, '_push_events', side_effect=push):
            result = dispatch.deliver_events([self.event(index) for index in range(30)], Client())
        self.assertEqual(result['sent'], 30)
        self.assertEqual(sorted(seen), list(range(30)))
        self.assertGreater(peak, 1)
        self.assertLessEqual(peak, 3)

    def test_other_connection_cannot_deliver_same_event_or_child(self):
        first, second = self.event(1), self.event(2)
        results = []

        def other(event):
            try:
                with delivery.guard_events([event]) as ready:
                    results.append(len(ready))
            finally:
                connections.close_all()

        with patch.object(delivery, 'entity_key', return_value='same-child'):
            with delivery.guard_events([first]) as ready:
                self.assertEqual(len(ready), 1)
                for event in (first, second):
                    thread = threading.Thread(target=other, args=(event,))
                    thread.start()
                    thread.join(timeout=10)
                    self.assertFalse(thread.is_alive())
            other(second)
        self.assertEqual(results, [0, 0, 1])

    @override_settings(DATASYNC_PARALLEL_UPLOADS=1)
    def test_slot_limit_applies_across_connections_and_releases_after_error(self):
        results = []

        def other():
            try:
                with delivery.guard_events([self.event(2, 'mscc.round')]) as ready:
                    results.append(len(ready))
            finally:
                connections.close_all()

        with self.assertRaisesRegex(RuntimeError, 'crash'):
            with delivery.guard_events([self.event(1, 'mscc.round')]):
                thread = threading.Thread(target=other)
                thread.start()
                thread.join(timeout=10)
                self.assertFalse(thread.is_alive())
                raise RuntimeError('crash')
        other()
        self.assertEqual(results, [0, 1])

    def test_dependency_stage_completes_before_registration_stage(self):
        order = []

        class Client:
            pass

        def push(events, client):
            order.extend(event.resource for event in events)
            return {'sent': len(events), 'failed': 0, 'abandoned': 0}

        events = [self.event(3), self.event(1, 'mscc.round'), self.event(2, 'locations.center')]
        with patch.object(delivery, 'entity_key', side_effect=lambda event: event.source_id), \
                patch.object(dispatch, '_push_events', side_effect=push):
            dispatch.deliver_events(events, Client())
        self.assertEqual(order, ['mscc.round', 'locations.center', 'mscc.registration'])
