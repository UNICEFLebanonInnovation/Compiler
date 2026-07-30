import json
from unittest.mock import patch

from django.test import RequestFactory

from student_registration.youth import utils, views


class Dummy:
    pass


def test_to_array_simple():
    """Ensure to_array extracts attributes properly."""
    obj = Dummy()
    obj.name = 'foo'
    result = utils.to_array(['name'], obj)
    assert result == {'name': 'foo'}


@patch('student_registration.youth.views.ProgramDocumentIndicator.objects')
@patch('student_registration.youth.views.SubProgram.objects')
def test_save_indicators_requires_available_sub_indicator(
    sub_program_objects, indicator_objects
):
    sub_program_objects.filter.return_value.values_list.return_value = [1]
    request = RequestFactory().post(
        '/program/program-document-indicators-save/',
        data=json.dumps({
            'indicators': [{
                'id': None,
                'program_document_id': 10,
                'master_indicator': '1',
                'sub_indicator': '',
                'baseline': '',
                'target': '5',
            }],
            'deleted_ids': [99],
        }),
        content_type='application/json',
    )

    response = views.save_indicators(request)

    assert response.status_code == 400
    assert json.loads(response.content.decode('utf-8')) == {
        'error': 'Sub indicator is required for the selected master indicator.'
    }
    indicator_objects.filter.assert_not_called()
