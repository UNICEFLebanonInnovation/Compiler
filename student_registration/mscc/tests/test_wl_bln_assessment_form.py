import pytest
from types import SimpleNamespace
from decimal import Decimal

from student_registration.mscc.education_form import WLBLNAssessmentForm


def test_wl_bln_pre_form_computes_totals():
    form = WLBLNAssessmentForm(
        data={
            'programme_type': 'BLN Level 1',
            'english_letter_sound': 13,
            'english_familiar_words': 10,
            'english_sentence': 10,
            'english_dictation': 10,
            'french_letter_sound': 13,
            'french_familiar_words': 10,
            'french_sentence': 10,
            'french_dictation': 10,
            'arabic_letter_sound': 28,
            'arabic_alphabet_vowel': 5,
            'arabic_alphabet_long_vowel': 5,
            'arabic_familiar_words': 10,
            'arabic_sentence': 10,
            'arabic_dictation': 10,
            'math_natural_numbers': 10,
            'math_addition_words': 8,
            'math_subtraction': 4,
        },
        registry='1',
        programme_type='BLN Level 1',
        pre_post='pre',
    )

    assert form.is_valid(), form.errors
    assert form.cleaned_data['english_grade'] == Decimal('43')
    assert form.cleaned_data['french_grade'] == Decimal('43')
    assert form.cleaned_data['arabic_grade'] == Decimal('68')
    assert form.cleaned_data['math_grade'] == Decimal('22')


def test_wl_bln_post_form_computes_totals():
    form = WLBLNAssessmentForm(
        data={
            'programme_type': 'BLN Level 2',
            'english_letter_sound': 10,
            'english_familiar_words': 10,
            'english_paragraph': 25,
            'english_dictation': 10,
            'english_reading_comprehension': 10,
            'french_letter_sound': 10,
            'french_familiar_words': 10,
            'french_paragraph': 25,
            'french_dictation': 10,
            'french_reading_comprehension': 10,
            'arabic_letter_sound': 10,
            'arabic_alphabet_vowel': 5,
            'arabic_alphabet_long_vowel': 5,
            'arabic_familiar_words': 10,
            'arabic_paragraph': 20,
            'arabic_reading_comprehension': 10,
            'arabic_dictation': 10,
            'math_natural_numbers': 10,
            'math_addition_words': 10,
            'math_subtraction': 7,
            'math_multiplication': 5,
        },
        registry='1',
        programme_type='BLN Level 2',
        pre_post='post',
    )

    assert form.is_valid(), form.errors
    assert form.cleaned_data['english_grade'] == Decimal('65')
    assert form.cleaned_data['french_grade'] == Decimal('65')
    assert form.cleaned_data['arabic_grade'] == Decimal('70')
    assert form.cleaned_data['math_grade'] == Decimal('32')


def test_wl_bln_validates_component_maximums():
    form = WLBLNAssessmentForm(
        data={
            'programme_type': 'BLN Level 3',
            'english_letter_sound': 10,
            'english_familiar_words': 10,
            'english_paragraph': 21,
            'english_dictation': 10,
            'english_reading_comprehension': 14,
            'french_letter_sound': 10,
            'french_familiar_words': 10,
            'french_paragraph': 15,
            'french_dictation': 10,
            'french_reading_comprehension': 14,
            'arabic_letter_sound': 10,
            'arabic_alphabet_vowel': 5,
            'arabic_alphabet_long_vowel': 5,
            'arabic_familiar_words': 10,
            'arabic_paragraph': 15,
            'arabic_reading_comprehension': 14,
            'arabic_dictation': 10,
            'math_natural_numbers': 8,
            'math_addition_words': 8,
            'math_subtraction': 6,
            'math_multiplication': 6,
            'math_division': 4,
        },
        registry='1',
        programme_type='BLN Level 3',
        pre_post='pre',
    )

    assert not form.is_valid()
    assert 'english_paragraph' in form.errors


def test_wl_bln_allows_zero_for_visible_fields():
    form = WLBLNAssessmentForm(
        data={
            'programme_type': 'BLN Level 1',
            'english_letter_sound': 0,
            'english_familiar_words': 10,
            'english_sentence': 10,
            'english_dictation': 10,
            'french_letter_sound': 13,
            'french_familiar_words': 10,
            'french_sentence': 10,
            'french_dictation': 10,
            'arabic_letter_sound': 28,
            'arabic_alphabet_vowel': 5,
            'arabic_alphabet_long_vowel': 5,
            'arabic_familiar_words': 10,
            'arabic_sentence': 10,
            'arabic_dictation': 10,
            'math_natural_numbers': 10,
            'math_addition_words': 8,
            'math_subtraction': 4,
        },
        registry='1',
        programme_type='BLN Level 1',
        pre_post='pre',
    )

    assert form.is_valid(), form.errors
    assert form.cleaned_data['english_letter_sound'] == Decimal('0')


@pytest.mark.parametrize(
    "provide_french_language, visible_total, hidden_total",
    [
        ("Yes", "french_grade", "english_grade"),
        ("No", "english_grade", "french_grade"),
    ],
)
def test_wl_bln_shows_only_center_language_fields(provide_french_language, visible_total, hidden_total):
    request = SimpleNamespace(
        user=SimpleNamespace(
            center=SimpleNamespace(provide_french_language=provide_french_language)
        )
    )

    form = WLBLNAssessmentForm(
        registry='1',
        programme_type='BLN Level 1',
        pre_post='pre',
        request=request,
    )

    assert visible_total in form.programme_config
    assert hidden_total not in form.programme_config


def test_wl_bln_validates_only_visible_language_fields():
    request = SimpleNamespace(
        user=SimpleNamespace(
            center=SimpleNamespace(provide_french_language="Yes")
        )
    )

    form = WLBLNAssessmentForm(
        data={
            'programme_type': 'BLN Level 1',
            'french_letter_sound': 13,
            'french_familiar_words': 10,
            'french_sentence': 10,
            'french_dictation': 10,
            'arabic_letter_sound': 28,
            'arabic_alphabet_vowel': 5,
            'arabic_alphabet_long_vowel': 5,
            'arabic_familiar_words': 10,
            'arabic_sentence': 10,
            'arabic_dictation': 10,
            'math_natural_numbers': 10,
            'math_addition_words': 8,
            'math_subtraction': 4,
        },
        registry='1',
        programme_type='BLN Level 1',
        pre_post='pre',
        request=request,
    )

    assert form.is_valid(), form.errors
