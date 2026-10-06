# -*- coding: utf-8 -*-
"""Dirasa (Bridging) child profile ID cards: card data and server-side PDF rendering."""
from __future__ import absolute_import, unicode_literals

import io
import logging
from pathlib import Path

from arabic_reshaper import ArabicReshaper
from arabic_reshaper.ligatures import LIGATURES
from bidi import get_display
from reportlab.lib.pagesizes import A5, landscape
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

logger = logging.getLogger(__name__)

SUBTITLE = 'الامتحان الاستثنائي لطلاب التعليم الغير نظامي'

# DejaVu Sans ships Arabic presentation forms, so one font covers both scripts.
FONTS_DIR = Path(__file__).resolve().parents[1] / 'static' / 'fonts'
FONT_REGULAR = 'DejaVuSans'
FONT_BOLD = 'DejaVuSans-Bold'

PAGE_SIZE = landscape(A5)
MARGIN = 8 * mm
PHOTO_WIDTH = 45 * mm
PHOTO_HEIGHT = 40 * mm
PHOTO_COLOR = (0x44 / 255.0, 0x72 / 255.0, 0xC4 / 255.0)
LINE_SPACING = 1.75


def _first_non_empty(*values):
    for value in values:
        if value:
            return value
    return ''


def _date_part(value):
    """Birthday day/month/year are stored as strings and default to 0 when unknown."""
    value = str(value or '').strip()
    return '' if value == '0' else value


def bridging_profile_id_card(bridging):
    """Collect the fields printed on a child's Dirasa profile ID card."""
    student = bridging.student
    full_name = ''
    birthday = ''
    place_of_birth = ''
    nationality = ''
    if student:
        full_name = ' '.join(
            part for part in (student.first_name, student.father_name, student.last_name) if part
        )
        day = _date_part(student.birthday_day)
        month = _date_part(student.birthday_month)
        year = _date_part(student.birthday_year)
        if day and month and year:
            birthday = '{}/{}/{}'.format(day, month, year[-2:])
        place_of_birth = student.place_of_birth or ''
        if student.nationality:
            nationality = _first_non_empty(student.nationality.name_en, student.nationality.name)

    governorate = ''
    if bridging.governorate:
        governorate = _first_non_empty(bridging.governorate.name_en, bridging.governorate.name)

    disability = bridging.disability
    physical_difficulties = _first_non_empty(disability.name_en, disability.name) if disability else 'No'

    return {
        'round': bridging.round.name if bridging.round else '',
        'id': bridging.id,
        'ngo': bridging.partner.name if bridging.partner else '',
        'full_name': full_name,
        'birthday': birthday,
        'place_of_birth': place_of_birth,
        'nationality': nationality,
        'governorate': governorate,
        'physical_difficulties': physical_difficulties,
        'has_picture': bool(bridging.profile_picture),
    }


def card_lines(card):
    """The text lines of a card, top to bottom, as (text, font, size)."""
    return [
        (card['round'], FONT_BOLD, 16),
        (SUBTITLE, FONT_BOLD, 9),
        ('ID: {}'.format(card['id']), FONT_BOLD, 13),
        ('NGO: {}'.format(card['ngo']), FONT_BOLD, 13),
        ('الاسم الثلاثي: {}'.format(card['full_name']), FONT_BOLD, 13),
        ('Date of Birth: {}'.format(card['birthday']), FONT_BOLD, 13),
        ('Place of Birth: {}'.format(card['place_of_birth']), FONT_BOLD, 13),
        ('Nationality: {}'.format(card['nationality']), FONT_BOLD, 13),
        ('Governorate: {}'.format(card['governorate']), FONT_BOLD, 13),
        ('Physical difficulties: {}'.format(card['physical_difficulties']), FONT_BOLD, 13),
    ]


_reshaper = None


def register_fonts():
    if FONT_BOLD not in pdfmetrics.getRegisteredFontNames():
        pdfmetrics.registerFont(TTFont(FONT_REGULAR, str(FONTS_DIR / 'DejaVuSans.ttf')))
        pdfmetrics.registerFont(TTFont(FONT_BOLD, str(FONTS_DIR / 'DejaVuSans-Bold.ttf')))


