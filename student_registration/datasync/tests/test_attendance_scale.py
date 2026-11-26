"""Attendance days contain child rows and need smaller HTTP batches."""
from types import SimpleNamespace
from unittest.mock import patch

from django.test import SimpleTestCase, TestCase, override_settings

from .. import dispatch
from ..constants import RESOURCE_ATTENDANCE


@override_settings(DATASYNC_ENABLED=True)
class AttendanceBatchTests(SimpleTestCase):
    def deliver(self, count):
        batches = []
        events = [SimpleNamespace(resource=RESOURCE_ATTENDANCE, pk=i) for i in range(count)]

        def send(rows, client):
            batches.append([row.pk for row in rows])
            return {'sent': len(rows), 'failed': 0, 'abandoned': 0}

        with patch('student_registration.datasync.bulk_jobs.restrict_bulk_events', side_effect=lambda rows: rows), \
                patch.object(dispatch, '_locked_push', side_effect=send):
            result = dispatch.deliver_events(events, object())
        self.assertEqual(result, {'sent': count, 'failed': 0, 'abandoned': 0})
        self.assertEqual([pk for batch in batches for pk in batch], list(range(count)))
        return batches

    def test_one_hundred_days_are_split_into_ten_complete_day_batches(self):
        self.assertEqual([len(rows) for rows in self.deliver(103)], [10] * 10 + [3])

    @override_settings(DATASYNC_ATTENDANCE_BATCH_SIZE=7, DATASYNC_BATCH_SIZE=3)
    def test_attendance_never_exceeds_the_configured_general_limit(self):
        self.assertEqual([len(rows) for rows in self.deliver(8)], [3, 3, 2])

    @override_settings(DATASYNC_ATTENDANCE_BATCH_SIZE=0)
    def test_zero_limit_still_delivers_one_complete_day(self):
        self.assertEqual([len(rows) for rows in self.deliver(2)], [1, 1])


class HistoryAdmissionTests(TestCase):
    from .test_bulk_sync import BulkRoundTests
    setUp = BulkRoundTests.setUp
    new_run = BulkRoundTests.new_run

    def test_completed_history_and_automatic_events_do_not_hide_the_oldest_outstanding_job(self):
        from ..bulk_jobs import current_run
        from ..models import BulkSyncRun, SyncEvent
        from ..constants import RESOURCE_ROUND
        history = [self.new_run(RESOURCE_ROUND) for _ in range(60)]
        BulkSyncRun.objects.filter(pk__in=[row.pk for row in history]).update(preparation='ready')
        SyncEvent.objects.bulk_create([SyncEvent(resource=RESOURCE_ROUND, source_id=str(index),
            bulk_run=run, status='sent') for index, run in enumerate(history)])
        SyncEvent.objects.create(resource=RESOURCE_ROUND, source_id='automatic', status='pending')
        failed = self.new_run(RESOURCE_ROUND)
        failed.preparation = 'failed'; failed.save()
        self.assertIsNone(current_run())
        active = history[30]
        active.preparation = 'cancelled'; active.save()
        active.events.update(status='failed')
        waiting = self.new_run(RESOURCE_ROUND)
        self.assertEqual(current_run().pk, active.pk)
        active.events.update(status='abandoned')
        self.assertEqual(current_run().pk, waiting.pk)
        waiting.preparation = 'cancelled'; waiting.save()
        self.assertIsNone(current_run())
