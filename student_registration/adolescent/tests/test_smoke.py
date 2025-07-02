from student_registration.adolescent.apps import AdolescentConfig


def test_app_name():
    """Ensure adolescent app is registered correctly."""
    assert AdolescentConfig.name == 'student_registration.adolescent'
