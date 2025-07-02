import pytest
from django.core.exceptions import ValidationError
from student_registration.mscc.utils import validate_date


def test_validate_date_ok():
    assert validate_date('2024-05-01').isoformat() == '2024-05-01'


def test_validate_date_error():
    with pytest.raises(ValidationError):
        validate_date('invalid')
