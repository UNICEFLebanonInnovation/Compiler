"""Compatibility between the incoming photo/referral models and the sync contract."""
import hashlib
import io
from datetime import timedelta
from tempfile import TemporaryDirectory
from types import SimpleNamespace
from unittest.mock import patch
import uuid

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import call_command
from django.test import TestCase, override_settings
from django.utils import timezone
from PIL import Image

from student_registration.child.models import Child
from student_registration.mscc.models import Registration, Referral
from student_registration.schools.models import PublicSchool
from student_registration.students.models import Student
from .. import photos
from ..models import SourcePhotoFingerprint, SyncEvent
from ..serializers import key_school, serialize_referral


@override_settings(DATASYNC_ENABLED=False)
class RegistrationPhotoCompatibilityTests(TestCase):
    def setUp(self):
        self.folder = TemporaryDirectory()
        self.addCleanup(self.folder.cleanup)
        storage = override_settings(MEDIA_ROOT=self.folder.name, STORAGES={
            'default': {'BACKEND': 'django.core.files.storage.FileSystemStorage',
                        'OPTIONS': {'location': self.folder.name}},
            'staticfiles': {'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage'},
        })
        storage.enable()
        self.addCleanup(storage.disable)
        self.child = Child.objects.create(first_name='Synthetic photo compatibility child')
        self.registration = Registration.objects.create(child=self.child, type='Core-Package')

    def image(self, color):
        output = io.BytesIO()
        Image.new('RGB', (2, 2), color).save(output, 'PNG')
        return output.getvalue()

    def put(self, instance, attribute, color):
        content = self.image(color)
        setattr(instance, attribute, SimpleUploadedFile(color + '.png', content, content_type='image/png'))
        instance.save()
        return content

    def prepare(self, allow_reuse=False, force_read=False):
        event = SimpleNamespace(source_id=str(self.registration.pk), event_id=uuid.uuid4(), created=timezone.now())
        with self.settings(DATASYNC_ENABLED=True):
            return photos.prepare_photo(self.child.pk, event, allow_reuse=allow_reuse, force_read=force_read)

    def legacy(self):
        student = Student.objects.create(first_name='Synthetic legacy photo')
        content = self.put(student, 'std_image', 'blue')
        self.registration.student_old = student.pk
        self.registration.save()
        return student, content

    def test_registration_picture_works_without_student_link(self):
        content = self.put(self.registration, 'profile_picture', 'red')
        descriptor, stream = self.prepare()
        self.assertEqual(stream.read(), content)
        stream.close()
        self.assertEqual(descriptor['sha256'], hashlib.sha256(content).hexdigest())
        self.assertNotIn('url', descriptor)

    def test_registration_picture_takes_precedence_over_legacy_student(self):
        self.legacy()
        content = self.put(self.registration, 'profile_picture', 'red')
        descriptor, stream = self.prepare()
        self.assertEqual(stream.read(), content)
        stream.close()

    def test_unset_registration_picture_keeps_legacy_fallback(self):
        student, content = self.legacy()
        self.registration.refresh_from_db()
        self.assertFalse(self.registration.profile_picture)
        self.assertFalse(self.registration.photo_sync_cleared)
        descriptor, stream = self.prepare()
        self.assertEqual(stream.read(), content)
        stream.close()

    def test_explicit_registration_clear_does_not_restore_legacy_picture(self):
        self.legacy()
        self.put(self.registration, 'profile_picture', 'red')
        self.registration.profile_picture = ''
        self.registration.save()
        descriptor, stream = self.prepare()
        self.assertEqual(descriptor['action'], 'remove')
        self.assertIsNone(stream)

    def test_shared_child_uses_one_deterministic_registration_picture(self):
        self.put(self.registration, 'profile_picture', 'red')
        other = Registration.objects.create(child=self.child, type='Walk-in')
        expected = self.put(other, 'profile_picture', 'green')
        Registration.objects.filter(pk=self.registration.pk).update(modified=timezone.now() - timedelta(days=1))
        descriptor, stream = self.prepare()
        self.assertEqual(stream.read(), expected)
        stream.close()
        self.assertEqual(descriptor['sha256'], hashlib.sha256(expected).hexdigest())

    def test_photo_selection_breaks_equal_timestamp_ties_by_primary_key(self):
        self.put(self.registration, 'profile_picture', 'red')
        other = Registration.objects.create(child=self.child, type='Core-Package')
        expected = self.put(other, 'profile_picture', 'green')
        Registration.objects.filter(child=self.child).update(modified=timezone.now())
        descriptor, stream = self.prepare()
        self.assertEqual(stream.read(), expected)
        stream.close()

    def test_latest_clear_overrides_an_older_registration_picture(self):
        self.put(self.registration, 'profile_picture', 'red')
        clear = Registration.objects.create(child=self.child, type='Walk-in')
        self.put(clear, 'profile_picture', 'blue')
        clear.profile_picture = ''
        clear.save()
        Registration.objects.filter(pk=self.registration.pk).update(modified=clear.modified - timedelta(days=1))
        descriptor, stream = self.prepare()
        self.assertEqual(descriptor['action'], 'remove')
        self.assertIsNone(stream)

    def test_tls_picture_cannot_override_a_makani_child_picture(self):
        expected = self.put(self.registration, 'profile_picture', 'red')
        tls = Registration.objects.create(child=self.child, type='TLS')
        self.put(tls, 'profile_picture', 'green')
        descriptor, stream = self.prepare()
        self.assertEqual(stream.read(), expected)
        stream.close()

    def test_explicit_picture_does_not_depend_on_conflicting_legacy_links(self):
        student, _ = self.legacy()
        Registration.objects.create(child=self.child, type='Core-Package', student_old=student.pk + 10)
        expected = self.put(self.registration, 'profile_picture', 'red')
        descriptor, stream = self.prepare()
        self.assertEqual(stream.read(), expected)
        stream.close()

    def test_registration_fingerprint_keeps_legacy_namespace_and_reuses_bytes(self):
        expected = self.put(self.registration, 'profile_picture', 'red')
        SourcePhotoFingerprint.objects.create(student_id=str(self.registration.pk),
            storage_name='legacy.png', source_version='legacy', sha256='f' * 64, size=10)
        descriptor, stream = self.prepare(allow_reuse=True)
        stream.close()
        cached = SourcePhotoFingerprint.objects.get(student_id='registration:' + str(self.registration.pk))
        self.assertEqual(cached.sha256, hashlib.sha256(expected).hexdigest())
        self.assertEqual(SourcePhotoFingerprint.objects.get(student_id=str(self.registration.pk)).sha256, 'f' * 64)
        storage = self.registration.profile_picture.storage
        with patch.object(storage, 'open', side_effect=AssertionError('Unchanged image downloaded again')):
            descriptor, stream = self.prepare(allow_reuse=True)
        self.assertEqual(descriptor['action'], 'verify')
        self.assertIsNone(stream)

    def test_unreadable_registration_photo_is_retryable_without_exposing_path(self):
        self.put(self.registration, 'profile_picture', 'red')
        with patch.object(self.registration.profile_picture.storage, 'open',
                          side_effect=OSError('private-storage-credential')):
            with self.assertRaisesRegex(photos.SyncTransportError, '^Cannot read source photo storage$'):
                self.prepare()

    def test_registration_photo_edit_uses_the_existing_outbox(self):
        with self.settings(DATASYNC_ENABLED=True):
            self.put(self.registration, 'profile_picture', 'red')
        events = list(SyncEvent.objects.values_list('resource', 'source_id'))
        self.assertEqual(events, [('mscc.registration', str(self.registration.pk))])

    def test_partial_photo_clear_persists_until_a_replacement_is_uploaded(self):
        self.legacy()
        self.put(self.registration, 'profile_picture', 'red')
        self.registration.profile_picture = ''
        self.registration.save(update_fields=['profile_picture'])
        self.registration.refresh_from_db()
        self.assertTrue(self.registration.photo_sync_cleared)
        self.registration.have_labour = 'No'
        self.registration.save(update_fields=['have_labour'])
        descriptor, stream = self.prepare()
        self.assertEqual(descriptor['action'], 'remove')
        self.put(self.registration, 'profile_picture', 'green')
        self.registration.refresh_from_db()
        self.assertFalse(self.registration.photo_sync_cleared)

    def test_private_clear_marker_is_not_a_new_nfe_contract_field(self):
        from ..serializers import serialize_registration
        self.assertNotIn('photo_sync_cleared', serialize_registration(self.registration)['fields'])

    def test_photo_audit_recognizes_registration_picture_without_legacy_link(self):
        self.put(self.registration, 'profile_picture', 'red')
        output = io.StringIO()
        call_command('datasync_backfill_photos', dry_run=True, stdout=output)
        self.assertIn("'ready': 1", output.getvalue())
        self.assertIn("'missing_link': 0", output.getvalue())
        self.assertFalse(SyncEvent.objects.exists())

    def test_photo_backfill_queues_each_makani_registration_once_for_shared_child(self):
        self.put(self.registration, 'profile_picture', 'red')
        other = Registration.objects.create(child=self.child, type='Core-Package')
        Registration.objects.create(child=self.child, type='TLS')
        output = io.StringIO()
        with self.settings(DATASYNC_ENABLED=True):
            call_command('datasync_backfill_photos', stdout=output)
        self.assertEqual(set(SyncEvent.objects.values_list('source_id', flat=True)),
                         {str(self.registration.pk), str(other.pk)})
        self.assertEqual(SyncEvent.objects.count(), 2)
        self.assertIn("'ready': 1", output.getvalue())

    def test_photo_backfill_does_not_restore_legacy_picture_after_explicit_clear(self):
        self.legacy()
        self.put(self.registration, 'profile_picture', 'red')
        self.registration.profile_picture = ''
        self.registration.save()
        output = io.StringIO()
        with self.settings(DATASYNC_ENABLED=True):
            call_command('datasync_backfill_photos', stdout=output)
        self.assertFalse(SyncEvent.objects.exists())
        self.assertIn("'no_photo': 1", output.getvalue())


@override_settings(DATASYNC_ENABLED=False)
class ReferralCompatibilityTests(TestCase):
    def test_public_school_is_sent_through_the_existing_school_cerd_key(self):
        school = PublicSchool.objects.create(name='Synthetic ministry school', cerd=12345)
        referral = Referral.objects.create(public_school=school)
        wire = serialize_referral(referral)
        self.assertEqual(wire['referred_school']['number'], '12345')
        self.assertEqual(wire['referred_school']['name'], school.name)
        self.assertNotIn('referred_formal_education', wire['fields'])
        self.assertNotIn('profile_picture', wire['fields'])

    def test_empty_public_school_remains_an_explicit_empty_reference(self):
        self.assertIsNone(serialize_referral(Referral.objects.create())['referred_school'])

    def test_zero_cerd_and_legacy_school_numbers_are_preserved(self):
        school = PublicSchool.objects.create(name='Synthetic zero CERD', cerd=0)
        self.assertEqual(key_school(school)['number'], '0')
        legacy = SimpleNamespace(pk=99, number='00123', name='Legacy school')
        self.assertEqual(key_school(legacy)['number'], '00123')
