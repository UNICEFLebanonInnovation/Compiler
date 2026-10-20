"""Exercise the Dirasa (Bridging) Excel export with student profile pictures."""

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

from student_registration.backends import utils as backend_utils
from student_registration.clm import bridging_exports, bridging_access
from student_registration.clm.bridging_exports import (
    BRIDGING_PROFILE, PHOTO_EXPORT_PREFIX, clean_filters, filter_bridging_registrations,
    scoped_bridging_registrations, user_can_export_bridging,
)
from student_registration.clm.models import Bridging
from student_registration.mscc.document_exports import (
    PHOTO_INCLUDED, PHOTO_MISSING, build_children_workbook, export_columns,
)
from student_registration.mscc.models import Round

# The list filters read the current cycles from the database when the MSCC
# views module is first imported. Stub that lookup so these tests need no database.
with patch.object(Round, 'objects') as _rounds:
    _rounds.filter.return_value.values_list.return_value.order_by.return_value.distinct.return_value = []
    from student_registration.clm import bridging_views
    from student_registration.mscc import views as mscc_views


SPREADSHEET_NS = {'s': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
DRAWING_NS = {
    'xdr': 'http://schemas.openxmlformats.org/drawingml/2006/spreadsheetDrawing',
    'a': 'http://schemas.openxmlformats.org/drawingml/2006/main',
    'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships',
}
RELATIONSHIP_NS = 'http://schemas.openxmlformats.org/package/2006/relationships'


def portrait_bytes(colour):
    output = io.BytesIO()
    Image.new('RGB', (48, 64), colour).save(output, format='PNG')
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
    with Image.open(io.BytesIO(content)) as photo:
        return photo.convert('RGB').getpixel((photo.width // 2, photo.height // 2))


def fake_reverse(name, args=()):
    """Avoid loading the project URLconf, whose filters query the database."""
    assert name == 'mscc:export_download'
    return '/mscc/export-download/%s/' % args[0]


class StoredPicture:
    """Model a saved image file that has neither a filesystem path nor a URL."""

    def __init__(self, data, name='uploads/bridging/profile_pictures/photo.png'):
        self.data = data
        self.name = name

    def __bool__(self):
        return True

    def open(self, mode='rb'):
        return io.BytesIO(self.data)


def make_student(pk, **fields):
    values = dict(
        pk=pk, id=pk, first_name='Layla', father_name='Hassan', last_name='Example',
        mother_fullname='Mother of Layla', sex='Female',
        birthday_year='2013', birthday_month='7', birthday_day='4',
        nationality=None, nationality_id=None, place_of_birth='Beirut',
    )
    values.update(fields)
    return SimpleNamespace(**values)


def make_bridging(pk, student, picture=None, **fields):
    values = dict(
        pk=pk, id=pk, student=student, student_id=student.pk, profile_picture=picture,
        round=None, round_id=None, partner=None, partner_id=None, school=None,
        school_id=None, deleted=False,
    )
    values.update(fields)
    return SimpleNamespace(**values)


class BridgingWorkbookTests(SimpleTestCase):
    def test_excel_keeps_each_student_photo_on_its_registration_row(self):
        first = make_bridging(501, make_student(31), StoredPicture(portrait_bytes('red')))
        second = make_bridging(
            502, make_student(32, first_name='Omar', father_name='Ali', last_name='Second'),
            StoredPicture(portrait_bytes('blue')),
        )
        third = make_bridging(503, make_student(33), None)
        consent_value, consent_label = next(iter(Bridging._meta.get_field('consent').flatchoices))
        first.consent = consent_value

        content = build_children_workbook([first, second, third], profile=BRIDGING_PROFILE)
        rows = workbook_rows(content)
        photos = workbook_photos_by_row(content)
        records = {row['Registration ID']: (number, row) for number, row in rows}
        self.assertEqual(set(records), {'501', '502', '503'})
        first_number, first_row = records['501']
        second_number, second_row = records['502']
        self.assertEqual(first_row['Student ID'], '31')
        self.assertEqual(first_row['Student full name'], 'Layla Hassan Example')
        self.assertEqual(second_row['Student full name'], 'Omar Ali Second')
        self.assertEqual(first_row['Date of birth'], '2013-07-04')
        self.assertEqual(first_row['Photograph status'], PHOTO_INCLUDED)
        self.assertEqual(first_row['Photograph'], '')
        self.assertEqual(records['503'][1]['Photograph status'], PHOTO_MISSING)
        self.assertEqual(records['503'][1]['Photograph'], PHOTO_MISSING)
        self.assertEqual(
            first_row['Informed Consent Received to Share Data Externally'], str(consent_label),
        )
        self.assertNotIn('Child ID', first_row)
        self.assertEqual(photo_colour(photos[first_number]), (255, 0, 0))
        self.assertEqual(photo_colour(photos[second_number]), (0, 0, 255))
        self.assertEqual(len(photos), 2)

    def test_bridging_headers_are_unambiguous_and_keep_identity_columns(self):
        labels = [column.label for column in export_columns(profile=BRIDGING_PROFILE)]
        self.assertEqual(labels[:4], ['Registration ID', 'Student ID', 'Photograph', 'Photograph status'])
        self.assertEqual(len(labels), len(set(labels)))
        self.assertIn('First name', labels)

    def test_mscc_export_is_unchanged_by_the_profile_parameter(self):
        labels = [column.label for column in export_columns()]
        self.assertEqual(labels[:4], ['Registration ID', 'Child ID', 'Photograph', 'Photograph status'])
        self.assertIn('Child full name', labels)


class BridgingAccessTests(SimpleTestCase):
    def user(self, groups, partner_id=None, school_id=None, staff=False, active=True):
        return SimpleNamespace(
            is_authenticated=True, is_active=active, is_staff=staff, is_superuser=False,
            partner=SimpleNamespace(name='Partner') if partner_id else None,
            partner_id=partner_id, school_id=school_id, groups=groups, _group_names_cache=groups,
        )

    def has_group(self):
        return patch.object(
            bridging_access, 'has_group',
            side_effect=lambda user, group: group in user.groups,
        )

    def test_export_roles(self):
        with self.has_group():
            self.assertTrue(user_can_export_bridging(self.user({'CLM_Bridging', 'CLM_BRIDGING_ALL'})))
            self.assertTrue(user_can_export_bridging(self.user({'CLM_Bridging'}, staff=True)))
            self.assertTrue(user_can_export_bridging(self.user({'CLM_Bridging'}, partner_id=4)))
            self.assertFalse(user_can_export_bridging(self.user({'CLM_Bridging'})))
            self.assertTrue(user_can_export_bridging(self.user({'CLM_BRIDGING_ALL'})))
            self.assertFalse(user_can_export_bridging(self.user({'CLM_Bridging'}, partner_id=4, active=False)))
            self.assertFalse(user_can_export_bridging(None))

    def scoped(self, user):
        qs = Mock()
        qs.select_related.return_value = qs
        qs.order_by.return_value = qs
        qs.filter.return_value = qs
        with patch.object(bridging_exports.Bridging, 'objects') as manager, self.has_group():
            manager.filter.return_value = qs
            result = scoped_bridging_registrations(user)
            manager.filter.assert_called_once_with(deleted=False, round__current_year=True)
        return qs, result

    def test_all_and_staff_users_see_every_registration(self):
        for user in (self.user({'CLM_Bridging', 'CLM_BRIDGING_ALL'}), self.user({'CLM_Bridging'}, staff=True)):
            qs, result = self.scoped(user)
            self.assertIs(result, qs)
            qs.filter.assert_not_called()

    def test_partner_users_are_limited_to_their_partner_and_school(self):
        qs, _ = self.scoped(self.user({'CLM_Bridging'}, partner_id=4))
        self.assertEqual(qs.filter.call_args.args[0].children, [('partner_id', 4)])
        qs, _ = self.scoped(self.user({'CLM_Bridging'}, partner_id=4, school_id=9))
        self.assertEqual(
            [call.kwargs for call in qs.filter.call_args_list],
            [{'school_id': 9}],
        )

    def test_users_without_a_role_have_no_records(self):
        qs, result = self.scoped(self.user({'CLM_Bridging'}))
        self.assertIs(result, qs.none.return_value)

    def test_filters_require_a_round_and_reject_invalid_ids(self):
        with self.assertRaises(ValidationError):
            clean_filters({})
        with self.assertRaises(ValidationError):
            clean_filters({'round': 'abc'})
        with self.assertRaises(ValidationError):
            clean_filters({'round': '3', 'partner': '1 OR 1=1'})
        self.assertEqual(
            clean_filters({'round': '3', 'school': '', 'student__first_name': 'La', 'partner': '2'}),
            {'round': 3, 'partner': 2, 'student__first_name': 'La'},
        )
        with self.assertRaises(ValidationError):
            clean_filters({'round': '3', 'has_photo': 'maybe'})
        self.assertEqual(clean_filters({'round': '3', 'has_photo': 'yes'}), {'round': 3, 'has_photo': 'yes'})
        self.assertEqual(clean_filters({'round': '3', 'has_photo': ''}), {'round': 3})

    def test_filters_apply_within_the_scope(self):
        qs = Mock()
        qs.filter.return_value = qs
        filter_bridging_registrations(qs, {
            'round': '3', 'student__nationality': '2', 'district': '8',
            'student__last_name': 'Ex', 'student__father_name': '',
        })
        self.assertEqual([call.kwargs for call in qs.filter.call_args_list], [
            {'round_id': 3}, {'student__nationality_id': 2}, {'district_id': 8},
            {'student__last_name__icontains': 'Ex'},
        ])
        qs.exclude.assert_not_called()

    def test_photo_filter_keeps_only_students_with_or_without_a_saved_picture(self):
        qs = Mock()
        qs.filter.return_value = qs
        qs.exclude.return_value = qs
        filter_bridging_registrations(qs, {'round': '3', 'has_photo': 'yes'})
        self.assertEqual(
            [call.kwargs for call in qs.exclude.call_args_list],
            [{'profile_picture': ''}, {'profile_picture__isnull': True}],
        )
        qs = Mock()
        qs.filter.return_value = qs
        filter_bridging_registrations(qs, {'round': '3', 'has_photo': 'no'})
        condition = qs.filter.call_args_list[-1].args[0]
        self.assertEqual(condition.connector, 'OR')
        self.assertEqual(
            sorted(condition.children), [('profile_picture', ''), ('profile_picture__isnull', True)],
        )


class BridgingExportViewTests(SimpleTestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = SimpleNamespace(is_authenticated=True, is_active=True, partner=None)

    def start(self, params, can_export=True):
        request = self.factory.get('/clm/bridging-export-photos/', params)
        request.user = self.user
        with patch.object(bridging_exports, 'user_can_export_bridging', return_value=can_export), \
                patch.object(bridging_views.ExportHistory.objects, 'create') as create, \
                patch.object(bridging_exports, 'queue_bridging_photo_export') as queue:
            create.return_value = SimpleNamespace(id=77)
            response = bridging_views.bridging_export_photos(request)
        return response, create, queue

    def test_photo_export_is_queued_with_the_list_filters(self):
        response, create, queue = self.start({
            'round': '5', 'student__first_name': 'La', 'partner': '2', 'school': '',
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content), {'status': 'started', 'export_id': 77})
        self.assertEqual(create.call_args.kwargs['file_format'], 'xlsx')
        self.assertEqual(create.call_args.kwargs['export_type'], 'Bridging List')
        export_id, filters = queue.call_args.args
        self.assertEqual(export_id, 77)
        self.assertEqual(filters['round'], '5')
        self.assertEqual(filters['student__first_name'], 'La')
        self.assertEqual(filters['partner'], '2')
        self.assertEqual(filters['district'], '')

    def test_invalid_requests_do_not_start_an_export(self):
        for params in ({}, {'round': 'abc'}, {'round': '5', 'student__nationality': 'x'}):
            response, create, queue = self.start(params)
            self.assertEqual(response.status_code, 400, params)
            create.assert_not_called()
            queue.assert_not_called()
        response, create, queue = self.start({'round': '5'}, can_export=False)
        self.assertEqual(response.status_code, 403)
        create.assert_not_called()

    def download(self, file_name, owned, can_export=True):
        request = self.factory.get('/mscc/export-download/%s/' % file_name)
        request.user = self.user
        with patch.object(mscc_views.ExportHistory.objects, 'filter') as history, \
                patch.object(mscc_views, 'reverse', side_effect=fake_reverse), \
                patch.object(bridging_exports, 'user_can_export_bridging', return_value=can_export), \
                patch.object(mscc_views, 'download_file') as download_file:
            history.return_value.exists.return_value = owned
            download_file.return_value = {}
            response = mscc_views.get_file(request, file_name)
        return response, history, download_file

    def test_dirasa_photo_archives_download_only_for_their_requester(self):
        file_name = PHOTO_EXPORT_PREFIX + '1234-abcd.zip'
        response, history, download_file = self.download(file_name, owned=True, can_export=False)
        self.assertEqual(response.status_code, 403)
        download_file.assert_not_called()
        with self.assertRaises(Http404):
            self.download(file_name, owned=False)
        response, history, download_file = self.download(file_name, owned=True)
        self.assertEqual(history.call_args.kwargs, {
            'created_by': self.user, 'status': 'done',
            'file_url': '/mscc/export-download/%s/' % file_name,
        })
        self.assertEqual(download_file.call_args.args, (file_name, 'output_file.zip'))
        self.assertIs(download_file.call_args.kwargs['request'].user, self.user)
        self.assertEqual(response['Cache-Control'], 'private, no-store')

    def test_shared_download_helper_refuses_dirasa_archives_without_a_requester(self):
        file_name = PHOTO_EXPORT_PREFIX + '1234-abcd.zip'
        with patch.object(backend_utils, 'ExportStorage') as storage:
            with self.assertRaises(Http404):
                backend_utils.download_file(file_name, 'output_file.zip')
            request = SimpleNamespace(user=self.user)
            with patch.object(bridging_exports, 'user_can_export_bridging', return_value=False):
                with self.assertRaises(Http404):
                    backend_utils.download_file(file_name, 'output_file.zip', request=request)
            storage.assert_not_called()


class BridgingExportTaskTests(SimpleTestCase):
    def run_export(self, registrations, can_export=True, filters=None):
        user = SimpleNamespace(pk=3, partner=None, partner_id=4)
        export = Mock(created_by=user, status='pending', file_url=None)
        queryset = Mock()
        queryset.iterator.return_value = iter(registrations)
        files = {}

        def save_file(name, content):
            files[name] = content.read()
            return name

        with patch.object(bridging_exports.ExportHistory.objects, 'select_related') as manager, \
                patch.object(bridging_exports, 'user_can_export_bridging', return_value=can_export), \
                patch.object(bridging_exports, 'scoped_bridging_registrations') as scoped, \
                patch.object(bridging_exports, 'filter_bridging_registrations', return_value=queryset) as filtered, \
                patch.object(bridging_exports, 'ExportStorage') as storage, \
                patch.object(bridging_exports, 'reverse', side_effect=fake_reverse), \
                patch.object(bridging_exports, '_notify_excel_export') as notify:
            manager.return_value.get.return_value = export
            storage.return_value.save.side_effect = save_file
            bridging_exports._generate_bridging_photo_export(9, filters or {'round': '5'})
        return export, files, notify, scoped, filtered

    def test_task_stores_a_zipped_workbook_with_photos_within_the_requesters_scope(self):
        registration = make_bridging(501, make_student(31), StoredPicture(portrait_bytes('red')))
        export, files, notify, scoped, filtered = self.run_export([registration])
        scoped.assert_called_once_with(export.created_by)
        self.assertEqual(filtered.call_args.args[1], {'round': '5'})
        name, archive_bytes = next(iter(files.items()))
        self.assertRegex(name, r'^bridging_photo_export_[0-9a-f-]{36}\.zip$')
        with zipfile.ZipFile(io.BytesIO(archive_bytes)) as archive:
            self.assertEqual(archive.namelist(), ['bridging_data.xlsx'])
            content = archive.read('bridging_data.xlsx')
        self.assertEqual(export.status, 'done')
        self.assertEqual(export.file_url, '/mscc/export-download/%s/' % name)
        rows = workbook_rows(content)
        self.assertEqual(rows[0][1]['Student ID'], '31')
        self.assertEqual(photo_colour(workbook_photos_by_row(content)[rows[0][0]]), (255, 0, 0))
        notify.assert_called_once_with(export, succeeded=True)

    def test_task_refuses_users_who_lost_their_export_role(self):
        export, files, notify, scoped, _ = self.run_export([], can_export=False)
        self.assertEqual(files, {})
        self.assertEqual(export.status, 'failed')
        scoped.assert_not_called()
        notify.assert_called_once_with(export, succeeded=False)


class SharedBridgingScopeTests(SimpleTestCase):
    """Execute the ORM's scope SQL against rows covering every access boundary."""

    def user(self, partner=None, school=None, groups=(), staff=False, superuser=False):
        return SimpleNamespace(
            is_authenticated=True, is_active=True, is_staff=staff,
            is_superuser=superuser, partner_id=partner, school_id=school,
            _group_names_cache=set(groups),
        )

    def visible(self, user):
        import sqlite3
        from django.core.exceptions import EmptyResultSet
        from .bridging_access import scope_bridging_queryset

        # Deliberately include another partner in the assigned school: a school
        # user's scope is the school, independently of their partner assignment.
        rows = [(1, 7, 10, 7), (2, 7, 11, 1), (3, 3, 20, 7),
                (4, 3, 21, 1), (5, 3, 22, 3), (6, 3, 23, 5),
                (7, 3, 24, 2), (8, 107, 30, 1), (9, 29, 40, 3),
                (10, 99, 10, 3), (11, 99, 50, 7)]
        queryset = scope_bridging_queryset(Bridging.objects.all(), user)
        try:
            sql, params = queryset.order_by().values_list('pk').query.sql_with_params()
        except EmptyResultSet:
            return set()
        with sqlite3.connect(':memory:') as database:
            table = Bridging._meta.db_table
            database.execute('CREATE TABLE "%s" (id INTEGER, partner_id INTEGER, school_id INTEGER, governorate_id INTEGER)' % table)
            database.executemany('INSERT INTO "%s" VALUES (?, ?, ?, ?)' % table, rows)
            return {row[0] for row in database.execute(sql.replace('%s', '?'), params)}

    def test_partner_exceptions_and_ordinary_partner_scope(self):
        for partner, expected in ((7, {1, 2, 3}), (107, {4, 8}),
                                  (29, {5, 6, 9}), (99, {10, 11})):
            with self.subTest(partner=partner):
                self.assertEqual(self.visible(self.user(partner=partner)), expected)

    def test_assigned_school_wins_over_every_partner_exception(self):
        for partner in (7, 107, 29, 99, None):
            with self.subTest(partner=partner):
                self.assertEqual(self.visible(self.user(partner=partner, school=10)), {1, 10})

    def test_unrestricted_roles_win_over_school_and_partner(self):
        for options in ({'staff': True}, {'superuser': True}, {'groups': ['CLM_BRIDGING_ALL']}):
            self.assertEqual(self.visible(self.user(partner=7, school=10, **options)), set(range(1, 12)))

    def test_no_assignment_and_inactive_users_have_no_rows(self):
        self.assertEqual(self.visible(self.user()), set())
        user = self.user(staff=True)
        user.is_active = False
        self.assertEqual(self.visible(user), set())

    def test_plain_excel_contains_data_without_opening_or_embedding_pictures(self):
        registration = make_bridging(501, make_student(31), StoredPicture(portrait_bytes('red')))
        with patch.object(registration.profile_picture, 'open', side_effect=AssertionError('Photo opened')):
            content = build_children_workbook([registration], profile=BRIDGING_PROFILE, include_photos=False)
        row = workbook_rows(content)[0][1]
        self.assertEqual(row['Registration ID'], '501')
        self.assertEqual(row['Student ID'], '31')
        self.assertNotIn('Photograph', row)
        self.assertNotIn('Photograph status', row)
        self.assertEqual(workbook_photos_by_row(content), {})

    def test_csv_school_parameter_cannot_replace_assigned_school(self):
        request = RequestFactory().get('/clm/bridging-school-export-data/99/', {'round': '5'})
        request.user = self.user(partner=29, school=10)
        sql, params = bridging_views._bridging_export_ids(request, school_id=99)
        self.assertIn(10, params)
        self.assertIn(99, params)
        self.assertNotIn(' OR ', sql)
        self.assertNotIn('governorate_id', sql)

    def test_excel_data_only_option_is_queued_and_invalid_option_is_rejected(self):
        tests = BridgingExportViewTests()
        tests.setUp()
        response, create, queue = tests.start({'round': '5', 'include_photos': 'no'})
        self.assertEqual(response.status_code, 200)
        self.assertFalse(queue.call_args.kwargs['include_photos'])
        response, create, queue = tests.start({'round': '5', 'include_photos': 'maybe'})
        self.assertEqual(response.status_code, 400)
        create.assert_not_called()
        queue.assert_not_called()
