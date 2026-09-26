from types import SimpleNamespace

from django.test import SimpleTestCase

from .id_cards import CARD_SIZE, build_cards_pdf, render_card

# Create your tests here.


class DirasaIdCardTests(SimpleTestCase):
    def registration(self):
        student = SimpleNamespace(
            std_image=None,
            number='2026-0002',
            id=2,
            full_name='ريهام المشتق علي المشتق',
            birthday='5/5/2014',
            place_of_birth='Hazmieh',
            nationality_name_en='Syrian',
            nationality_name=lambda: 'Syrian',
        )
        return SimpleNamespace(
            student=student,
            round=SimpleNamespace(name='2026-2027'),
            internal_number='2',
            partner=SimpleNamespace(name='SAVE'),
            governorate=SimpleNamespace(name='Baalbek-Hermel'),
            disability=SimpleNamespace(name_en='No', name='No'),
        )

    def test_renders_landscape_card_without_photo(self):
        card = render_card(self.registration())

        self.assertEqual(card.size, CARD_SIZE)
        self.assertEqual(card.mode, 'RGB')

    def test_builds_one_pdf_page_per_child(self):
        registration = self.registration()
        pdf = build_cards_pdf([registration, registration]).read()

        self.assertTrue(pdf.startswith(b'%PDF'))
        self.assertGreater(len(pdf), 1000)
