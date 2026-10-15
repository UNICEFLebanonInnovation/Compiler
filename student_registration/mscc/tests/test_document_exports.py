"""Exercise the Excel export that keeps each profile picture on its own row."""

import io
import json
import posixpath
import zipfile
from types import SimpleNamespace
from unittest.mock import Mock, patch
from xml.etree import ElementTree

from django.core.exceptions import ValidationError
from django.http import Http404
from django.test import RequestFactory, SimpleTestCase
from PIL import Image

from student_registration.mscc import tasks
from student_registration.mscc.document_exports import (
    PHOTO_INCLUDED, PHOTO_MISSING, PHOTO_UNAVAILABLE,
    build_children_workbook, export_columns, load_registration_photo,
)
from student_registration.mscc.export_access import (
    filter_registrations, scoped_registrations, user_can_export,
)
from student_registration.mscc.models import Registration, Round

# The list filters read the current cycles from the database when the views
# module is first imported. Stub that lookup so these tests need no database.
with patch.object(Round, 'objects') as _rounds:
    _rounds.filter.return_value.values_list.return_value.order_by.return_value.distinct.return_value = []
    from student_registration.mscc import views


SPREADSHEET_NS = {'s': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
DRAWING_NS = {
    'xdr': 'http://schemas.openxmlformats.org/drawingml/2006/spreadsheetDrawing',
    'a': 'http://schemas.openxmlformats.org/drawingml/2006/main',
    'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships',
}
RELATIONSHIP_NS = 'http://schemas.openxmlformats.org/package/2006/relationships'


def portrait_bytes(colour, image_format='PNG'):
    output = io.BytesIO()
    Image.new('RGB', (48, 64), colour).save(output, format=image_format)
    return output.getvalue()


def workbook_rows(content):
    """Read real cell values without relying on a writer's internal objects."""
    with zipfile.ZipFile(io.BytesIO(content)) as archive:
        shared_strings = []
        if 'xl/sharedStrings.xml' in archive.namelist():
            root = ElementTree.fromstring(archive.read('xl/sharedStrings.xml'))
            shared_strings = [
                ''.join(value.itertext()) for value in root.findall('s:si', SPREADSHEET_NS)
            ]
        root = ElementTree.fromstring(archive.read('xl/worksheets/sheet1.xml'))
        rows = []
        for row in root.findall('s:sheetData/s:row', SPREADSHEET_NS):
            values = {}
            for cell in row.findall('s:c', SPREADSHEET_NS):
                value = cell.find('s:v', SPREADSHEET_NS)
                if cell.get('t') == 's':
                    values[cell.get('r')] = shared_strings[int(value.text)]
                elif cell.get('t') == 'inlineStr':
                    values[cell.get('r')] = ''.join(
                        cell.find('s:is', SPREADSHEET_NS).itertext()
                    )
                else:
                    values[cell.get('r')] = value.text if value is not None else ''
            rows.append((int(row.get('r')), values))
    headers = {}
    for address, value in rows[0][1].items():
        headers[''.join(character for character in address if character.isalpha())] = value
    return [
        (number, {
            headers[''.join(character for character in address if character.isalpha())]: value
            for address, value in values.items()
        }) for number, values in rows[1:]
    ]


def workbook_photos_by_row(content):
    """Follow each drawing's relationship to its image and its real row anchor."""
    photos = {}
    with zipfile.ZipFile(io.BytesIO(content)) as archive:
        for drawing_name in archive.namelist():
            if not drawing_name.startswith('xl/drawings/drawing') or not drawing_name.endswith('.xml'):
                continue
            relation_name = posixpath.join(
                posixpath.dirname(drawing_name), '_rels',
                posixpath.basename(drawing_name) + '.rels',
            )
            relationships = ElementTree.fromstring(archive.read(relation_name))
            targets = {
                relation.get('Id'): posixpath.normpath(posixpath.join(
                    posixpath.dirname(drawing_name), relation.get('Target'),
                ))
                for relation in relationships.findall('{%s}Relationship' % RELATIONSHIP_NS)
            }
            drawing = ElementTree.fromstring(archive.read(drawing_name))
            for anchor in drawing:
                row = anchor.find('xdr:from/xdr:row', DRAWING_NS)
                blip = anchor.find('.//a:blip', DRAWING_NS)
                if row is not None and blip is not None:
                    image_id = blip.get('{%s}embed' % DRAWING_NS['r'])
                    photos[int(row.text) + 1] = archive.read(targets[image_id])
    return photos


def photo_colour(content):
    """Return the centre pixel, rounding away JPEG compression noise."""
    with Image.open(io.BytesIO(content)) as photo:
        pixel = photo.convert('RGB').getpixel((photo.width // 2, photo.height // 2))
    return tuple(0 if channel < 8 else 255 if channel > 247 else channel for channel in pixel)


def fake_reverse(name, args=()):
    """Avoid loading the project URLconf, whose filters query the database."""
    assert name == 'mscc:export_download'
    return '/mscc/export-download/%s/' % args[0]


class StoredPicture:
    """Model a saved image file that has neither a filesystem path nor a URL."""

    def __init__(self, data, name='mscc/profile_pictures/photo.png'):
        self.data = data
        self.name = name

    def __bool__(self):
        return True

    def open(self, mode='rb'):
        return io.BytesIO(self.data)


class UnreadablePicture(StoredPicture):
    def open(self, mode='rb'):
        raise RuntimeError('storage unavailable')


def make_child(pk, **fields):
    values = dict(
        pk=pk, id=pk, first_name='Rania', father_name='Samir', last_name='Example',
        mother_fullname='Mother of Rania', gender='Female',
        birthday_year='2014', birthday_month='3', birthday_day='12',
        nationality=None, nationality_id=None, unicef_id='CHILD-%s' % pk,
    )
    values.update(fields)
    return SimpleNamespace(**values)


def make_registration(pk, child, picture=None, **fields):
    values = dict(
        pk=pk, id=pk, child=child, child_id=child.pk, profile_picture=picture,
        round=None, round_id=None, partner=None, partner_id=None, center=None,
        center_id=None, type='Core-Package', deleted=False,
    )
    values.update(fields)
    return SimpleNamespace(**values)


class WorkbookTests(SimpleTestCase):
    def setUp(self):
        self.first_child = make_child(11)
        self.second_child = make_child(
            12, first_name='Karim', father_name='Ibrahim', last_name='Second',
            birthday_year='2015', birthday_month='', birthday_day='',
        )
        self.consent_value, self.consent_label = next(
            iter(Registration._meta.get_field('consent').flatchoices)
        )
        self.first_registration = make_registration(
            101, self.first_child, StoredPicture(portrait_bytes('red'), 'mscc/profile_pictures/rania.png'),
            consent=self.consent_value,
        )
        self.second_registration = make_registration(
            102, self.second_child, StoredPicture(portrait_bytes('blue', 'JPEG'), 'mscc/profile_pictures/karim.jpg'),
        )

    def test_excel_keeps_each_photo_on_the_corresponding_row_with_registration_values(self):
        content = build_children_workbook([self.first_registration, self.second_registration])
        rows = workbook_rows(content)
        photos = workbook_photos_by_row(content)
        self.assertEqual(len(rows), 2)
        records = {row['Registration ID']: (number, row) for number, row in rows}
        first_number, first = records['101']
        second_number, second = records['102']
        self.assertEqual(first['Child ID'], '11')
        self.assertEqual(second['Child ID'], '12')
        self.assertEqual(first['Child full name'], 'Rania Samir Example')
        self.assertEqual(second['Child full name'], 'Karim Ibrahim Second')
        self.assertEqual(first['Date of birth'], '2014-03-12')
        self.assertEqual(second['Date of birth'], '2015')
        self.assertEqual(first['Photograph status'], PHOTO_INCLUDED)
        self.assertEqual(first['Photograph'], '')
        self.assertEqual(first['Type'], 'Core-Package')
        self.assertEqual(
            first['Informed Consent Received to Share Data Externally'], str(self.consent_label),
        )
        self.assertEqual(photo_colour(photos[first_number]), (255, 0, 0))
        self.assertEqual(photo_colour(photos[second_number]), (0, 0, 255))
        self.assertNotIn('Profile Picture', first)

    def test_multiple_registrations_for_one_child_keep_their_own_pictures(self):
        newer = make_registration(
            103, self.first_child, StoredPicture(portrait_bytes('green')), type='Walk-in',
        )
        content = build_children_workbook([self.first_registration, newer])
        rows = workbook_rows(content)
        photos = workbook_photos_by_row(content)
        self.assertEqual({row['Child ID'] for _, row in rows}, {'11'})
        colours = {row['Registration ID']: photo_colour(photos[number]) for number, row in rows}
        self.assertEqual(colours, {'101': (255, 0, 0), '103': (0, 128, 0)})

    def test_missing_unreadable_and_corrupt_photos_have_explicit_status_and_no_wrong_image(self):
        registrations = [
            make_registration(201, self.first_child, None),
            make_registration(202, self.first_child, UnreadablePicture(b'')),
            make_registration(203, self.first_child, StoredPicture(b'not-an-image')),
            self.second_registration,
        ]
        content = build_children_workbook(registrations)
        rows = {row['Registration ID']: (number, row) for number, row in workbook_rows(content)}
        photos = workbook_photos_by_row(content)
        self.assertEqual(rows['201'][1]['Photograph status'], PHOTO_MISSING)
        self.assertEqual(rows['201'][1]['Photograph'], PHOTO_MISSING)
        self.assertEqual(rows['202'][1]['Photograph status'], PHOTO_UNAVAILABLE)
        self.assertEqual(rows['203'][1]['Photograph status'], PHOTO_UNAVAILABLE)
        self.assertEqual(rows['102'][1]['Photograph status'], PHOTO_INCLUDED)
        self.assertEqual(list(photos), [rows['102'][0]])

    def test_photo_loader_reports_status_without_raising(self):
        self.assertEqual(load_registration_photo(make_registration(1, self.first_child)), (None, PHOTO_MISSING))
        data, status = load_registration_photo(self.first_registration)
        self.assertEqual(status, PHOTO_INCLUDED)
        self.assertEqual(photo_colour(data), (255, 0, 0))

    def test_excel_writes_registered_formula_like_text_as_literal_values(self):
        self.first_child.first_name = '=HYPERLINK("https://example.invalid","name")'
        self.first_child.mother_fullname = '=1+2'
        content = build_children_workbook([self.first_registration])
        row = workbook_rows(content)[0][1]
        self.assertEqual(row['First name'], self.first_child.first_name)
        self.assertEqual(row['Mother fullname'], '=1+2')
        with zipfile.ZipFile(io.BytesIO(content)) as archive:
            worksheet = ElementTree.fromstring(archive.read('xl/worksheets/sheet1.xml'))
        self.assertEqual(worksheet.findall('.//s:f', SPREADSHEET_NS), [])

    def test_invalid_xml_characters_and_structured_values_are_written_safely(self):
        self.first_child.first_name = 'Ra\x00nia\x0b'
        self.first_child.cash_programmes = {'haddi': True}
        self.first_registration.labour_condition = [
            value for value, _ in Registration._meta.get_field('labour_condition').base_field.flatchoices
        ][:2]
        row = workbook_rows(build_children_workbook([self.first_registration]))[0][1]
        self.assertEqual(row['First name'], 'Rania')
        self.assertEqual(json.loads(row['Cash programmes'] if 'Cash programmes' in row else row['cash programmes']), {'haddi': True})
        labels = dict(Registration._meta.get_field('labour_condition').base_field.flatchoices)
        self.assertEqual(
            row['What is the work condition that the child is exposed to?'],
            '; '.join(str(labels[value]) for value in self.first_registration.labour_condition),
        )

    def test_selected_fields_keep_identity_and_photo_columns(self):
        columns = export_columns(['first_name', 'registration.type', 'Date of birth'])
        self.assertEqual(
            [column.label for column in columns],
            ['Registration ID', 'Child ID', 'Photograph', 'Photograph status',
             'Date of birth', 'First name', 'Type'],
        )
        self.assertEqual(
            [column.label for column in export_columns(['unknown'])][:4],
            ['Registration ID', 'Child ID', 'Photograph', 'Photograph status'],
        )
        self.assertEqual(len(export_columns(['unknown'])), 4)
        labels = [column.label for column in export_columns()]
        self.assertEqual(len(labels), len(set(labels)), 'headers must be unambiguous')


class ExportAccessTests(SimpleTestCase):
    def user(self, groups, partner_id=None, center_id=None, world_learning=False, active=True):
        partner = SimpleNamespace(is_world_learning=world_learning) if partner_id else None
        return SimpleNamespace(
            is_authenticated=True, is_active=active, is_superuser=False,
            partner=partner, partner_id=partner_id, center_id=center_id,
            groups=groups,
        )

    def has_group(self):
        return patch(
            'student_registration.mscc.export_access.has_group',
            side_effect=lambda user, group: group in user.groups,
        )

    def test_export_roles(self):
        with self.has_group():
            self.assertTrue(user_can_export(self.user({'MSCC_UNICEF'})))
            self.assertTrue(user_can_export(self.user({'MSCC'}, partner_id=3, world_learning=True)))
            self.assertTrue(user_can_export(self.user({'MSCC_PARTNER'}, partner_id=3)))
            self.assertTrue(user_can_export(self.user({'MSCC_CENTER'}, center_id=4)))
            self.assertFalse(user_can_export(self.user({'MSCC_PARTNER'})))
            self.assertFalse(user_can_export(self.user({'MSCC_CENTER'})))
            self.assertFalse(user_can_export(self.user({'MSCC'})))
            self.assertFalse(user_can_export(self.user({'MSCC_UNICEF'}, active=False)))
            self.assertFalse(user_can_export(None))

    def scoped(self, user):
        qs = Mock()
        qs.select_related.return_value = qs
        qs.order_by.return_value = qs
        qs.filter.return_value = qs
        with patch('student_registration.mscc.export_access.Registration.objects') as manager, self.has_group():
            manager.filter.return_value = qs
            result = scoped_registrations(user)
            manager.filter.assert_called_once_with(deleted=False)
        return qs, result

    def test_unicef_and_world_learning_users_see_every_registration(self):
        for user in (self.user({'MSCC_UNICEF'}), self.user(set(), partner_id=2, world_learning=True)):
            qs, result = self.scoped(user)
            self.assertIs(result, qs)
            qs.filter.assert_not_called()
            qs.none.assert_not_called()

    def test_partner_and_centre_scopes(self):
        qs, _ = self.scoped(self.user({'MSCC_PARTNER'}, partner_id=5))
        qs.filter.assert_called_once_with(partner_id=5)
        qs, _ = self.scoped(self.user({'MSCC_CENTER'}, center_id=7))
        qs.filter.assert_called_once_with(center_id=7)

    def test_unassigned_users_have_no_records(self):
        qs, result = self.scoped(self.user({'MSCC'}))
        qs.none.assert_called_once()
        self.assertIs(result, qs.none.return_value)

    def queryset(self):
        qs = Mock()
        qs.filter.return_value = qs
        return qs

    def test_cycle_is_required(self):
        qs = self.queryset()
        self.assertIs(filter_registrations(qs, {}), qs.none.return_value)
        qs = self.queryset()
        filter_registrations(qs, {'round': 'no_round'})
        qs.filter.assert_called_once_with(round__isnull=True)
        qs = self.queryset()
        filter_registrations(qs, {'round': '9'})
        qs.filter.assert_called_once_with(round_id=9)
        with self.assertRaises(ValidationError):
            filter_registrations(self.queryset(), {'round': '9 OR 1=1'})
        with self.assertRaises(ValidationError):
            filter_registrations(self.queryset(), {'round': '3', 'nationality': 'x'})

    def test_name_and_nationality_filters(self):
        qs = self.queryset()
        filter_registrations(qs, {
            'round': '3', 'nationality': '2', 'first_name': 'Ra', 'mother_fullname': 'Mo',
            'last_name': '', 'father_name': None,
        })
        calls = [call.kwargs for call in qs.filter.call_args_list]
        self.assertEqual(calls, [
            {'round_id': 3}, {'child__nationality_id': 2},
            {'child__first_name__icontains': 'Ra'}, {'child__mother_fullname__icontains': 'Mo'},
        ])


class ExportViewTests(SimpleTestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = SimpleNamespace(
            is_authenticated=True, is_active=True, partner=None, partner_id=None, center_id=None,
        )

    def start(self, params, can_export=True):
        request = self.factory.get('/mscc/export-list-background/', params)
        request.user = self.user
        with patch.object(views, 'user_can_export', return_value=can_export), \
                patch.object(views.ExportHistory.objects, 'create') as create, \
                patch.object(views, 'queue_filtered_mscc_export') as queue:
            create.return_value = SimpleNamespace(id=55)
            response = views.export_list_background(request)
        return response, create, queue

    def test_excel_export_is_queued_with_its_format_and_filters(self):
        response, create, queue = self.start({
            'round': '4', 'format': 'xlsx', 'first_name': 'Ra', 'nationality': '2',
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content), {'status': 'started', 'export_id': 55})
        self.assertEqual(create.call_args.kwargs['file_format'], 'xlsx')
        queue.assert_called_once_with(55, '2', 'Ra', '', '', '', '4', 'xlsx')

    def test_csv_remains_the_default_format(self):
        response, create, queue = self.start({'round': 'no_round'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(create.call_args.kwargs['file_format'], 'csv')
        self.assertEqual(queue.call_args.args[-2:], ('no_round', 'csv'))

    def test_invalid_requests_do_not_start_an_export(self):
        for params, status in (
            ({'round': '4', 'format': 'docx'}, 400),
            ({'format': 'xlsx'}, 400),
            ({'round': 'abc', 'format': 'xlsx'}, 400),
            ({'round': '4', 'nationality': 'abc', 'format': 'xlsx'}, 400),
        ):
            response, create, queue = self.start(params)
            self.assertEqual(response.status_code, status, params)
            create.assert_not_called()
            queue.assert_not_called()
        response, create, queue = self.start({'round': '4', 'format': 'xlsx'}, can_export=False)
        self.assertEqual(response.status_code, 403)
        create.assert_not_called()

    def download(self, file_name, owned):
        request = self.factory.get('/mscc/export-download/%s/' % file_name)
        request.user = self.user
        with patch.object(views.ExportHistory.objects, 'filter') as history, \
                patch.object(views, 'reverse', side_effect=fake_reverse), \
                patch.object(views, 'download_file') as download_file:
            history.return_value.exists.return_value = owned
            response = views.get_file(request, file_name)
        return response, history, download_file

    def test_photo_workbooks_download_only_for_their_requester(self):
        file_name = 'out_file_1234-abcd.xlsx'
        with self.assertRaises(Http404):
            self.download(file_name, owned=False)
        response, history, download_file = self.download(file_name, owned=True)
        self.assertEqual(history.call_args.kwargs, {
            'created_by': self.user, 'status': 'done',
            'file_url': '/mscc/export-download/%s/' % file_name,
        })
        download_file.assert_called_once_with(
            file_name, 'exported_data.xlsx',
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        )
        self.assertIs(response, download_file.return_value)

    def test_other_file_names_are_rejected_and_zip_downloads_are_unchanged(self):
        for file_name in ('../secret.xlsx', 'out_file.xlsx.zip.txt', 'out_file.docx'):
            response, history, download_file = self.download(file_name, owned=True)
            self.assertEqual(response.content, b'Invalid file.')
            download_file.assert_not_called()
        response, history, download_file = self.download('out_file_1.zip', owned=False)
        history.assert_not_called()
        download_file.assert_called_once_with('out_file_1.zip', 'output_file.zip')


class ExportTaskTests(SimpleTestCase):
    def run_export(self, file_format, registrations=()):
        user = SimpleNamespace(partner=None, partner_id=None, center_id=None)
        export = Mock(created_by=user, status='pending', file_url=None)
        queryset = Mock()
        queryset.iterator.return_value = iter(registrations)
        files = {}

        def save_file(name, content):
            files[name] = content.read()
            return name

        with patch.object(tasks.ExportHistory.objects, 'get', return_value=export), \
                patch.object(tasks, 'scoped_registrations') as scoped, \
                patch.object(tasks, 'filter_registrations', return_value=queryset) as filtered, \
                patch.object(tasks, 'ExportStorage') as storage, \
                patch.object(tasks, 'reverse', side_effect=fake_reverse), \
                patch.object(tasks, 'send_push_to_web') as notify, \
                patch.object(tasks, 'connection') as connection:
            storage.return_value.save.side_effect = save_file
            tasks._generate_filtered_mscc_export(
                7, nationality='2', first_name='Ra', round='4', file_format=file_format,
            )
        return export, files, notify, scoped, filtered, connection

    def test_excel_export_stores_a_workbook_with_photos_within_the_requesters_scope(self):
        child = make_child(11)
        registration = make_registration(101, child, StoredPicture(portrait_bytes('red')))
        export, files, notify, scoped, filtered, connection = self.run_export('xlsx', [registration])
        scoped.assert_called_once_with(export.created_by)
        self.assertEqual(filtered.call_args.args[1], {
            'round': '4', 'nationality': '2', 'first_name': 'Ra',
            'last_name': '', 'father_name': '', 'mother_fullname': '',
        })
        self.assertEqual(len(files), 1)
        name, content = next(iter(files.items()))
        self.assertRegex(name, r'^out_file_[0-9a-f-]{36}\.xlsx$')
        self.assertEqual(export.status, 'done')
        self.assertEqual(export.file_url, '/mscc/export-download/%s/' % name)
        export.save.assert_called_once()
        photos = workbook_photos_by_row(content)
        rows = workbook_rows(content)
        self.assertEqual(rows[0][1]['Registration ID'], '101')
        self.assertEqual(photo_colour(photos[rows[0][0]]), (255, 0, 0))
        notify.assert_called_once()
        self.assertEqual(notify.call_args.kwargs['data']['url'], export.file_url)
        connection.cursor.assert_not_called()

    def test_unsupported_format_marks_the_export_failed(self):
        export, files, notify, _, _, _ = self.run_export('docx')
        self.assertEqual(files, {})
        self.assertEqual(export.status, 'failed')
        self.assertEqual(notify.call_args.args[1], 'Makani export failed')
