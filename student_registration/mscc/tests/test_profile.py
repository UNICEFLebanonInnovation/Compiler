from io import BytesIO
from types import SimpleNamespace
from unittest.mock import Mock, patch

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import SimpleTestCase
from PIL import Image

from student_registration.mscc.profile_forms import ProfilePictureForm
from student_registration.mscc.profile_views import (
    ProfileRegistrationMixin, registration_profile_id_card,
)


class ProfilePictureTests(SimpleTestCase):
    def picture(self, name, image_format):
        stream = BytesIO()
        Image.new('RGB', (10, 10)).save(stream, format=image_format)
        return SimpleUploadedFile(name, stream.getvalue())

    def test_png_and_jpeg_uploads(self):
        for name, image_format in [('photo.png', 'PNG'), ('photo.jpg', 'JPEG')]:
            form = ProfilePictureForm(files={'profile_picture': self.picture(name, image_format)})
            self.assertTrue(form.is_valid(), form.errors)

    def test_rejects_other_extensions_and_image_formats(self):
        for name, image_format in [('photo.gif', 'GIF'), ('photo.png', 'GIF')]:
            form = ProfilePictureForm(files={'profile_picture': self.picture(name, image_format)})
            self.assertFalse(form.is_valid())
            self.assertIn('profile_picture', form.errors)

    def test_clear_picture(self):
        form = ProfilePictureForm(
            data={'profile_picture-clear': 'on'},
            initial={'profile_picture': SimpleNamespace(url='/photo.png')},
        )
        self.assertTrue(form.is_valid(), form.errors)
        self.assertIs(form.cleaned_data['profile_picture'], False)


class ProfileAccessTests(SimpleTestCase):
    def queryset(self, groups, partner_id=None, center_id=None):
        view = ProfileRegistrationMixin()
        view.request = SimpleNamespace(user=SimpleNamespace(
            partner=None, partner_id=partner_id, center_id=center_id,
        ))
        qs = Mock()
        qs.select_related.return_value = qs
        qs.filter.return_value = qs
        with patch('student_registration.mscc.profile_views.Registration.objects') as manager, patch(
                'student_registration.mscc.profile_views.has_group',
                side_effect=lambda user, group: group in groups):
            manager.filter.return_value = qs
            view.get_queryset()
            manager.filter.assert_called_once_with(deleted=False)
        return qs

    def test_partner_scope(self):
        self.queryset({'MSCC_PARTNER'}, partner_id=5).filter.assert_called_once_with(partner_id=5)

    def test_center_scope(self):
        self.queryset({'MSCC_CENTER'}, center_id=7).filter.assert_called_once_with(center_id=7)

    def test_unassigned_user_has_no_records(self):
        self.queryset(set()).none.assert_called_once()

    def test_missing_child_and_registration_details(self):
        card = registration_profile_id_card(SimpleNamespace(
            child=None, center=None, round=None, partner=None, pk=1,
            child_fullname='', profile_picture=None,
        ))
        self.assertEqual(card['birthday'], '')
        self.assertEqual(card['full_name'], '')
        self.assertFalse(card['has_picture'])
