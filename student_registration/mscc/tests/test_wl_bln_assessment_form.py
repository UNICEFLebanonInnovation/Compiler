import pytest

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
    assert form.cleaned_data['english_grade'] == 43
    assert form.cleaned_data['french_grade'] == 43
    assert form.cleaned_data['arabic_grade'] == 68
    assert form.cleaned_data['math_grade'] == 22


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
    assert form.cleaned_data['english_grade'] == 65
    assert form.cleaned_data['french_grade'] == 65
    assert form.cleaned_data['arabic_grade'] == 70
    assert form.cleaned_data['math_grade'] == 32


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


def test_wl_bln_rejects_zero_for_visible_fields():
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

    assert not form.is_valid()
    assert 'english_letter_sound' in form.errors