def _reshaper_for_font():
    """A reshaper that only emits ligature glyphs the bundled font can draw.

    arabic_reshaper enables ligatures such as "الله" (U+FDF2) by default, which
    DejaVu Sans lacks and would print as a missing-glyph box.
    """
    global _reshaper
    if _reshaper is None:
        register_fonts()
        glyphs = pdfmetrics.getFont(FONT_BOLD).face.charToGlyph
        configuration = {'delete_harakat': False, 'support_ligatures': True}
        for name, (_, forms) in LIGATURES:
            configuration[name] = all(ord(char) in glyphs for form in forms for char in form)
        _reshaper = ArabicReshaper(configuration=configuration)
    return _reshaper


def shape_text(text):
    """Join Arabic letters and reorder right-to-left runs so the PDF shows them correctly.

    Latin-only text comes back unchanged.
    """
    text = '' if text is None else str(text)
    return get_display(_reshaper_for_font().reshape(text))


def read_profile_picture(bridging):
    """Raw bytes of the child's uploaded photo, or None when missing or unreadable."""
    if not bridging.profile_picture:
        return None
    try:
        with bridging.profile_picture.open('rb') as fh:
            return fh.read()
    except Exception:
        logger.warning('Could not read profile picture of Bridging %s', bridging.pk, exc_info=True)
        return None


def _fit_font_size(pdf, text, font, size, max_width, minimum=7):
    while size > minimum and pdf.stringWidth(text, font, size) > max_width:
        size -= 1
    return size


def draw_card(pdf, card, photo_bytes=None):
    """Draw one profile ID card on the current page of ``pdf``."""
    width, height = PAGE_SIZE

    pdf.setLineWidth(0.8)
    pdf.setStrokeColorRGB(0, 0, 0)
    pdf.rect(MARGIN / 2, MARGIN / 2, width - MARGIN, height - MARGIN)

    photo_x = MARGIN
    photo_y = height - MARGIN - PHOTO_HEIGHT
    pdf.setFillColorRGB(*PHOTO_COLOR)
    pdf.rect(photo_x, photo_y, PHOTO_WIDTH, PHOTO_HEIGHT, stroke=0, fill=1)
    drawn = False
    if photo_bytes:
        try:
            pdf.drawImage(ImageReader(io.BytesIO(photo_bytes)), photo_x, photo_y, PHOTO_WIDTH, PHOTO_HEIGHT,
                          preserveAspectRatio=True, anchor='c', mask='auto')
            drawn = True
        except Exception:
            logger.warning('Could not draw profile picture of Bridging %s', card['id'], exc_info=True)
    if not drawn:
        pdf.setFillColorRGB(1, 1, 1)
        pdf.setFont(FONT_REGULAR, 9)
        pdf.drawCentredString(photo_x + PHOTO_WIDTH / 2, photo_y + PHOTO_HEIGHT / 2 - 3, 'picture')

    pdf.setFillColorRGB(0, 0, 0)
    centre = width / 2
    cursor = height - MARGIN - 20 * mm
    for text, font, size in card_lines(card):
        shaped = shape_text(text)
        # Lines level with the photo must not run into it.
        beside_photo = cursor > photo_y
        max_width = (width - 2 * (PHOTO_WIDTH + MARGIN + 4 * mm)) if beside_photo else (width - 2 * MARGIN)
        size = _fit_font_size(pdf, shaped, font, size, max_width)
        pdf.setFont(font, size)
        pdf.drawCentredString(centre, cursor, shaped)
        cursor -= max(size, 12) * LINE_SPACING


def build_profile_ids_pdf(registrations):
    """One PDF with a profile ID card per registration, each on its own A5 landscape page."""
    register_fonts()
    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=PAGE_SIZE)
    pdf.setTitle('Dirasa profile IDs')
    pdf.setAuthor('BMA')

    count = 0
    for bridging in registrations:
        draw_card(pdf, bridging_profile_id_card(bridging), read_profile_picture(bridging))
        pdf.showPage()
        count += 1

    if count == 0:
        pdf.setFont(FONT_REGULAR, 12)
        pdf.drawCentredString(PAGE_SIZE[0] / 2, PAGE_SIZE[1] / 2, 'No children to generate.')
        pdf.showPage()

    pdf.save()
    return buffer.getvalue()
