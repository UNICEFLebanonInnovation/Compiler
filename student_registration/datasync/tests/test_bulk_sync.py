"""Real database checks for round selection, durable queueing and admin access."""
import uuid
import threading
from concurrent.futures import ThreadPoolExecutor
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.db import connections
from django.test import Client, TestCase, TransactionTestCase, override_settings
from django.urls import reverse

from student_registration.attendances.models import MSCCAttendance, MSCCAttendanceChild
from student_registration.child.models import Child
from student_registration.locations.models import Center, ProgramStaff
from student_registration.mscc.models import (
    EducationAssessment, EducationProgrammeAssessment, EducationService,
    Referral, Registration, Round,
)
from student_registration.schools.models import CLMRound, PartnerOrganization, School

from ..bulk_sync import RoundSyncPlan, prepare_run, prepare_waiting_runs, run_progress, schedule_bulk_sweep
from ..bulk_types import ALL_CATEGORIES
from ..constants import (
    RESOURCE_ATTENDANCE, RESOURCE_CENTER, RESOURCE_EDUCATION_ASSESSMENT,
    RESOURCE_EDUCATION_SERVICE, RESOURCE_GRADING, RESOURCE_REFERRAL,
    RESOURCE_REGISTRATION, RESOURCE_ROUND, RESOURCE_TEACHER,
)
from ..models import BulkSyncRun, SchoolCenterLink, SyncEvent
from ..serializers import serialize_teacher


@override_settings(DATASYNC_ENABLED=True, DATASYNC_TARGET_URL='https://nfe.test/api/sync/events/',
                   DATASYNC_TARGET_TOKEN='isolated-test-token')
