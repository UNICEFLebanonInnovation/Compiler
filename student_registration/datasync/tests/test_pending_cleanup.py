"""Pending removal respects confirmation, partner scopes and worker locks."""
from concurrent.futures import ThreadPoolExecutor
import threading
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.core import signing
from django.db import connections, transaction
from django.test import Client, TestCase, TransactionTestCase, override_settings, skipUnlessDBFeature
from django.urls import reverse

from . import test_bulk_sync as fixture
from ..bulk_sync import prepare_run
from ..constants import RESOURCE_ROUND
from ..models import BulkSyncRun, SyncEvent
from ..pending_cleanup import pending_for_user, remove_pending
from student_registration.mscc.models import Round
from student_registration.schools.models import PartnerOrganization


@override_settings(DATASYNC_ENABLED=True, DATASYNC_TARGET_URL='https://nfe.test/api/sync/events/',
                   DATASYNC_TARGET_TOKEN='isolated-cleanup-test')
class PendingRemovalTests(TestCase):
    setUp = fixture.BulkRoundTests.setUp
    new_run = fixture.BulkRoundTests.new_run

    def removal_url(self, partner=None):
        return '{}?partner={}'.format(reverse('admin:datasync_bulksyncrun_remove_pending'),
                                      (partner or self.partner).pk)

    def confirmation(self, partner=None):
        response = self.client.get(self.removal_url(partner))
        self.assertEqual(response.status_code, 200)
        return response.context['confirmation']

    def staff(self, name, can_start=True, partner=None):
        user = get_user_model().objects.create_user(username=name, is_staff=True,
                                                    partner=partner or self.partner)
        codes = ['view_bulksyncrun', 'view_partnerorganization', 'view_round']
        if can_start:
            codes.append('add_bulksyncrun')
        user.user_permissions.add(*Permission.objects.filter(codename__in=codes))
        return user

    def test_confirmation_get_lists_requests_without_deleting_them(self):
        run = self.new_run()
        response = self.client.get(self.removal_url())
        self.assertContains(response, str(run.pk))
        self.assertContains(response, 'Remove 1 pending request')
        self.assertContains(response, 'Source records and data in BMA-NFE are preserved')
        self.assertTrue(BulkSyncRun.objects.filter(pk=run.pk).exists())

    def test_selected_partner_button_is_available_on_bulk_page(self):
        self.new_run()
        response = self.client.get(self.url, {'partner': self.partner.pk, 'category': RESOURCE_ROUND,
                                             'round': self.round.pk})
        self.assertContains(response, self.removal_url())
        self.assertContains(response, 'Remove pending bulk syncs')

    def test_empty_selection_shows_partner_hint_and_no_removal_link(self):
        self.new_run()
        response = self.client.get(self.url)
        self.assertContains(response, 'Choose a partner above to manage its pending requests')
        self.assertNotContains(response, self.removal_url())

    def test_confirmed_pending_requests_are_removed_without_source_data_changes(self):
        first, second = self.new_run(), self.new_run()
        token = self.confirmation()
        response = self.client.post(self.removal_url(), {'confirmation': token})
        self.assertRedirects(response, self.url)
        self.assertFalse(BulkSyncRun.objects.filter(pk__in=[first.pk, second.pk]).exists())
        self.assertFalse(SyncEvent.objects.exists())
        self.assertTrue(Round.objects.filter(pk=self.round.pk).exists())
        self.assertTrue(type(self.center).objects.filter(pk=self.center.pk).exists())
        self.assertTrue(type(self.child).objects.filter(pk=self.child.pk).exists())
        self.assertTrue(PartnerOrganization.objects.filter(pk=self.partner.pk).exists())

    def test_other_partners_requests_are_preserved(self):
        ours = self.new_run()
        with override_settings(DATASYNC_ENABLED=False):
            other_partner = PartnerOrganization.objects.create(name='Other removal partner')
        other = BulkSyncRun.objects.create(partner=other_partner, round=self.round,
                                          category=RESOURCE_ROUND, requested_by=self.user)
        self.client.post(self.removal_url(), {'confirmation': self.confirmation()})
        self.assertFalse(BulkSyncRun.objects.filter(pk=ours.pk).exists())
        self.assertTrue(BulkSyncRun.objects.filter(pk=other.pk).exists())

    def test_ready_failed_and_event_bearing_requests_are_preserved(self):
        removable = self.new_run()
        ready = self.new_run()
        ready.preparation = 'ready'
        ready.save(update_fields=['preparation'])
        failed = self.new_run()
        failed.preparation = 'failed'
        failed.save(update_fields=['preparation'])
        events = self.new_run(RESOURCE_ROUND)
        prepare_run(events.pk)
        BulkSyncRun.objects.filter(pk=events.pk).update(preparation='waiting', queued_counts={})
        self.assertQuerySetEqual(pending_for_user(self.user, self.partner), [removable])
        self.client.post(self.removal_url(), {'confirmation': self.confirmation()})
        self.assertSetEqual(set(BulkSyncRun.objects.values_list('pk', flat=True)),
                            {ready.pk, failed.pk, events.pk})
        self.assertEqual(SyncEvent.objects.filter(bulk_run=events).count(), 1)

    def test_nonempty_queue_counts_are_preserved_even_if_no_events_remain(self):
        run = self.new_run()
        run.queued_counts = {RESOURCE_ROUND: 1}
        run.save(update_fields=['queued_counts'])
        self.assertFalse(pending_for_user(self.user, self.partner).exists())

    def test_confirmation_does_not_include_requests_created_after_review(self):
        old = self.new_run()
        token = self.confirmation()
        new = self.new_run()
        self.client.post(self.removal_url(), {'confirmation': token})
        self.assertFalse(BulkSyncRun.objects.filter(pk=old.pk).exists())
        self.assertTrue(BulkSyncRun.objects.filter(pk=new.pk).exists())

    def test_request_that_starts_after_review_is_kept(self):
        run = self.new_run(RESOURCE_ROUND)
        token = self.confirmation()
        prepare_run(run.pk)
        self.client.post(self.removal_url(), {'confirmation': token})
        self.assertTrue(BulkSyncRun.objects.filter(pk=run.pk).exists())
        self.assertEqual(SyncEvent.objects.filter(bulk_run=run).count(), 1)

    def test_repeated_confirmation_is_idempotent(self):
        run = self.new_run()
        token = self.confirmation()
        self.client.post(self.removal_url(), {'confirmation': token})
        response = self.client.post(self.removal_url(), {'confirmation': token})
        self.assertEqual(response.status_code, 302)
        self.assertFalse(BulkSyncRun.objects.filter(pk=run.pk).exists())

    def test_csrf_is_required_for_confirmation(self):
        run = self.new_run()
        token = self.confirmation()
        client = Client(enforce_csrf_checks=True)
        client.force_login(self.user)
        self.assertEqual(client.post(self.removal_url(), {'confirmation': token}).status_code, 403)
        self.assertTrue(BulkSyncRun.objects.filter(pk=run.pk).exists())

    def test_missing_tampered_and_expired_confirmations_do_not_delete(self):
        run = self.new_run()
        token = self.confirmation()
        for invalid in ('', token + 'tampered'):
            self.assertEqual(self.client.post(self.removal_url(), {'confirmation': invalid}).status_code, 400)
        with patch('django.core.signing.TimestampSigner.timestamp', return_value='0'):
            expired = self.confirmation()
        self.assertEqual(self.client.post(self.removal_url(), {'confirmation': expired}).status_code, 400)
        self.assertTrue(BulkSyncRun.objects.filter(pk=run.pk).exists())

    def test_confirmation_is_bound_to_partner(self):
        run = self.new_run()
        token = self.confirmation()
        with override_settings(DATASYNC_ENABLED=False):
            other = PartnerOrganization.objects.create(name='Token partner')
        self.assertEqual(self.client.post(self.removal_url(other), {'confirmation': token}).status_code, 403)
        self.assertTrue(BulkSyncRun.objects.filter(pk=run.pk).exists())

    def test_staff_can_remove_only_their_own_requests(self):
        original = self.new_run()
        user = self.staff('cleanup-owner')
        ours = BulkSyncRun.objects.create(partner=self.partner, round=self.round,
                                         category=RESOURCE_ROUND, requested_by=user)
        self.client.force_login(user)
        response = self.client.get(self.removal_url())
        self.assertContains(response, str(ours.pk))
        self.assertNotContains(response, str(original.pk))
        self.client.post(self.removal_url(), {'confirmation': response.context['confirmation']})
        self.assertFalse(BulkSyncRun.objects.filter(pk=ours.pk).exists())
        self.assertTrue(BulkSyncRun.objects.filter(pk=original.pk).exists())

    def test_confirmation_is_bound_to_operator(self):
        run = self.new_run()
        token = self.confirmation()
        user = self.staff('other-confirmation-user')
        self.client.force_login(user)
        self.assertEqual(self.client.post(self.removal_url(), {'confirmation': token}).status_code, 403)
        self.assertTrue(BulkSyncRun.objects.filter(pk=run.pk).exists())

    def test_revoked_partner_access_prevents_removal(self):
        user = self.staff('moved-cleanup-user')
        run = BulkSyncRun.objects.create(partner=self.partner, round=self.round,
                                        category=RESOURCE_ROUND, requested_by=user)
        self.client.force_login(user)
        token = self.confirmation()
        with override_settings(DATASYNC_ENABLED=False):
            other = PartnerOrganization.objects.create(name='New user assignment')
        user.partner = other
        user.save(update_fields=['partner'])
        self.assertEqual(self.client.post(self.removal_url(), {'confirmation': token}).status_code, 404)
        self.assertTrue(BulkSyncRun.objects.filter(pk=run.pk).exists())

    def test_view_only_user_and_anonymous_user_cannot_remove(self):
        self.new_run()
        user = self.staff('cleanup-viewer', can_start=False)
        self.client.force_login(user)
        self.assertEqual(self.client.get(self.removal_url()).status_code, 403)
        self.assertEqual(self.client.post(self.removal_url(), {'confirmation': 'anything'}).status_code, 403)
        self.client.logout()
        self.assertEqual(self.client.get(self.removal_url()).status_code, 302)

    def test_invalid_partner_and_unsupported_method_do_not_remove(self):
        run = self.new_run()
        root = reverse('admin:datasync_bulksyncrun_remove_pending')
        for query in ('', '?partner=bad', '?partner=999999999'):
            self.assertEqual(self.client.get(root + query).status_code, 404)
        self.assertEqual(self.client.put(self.removal_url()).status_code, 405)
        self.assertTrue(BulkSyncRun.objects.filter(pk=run.pk).exists())


