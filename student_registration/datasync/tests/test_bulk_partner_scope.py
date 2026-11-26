"""Partner isolation must include parents, embedded rows and delayed delivery."""
import uuid
from unittest.mock import Mock, patch

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.test import TestCase, override_settings

from student_registration.attendances.models import MSCCAttendance, MSCCAttendanceChild
from student_registration.child.models import Child
from student_registration.locations.models import Center, ProgramStaff
from student_registration.mscc.models import (
    EducationAssessment, EducationProgrammeAssessment, EducationService, Referral, Registration,
)
from student_registration.schools.models import PartnerOrganization, School
from ..bulk_sync import PlanError, RoundSyncPlan, prepare_run
from ..constants import (
    RESOURCE_ATTENDANCE, RESOURCE_CENTER, RESOURCE_EDUCATION_ASSESSMENT,
    RESOURCE_EDUCATION_SERVICE, RESOURCE_GRADING, RESOURCE_REFERRAL,
    RESOURCE_REGISTRATION, RESOURCE_ROUND, RESOURCE_TEACHER,
)
from ..dispatch import build_wire_event, deliver_events
from ..models import BulkSyncRun, SchoolCenterLink, SyncEvent
from ..partner_scope import PartnerScopeError
from ..serializers import serialize_teacher
from . import test_bulk_sync


@override_settings(DATASYNC_ENABLED=True, DATASYNC_TARGET_URL='https://nfe.test/api/sync/events/',
                   DATASYNC_TARGET_TOKEN='isolated-test-token')
