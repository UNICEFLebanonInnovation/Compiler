# -*- coding: utf-8 -*-
"""Tests for change capture, payload building and delivery."""

from __future__ import unicode_literals, absolute_import, division

from django.test import TestCase, override_settings
from django.utils import timezone

from student_registration.attendances.models import (
    MSCCAttendance,
    MSCCAttendanceChild,
)
from student_registration.child.models import Child
from student_registration.clm.models import Disability
from student_registration.locations.models import Center
from student_registration.mscc.models import (
    EducationService,
    Referral,
    Registration,
    Round,
)
from student_registration.schools.models import CLMRound, PartnerOrganization, School
from student_registration.students.models import Nationality, Teacher, Training

from ..client import SyncTransportError
from ..constants import (
    OPERATION_DELETE,
    OPERATION_UPSERT,
    RESOURCE_ATTENDANCE,
    RESOURCE_CENTER,
    RESOURCE_REGISTRATION,
    RESOURCE_TEACHER,
)
from ..dispatch import build_wire_event, deliver_events, due_events, flush_outbox
from ..models import (
    STATUS_ABANDONED,
    STATUS_FAILED,
    STATUS_PENDING,
    STATUS_SENT,
    SchoolCenterLink,
    SyncEvent,
)
from ..serializers import serialize_teacher


class RecordingClient(object):
    """Stands in for :class:`~...client.SyncClient` and applies everything."""

    def __init__(self, status='applied', detail='', conflict=False, error=None):
        self.batches = []
        self.status = status
        self.detail = detail
        self.conflict = conflict
        self.error = error

    def push(self, events):
        if self.error:
            raise self.error
        self.batches.append(events)
        return {
            'applied': len(events),
            'results': [
                {
                    'event_id': item['event_id'],
                    'resource': item['resource'],
                    'source_id': item['source_id'],
                    'status': self.status,
                    'detail': self.detail,
                    'local_id': 900 + index,
                    'conflict': self.conflict,
                    'retryable': False,
                    'ignored_fields': [],
                }
                for index, item in enumerate(events)
            ],
        }


@override_settings(DATASYNC_ENABLED=True, DATASYNC_TARGET_URL='https://bma.test/api/sync/events/',
                   DATASYNC_TARGET_TOKEN='test-token')
class CaptureTests(TestCase):
    """Saving a replicated record must queue exactly one push."""

    def test_saving_a_registration_queues_an_upsert(self):
        registration = Registration.objects.create(have_labour='No')

        event = SyncEvent.objects.get(resource=RESOURCE_REGISTRATION)
        self.assertEqual(event.source_id, str(registration.pk))
        self.assertEqual(event.operation, OPERATION_UPSERT)
        self.assertEqual(event.status, STATUS_PENDING)

    def test_repeated_saves_collapse_into_one_pending_event(self):
        registration = Registration.objects.create(have_labour='No')
        registration.have_labour = 'Yes - Morning'
        registration.save()
        registration.have_labour = 'Yes - Full Day'
        registration.save()

        self.assertEqual(
            SyncEvent.objects.filter(resource=RESOURCE_REGISTRATION).count(), 1
        )

    def test_a_failed_event_is_revived_by_a_new_save(self):
        registration = Registration.objects.create(have_labour='No')
        event = SyncEvent.objects.get(resource=RESOURCE_REGISTRATION)
        event.status = STATUS_FAILED
        event.next_attempt = timezone.now() + timezone.timedelta(hours=1)
        event.save()

        registration.have_labour = 'Yes - Morning'
        registration.save()

        event.refresh_from_db()
        self.assertEqual(event.status, STATUS_PENDING)
        self.assertIsNone(event.next_attempt)

    def test_deleting_a_registration_queues_a_delete(self):
        registration = Registration.objects.create(have_labour='No')
        source_id = str(registration.pk)
        SyncEvent.objects.all().delete()

        registration.delete()

        event = SyncEvent.objects.get()
        self.assertEqual(event.operation, OPERATION_DELETE)
        self.assertEqual(event.source_id, source_id)

    def test_editing_a_child_republishes_its_registrations(self):
        child = Child.objects.create(first_name='Lina', last_name='Haddad')
        registration = Registration.objects.create(child=child)
        SyncEvent.objects.all().delete()

        child.first_name = 'Lina-Maria'
        child.save()

        event = SyncEvent.objects.get(resource=RESOURCE_REGISTRATION)
        self.assertEqual(event.source_id, str(registration.pk))

    def test_editing_an_attendance_row_republishes_the_day(self):
        center = Center.objects.create(name='Makani One', p_code='LB-01')
        day = MSCCAttendance.objects.create(center=center, attendance_date='2026-03-02')
        registration = Registration.objects.create()
        SyncEvent.objects.all().delete()

        MSCCAttendanceChild.objects.create(
            attendance_day=day, registration=registration, attended='Yes'
        )

        event = SyncEvent.objects.get(resource=RESOURCE_ATTENDANCE)
        self.assertEqual(event.source_id, str(day.pk))

    def test_changing_teacher_trainings_republishes_the_teacher(self):
        teacher = Teacher.objects.create(first_name='Rana')
        SyncEvent.objects.all().delete()

        teacher.trainings.add(Training.objects.create(name='Numeracy'))

        event = SyncEvent.objects.get(resource=RESOURCE_TEACHER)
        self.assertEqual(event.source_id, str(teacher.pk))

    @override_settings(DATASYNC_ENABLED=False)
    def test_nothing_is_queued_while_replication_is_off(self):
        Registration.objects.create(have_labour='No')

        self.assertEqual(SyncEvent.objects.count(), 0)


