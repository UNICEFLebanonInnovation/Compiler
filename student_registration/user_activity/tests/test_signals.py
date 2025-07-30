import json
from django.contrib.auth import get_user_model
from unittest.mock import patch

from student_registration.user_activity import set_current_user

User = get_user_model()


def test_model_change_logged(db):
    user = User.objects.create(username="logger")
    set_current_user(user)
    target = User.objects.create(username="target")
    with patch("student_registration.user_activity_signals.UserActivity.objects.create") as create_mock:
        target.first_name = "Bob"
        target.save()
    create_mock.assert_called_once()
    kwargs = create_mock.call_args.kwargs
    assert kwargs["username"] == "logger"
    changed = json.loads(kwargs["changed_data"])
    assert changed["first_name"]["after"] == "Bob"
    set_current_user(None)
