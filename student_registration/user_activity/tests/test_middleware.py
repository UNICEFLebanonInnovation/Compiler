import json
from django.test import RequestFactory
from django.http import HttpResponse
from django.contrib.auth import get_user_model
from unittest.mock import patch

from student_registration.user_activity import UserActivityMiddleware
from student_registration.backends.models import UserActivity


User = get_user_model()


def get_response(_request):
    return HttpResponse("ok")


def make_user(username="bob"):
    return User.objects.create(username=username)


def test_logs_get_request_authenticated_user(db):
    request = RequestFactory().get("/sample/?q=1")
    request.user = make_user()
    middleware = UserActivityMiddleware(get_response)
    with patch("student_registration.user_activity.UserActivity.objects.create") as create_mock:
        response = middleware(request)
    assert response.status_code == 200
    create_mock.assert_called_once()
    kwargs = create_mock.call_args.kwargs
    assert kwargs["username"] == "bob"
    assert kwargs["path"] == "/sample/"
    assert kwargs["method"] == "GET"
    data = json.loads(kwargs["data"])
    assert data["q"] == ["1"]


def test_logs_json_body(db):
    payload = {"foo": "bar"}
    request = RequestFactory().post(
        "/api/", data=json.dumps(payload), content_type="application/json"
    )
    request.user = make_user()
    middleware = UserActivityMiddleware(get_response)
    with patch("student_registration.user_activity.UserActivity.objects.create") as create_mock:
        middleware(request)
    create_mock.assert_called_once()
    data = json.loads(create_mock.call_args.kwargs["data"])
    assert data["foo"] == "bar"


def test_handles_long_paths(db):
    long_path = "/sample/" + "a" * 300
    request = RequestFactory().get(long_path)
    request.user = make_user()
    middleware = UserActivityMiddleware(get_response)
    response = middleware(request)
    assert response.status_code == 200
    activity = UserActivity.objects.get()
    assert activity.path == long_path


def test_logs_admin_request_for_authenticated_user(db):
    request = RequestFactory().get("/admin/backends/useractivity/")
    request.user = make_user(username="admin-user")
    middleware = UserActivityMiddleware(get_response)
    with patch("student_registration.user_activity.UserActivity.objects.create") as create_mock:
        response = middleware(request)
    assert response.status_code == 200
    create_mock.assert_called_once()
    kwargs = create_mock.call_args.kwargs
    assert kwargs["username"] == "admin-user"
    assert kwargs["path"] == "/admin/backends/useractivity/"
    data = json.loads(kwargs["data"])
    assert data["is_admin"] is True
    assert data["status_code"] == 200


def test_redacts_sensitive_admin_post_data(db):
    request = RequestFactory().post(
        "/admin/users/user/1/change/",
        data={
            "csrfmiddlewaretoken": "csrf-value",
            "username": "student",
            "password": "secret-value",
        },
    )
    request.user = make_user(username="admin-user")
    middleware = UserActivityMiddleware(get_response)
    with patch("student_registration.user_activity.UserActivity.objects.create") as create_mock:
        middleware(request)
    create_mock.assert_called_once()
    data = json.loads(create_mock.call_args.kwargs["data"])
    assert data["username"] == ["student"]
    assert data["csrfmiddlewaretoken"] == "********"
    assert data["password"] == "********"