class BulkRoundTests(TestCase):
    def setUp(self):
        with override_settings(DATASYNC_ENABLED=False):
            self.partner = PartnerOrganization.objects.create(name='Bulk partner A')
            self.round = Round.objects.create(name='Bulk round A', year=2026)
            self.other_round = Round.objects.create(name='Bulk round B', year=2025)
            self.center = Center.objects.create(name='Centre A', p_code='BULK-A', partner=self.partner)
            self.other_center = Center.objects.create(name='Centre B', p_code='BULK-B', partner=self.partner)
            self.child = Child.objects.create(first_name='Preview child')
            self.registration = Registration.objects.create(round=self.round, center=self.center, child=self.child, partner=self.partner)
            self.other_registration = Registration.objects.create(round=self.other_round, center=self.other_center, partner=self.partner)
            self.unneeded_registration = Registration.objects.create(round=self.round, center=self.center, partner=self.partner)
            self.assessment = EducationAssessment.objects.create(registration=self.registration)
            self.other_assessment = EducationAssessment.objects.create(registration=self.other_registration)
            self.service = EducationService.objects.create(registration=self.registration, round=self.round)
            self.grading = EducationProgrammeAssessment.objects.create(registration=self.registration)
            self.referral = Referral.objects.create(registration=self.registration)
            self.day = MSCCAttendance.objects.create(round_id=self.round.pk, center=self.center)
            self.other_day = MSCCAttendance.objects.create(round_id=self.other_round.pk, center=self.other_center)
            MSCCAttendanceChild.objects.create(attendance_day=self.day, registration=self.registration, child=self.child)
            self.school = School.objects.create(name='Mapped school', number='BULK-SCHOOL')
            self.partner.schools.add(self.school)
            self.teacher_round = CLMRound.objects.create(pk=10001, name=self.round.name)
            self.teacher = ProgramStaff.objects.create(facilitator_name='Bulk Teacher', center=self.center, programs=['BLN'])
            SchoolCenterLink.objects.create(school=self.school, center=self.center)
            self.other_teacher = ProgramStaff.objects.create(facilitator_name='Unrelated teacher', center=self.center, programs=['RS'])
        self.user = get_user_model().objects.create_superuser(username='bulk-admin', password='test-password', email='bulk@example.test')
        self.client.force_login(self.user)
        self.url = reverse('admin:datasync_bulksyncrun_changelist')

    def ids(self, plan, resource):
        return set(plan.queries[resource].values_list('pk', flat=True)) if resource in plan.queries else set()

    def new_run(self, category=RESOURCE_EDUCATION_ASSESSMENT):
        return BulkSyncRun.objects.create(round=self.round, category=category, requested_by=self.user, partner=self.partner)

    def post_data(self, **extra):
        return dict(round=self.round.pk, category=RESOURCE_EDUCATION_ASSESSMENT,
                    request_id=str(uuid.uuid4()), **extra, partner=self.partner.pk)

    def test_assessment_plan_queues_only_required_parents_in_same_round(self):
        plan = RoundSyncPlan(self.round, RESOURCE_EDUCATION_ASSESSMENT, partner=self.partner)
        self.assertEqual(self.ids(plan, RESOURCE_ROUND), {self.round.pk})
        self.assertEqual(self.ids(plan, RESOURCE_EDUCATION_ASSESSMENT), {self.assessment.pk})
        self.assertEqual(self.ids(plan, RESOURCE_REGISTRATION), {self.registration.pk})
        self.assertEqual(self.ids(plan, RESOURCE_CENTER), {self.center.pk})
        self.assertNotIn(RESOURCE_TEACHER, plan.queries)
        self.assertEqual(plan.errors(), [])

    def test_all_categories_use_global_masters_and_round_scoped_child_records(self):
        plan = RoundSyncPlan(self.round, ALL_CATEGORIES, partner=self.partner)
        expected = {
            RESOURCE_ROUND: {self.round.pk}, RESOURCE_CENTER: {self.center.pk, self.other_center.pk},
            RESOURCE_TEACHER: {self.teacher.pk, self.other_teacher.pk},
            RESOURCE_REGISTRATION: {self.registration.pk, self.unneeded_registration.pk},
            RESOURCE_EDUCATION_SERVICE: {self.service.pk}, RESOURCE_EDUCATION_ASSESSMENT: {self.assessment.pk},
            RESOURCE_GRADING: {self.grading.pk}, RESOURCE_REFERRAL: {self.referral.pk},
            RESOURCE_ATTENDANCE: {self.day.pk},
        }
        self.assertEqual({key: self.ids(plan, key) for key in plan.queries}, expected)

    def test_program_staff_are_global_and_have_no_round_metadata(self):
        plan = RoundSyncPlan(self.round, RESOURCE_TEACHER, partner=self.partner)
        self.assertEqual(self.ids(plan, RESOURCE_TEACHER), {self.teacher.pk, self.other_teacher.pk})
        self.assertIsNone(plan.round)
        self.assertNotEqual(self.teacher_round.pk, self.round.pk)
        self.assertNotIn('round', serialize_teacher(self.teacher))

    def test_centres_include_attendance_and_teacher_links_without_registrations(self):
        with override_settings(DATASYNC_ENABLED=False):
            attendance_center = Center.objects.create(name='Attendance only', p_code='BULK-ATT', partner=self.partner)
            MSCCAttendance.objects.create(round_id=self.round.pk, center=attendance_center)
            teacher_center = Center.objects.create(name='Teacher only', p_code='BULK-TCH', partner=self.partner)
            SchoolCenterLink.objects.filter(school=self.school).update(center=teacher_center)
        plan = RoundSyncPlan(self.round, RESOURCE_CENTER, partner=self.partner)
        self.assertEqual(self.ids(plan, RESOURCE_CENTER), {
            self.center.pk, self.other_center.pk, attendance_center.pk, teacher_center.pk})

    def test_attendance_includes_its_registration_dependencies(self):
        plan = RoundSyncPlan(self.round, RESOURCE_ATTENDANCE, partner=self.partner)
        self.assertEqual(self.ids(plan, RESOURCE_REGISTRATION), {self.registration.pk})
        self.assertEqual(self.ids(plan, RESOURCE_ATTENDANCE), {self.day.pk})

    def test_cross_round_attendance_is_rejected_before_any_queueing(self):
        with override_settings(DATASYNC_ENABLED=False):
            MSCCAttendanceChild.objects.create(attendance_day=self.day, registration=self.other_registration)
        run = self.new_run(RESOURCE_ATTENDANCE)
        prepare_run(run.pk)
        run.refresh_from_db()
        self.assertEqual(run.preparation, 'failed')
        self.assertIn('another round', run.last_error)
        self.assertEqual(run.events.count(), 0)

    def test_conflicting_education_service_round_is_reported(self):
        EducationService.objects.filter(pk=self.service.pk).update(round=self.other_round)
        self.assertIn('different round', ' '.join(RoundSyncPlan(self.round, RESOURCE_EDUCATION_SERVICE, partner=self.partner).errors()))

    def test_staff_does_not_require_a_school_to_centre_link(self):
        SchoolCenterLink.objects.all().delete()
        self.assertEqual(RoundSyncPlan(self.round, RESOURCE_TEACHER, partner=self.partner).errors(), [])

    def test_preparation_is_idempotent_and_uses_standard_outbox(self):
        run = self.new_run()
        prepare_run(run.pk)
        event_ids = list(run.events.values_list('event_id', flat=True))
        prepare_run(run.pk)
        run.refresh_from_db()
        self.assertEqual(run.preparation, 'ready')
        self.assertEqual(list(run.events.values_list('event_id', flat=True)), event_ids)
        self.assertEqual(run.events.count(), 4)
        self.assertEqual(set(run.events.values_list('status', flat=True)), {'pending'})
        self.assertEqual(set(run.events.values_list('operation', flat=True)), {'upsert'})

    def test_queue_preparation_rolls_back_partial_outbox_on_error(self):
        from .. import bulk_sync
        real_enqueue = bulk_sync.enqueue_many
        def fail_second(resource, source_ids, run):
            if resource == RESOURCE_CENTER:
                raise RuntimeError('Synthetic queue interruption')
            return real_enqueue(resource, source_ids, run)
        run = self.new_run()
        with patch.object(bulk_sync, 'enqueue_many', side_effect=fail_second):
            prepare_run(run.pk)
        run.refresh_from_db()
        self.assertEqual(run.preparation, 'failed')
        self.assertFalse(run.events.exists())

    def test_waiting_run_recovers_after_missed_broker_notification(self):
        run = self.new_run()
        with patch('student_registration.datasync.tasks.flush_sync_outbox.apply_async', side_effect=OSError('offline')):
            schedule_bulk_sweep()
        prepare_waiting_runs()
        run.refresh_from_db()
        self.assertEqual(run.preparation, 'ready')

    def test_existing_periodic_task_prepares_and_flushes_the_outbox(self):
        from ..tasks import flush_sync_outbox
        run = self.new_run()
        with patch('student_registration.datasync.dispatch.flush_outbox', return_value={'batches': 0}) as flush:
            flush_sync_outbox()
        run.refresh_from_db()
        self.assertEqual(run.preparation, 'ready')
        flush.assert_called_once()

    def test_disabled_sync_keeps_durable_request_waiting(self):
        run = self.new_run()
        with override_settings(DATASYNC_ENABLED=False):
            prepare_run(run.pk)
        run.refresh_from_db()
        self.assertEqual(run.preparation, 'waiting')
        self.assertFalse(run.events.exists())

    def test_selection_page_never_creates_runs_or_reads_supporting_records(self):
        response = self.client.get(self.url, {'round': self.round.pk, 'category': RESOURCE_EDUCATION_ASSESSMENT, 'partner': self.partner.pk})
        self.assertContains(response, 'Start sync')
        self.assertNotContains(response, 'Preview child')
        self.assertNotContains(response, 'Record preview')
        self.assertEqual(SyncEvent.objects.count(), 0)
        self.assertEqual(BulkSyncRun.objects.count(), 0)

    def test_double_submit_creates_one_request_and_never_uploads_in_web_request(self):
        data = self.post_data()
        with patch('student_registration.datasync.bulk_admin.schedule_bulk_sweep') as schedule, \
                self.captureOnCommitCallbacks(execute=True):
            first = self.client.post(self.url, data)
            second = self.client.post(self.url, data)
        self.assertEqual(first.status_code, 302)
        self.assertEqual(second.status_code, 302)
        self.assertEqual(BulkSyncRun.objects.count(), 1)
        self.assertFalse(SyncEvent.objects.exists())
        schedule.assert_called_once()

    def test_invalid_round_and_category_cannot_queue_records(self):
        for data in ({'round': self.round.pk, 'category': 'child.photo'},
                     {'round': 9999999, 'category': RESOURCE_REGISTRATION}):
            response = self.client.post(self.url, {**data, 'request_id': str(uuid.uuid4()), 'partner': self.partner.pk})
            self.assertEqual(response.status_code, 200)
        self.assertFalse(BulkSyncRun.objects.exists())

    def test_disabled_sync_cannot_start(self):
        with override_settings(DATASYNC_ENABLED=False):
            response = self.client.post(self.url, self.post_data())
        self.assertContains(response, 'Synchronization is disabled')
        self.assertFalse(BulkSyncRun.objects.exists())

    def test_start_requires_csrf(self):
        client = Client(enforce_csrf_checks=True)
        client.force_login(self.user)
        self.assertEqual(client.post(self.url, self.post_data()).status_code, 403)
        self.assertFalse(BulkSyncRun.objects.exists())

    def test_view_only_staff_can_preview_but_cannot_start(self):
        user = get_user_model().objects.create_user(username='bulk-viewer', password='test', is_staff=True)
        user.user_permissions.add(*Permission.objects.filter(codename__in=[
            'view_bulksyncrun', 'view_round', 'view_registration', 'view_center', 'view_educationassessment',
        'view_partnerorganization']))
        self.client.force_login(user)
        response = self.client.get(self.url, {'round': self.round.pk, 'category': RESOURCE_EDUCATION_ASSESSMENT, 'partner': self.partner.pk})
        self.assertContains(response, 'view-only access')
        self.assertEqual(self.client.post(self.url, self.post_data()).status_code, 403)

    def test_cannot_start_without_supporting_record_permissions(self):
        user = get_user_model().objects.create_user(username='bulk-limited', password='test', is_staff=True)
        user.user_permissions.add(*Permission.objects.filter(codename__in=[
            'view_bulksyncrun', 'add_bulksyncrun', 'view_round', 'view_educationassessment',
        'view_partnerorganization']))
        self.client.force_login(user)
        self.assertEqual(self.client.get(self.url, {'round': self.round.pk,
            'category': RESOURCE_EDUCATION_ASSESSMENT, 'partner': self.partner.pk}).status_code, 200)
        self.assertEqual(self.client.post(self.url, self.post_data()).status_code, 403)

    def test_preview_pagination_does_not_repeat_or_omit_records(self):
        plan = RoundSyncPlan(self.round, ALL_CATEGORIES, partner=self.partner)
        expected = sum(item['count'] for item in plan.summary())
        keys = []
        for offset in range(0, expected, 3):
            rows = plan.preview(offset, 3)
            keys.extend((row['label'], row['source_id']) for row in rows)
        self.assertEqual(len(keys), expected)
        self.assertEqual(len(set(keys)), expected)

    def test_progress_does_not_label_failed_delivery_as_completed(self):
        run = self.new_run()
        prepare_run(run.pk)
        run.refresh_from_db()
        run.events.update(status='sent')
        run.events.filter(resource=RESOURCE_EDUCATION_ASSESSMENT).update(status='failed', last_error='HTTP 403')
        progress = run_progress(run)
        self.assertEqual(progress['status'], 'Retrying failed deliveries')
        self.assertEqual(progress['failed'], 1)
        response = self.client.get(self.url, {'run': run.pk, 'partner': self.partner.pk})
        self.assertContains(response, 'HTTP 403')
        run.events.update(status='sent')
        self.assertEqual(run_progress(run)['status'], 'Completed')

    def test_run_event_filter_is_accepted_by_existing_admin(self):
        run = self.new_run()
        prepare_run(run.pk)
        response = self.client.get(reverse('admin:datasync_syncevent_changelist'), {'bulk_run__id__exact': run.pk})
        self.assertEqual(response.status_code, 200)
        self.assertNotIn('?e=1', response.get('Location', ''))

    def test_staff_cannot_read_another_operators_request(self):
        run = self.new_run()
        user = get_user_model().objects.create_user(username='bulk-other', password='test', is_staff=True)
        user.user_permissions.add(*Permission.objects.filter(codename__in=['view_bulksyncrun', 'view_round', 'view_partnerorganization']))
        self.client.force_login(user)
        self.assertEqual(self.client.get(self.url, {'run': run.pk, 'partner': self.partner.pk}).status_code, 404)

    def test_multiple_categories_share_dependencies_without_duplicate_events(self):
        categories = [RESOURCE_REFERRAL, RESOURCE_EDUCATION_ASSESSMENT]
        plan = RoundSyncPlan(self.round, categories, partner=self.partner)
        self.assertEqual(plan.errors(), [])
        self.assertEqual(self.ids(plan, RESOURCE_REGISTRATION), {self.registration.pk})
        self.assertEqual(self.ids(plan, RESOURCE_REFERRAL), {self.referral.pk})
        self.assertEqual(sum(row['count'] for row in plan.summary()), 5)
        run = BulkSyncRun.objects.create(round=self.round, category=plan.category, categories=plan.categories, partner=self.partner)
        prepare_run(run.pk)
        pairs = list(run.events.values_list('resource', 'source_id'))
        self.assertEqual(len(pairs), 5)
        self.assertEqual(len(set(pairs)), 5)

    def test_all_combined_with_categories_is_one_complete_selection(self):
        plan = RoundSyncPlan(self.round, [RESOURCE_REGISTRATION, ALL_CATEGORIES, RESOURCE_REFERRAL], partner=self.partner)
        self.assertEqual(plan.categories, [ALL_CATEGORIES])
        self.assertEqual(plan.selected, RoundSyncPlan(self.round, ALL_CATEGORIES, partner=self.partner).selected)

    def test_selection_order_and_duplicates_are_normalized(self):
        first = RoundSyncPlan(self.round, [RESOURCE_REFERRAL, RESOURCE_EDUCATION_ASSESSMENT, RESOURCE_REFERRAL], partner=self.partner)
        second = RoundSyncPlan(self.round, [RESOURCE_EDUCATION_ASSESSMENT, RESOURCE_REFERRAL], partner=self.partner)
        self.assertEqual(first.categories, second.categories)

    def test_legacy_single_category_run_retains_its_scope(self):
        run = self.new_run()
        self.assertEqual(run.categories, [])
        self.assertEqual(run.selected_categories, [RESOURCE_EDUCATION_ASSESSMENT])
        self.assertEqual(run.get_category_display(), 'Education assessments')
        prepare_run(run.pk)
        self.assertEqual(run.events.count(), 4)

    def test_multi_category_post_saves_exact_selection_in_one_request(self):
        data = self.post_data()
        data['category'] = [RESOURCE_EDUCATION_ASSESSMENT, RESOURCE_REFERRAL]
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 302)
        run = BulkSyncRun.objects.get()
        self.assertEqual(run.category, 'selected')
        self.assertEqual(run.selected_categories, data['category'])
        self.assertEqual(run.get_category_display(), 'Education assessments, Referrals')
        response = self.client.get(self.url, {'run': run.pk, 'partner': self.partner.pk})
        self.assertContains(response, 'Education assessments, Referrals')

    def test_double_submit_with_reordered_categories_creates_one_request(self):
        data = self.post_data()
        data['category'] = [RESOURCE_EDUCATION_ASSESSMENT, RESOURCE_REFERRAL]
        with patch('student_registration.datasync.bulk_admin.schedule_bulk_sweep') as schedule, \
                self.captureOnCommitCallbacks(execute=True):
            first = self.client.post(self.url, data)
            data['category'].reverse()
            second = self.client.post(self.url, data)
        self.assertEqual(first.status_code, 302)
        self.assertEqual(second.status_code, 302)
        self.assertEqual(BulkSyncRun.objects.count(), 1)
        schedule.assert_called_once()

    def test_request_id_cannot_be_reused_for_different_categories(self):
        data = self.post_data()
        self.assertEqual(self.client.post(self.url, data).status_code, 302)
        data['category'] = [RESOURCE_EDUCATION_ASSESSMENT, RESOURCE_REFERRAL]
        self.assertEqual(self.client.post(self.url, data).status_code, 403)
        self.assertEqual(BulkSyncRun.objects.get().selected_categories, [RESOURCE_EDUCATION_ASSESSMENT])

    def test_multiple_categories_stay_selected_without_loading_records(self):
        Registration.objects.bulk_create([Registration(round=self.round, center=self.center, partner=self.partner) for _ in range(52)])
        categories = [RESOURCE_REGISTRATION, RESOURCE_EDUCATION_ASSESSMENT]
        response = self.client.get(self.url, {'round': self.round.pk, 'category': categories, 'partner': self.partner.pk})
        self.assertEqual(response.context['form'].cleaned_data['category'], categories)
        response = self.client.get(self.url, {'round': self.round.pk, 'category': categories, 'page': 2, 'partner': self.partner.pk})
        self.assertEqual(response.context['form'].cleaned_data['category'], categories)
        self.assertNotContains(response, 'Record preview')
        self.assertFalse(BulkSyncRun.objects.exists())

    def test_empty_or_invalid_multi_selection_cannot_queue(self):
        for categories in ([], ['child.photo', ALL_CATEGORIES]):
            data = self.post_data()
            data['category'] = categories
            self.assertEqual(self.client.post(self.url, data).status_code, 200)
        self.assertFalse(BulkSyncRun.objects.exists())

    def test_unauthorized_category_cannot_be_added_to_a_multi_selection(self):
        user = get_user_model().objects.create_user(username='bulk-multi-limited', password='test', is_staff=True)
        user.user_permissions.add(*Permission.objects.filter(codename__in=[
            'view_bulksyncrun', 'add_bulksyncrun', 'view_round', 'view_center',
            'view_registration', 'view_educationassessment',
        'view_partnerorganization']))
        self.client.force_login(user)
        data = self.post_data()
        data['category'] = [RESOURCE_EDUCATION_ASSESSMENT, RESOURCE_REFERRAL]
        self.assertEqual(self.client.post(self.url, data).status_code, 200)
        self.assertFalse(BulkSyncRun.objects.exists())

    def test_empty_category_does_not_block_another_selected_category_with_records(self):
        with override_settings(DATASYNC_ENABLED=False):
            self.referral.delete()
        plan = RoundSyncPlan(self.round, [RESOURCE_REFERRAL, RESOURCE_EDUCATION_ASSESSMENT], partner=self.partner)
        self.assertEqual(plan.errors(), [])
        self.assertEqual(self.ids(plan, RESOURCE_REFERRAL), set())

    def test_selecting_each_category_is_equivalent_to_all(self):
        from ..constants import RESOURCE_ORDER
        self.assertEqual(RoundSyncPlan(self.round, RESOURCE_ORDER, partner=self.partner).categories, [ALL_CATEGORIES])

    def test_centres_can_be_synced_without_a_round_or_any_round_relationship(self):
        with override_settings(DATASYNC_ENABLED=False):
            unused = Center.objects.create(name='Never assigned to a round', p_code='UNASSIGNED', partner=self.partner)
        plan = RoundSyncPlan(None, RESOURCE_CENTER, partner=self.partner)
        self.assertEqual(self.ids(plan, RESOURCE_CENTER), {self.center.pk, self.other_center.pk, unused.pk})
        self.assertFalse(self.ids(plan, RESOURCE_ROUND))
        self.assertFalse(self.ids(plan, RESOURCE_REGISTRATION))
        self.assertEqual(plan.errors(), [])

    def test_teachers_from_other_rounds_and_without_a_round_are_all_selected(self):
        with override_settings(DATASYNC_ENABLED=False):
            unassigned = ProgramStaff.objects.create(facilitator_name='No round', center=self.center)
        expected = {self.teacher.pk, self.other_teacher.pk, unassigned.pk}
        for round_object in (None, self.round, self.other_round):
            plan = RoundSyncPlan(round_object, RESOURCE_TEACHER, partner=self.partner)
            self.assertEqual(self.ids(plan, RESOURCE_TEACHER), expected)
            self.assertEqual(self.ids(plan, RESOURCE_CENTER), {self.center.pk})
            self.assertFalse(self.ids(plan, RESOURCE_ROUND))
            self.assertFalse(self.ids(plan, RESOURCE_REGISTRATION))

    def test_global_request_is_saved_without_round_and_queues_only_global_records(self):
        response = self.client.post(self.url, {'category': [RESOURCE_CENTER, RESOURCE_TEACHER], 'request_id': str(uuid.uuid4()), 'partner': self.partner.pk})
        self.assertEqual(response.status_code, 302)
        run = BulkSyncRun.objects.get()
        self.assertIsNone(run.round_id)
        self.assertEqual(run.scope_label, '{} · All rounds (centres and teachers)'.format(self.partner))
        prepare_run(run.pk)
        self.assertEqual(run.events.count(), 4)
        self.assertEqual(set(run.events.values_list('resource', flat=True)), {RESOURCE_CENTER, RESOURCE_TEACHER})

    def test_selected_round_never_filters_global_categories(self):
        data = {'partner': self.partner.pk, 'round': self.round.pk, 'category': [RESOURCE_CENTER, RESOURCE_TEACHER], 'request_id': str(uuid.uuid4())}
        self.assertEqual(self.client.post(self.url, data).status_code, 302)
        data['round'] = self.other_round.pk
        self.assertEqual(self.client.post(self.url, data).status_code, 302)
        self.assertEqual(BulkSyncRun.objects.count(), 1)
        self.assertIsNone(BulkSyncRun.objects.get().round_id)

    def test_mixed_categories_keep_registration_scope_and_include_every_centre(self):
        plan = RoundSyncPlan(self.round, [RESOURCE_CENTER, RESOURCE_REGISTRATION], partner=self.partner)
        self.assertEqual(self.ids(plan, RESOURCE_CENTER), {self.center.pk, self.other_center.pk})
        self.assertEqual(self.ids(plan, RESOURCE_REGISTRATION), {self.registration.pk, self.unneeded_registration.pk})
        self.assertNotIn(self.other_registration.pk, self.ids(plan, RESOURCE_REGISTRATION))
        scopes = {item['resource']: item['scope'] for item in plan.summary()}
        self.assertEqual(scopes[RESOURCE_CENTER], 'Selected partner — all rounds')
        self.assertEqual(scopes[RESOURCE_REGISTRATION], 'Selected partner and round')

    def test_round_is_required_for_round_based_or_mixed_selections(self):
        for categories in ([RESOURCE_REGISTRATION], [RESOURCE_CENTER, RESOURCE_REFERRAL], [ALL_CATEGORIES]):
            response = self.client.post(self.url, {'category': categories, 'request_id': str(uuid.uuid4()), 'partner': self.partner.pk})
            self.assertContains(response, 'Choose a round for the selected categories.')
        self.assertFalse(BulkSyncRun.objects.exists())

    def test_global_selection_has_explicit_scope_and_no_hidden_round_requirement(self):
        response = self.client.get(self.url, {'category': [RESOURCE_CENTER, RESOURCE_TEACHER], 'partner': self.partner.pk})
        self.assertContains(response, 'include all rounds for the partner')
        self.assertNotContains(response, 'type="hidden" name="round"')
        self.assertContains(response, 'Start sync')

    def test_unassigned_registrations_do_not_leak_into_global_requests(self):
        with override_settings(DATASYNC_ENABLED=False):
            Registration.objects.create(center=self.center, round=None, partner=self.partner)
        plan = RoundSyncPlan(None, [RESOURCE_CENTER, RESOURCE_TEACHER], partner=self.partner)
        self.assertFalse(self.ids(plan, RESOURCE_REGISTRATION))

    def test_global_operator_does_not_need_round_access_or_see_round_names(self):
        user = get_user_model().objects.create_user(username='global-operator', password='test', is_staff=True)
        user.user_permissions.add(*Permission.objects.filter(codename__in=[
            'view_bulksyncrun', 'add_bulksyncrun', 'view_center', 'view_programstaff',
        'view_partnerorganization']))
        self.client.force_login(user)
        response = self.client.get(self.url, {'category': [RESOURCE_CENTER, RESOURCE_TEACHER], 'partner': self.partner.pk})
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, self.round.name)
        response = self.client.post(self.url, {'category': [RESOURCE_CENTER, RESOURCE_TEACHER], 'request_id': str(uuid.uuid4()), 'partner': self.partner.pk})
        self.assertEqual(response.status_code, 302)
        run = BulkSyncRun.objects.get()
        response = self.client.get(self.url, {'run': run.pk, 'partner': self.partner.pk})
        self.assertContains(response, 'All rounds (centres and teachers)')
        self.assertNotContains(response, self.round.name)

    def test_round_based_plan_without_round_is_rejected_before_querying_records(self):
        from ..bulk_sync import PlanError
        with self.assertRaisesRegex(PlanError, 'Choose a round'):
            RoundSyncPlan(None, RESOURCE_REGISTRATION, partner=self.partner)


