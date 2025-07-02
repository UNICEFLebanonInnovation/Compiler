from student_registration.youth import utils


class Dummy:
    pass


def test_to_array_simple():
    """Ensure to_array extracts attributes properly."""
    obj = Dummy()
    obj.name = 'foo'
    result = utils.to_array(['name'], obj)
    assert result == {'name': 'foo'}
