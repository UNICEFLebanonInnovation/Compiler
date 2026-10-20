"""The shared 7–10-year-old photograph roster for Makani and Dirasa."""

import datetime
import io

import xlsxwriter
from django.http import HttpResponse, HttpResponseBadRequest
from django.utils import timezone
from PIL import Image

from student_registration.mscc.document_exports import load_registration_photo, _text, _date_of_birth


HEADERS = (
    'Photograph', 'Student full name', 'Date of birth', 'First name',
    'Last name', 'Father name', 'Mother fullname', 'Sex', 'Birthday year',
    'Birthday month', 'Birthday day', 'Nationality', 'Governorate', 'District',
    'Cadaster', 'Disability', 'Partner', 'Phone Number', 'Main Language',
    'Math Language', 'ID',
)


def birth_date(child):
    if child is None:
        return None
    try:
        return datetime.date(int(child.birthday_year), int(child.birthday_month),
                             int(child.birthday_day))
    except (TypeError, ValueError):
        return None


def roster_values(registration, programme, birthday):
    makani = programme == 'makani'
    child = registration.child if makani else registration.student
    location = registration.center if makani else registration
    names = [child.first_name, child.father_name, child.last_name]
    language = getattr(registration, 'language', '') or ''
    if language and hasattr(registration, 'get_language_display'):
        language = registration.get_language_display()
    return (
        '', ' '.join(str(name).strip() for name in names if name),
        birthday.isoformat() if birthday else _date_of_birth(child), child.first_name, child.last_name, child.father_name,
        child.mother_fullname, child.gender if makani else child.sex,
        child.birthday_year, child.birthday_month, child.birthday_day,
        child.nationality, getattr(location, 'governorate', None),
        getattr(location, 'caza' if makani else 'district', None),
        getattr(location, 'cadaster', None),
        child.disability if makani else registration.disability,
        registration.partner,
        child.first_phone_number if makani else registration.phone_number,
        language, language, registration.pk,
    )


def build_photo_roster(registrations, programme, today=None, unavailable_only=False, all_ages=False):
    """Export ages 7–10 by default, or every age without requiring a valid DOB.

    One row is one visible registration; missing photos do not remove children.
    Text is written literally so names and telephone numbers remain unchanged.
    The unavailable-only report excludes readable photos and uses their saved
    filenames in the Photograph column; absent uploads retain the missing label.
    """
    if today is None:
        now = timezone.now()
        today = (timezone.localtime(now) if timezone.is_aware(now) else now).date()
    output = io.BytesIO()
    workbook = xlsxwriter.Workbook(output, {
        'in_memory': True, 'strings_to_formulas': False, 'strings_to_urls': False,
    })
    sheet_name = 'All ages' if all_ages else 'Children aged 7-10'
    sheet = workbook.add_worksheet('Unavailable photos' if unavailable_only else sheet_name)
    heading = workbook.add_format({'bold': True, 'text_wrap': True,
                                  'bg_color': '#164A68', 'font_color': '#FFFFFF'})
    body = workbook.add_format({'text_wrap': True, 'valign': 'top'})
    sheet.freeze_panes(1, 2)
    sheet.set_row(0, 32)
    sheet.set_column(0, len(HEADERS) - 1, 22)
    sheet.set_column(0, 0, 20)
    for column, label in enumerate(HEADERS):
        sheet.write_string(0, column, label, heading)
    row = 0
    for registration in registrations:
        child = registration.child if programme == 'makani' else registration.student
        if child is None:
            continue
        birthday = birth_date(child)
        if not all_ages:
            if birthday is None:
                continue
            age = today.year - birthday.year - ((today.month, today.day) < (birthday.month, birthday.day))
            if not 7 <= age <= 10:
                continue
        photo, photo_status = load_registration_photo(registration)
        if unavailable_only and photo:
            continue
        row += 1
        if row >= 1048576:
            raise ValueError('The export exceeds the Excel worksheet row limit.')
        sheet.set_row(row, 108)
        for column, value in enumerate(roster_values(registration, programme, birthday)):
            sheet.write_string(row, column, _text(value), body)
        if photo:
            image_data = io.BytesIO(photo)
            with Image.open(image_data) as image:
                scale = min(112 / image.width, 136 / image.height, 1)
            sheet.insert_image(row, 0, 'photograph.png', {
                'image_data': image_data, 'x_offset': 4, 'y_offset': 4,
                'x_scale': scale, 'y_scale': scale, 'positioning': 1,
            })
        else:
            picture = registration.profile_picture
            filename = picture.name.rsplit('/', 1)[-1] if picture else ''
            sheet.write_string(row, 0, _text(filename) if unavailable_only and filename else photo_status, body)
    sheet.autofilter(0, 0, row, len(HEADERS) - 1)
    workbook.close()
    return output.getvalue()


class ChildPhotoExportMixin:
    """Reuse the list's role scope and filters, without its page size."""

    unavailable_only = False
    all_ages = False

    def get_context_data(self, **kwargs):
        return kwargs

    def render_to_response(self, context, **response_kwargs):
        if self.filterset.is_bound and not self.filterset.is_valid():
            return HttpResponseBadRequest('Please correct the list filters before exporting.')
        content = build_photo_roster(self.object_list.iterator(chunk_size=200), self.programme,
                                    unavailable_only=self.unavailable_only, all_ages=self.all_ages)
        response = HttpResponse(content, content_type=(
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'))
        report = 'unavailable-photos' if self.unavailable_only else 'children'
        age_range = 'all-ages' if self.all_ages else '7-10'
        response['Content-Disposition'] = 'attachment; filename="{}-{}-{}.xlsx"'.format(self.programme, report, age_range)
        response['Cache-Control'] = 'private, no-store'
        return response