@override_settings(DATASYNC_ENABLED=True)
class PayloadTests(TestCase):
    """Payloads must be expressed in natural keys, never local ids."""

    def test_registration_payload_uses_natural_keys(self):
        partner = PartnerOrganization.objects.create(name='Partner One')
        center = Center.objects.create(
            name='Makani Tripoli', p_code='LB-0301', partner=partner
        )
        round_object = Round.objects.create(name='2026 Round A', year=2026)
        child = Child.objects.create(
            first_name='Lina', last_name='Haddad', unicef_id='UNI-900'
        )
        registration = Registration.objects.create(
            child=child, center=center, round=round_object, partner=partner,
            have_labour='No',
        )

        event = SyncEvent.objects.get(resource=RESOURCE_REGISTRATION)
        payload = build_wire_event(event)['payload']

        self.assertEqual(payload['center']['p_code'], 'LB-0301')
        self.assertEqual(payload['center']['partner']['name'], 'Partner One')
        self.assertEqual(payload['round']['name'], '2026 Round A')
        self.assertEqual(payload['child']['fields']['unicef_id'], 'UNI-900')
        self.assertEqual(payload['fields']['have_labour'], 'No')
        self.assertNotIn('center', payload['fields'])
        self.assertNotIn('owner', payload['fields'])
        self.assertEqual(payload['child']['source_id'], child.pk)
        self.assertEqual(event.source_id, str(registration.pk))

    def test_child_lookups_travel_by_name(self):
        nationality = Nationality.objects.create(name='Lebanese', name_en='Lebanese')
        disability = Disability.objects.create(name='None')
        child = Child.objects.create(
            first_name='Lina', nationality=nationality, disability=disability
        )
        Registration.objects.create(child=child)

        event = SyncEvent.objects.get(resource=RESOURCE_REGISTRATION)
        payload = build_wire_event(event)['payload']

        self.assertEqual(payload['child']['nationality']['name'], 'Lebanese')
        self.assertEqual(payload['child']['disability']['name'], 'None')

    def test_attendance_payload_carries_its_child_rows(self):
        center = Center.objects.create(name='Makani One', p_code='LB-01')
        round_object = Round.objects.create(name='2026 Round A')
        day = MSCCAttendance.objects.create(
            center=center, attendance_date='2026-03-02', round_id=round_object.pk
        )
        registration = Registration.objects.create()
        MSCCAttendanceChild.objects.create(
            attendance_day=day, registration=registration, attended='Yes'
        )

        event = SyncEvent.objects.filter(resource=RESOURCE_ATTENDANCE).first()
        payload = build_wire_event(event)['payload']

        self.assertEqual(payload['round']['name'], '2026 Round A')
        self.assertNotIn('round_id', payload['fields'])
        self.assertEqual(len(payload['children']), 1)
        self.assertEqual(
            payload['children'][0]['registration']['source_id'], registration.pk
        )

    def test_deleted_record_produces_no_payload(self):
        registration = Registration.objects.create()
        upsert = SyncEvent.objects.get(
            resource=RESOURCE_REGISTRATION, operation=OPERATION_UPSERT
        )
        registration.delete()

        self.assertIsNone(build_wire_event(upsert))


