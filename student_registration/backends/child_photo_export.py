"""Shared photograph rosters for Makani and Dirasa."""

import datetime
import io

import xlsxwriter
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseNotAllowed
from django.shortcuts import redirect, render
from django.utils import timezone
from PIL import Image

from student_registration.mscc.document_exports import load_registration_photo, _text, _date_of_birth, PHOTO_UNAVAILABLE


HEADERS = (
    'Photograph', 'Student full name', 'Date of birth', 'First name',
    'Last name', 'Father name', 'Mother fullname', 'Sex', 'Birthday year',
    'Birthday month', 'Birthday day', 'Nationality', 'Governorate', 'District',
    'Cadaster', 'Disability', 'Partner', 'Phone Number', 'Main Language',
    'Math Language', 'ID',
)
MAKANI_EXTRA_HEADERS = ('Grading/level', 'Age')


def birth_date(child):
    if child is None:
        return None
    try:
        return datetime.date(int(child.birthday_year), int(child.birthday_month),
                             int(child.birthday_day))
    except (TypeError, ValueError):
        return None


def roster_values(registration, programme, birthday, today):
    makani = programme == 'makani'
    child = registration.child if makani else registration.student
    location = registration.center if makani else registration
    names = [child.first_name, child.father_name, child.last_name]
    language = getattr(registration, 'language', '') or ''
    if makani:
        language = ('French' if getattr(location, 'provide_french_language', None) == 'Yes'
                    else 'English') if location is not None else ''
    elif language and hasattr(registration, 'get_language_display'):
        language = registration.get_language_display()
    values = (
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
    if makani:
        manager = getattr(registration, 'education_service', None)
        # The list prefetches these services in ID order. Reuse that cache
        # rather than querying .last() for each of thousands of registrations.
        services = list(manager.all()) if manager is not None else []
        level = services[-1].get_education_program_display() if services else ''
        age = ''
        if birthday and birthday <= today:
            age = today.year - birthday.year - ((today.month, today.day) < (birthday.month, birthday.day))
        values += (level, age)
    return values


def build_photo_roster(registrations, programme, today=None, unavailable_only=False, all_ages=False):
    """Export ages 7–10 by default, or every age without requiring a valid DOB.

    One row is one visible registration; missing photos do not remove children.
    Text is written literally so names and telephone numbers remain unchanged.
    The unavailable-only report excludes readable photos and uses their saved
    filenames in the Photograph column; blank photo fields are excluded.
    """
    if today is None:
        now = timezone.now()
        today = (timezone.localtime(now) if timezone.is_aware(now) else now).date()
    output = io.BytesIO()
    headers = HEADERS + MAKANI_EXTRA_HEADERS if programme == 'makani' else HEADERS
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
    sheet.set_column(0, len(headers) - 1, 22)
    sheet.set_column(0, 0, 20)
    for column, label in enumerate(headers):
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
        if unavailable_only and not registration.profile_picture:
            continue
        photo, photo_status = load_registration_photo(registration)
        if unavailable_only and photo_status != PHOTO_UNAVAILABLE:
            continue
        row += 1
        if row >= 1048576:
            raise ValueError('The export exceeds the Excel worksheet row limit.')
        sheet.set_row(row, 108)
        for column, value in enumerate(roster_values(registration, programme, birthday, today)):
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
    sheet.autofilter(0, 0, row, len(headers) - 1)
    workbook.close()
    return output.getvalue()


class ChildPhotoExportMixin:
    """Reuse the list's role scope and filters, without its page size."""

    unavailable_only = False
    all_ages = False

    def get_context_data(self, **kwargs):
        return kwargs

    def post(self, request, *args, **kwargs):
        if not self.all_ages:
            return HttpResponseNotAllowed(['GET'])
        return self.get(request, *args, **kwargs)

    def render_to_response(self, context, **response_kwargs):
        if self.filterset.is_bound and not self.filterset.is_valid():
            return HttpResponseBadRequest('Please correct the list filters before exporting.')
        if self.unavailable_only:
            self.object_list = self.object_list.exclude(profile_picture='').exclude(profile_picture__isnull=True)
        if self.all_ages:
            if self.request.method == 'POST':
                from .photo_batches import create_job
                job = create_job(self.request.user, self.programme, self.object_list,
                                 dict(self.request.GET.lists()), unavailable_only=self.unavailable_only)
                return redirect('backends:photo_batch_progress', job_id=job.pk)
            return render(self.request, 'backends/photo_batch_start.html', {
                'module_base': 'mscc/base.html' if self.programme == 'makani' else 'clm/base.html',
                'unavailable_only': self.unavailable_only,
            })
        content = build_photo_roster(self.object_list.iterator(chunk_size=200), self.programme,
                                    unavailable_only=self.unavailable_only, all_ages=self.all_ages)
        response = HttpResponse(content, content_type=(
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'))
        report = 'unavailable-photos' if self.unavailable_only else 'children'
        age_range = 'all-ages' if self.all_ages else '7-10'
        response['Content-Disposition'] = 'attachment; filename="{}-{}-{}.xlsx"'.format(self.programme, report, age_range)
        response['Cache-Control'] = 'private, no-store'
        return response
