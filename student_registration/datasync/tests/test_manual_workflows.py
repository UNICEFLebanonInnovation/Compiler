"""Regressions found while exercising normal sync entry forms."""
from django.contrib.messages.storage.fallback import FallbackStorage
from django.test import RequestFactory, TestCase, override_settings

from student_registration.mscc.education_form import EducationAssessmentForm
from student_registration.mscc.models import EducationAssessment, Registration
from ..models import SyncEvent


@override_settings(DATASYNC_ENABLED=True)
class AssessmentFormSaveTests(TestCase):
    def setUp(self):
        with override_settings(DATASYNC_ENABLED=False):
            self.registration = Registration.objects.create()

    def form(self, **changes):
        data = {'participation': 'No Absence', 'post_test_done': 'No', 'school_year_completed': 'No',
                'post_attended_arabic': 'No', 'post_attended_language': 'No', 'post_attended_math': 'No',
                'post_arabic_grade': '', 'post_language_grade': '', 'post_math_grade': ''}
        data.update(changes)
        request = RequestFactory().post('/assessment/', data)
        request.session = {}
        request._messages = FallbackStorage(request)
        return EducationAssessmentForm(data, request=request, registry=self.registration.pk), request

    def test_optional_blank_grades_create_one_complete_record_and_one_sync_event(self):
        form, request = self.form()
        self.assertTrue(form.is_valid(), form.errors)
        assessment = form.save(request=request, registry=self.registration.pk)
        self.assertEqual(EducationAssessment.objects.count(), 1)
        self.assertEqual((assessment.post_arabic_grade, assessment.post_language_grade, assessment.post_math_grade), (0, 0, 0))
        self.assertEqual(SyncEvent.objects.filter(resource='mscc.education_assessment').count(), 1)

    def test_invalid_grade_cannot_leave_a_partial_record_or_sync_event(self):
        form, request = self.form(post_arabic_grade='not a number')
        self.assertFalse(form.is_valid())
        with self.assertRaises(ValueError):
            form.save(request=request, registry=self.registration.pk)
        self.assertFalse(EducationAssessment.objects.exists())
        self.assertFalse(SyncEvent.objects.exists())

    def test_edit_updates_the_same_assessment(self):
        form, request = self.form()
        assessment = form.save(request=request, registry=self.registration.pk)
        form, request = self.form(post_test_done='Yes', post_attended_arabic='Yes',
                                  post_modality_arabic='Offline (F2F)', post_arabic_grade='12')
        self.assertTrue(form.is_valid(), form.errors)
        updated = form.save(request=request, registry=self.registration.pk, instance=assessment.pk)
        self.assertEqual(updated.pk, assessment.pk)
        self.assertEqual(updated.post_arabic_grade, 12)
        self.assertEqual(EducationAssessment.objects.count(), 1)

    def test_completed_assessment_accepts_zero_grades_for_all_subjects(self):
        values = dict(post_test_done='Yes')
        for subject in ('arabic', 'language', 'math'):
            values.update({f'post_attended_{subject}': 'Yes',
                f'post_modality_{subject}': 'Offline (F2F)', f'post_{subject}_grade': '0'})
        form, request = self.form(**values)
        self.assertTrue(form.is_valid(), form.errors)
        assessment = form.save(request=request, registry=self.registration.pk)
        self.assertEqual((assessment.post_arabic_grade, assessment.post_language_grade,
                          assessment.post_math_grade), (0, 0, 0))
        self.assertEqual(SyncEvent.objects.filter(resource='mscc.education_assessment').count(), 1)

    def test_completed_attended_subjects_still_require_a_grade(self):
        values = dict(post_test_done='Yes')
        for subject in ('arabic', 'language', 'math'):
            values.update({f'post_attended_{subject}': 'Yes',
                f'post_modality_{subject}': 'Offline (F2F)', f'post_{subject}_grade': ''})
        form, _ = self.form(**values)
        self.assertFalse(form.is_valid())
        for subject in ('arabic', 'language', 'math'):
            self.assertIn(f'post_{subject}_grade', form.errors)


@override_settings(DATASYNC_ENABLED=True)
class SchoolCenterMappingSaveTests(TestCase):
    def setUp(self):
        from student_registration.locations.models import Center
        from student_registration.schools.models import School
        from student_registration.students.models import Teacher
        from ..models import SchoolCenterLink
        with override_settings(DATASYNC_ENABLED=False):
            self.school = School.objects.create(name='QA mapped school', number='QA-mapping')
            self.center = Center.objects.create(name='QA centre', p_code='QA-map')
            self.teacher = Teacher.objects.create(school=self.school)
            self.other = Teacher.objects.create(school=School.objects.create(name='Other', number='QA-other'))
        self.link_model = SchoolCenterLink

    def test_creating_old_dirasa_mapping_does_not_queue_teachers(self):
        self.link_model.objects.create(school=self.school, center=self.center)
        self.assertFalse(SyncEvent.objects.exists())

    def test_changing_old_dirasa_mapping_does_not_queue_teachers(self):
        from student_registration.locations.models import Center
        with override_settings(DATASYNC_ENABLED=False):
            link = self.link_model.objects.create(school=self.school, center=self.center)
            other_center = Center.objects.create(name='QA second centre', p_code='QA-map-2')
        link.center = other_center
        link.save()
        self.assertFalse(SyncEvent.objects.exists())

    def test_disabled_sync_does_not_queue_mapping_changes(self):
        with override_settings(DATASYNC_ENABLED=False):
            self.link_model.objects.create(school=self.school, center=self.center)
        self.assertFalse(SyncEvent.objects.exists())


@override_settings(DATASYNC_ENABLED=True)
class PartnerSaveTests(TestCase):
    def setUp(self):
        from student_registration.locations.models import Center
        from student_registration.schools.models import PartnerOrganization
        with override_settings(DATASYNC_ENABLED=False):
            self.partner = PartnerOrganization.objects.create(name='QA partner')
            self.center = Center.objects.create(name='QA linked centre', partner=self.partner)
            self.registration = Registration.objects.create(partner=self.partner)
            other = PartnerOrganization.objects.create(name='QA other partner')
            Center.objects.create(name='Other centre', partner=other)
            Registration.objects.create(partner=other)

    def test_partner_edit_queues_only_its_linked_centres_and_registrations(self):
        self.partner.name = 'QA renamed partner'
        self.partner.save()
        self.assertCountEqual(list(SyncEvent.objects.values_list('resource', 'source_id')),
                              [('locations.center', str(self.center.pk)),
                               ('mscc.registration', str(self.registration.pk))])

    def test_disabled_sync_does_not_queue_partner_changes(self):
        with override_settings(DATASYNC_ENABLED=False):
            self.partner.save()
        self.assertFalse(SyncEvent.objects.exists())

    def test_raw_fixture_partner_save_does_not_queue_changes(self):
        from ..signals import partner_saved
        partner_saved(type(self.partner), self.partner, raw=True)
        self.assertFalse(SyncEvent.objects.exists())
