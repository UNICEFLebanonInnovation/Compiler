import io
import os

from PIL import Image, ImageDraw, ImageFont, ImageOps, features


CARD_SIZE = (1200, 660)
FONT_CANDIDATES = (
    os.path.join(os.path.dirname(__file__), '..', 'static', 'fonts', 'DejaVuSans.ttf'),
    '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
)
BOLD_FONT_CANDIDATES = (
    os.path.join(os.path.dirname(__file__), '..', 'static', 'fonts', 'DejaVuSans-Bold.ttf'),
    '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',
)
HAS_RAQM = features.check('raqm')


def _font(size, bold=False):
    candidates = BOLD_FONT_CANDIDATES if bold else FONT_CANDIDATES
    for path in candidates:
        if os.path.exists(path):
            layout_engine = ImageFont.Layout.RAQM if HAS_RAQM else ImageFont.Layout.BASIC
            return ImageFont.truetype(path, size, layout_engine=layout_engine)
    return ImageFont.load_default()


def _centered(draw, text, y, font, direction=None):
    text = str(text or '-')
    kwargs = {'direction': direction} if direction and HAS_RAQM else {}
    box = draw.textbbox((0, 0), text, font=font, **kwargs)
    draw.text(((CARD_SIZE[0] - (box[2] - box[0])) / 2, y), text, fill='black', font=font, **kwargs)


def _profile_photo(registration):
    photo = registration.student.std_image
    if not photo:
        return None
    try:
        photo.open('rb')
        with Image.open(photo) as source:
            return ImageOps.fit(ImageOps.exif_transpose(source).convert('RGB'), (230, 230), Image.Resampling.LANCZOS)
    except (OSError, ValueError):
        return None
    finally:
        try:
            photo.close()
        except (AttributeError, ValueError):
            pass


def render_card(registration):
    """Render one Dirasa child card in the landscape layout used for printing."""
    card = Image.new('RGB', CARD_SIZE, 'white')
    draw = ImageDraw.Draw(card)
    regular = _font(27)
    bold = _font(28, bold=True)
    heading = _font(31, bold=True)

    photo = _profile_photo(registration)
    photo_box = (34, 35, 264, 265)
    if photo:
        card.paste(photo, photo_box[:2])
    else:
        draw.rectangle(photo_box, fill='#4775c5', outline='#244d92', width=3)
        placeholder = _font(24)
        draw.text((99, 136), 'picture', fill='white', font=placeholder)

    student = registration.student
    _centered(draw, registration.round.name if registration.round else '-', 36, heading)
    _centered(draw, 'الامتحان الاستثنائي لطلاب التعليم غير النظامي', 82, regular, direction='rtl')

    details = (
        'ID: {}'.format(registration.internal_number or student.number or student.id),
        'NGO: {}'.format(registration.partner.name if registration.partner else '-'),
        'الاسم الثلاثي: {}'.format(student.full_name),
        'Date of Birth: {}'.format(student.birthday),
        'Place of Birth: {}'.format(student.place_of_birth or '-'),
        'Nationality: {}'.format(student.nationality_name_en or student.nationality_name()),
        'Governorate: {}'.format(registration.governorate.name if registration.governorate else '-'),
        'Physical difficulties: {}'.format(
            registration.disability.name_en or registration.disability.name
            if registration.disability else 'No'
        ),
    )
    y = 137
    for index, detail in enumerate(details):
        direction = 'rtl' if index == 2 else None
        _centered(draw, detail, y, bold, direction=direction)
        y += 55

    draw.rectangle((1, 1, CARD_SIZE[0] - 2, CARD_SIZE[1] - 2), outline='#d2d2d2', width=2)
    return card


def build_cards_pdf(registrations):
    """Return a multi-page PDF with one printable ID card per page."""
    cards = [render_card(registration) for registration in registrations]
    if not cards:
        return None

    output = io.BytesIO()
    first, remaining = cards[0], cards[1:]
    first.save(
        output,
        format='PDF',
        save_all=True,
        append_images=remaining,
        resolution=300,
        quality=85,
        title='Dirasa child ID cards',
    )
    output.seek(0)
    for card in cards:
        card.close()
    return output
