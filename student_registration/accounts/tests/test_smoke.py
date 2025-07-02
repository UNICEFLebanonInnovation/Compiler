from student_registration.accounts.apps import AccountsConfig


def test_app_name():
    """Ensure the accounts app is properly configured."""
    assert AccountsConfig.name == 'student_registration.accounts'
