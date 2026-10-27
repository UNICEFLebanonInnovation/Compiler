"""The Makani channel must never translate Dirasa or leak TLS child data."""
from unittest.mock import Mock, patch

from django.test import TestCase, override_settings

from student_registration.attendances.models import MSCCAttendance, MSCCAttendanceChild
from student_registration.child.models import Child
from student_registration.locations.models import Center, ProgramStaff
from student_registration.mscc.models import EducationService, Registration, Round
from student_registration.schools.models import PartnerOrganization
from student_registration.students.models import Teacher

from ..bulk_sync import RoundSyncPlan
from ..constants import RESOURCE_ATTENDANCE, RESOURCE_REGISTRATION, RESOURCE_TEACHER
from ..dispatch import build_wire_event, deliver_events
from ..makani_scope import MakaniScopeError, scoped_queryset
from ..models import SyncEvent
from ..outbox import enqueue_delete, enqueue_instance
from ..photos import linked_student_id
from ..serializers import MODEL_FOR_RESOURCE, serialize_teacher


@override_settings(DATASYNC_ENABLED=True)
class MakaniScopeTests(TestCase):
    def setUp(self):
        with override_settings(DATASYNC_ENABLED=False):
            self.partner = PartnerOrganization.objects.create(name='Makani partner')
            self.center = Center.objects.create(name='Makani centre', partner=self.partner)
            self.tls_center = Center.objects.create(name='TLS only', partner=self.partner, is_tls='Yes')
            self.round = Round.objects.create(name='Shared round')
            self.staff = ProgramStaff.objects.create(center=self.center,
                facilitator_name='Facilitator ' + 'long name ' * 15, programs=['BLN'],
                subject=['Education'], gender='Female', weekly_hours_taught=12,
                training_topics=['PSEA'], attendance_training='Yes', is_active_current_round='Yes')
            self.dirasa = Teacher.objects.create(first_name='Dirasa teacher')
            self.child = Child.objects.create(first_name='Makani child')
            self.registration = Registration.objects.create(child=self.child, center=self.center,
                round=self.round, partner=self.partner, type='Core-Package')
            self.tls = Registration.objects.create(child=Child.objects.create(first_name='TLS child'),
                center=self.tls_center, round=self.round, partner=self.partner, type='TLS', student_old=99999)
            self.service = EducationService.objects.create(registration=self.registration)
            self.tls_service = EducationService.objects.create(registration=self.tls)

    def test_teacher_registry_is_program_staff_only(self):
        self.assertIs(MODEL_FOR_RESOURCE[RESOURCE_TEACHER], ProgramStaff)
        self.assertIsNone(enqueue_instance(self.dirasa, deliver=False))

    def test_staff_payload_preserves_full_name_and_distinct_programme_fields(self):
        payload = serialize_teacher(self.staff)
        self.assertEqual(payload['source_model'], 'locations.programstaff')
        self.assertEqual(payload['fields']['facilitator_name'], self.staff.facilitator_name)
        self.assertGreater(len(payload['fields']['facilitator_name']), 64)
        self.assertEqual(payload['fields']['program_staff_details']['programs'], ['BLN'])
        self.assertEqual(payload['fields']['teaching_hours_mscc'], 12)
        self.assertNotIn('round', payload)
        self.assertNotIn('attach_cv', payload['fields'])

    def test_bulk_excludes_tls_registration_services_and_dirasa_teachers(self):
        plan = RoundSyncPlan(self.round, 'all', self.partner)
        self.assertEqual(plan.errors(), [])
        self.assertEqual(set(plan.queries[RESOURCE_TEACHER].values_list('pk', flat=True)), {self.staff.pk})
        self.assertNotIn(self.tls.pk, plan.queries[RESOURCE_REGISTRATION].values_list('pk', flat=True))
        self.assertNotIn(self.tls_service.pk, plan.queries['mscc.education_service'].values_list('pk', flat=True))

    def test_tls_and_unknown_types_are_not_queued_on_individual_save(self):
        with patch('student_registration.datasync.outbox._schedule'):
            for value in ('TLS', 'Dirasa', 'Future programme'):
                self.registration.type = value
                self.registration.save()
        self.assertFalse(SyncEvent.objects.filter(resource=RESOURCE_REGISTRATION).exists())

    def test_historical_blank_and_walkin_types_still_sync(self):
        for value in (None, '', 'Walk-in', 'Walk-in-OOSC', 'Walk-in-In-School'):
            Registration.objects.filter(pk=self.registration.pk).update(type=value)
            self.registration.refresh_from_db()
            self.assertIsNotNone(enqueue_instance(self.registration, deliver=False))

    def test_queued_record_changed_to_tls_is_blocked_before_http_and_photo(self):
        event = enqueue_instance(self.registration, deliver=False)
        Registration.objects.filter(pk=self.registration.pk).update(type='TLS')
        client = Mock()
        with patch('student_registration.datasync.photos.prepare_photo') as photo:
            result = deliver_events([event], client=client)
        self.assertEqual(result['failed'], 1)
        client.push.assert_not_called()
        photo.assert_not_called()

    def test_pending_legacy_teacher_is_not_reinterpreted_as_programstaff(self):
        event = SyncEvent.objects.create(resource='mscc.teacher', source_id=str(self.staff.pk))
        with self.assertRaisesRegex(MakaniScopeError, 'Legacy Dirasa'):
            build_wire_event(event)

    def test_photo_linking_ignores_tls_only_registrations(self):
        self.assertIsNone(linked_student_id(self.tls.child_id))

    def test_mixed_attendance_is_not_partially_published(self):
        with override_settings(DATASYNC_ENABLED=False):
            day = MSCCAttendance.objects.create(center=self.center, round_id=self.round.pk)
            MSCCAttendanceChild.objects.create(attendance_day=day, registration=self.registration, child=self.child)
            MSCCAttendanceChild.objects.create(attendance_day=day, registration=self.tls, child=self.tls.child)
        self.assertFalse(scoped_queryset(RESOURCE_ATTENDANCE).filter(pk=day.pk).exists())
        event = SyncEvent.objects.create(resource=RESOURCE_ATTENDANCE, source_id=str(day.pk))
        with self.assertRaises(MakaniScopeError):
            build_wire_event(event)

    def test_staff_deletion_has_proven_scope_and_stable_source_identity(self):
        with patch('student_registration.datasync.outbox._schedule'):
            event = enqueue_delete(self.staff)
        self.assertEqual(build_wire_event(event)['payload']['scope'], 'makani')
        self.assertEqual(event.resource, 'locations.program_staff')

    def test_tls_delete_does_not_create_a_tombstone(self):
        self.assertIsNone(enqueue_delete(self.tls))

    def test_tls_only_center_is_excluded_but_shared_center_is_allowed(self):
        self.assertFalse(scoped_queryset('locations.center').filter(pk=self.tls_center.pk).exists())
        ProgramStaff.objects.filter(pk=self.staff.pk).update(center=self.tls_center)
        self.assertTrue(scoped_queryset('locations.center').filter(pk=self.tls_center.pk).exists())

    def test_automatic_registration_mismatch_has_a_durable_event_but_cannot_send(self):
        from ..partner_scope import PartnerScopeError
        other = PartnerOrganization.objects.create(name='Other partner')
        self.registration.partner = other
        with patch('student_registration.datasync.outbox._schedule'):
            self.registration.save()
        event = SyncEvent.objects.filter(resource=RESOURCE_REGISTRATION).latest('id')
        with self.assertRaisesRegex(PartnerScopeError, 'different partner'):
            build_wire_event(event)

    def test_automatic_attendance_cannot_send_another_center_or_round(self):
        from ..partner_scope import PartnerScopeError
        with override_settings(DATASYNC_ENABLED=False):
            other_center = Center.objects.create(name='Another centre', partner=self.partner)
            day = MSCCAttendance.objects.create(center=other_center, round_id=self.round.pk)
            MSCCAttendanceChild.objects.create(attendance_day=day, registration=self.registration, child=self.child)
        event = SyncEvent.objects.create(resource=RESOURCE_ATTENDANCE, source_id=str(day.pk))
        with self.assertRaisesRegex(PartnerScopeError, 'different centre'):
            build_wire_event(event)
        MSCCAttendance.objects.filter(pk=day.pk).update(center=self.center, round_id=999999)
        with self.assertRaisesRegex(PartnerScopeError, 'different round'):
            build_wire_event(event)

    def test_automatic_attendance_child_must_match_registration(self):
        from ..partner_scope import PartnerScopeError
        with override_settings(DATASYNC_ENABLED=False):
            day = MSCCAttendance.objects.create(center=self.center, round_id=self.round.pk)
            MSCCAttendanceChild.objects.create(attendance_day=day, registration=self.registration, child=self.tls.child)
        event = SyncEvent.objects.create(resource=RESOURCE_ATTENDANCE, source_id=str(day.pk))
        with self.assertRaisesRegex(PartnerScopeError, 'child differs'):
            build_wire_event(event)
