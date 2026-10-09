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


class BulkProfileTests(SimpleTestCase):
    def view(self, parameters):
        from student_registration.mscc.profile_views import BulkProfileIdView
        view = BulkProfileIdView()
        view.request = SimpleNamespace(GET=parameters)
        return view

    def test_missing_and_invalid_cycle(self):
        for parameters in ({}, {'round': 'bad'}):
            view = self.view(parameters)
            self.assertEqual(view.get(view.request).status_code, 400)

    def test_cycle_name_and_nationality_filters(self):
        view = self.view({'round': '24', 'first_name': 'أحمد', 'nationality': '2'})
        qs = Mock()
        for method in ('exclude', 'filter', 'only', 'order_by'):
            getattr(qs, method).return_value = qs
        with patch.object(view, 'get_queryset', return_value=qs):
            view.get_registrations('24')
        qs.exclude.assert_called_once_with(type='TLS')
        self.assertIn(({'round_id': '24'}), [call.kwargs for call in qs.filter.call_args_list])
        self.assertIn(({'child__first_name__icontains': 'أحمد'}), [call.kwargs for call in qs.filter.call_args_list])
        self.assertIn(({'child__nationality_id': '2'}), [call.kwargs for call in qs.filter.call_args_list])

    def test_no_cycle_filter(self):
        view = self.view({'round': 'no_round'})
        qs = Mock()
        for method in ('exclude', 'filter', 'only', 'order_by'):
            getattr(qs, method).return_value = qs
        with patch.object(view, 'get_queryset', return_value=qs):
            view.get_registrations('no_round')
        qs.filter.assert_called_once_with(round__isnull=True)

    def test_printable_page_does_not_open_picture_storage(self):
        view = self.view({'round': '24'})
        picture = Mock()
        registration = SimpleNamespace(
            child=None, center=None, round=None, partner=None, pk=12,
            child_fullname='Child Name', profile_picture=picture,
        )
        qs = Mock()
        qs.iterator.return_value = iter([registration])
        with patch.object(view, 'get_registrations', return_value=qs), patch(
                'student_registration.mscc.profile_views.get_object_or_404'):
            response = view.get(view.request)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Child Name')
        self.assertContains(response, '/mscc/profile-picture/12/file/')
        self.assertContains(response, 'No photo available')
        self.assertContains(response, 'Print / Save as PDF')
        picture.open.assert_not_called()
        qs.iterator.assert_called_once_with(chunk_size=250)


    def test_missing_picture_does_not_raise_server_error(self):
        from django.http import Http404
        from student_registration.mscc.profile_views import ProfilePictureFileView
        picture = Mock()
        picture.open.side_effect = FileNotFoundError('missing')
        view = ProfilePictureFileView()
        with patch.object(view, 'get_object', return_value=SimpleNamespace(
                pk=12, profile_picture=picture)):
            with self.assertRaises(Http404):
                view.get(SimpleNamespace())