class PartnerBulkTests(TestCase):
    ids = test_bulk_sync.BulkRoundTests.ids

    def setUp(self):
        test_bulk_sync.BulkRoundTests.setUp(self)
        with override_settings(DATASYNC_ENABLED=False):
            self.partner_b = PartnerOrganization.objects.create(name='Bulk partner B')
            self.center_b = Center.objects.create(name='Foreign centre B', partner=self.partner_b)
            self.school_b = School.objects.create(name='Foreign school B', number='PARTNER-B')
            self.partner_b.schools.add(self.school_b)
            self.link_b = SchoolCenterLink.objects.create(school=self.school_b, center=self.center_b)
            self.teacher_b = ProgramStaff.objects.create(facilitator_name='Foreign teacher B', center=self.center_b)
            self.child_b = Child.objects.create(first_name='Foreign child B')
            self.registration_b = Registration.objects.create(
                partner=self.partner_b, center=self.center_b, round=self.round, child=self.child_b)
            self.assessment_b = EducationAssessment.objects.create(registration=self.registration_b)
            self.service_b = EducationService.objects.create(registration=self.registration_b, round=self.round)
            self.grading_b = EducationProgrammeAssessment.objects.create(registration=self.registration_b)
            self.referral_b = Referral.objects.create(registration=self.registration_b)
            self.day_b = MSCCAttendance.objects.create(center=self.center_b, round_id=self.round.pk)
            self.attendance_child_b = MSCCAttendanceChild.objects.create(attendance_day=self.day_b,
                registration=self.registration_b, child=self.child_b)

    def data(self, partner=None, category='all', **changes):
        result = dict(partner=(partner or self.partner).pk, round=self.round.pk,
                      category=category, request_id=str(uuid.uuid4()))
        result.update(changes)
        return result

    def new_partner_run(self, category=RESOURCE_REGISTRATION, **changes):
        values = dict(partner=self.partner, round=self.round, category=category, requested_by=self.user)
        values.update(changes)
        return BulkSyncRun.objects.create(**values)

    def staff(self, assigned=True):
        user = get_user_model().objects.create_user(username='partner-operator',is_staff=True,
                                                    partner=self.partner if assigned else None)
        user.user_permissions.add(*Permission.objects.filter(codename__in=[
            'view_bulksyncrun','add_bulksyncrun','view_partnerorganization','view_round',
            'view_center','view_programstaff','view_registration','view_educationassessment',
        ]))
        self.client.force_login(user)
        return user

    def test_partner_is_required_in_the_plan_and_post(self):
        with self.assertRaisesRegex(PlanError,'Choose a partner'):
            RoundSyncPlan(self.round,'all')
        data = self.data()
        del data['partner']
        self.assertContains(self.client.post(self.url,data),'This field is required')
        self.assertFalse(BulkSyncRun.objects.exists())

    def test_all_categories_exclude_the_other_partner_in_the_same_round(self):
        plan = RoundSyncPlan(self.round,'all',self.partner)
        foreign = {RESOURCE_CENTER:self.center_b,RESOURCE_TEACHER:self.teacher_b,
            RESOURCE_REGISTRATION:self.registration_b,RESOURCE_EDUCATION_ASSESSMENT:self.assessment_b,
            RESOURCE_EDUCATION_SERVICE:self.service_b,RESOURCE_GRADING:self.grading_b,
            RESOURCE_REFERRAL:self.referral_b,RESOURCE_ATTENDANCE:self.day_b}
        self.assertEqual(plan.errors(),[])
        for resource,instance in foreign.items():
            self.assertNotIn(instance.pk,self.ids(plan,resource),resource)
        self.assertIn(self.round.pk,self.ids(plan,RESOURCE_ROUND))

    def test_selecting_partner_b_excludes_partner_a_and_includes_its_own_parents(self):
        plan = RoundSyncPlan(self.round,RESOURCE_EDUCATION_ASSESSMENT,self.partner_b)
        self.assertEqual(self.ids(plan,RESOURCE_EDUCATION_ASSESSMENT),{self.assessment_b.pk})
        self.assertEqual(self.ids(plan,RESOURCE_REGISTRATION),{self.registration_b.pk})
        self.assertEqual(self.ids(plan,RESOURCE_CENTER),{self.center_b.pk})
        self.assertNotIn(self.assessment.pk,self.ids(plan,RESOURCE_EDUCATION_ASSESSMENT))

    def test_global_categories_are_partner_scoped_and_do_not_need_a_round(self):
        plan = RoundSyncPlan(None,[RESOURCE_CENTER,RESOURCE_TEACHER],self.partner)
        self.assertEqual(self.ids(plan,RESOURCE_CENTER),{self.center.pk,self.other_center.pk})
        self.assertEqual(self.ids(plan,RESOURCE_TEACHER),{self.teacher.pk,self.other_teacher.pk})
        self.assertIsNone(plan.round)

    def test_another_partners_unmapped_teacher_does_not_block_the_selection(self):
        self.link_b.delete()
        self.assertEqual(RoundSyncPlan(None,RESOURCE_TEACHER,self.partner).errors(),[])
        self.assertEqual(RoundSyncPlan(None,RESOURCE_TEACHER,self.partner_b).errors(),[])

    def test_cross_partner_registration_centre_blocks_queue_preparation(self):
        Registration.objects.filter(pk=self.registration.pk).update(center=self.center_b)
        run = self.new_partner_run()
        prepare_run(run.pk)
        run.refresh_from_db()
        self.assertEqual(run.preparation,'failed')
        self.assertIn('another partner',run.last_error)
        self.assertFalse(run.events.exists())

    def test_cross_partner_attendance_is_not_silently_filtered_or_sent(self):
        with override_settings(DATASYNC_ENABLED=False):
            MSCCAttendanceChild.objects.create(attendance_day=self.day,
                registration=self.registration_b,child=self.child_b)
        run = self.new_partner_run(RESOURCE_ATTENDANCE)
        prepare_run(run.pk)
        run.refresh_from_db()
        self.assertEqual(run.preparation,'failed')
        self.assertIn('another partner',run.last_error)
        self.assertFalse(run.events.exists())

    def test_attendance_child_must_match_its_registration(self):
        MSCCAttendanceChild.objects.filter(attendance_day=self.day).update(child=self.child_b)
        run = self.new_partner_run(RESOURCE_ATTENDANCE)
        prepare_run(run.pk)
        run.refresh_from_db()
        self.assertEqual(run.preparation,'failed')
        self.assertIn('child differs',run.last_error)

    def test_form_identity_includes_the_selected_partner(self):
        data = self.data(category=RESOURCE_CENTER)
        self.assertEqual(self.client.post(self.url,data).status_code,302)
        data['partner']=self.partner_b.pk
        self.assertEqual(self.client.post(self.url,data).status_code,403)
        self.assertEqual(BulkSyncRun.objects.get().partner_id,self.partner.pk)

    def test_selection_keeps_partner_and_does_not_expose_records(self):
        Registration.objects.bulk_create([Registration(partner=self.partner,center=self.center,round=self.round)
                                          for _ in range(52)])
        response = self.client.get(self.url,self.data(category=RESOURCE_REGISTRATION,page=2))
        self.assertEqual(response.status_code,200)
        self.assertEqual(response.context['form'].cleaned_data['partner'].pk,self.partner.pk)
        self.assertNotContains(response,self.child_b.first_name)

    def test_progress_and_history_retain_the_selected_partner(self):
        run = self.new_partner_run()
        response = self.client.get(self.url,{'run':run.pk})
        self.assertEqual(response.context['form']['partner'].value(),self.partner.pk)
        self.assertIn(self.partner.name,run.scope_label)
        self.assertContains(response,self.partner.name)

    def test_partner_assigned_operator_cannot_choose_another_partner(self):
        self.staff()
        response = self.client.get(self.url)
        self.assertNotContains(response,self.partner_b.name)
        self.assertEqual(self.client.post(self.url,self.data(self.partner_b,RESOURCE_CENTER)).status_code,200)
        self.assertFalse(BulkSyncRun.objects.exists())
        self.assertEqual(self.client.post(self.url,self.data(category=RESOURCE_CENTER)).status_code,302)

    def test_partner_model_permission_is_required(self):
        user = self.staff()
        user.user_permissions.remove(Permission.objects.get(codename='view_partnerorganization'))
        response = self.client.post(self.url,self.data(category=RESOURCE_CENTER))
        self.assertEqual(response.status_code,200)
        self.assertFalse(BulkSyncRun.objects.exists())

    def test_partner_assignment_is_rechecked_when_reading_a_saved_run(self):
        user = self.staff()
        run = self.new_partner_run(partner=self.partner_b,requested_by=user)
        self.assertEqual(self.client.get(self.url,{'run':run.pk}).status_code,404)

    def test_legacy_waiting_run_without_partner_cannot_queue_everyone(self):
        run = self.new_partner_run(partner=None)
        prepare_run(run.pk)
        run.refresh_from_db()
        self.assertEqual(run.preparation,'failed')
        self.assertIn('partner',run.last_error)
        self.assertFalse(run.events.exists())

    def test_legacy_completed_run_remains_readable_by_superuser(self):
        run = self.new_partner_run(partner=None,preparation='ready')
        self.assertContains(self.client.get(self.url,{'run':run.pk}),'All partners (legacy)')

    def test_requester_partner_change_before_worker_preparation_blocks_queueing(self):
        user = self.staff()
        run = self.new_partner_run(requested_by=user)
        get_user_model().objects.filter(pk=user.pk).update(partner=self.partner_b)
        prepare_run(run.pk)
        run.refresh_from_db()
        self.assertEqual(run.preparation,'failed')
        self.assertFalse(run.events.exists())

    def test_registration_moved_after_queue_is_blocked_before_http(self):
        run = self.new_partner_run()
        prepare_run(run.pk)
        event = run.events.get(resource=RESOURCE_REGISTRATION,source_id=str(self.registration.pk))
        Registration.objects.filter(pk=self.registration.pk).update(partner=self.partner_b)
        with self.assertRaises(PartnerScopeError):
            build_wire_event(event)
        client = Mock()
        result = deliver_events([event],client=client)
        client.push.assert_not_called()
        self.assertEqual(result['failed'],1)

    def test_teacher_mapping_moved_after_queue_is_blocked_before_http(self):
        run = self.new_partner_run(RESOURCE_TEACHER,round=None)
        prepare_run(run.pk)
        event = run.events.get(resource=RESOURCE_TEACHER,source_id=str(self.teacher.pk))
        ProgramStaff.objects.filter(pk=self.teacher.pk).update(center=self.center_b)
        with self.assertRaises(PartnerScopeError):
            build_wire_event(event)

    def test_foreign_attendance_added_after_queue_is_blocked_before_http(self):
        run = self.new_partner_run(RESOURCE_ATTENDANCE)
        prepare_run(run.pk)
        event = run.events.get(resource=RESOURCE_ATTENDANCE,source_id=str(self.day.pk))
        with override_settings(DATASYNC_ENABLED=False):
            MSCCAttendanceChild.objects.create(attendance_day=self.day,registration=self.registration_b,child=self.child_b)
        with self.assertRaises(PartnerScopeError):
            build_wire_event(event)

    def test_serialized_teacher_reference_is_checked_after_building_payload(self):
        run = self.new_partner_run(RESOURCE_TEACHER,round=None)
        prepare_run(run.pk)
        event = run.events.get(resource=RESOURCE_TEACHER,source_id=str(self.teacher.pk))
        payload = serialize_teacher(self.teacher_b)
        with patch('student_registration.datasync.dispatch.serialize',return_value=payload):
            with self.assertRaises(PartnerScopeError):
                build_wire_event(event)

    def test_normal_non_bulk_events_keep_the_existing_sync_behavior(self):
        event = SyncEvent.objects.create(resource=RESOURCE_REGISTRATION,source_id=str(self.registration_b.pk))
        wire = build_wire_event(event)
        self.assertEqual(wire['payload']['partner']['source_id'],self.partner_b.pk)

    def test_requester_access_revoked_after_queue_blocks_delivery(self):
        user = self.staff()
        run = self.new_partner_run(requested_by=user)
        prepare_run(run.pk)
        event = run.events.get(resource=RESOURCE_REGISTRATION,source_id=str(self.registration.pk))
        get_user_model().objects.filter(pk=user.pk).update(is_active=False)
        with self.assertRaises(PartnerScopeError):
            build_wire_event(event)

    def test_requester_partner_changed_after_queue_blocks_cached_related_objects(self):
        user = self.staff()
        run = self.new_partner_run(requested_by=user)
        prepare_run(run.pk)
        event = run.events.get(resource=RESOURCE_REGISTRATION,source_id=str(self.registration.pk))
        get_user_model().objects.filter(pk=user.pk).update(partner=self.partner_b)
        with self.assertRaises(PartnerScopeError):
            build_wire_event(event)

    def test_each_valid_partner_event_builds_its_original_contract(self):
        run = self.new_partner_run('all')
        prepare_run(run.pk)
        run.refresh_from_db()
        self.assertEqual(run.preparation,'ready')
        for event in run.events.all():
            with self.subTest(resource=event.resource):
                self.assertEqual(build_wire_event(event)['resource'],event.resource)

    def test_legacy_queued_event_cannot_continue_a_partnerless_delivery(self):
        run = self.new_partner_run(partner=None,preparation='ready')
        event = SyncEvent.objects.create(bulk_run=run,resource=RESOURCE_CENTER,source_id=str(self.center.pk))
        with self.assertRaisesRegex(PartnerScopeError,'no partner'):
            build_wire_event(event)

    def test_history_for_selected_partner_does_not_show_another_partners_run(self):
        own = self.new_partner_run()
        foreign = self.new_partner_run(partner=self.partner_b)
        response = self.client.get(self.url,self.data(category=RESOURCE_REGISTRATION))
        self.assertContains(response,'?run='+str(own.pk))
        self.assertNotContains(response,'?run='+str(foreign.pk))