@override_settings(DATASYNC_ENABLED=True)
class TeacherMappingTests(TestCase):
    """The Compiler's Dirasa teacher becomes BMA-NFE's centre teacher."""

    def setUp(self):
        self.school = School.objects.create(name='Some School', number='12345')
        self.teacher = Teacher.objects.create(
            first_name='Rana',
            father_name='Sami',
            last_name='Khoury',
            sex='Female',
            birthday_year='1990',
            birthday_month='7',
            birthday_day='3',
            school=self.school,
            teacher_assignment='Private and Dirasa',
            teaching_hours_dirasa=12,
            teaching_hours_private_school=8,
        )

    def test_birthday_parts_become_a_single_date(self):
        payload = serialize_teacher(self.teacher)

        self.assertEqual(payload['fields']['birthdate'], '1990-07-03')

    def test_incomplete_birthday_is_left_empty(self):
        self.teacher.birthday_day = None
        payload = serialize_teacher(self.teacher)

        self.assertIsNone(payload['fields']['birthdate'])

    def test_dirasa_vocabulary_is_translated(self):
        payload = serialize_teacher(self.teacher)

        self.assertEqual(payload['fields']['teacher_assignment'], 'Private and Makani')
        self.assertEqual(payload['fields']['teaching_hours_mscc'], 12)
        self.assertEqual(payload['fields']['teaching_hours_private_school'], 8)

    def test_centre_comes_from_the_school_link(self):
        payload = serialize_teacher(self.teacher)
        self.assertIsNone(payload['center'])

        center = Center.objects.create(name='Makani One', p_code='LB-01')
        SchoolCenterLink.objects.create(school=self.school, center=center)

        payload = serialize_teacher(self.teacher)
        self.assertEqual(payload['center']['p_code'], 'LB-01')

    def test_round_travels_by_name(self):
        self.teacher.round = CLMRound.objects.create(name='2026 Round A')
        payload = serialize_teacher(self.teacher)

        self.assertEqual(payload['round']['name'], '2026 Round A')


@override_settings(DATASYNC_ENABLED=True, DATASYNC_TARGET_URL='https://bma.test/api/sync/events/',
                   DATASYNC_TARGET_TOKEN='test-token')
class DeliveryTests(TestCase):
    """What happens to an outbox row once BMA-NFE answers."""

    def test_successful_delivery_marks_the_event_sent(self):
        Registration.objects.create()
        client = RecordingClient(detail='ok')

        counts = deliver_events(list(SyncEvent.objects.all()), client=client)

        self.assertEqual(counts['sent'], 1)
        event = SyncEvent.objects.get()
        self.assertEqual(event.status, STATUS_SENT)
        self.assertEqual(event.remote_id, '900')
        self.assertIsNotNone(event.sent_at)

    def test_a_conflict_reported_by_bma_is_recorded(self):
        Registration.objects.create()
        client = RecordingClient(conflict=True, detail='1 field overwritten')

        deliver_events(list(SyncEvent.objects.all()), client=client)

        event = SyncEvent.objects.get()
        self.assertTrue(event.conflict)
        self.assertEqual(event.remote_detail, '1 field overwritten')

    def test_transport_failure_schedules_a_retry(self):
        Registration.objects.create()
        client = RecordingClient(error=SyncTransportError('connection refused'))

        counts = deliver_events(list(SyncEvent.objects.all()), client=client)

        self.assertEqual(counts['failed'], 1)
        event = SyncEvent.objects.get()
        self.assertEqual(event.status, STATUS_FAILED)
        self.assertEqual(event.attempts, 1)
        self.assertIsNotNone(event.next_attempt)
        self.assertIn('connection refused', event.last_error)

    def test_an_event_not_yet_due_is_left_alone(self):
        Registration.objects.create()
        SyncEvent.objects.update(
            status=STATUS_FAILED,
            next_attempt=timezone.now() + timezone.timedelta(hours=1),
        )

        self.assertEqual(due_events(), [])

    @override_settings(DATASYNC_MAX_ATTEMPTS=1)
    def test_an_event_is_abandoned_once_the_budget_runs_out(self):
        Registration.objects.create()
        client = RecordingClient(error=SyncTransportError('still down'))

        deliver_events(list(SyncEvent.objects.all()), client=client)

        event = SyncEvent.objects.get()
        self.assertEqual(event.status, STATUS_ABANDONED)
        self.assertIsNone(event.next_attempt)

    def test_rejected_event_is_retried_when_bma_says_so(self):
        Registration.objects.create()
        client = RecordingClient()
        client.push = lambda events: {
            'results': [{
                'event_id': events[0]['event_id'],
                'status': 'failed',
                'detail': 'registration #7 has not been replicated yet',
                'retryable': True,
            }],
        }

        deliver_events(list(SyncEvent.objects.all()), client=client)

        event = SyncEvent.objects.get()
        self.assertEqual(event.status, STATUS_FAILED)
        self.assertIsNotNone(event.next_attempt)

    def test_flush_sends_parents_before_children(self):
        center = Center.objects.create(name='Makani One', p_code='LB-01')
        registration = Registration.objects.create(center=center)
        EducationService.objects.create(registration=registration)
        Referral.objects.create(registration=registration)
        client = RecordingClient()

        flush_outbox(client=client)

        sent = [item['resource'] for batch in client.batches for item in batch]
        self.assertLess(sent.index(RESOURCE_CENTER), sent.index(RESOURCE_REGISTRATION))
        self.assertLess(
            sent.index(RESOURCE_REGISTRATION),
            sent.index('mscc.education_service'),
        )
        self.assertEqual(SyncEvent.objects.exclude(status=STATUS_SENT).count(), 0)