@override_settings(DATASYNC_ENABLED=True)
class ConcurrentPreparationTests(TransactionTestCase):
    def test_two_workers_cannot_queue_the_same_run_twice(self):
        from .. import bulk_sync
        with override_settings(DATASYNC_ENABLED=False):
            partner = PartnerOrganization.objects.create(name='Concurrent partner')
            round_object = Round.objects.create(name='Concurrent preparation')
        run = BulkSyncRun.objects.create(round=round_object, category=RESOURCE_ROUND, partner=partner)
        entered = threading.Event()
        release = threading.Event()
        real_enqueue = bulk_sync.enqueue_many

        def delayed_enqueue(resource, ids, bulk_run):
            entered.set()
            if not release.wait(10):
                raise RuntimeError('Preparation test did not release the worker')
            return real_enqueue(resource, ids, bulk_run)

        def worker():
            try:
                prepare_run(run.pk)
            finally:
                connections.close_all()

        with patch.object(bulk_sync, 'enqueue_many', side_effect=delayed_enqueue), \
                ThreadPoolExecutor(max_workers=2) as pool:
            first = pool.submit(worker)
            try:
                self.assertTrue(entered.wait(10))
                pool.submit(worker).result(timeout=5)
            finally:
                release.set()
            first.result(timeout=10)
        run.refresh_from_db()
        self.assertEqual(run.preparation, 'ready')
        self.assertEqual(run.events.count(), 1)
