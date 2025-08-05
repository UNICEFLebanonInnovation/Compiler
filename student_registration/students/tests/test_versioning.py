import pytest
import reversion
from reversion.models import Version
from student_registration.students.models import Student


@pytest.mark.django_db
def test_student_revisions_created():
    with reversion.create_revision():
        student = Student.objects.create(
            first_name='A',
            father_name='B',
            last_name='C',
            mother_fullname='D',
            sex='Male',
            birthday_day='1',
            birthday_month='1',
            birthday_year='2000',
        )
    assert Version.objects.get_for_object(student).count() == 1
    with reversion.create_revision():
        student.first_name = 'Z'
        student.save()
    assert Version.objects.get_for_object(student).count() == 2
