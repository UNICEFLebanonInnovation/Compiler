from types import SimpleNamespace
from unittest.mock import patch

import pytest

from student_registration.mscc.education_form import WLBLNAssessmentForm
from student_registration.mscc.rs_assessment_config import RS_PROGRAMME_CONFIG


@pytest.mark.parametrize('grade,totals', [
    (1, (34, 50, 40, 40)), (2, (34, 50, 40, 40)), (3, (34, 50, 40, 40)),
    (4, (58, 34, 32, 32)), (5, (58, 34, 32, 32)), (6, (58, 34, 32, 32)),
    (7, (40, 40, 42, 40)), (8, (50, 40, 42, 40)), (9, (60, 40, 42, 40)),
])
@pytest.mark.parametrize('language', ['english', 'french'])
@pytest.mark.parametrize('period', ['pre', 'post'])
def test_rs_components_validate_and_compute_totals(grade, totals, language, period):
    programme = 'RS Grade {}'.format(grade)
    config = RS_PROGRAMME_CONFIG[programme]
    expected = dict(zip(['math_grade', 'arabic_grade', 'english_grade', 'french_grade'], totals))
    for total_field, subject in config.items():
        assert subject['total'] == expected[total_field]
        assert sum(component[2] for component in subject['components']) == expected[total_field]
    request = SimpleNamespace(user=SimpleNamespace(center=SimpleNamespace(
        provide_french_language='Yes' if language == 'french' else 'No')))
    kwargs = dict(registry='1', programme_type=programme, pre_post=period, request=request)
    if period == 'post':
        kwargs['instance'] = '2'
    visible = {key: subject for key, subject in config.items()
               if not key.startswith('english_' if language == 'french' else 'french_')}
    data = {field: maximum for subject in visible.values()
            for field, label, maximum in subject['components']}
    data.update({key: 999 for key in visible})
    form = WLBLNAssessmentForm(data=data, **kwargs)
    assert form.is_valid(), form.errors
    for key, subject in visible.items():
        assert form.cleaned_data[key] == expected[key]
        for field, label, maximum in subject['components']:
            assert not form.fields[field].widget.is_hidden
            invalid = dict(data, **{field: maximum + 1})
            bad_form = WLBLNAssessmentForm(data=invalid, **kwargs)
            assert not bad_form.is_valid()
            assert field in bad_form.errors
    zeroes = {field: 0 for subject in visible.values() for field, _, _ in subject['components']}
    assert WLBLNAssessmentForm(data=zeroes, **kwargs).is_valid()
    field = next(iter(zeroes))
    zeroes[field] = -1
    assert not WLBLNAssessmentForm(data=zeroes, **kwargs).is_valid()
    del zeroes[field]
    assert not WLBLNAssessmentForm(data=zeroes, **kwargs).is_valid()
    # JSON persistence retains component scores and calculated totals for the requested period.
    instance = SimpleNamespace(pre_test={}, post_test={})
    instance.save = lambda: None
    with patch('student_registration.mscc.education_form.EducationProgrammeWLAssessment.objects') as objects, \
            patch('student_registration.mscc.education_form.messages.success'):
        objects.create.return_value = instance
        objects.get.return_value = instance
        form.save(request=request, registry='1', programme_type=programme, pre_post=period,
                  instance='2' if period == 'post' else None)
    scores = instance.post_test if period == 'post' else instance.pre_test
    assert scores['math_grade'] == expected['math_grade']
    assert instance.programme_type == programme


def test_workbook_specific_components():
    def components(grade, subject):
        return {name: maximum for name, _, maximum in
                RS_PROGRAMME_CONFIG['RS Grade {}'.format(grade)][subject + '_grade']['components']}
    assert components(7, 'math') == {
        'math_powers': 3, 'math_prime_numbers': 6, 'math_fractions_and_decimals': 3,
        'math_algebraic_expressions_and_equations': 6, 'math_signed_numbers': 3,
        'math_proportionality': 3, 'math_geometry': 16,
    }
    assert components(8, 'math')['math_geometry'] == 21
    assert components(9, 'math')['math_geometry'] == 25
    assert 'english_sentence_dictation' in components(3, 'english')
    assert 'english_picture_description' in components(3, 'english')
    assert 'english_word_dictation' not in components(3, 'english')