@override_settings(DATASYNC_ENABLED=True)
class PendingRemovalConcurrencyTests(TransactionTestCase):
    def setUp(self):
        with override_settings(DATASYNC_ENABLED=False):
            self.partner = PartnerOrganization.objects.create(name='Cleanup race partner')
            self.round = Round.objects.create(name='Cleanup race round')
        self.user = get_user_model().objects.create_superuser(
            username='cleanup-race-user', password='test', email='race@example.test')
        self.run = BulkSyncRun.objects.create(partner=self.partner, round=self.round,
                                             category=RESOURCE_ROUND, requested_by=self.user)

    @skipUnlessDBFeature('has_select_for_update_skip_locked')
    def test_worker_lock_protects_request_during_removal(self):
        entered, release = threading.Event(), threading.Event()

        def worker():
            try:
                with transaction.atomic():
                    BulkSyncRun.objects.select_for_update().get(pk=self.run.pk)
                    entered.set()
                    if not release.wait(10):
                        raise RuntimeError('Cleanup race did not release worker')
                    prepare_run(self.run.pk)
            finally:
                connections.close_all()

        with ThreadPoolExecutor(max_workers=1) as pool:
            task = pool.submit(worker)
            try:
                self.assertTrue(entered.wait(10))
                self.assertEqual(remove_pending(self.user, self.partner, [self.run.pk]), (0, 1))
            finally:
                release.set()
            task.result(timeout=10)
        self.run.refresh_from_db()
        self.assertEqual(self.run.preparation, 'ready')
        self.assertEqual(self.run.events.count(), 1)

    @skipUnlessDBFeature('has_select_for_update_skip_locked')
    def test_removed_request_cannot_be_prepared_by_worker(self):
        def worker():
            try:
                prepare_run(self.run.pk)
            finally:
                connections.close_all()

        with transaction.atomic():
            self.assertEqual(remove_pending(self.user, self.partner, [self.run.pk]), (1, 0))
            with ThreadPoolExecutor(max_workers=1) as pool:
                pool.submit(worker).result(timeout=5)
        prepare_run(self.run.pk)
        self.assertFalse(BulkSyncRun.objects.filter(pk=self.run.pk).exists())
        self.assertFalse(SyncEvent.objects.exists())
