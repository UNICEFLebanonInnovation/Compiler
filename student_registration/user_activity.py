# middleware/user_activity.py
import json
import logging

from django.utils.deprecation import MiddlewareMixin

from student_registration.backends.models import UserActivity

logger = logging.getLogger(__name__)

SENSITIVE_FIELDS = {
    "csrfmiddlewaretoken",
    "password",
    "password1",
    "password2",
    "old_password",
    "new_password",
    "new_password1",
    "new_password2",
    "token",
    "key",
    "secret",
}


class UserActivityMiddleware(MiddlewareMixin):
    """Middleware to log user activity for authenticated users, including admin."""

    def __init__(self, get_response=None):
        self.get_response = get_response
        super().__init__(get_response)

    def _extract_data(self, request):
        if request.method in {"POST", "PUT", "PATCH"}:
            content_type = request.META.get("CONTENT_TYPE", "").lower()
            if "application/json" in content_type:
                try:
                    body = request.body.decode(request.encoding or "utf-8")
                    return json.loads(body)
                except Exception:  # pragma: no cover - fall back to POST
                    return {}
            return request.POST.copy()
        return request.GET.copy()

    def _sanitize_data(self, data):
        if hasattr(data, "lists"):
            data = dict(data.lists())

        if not isinstance(data, dict):
            return data

        sanitized_data = {}
        for key, value in data.items():
            if key.lower() in SENSITIVE_FIELDS:
                sanitized_data[key] = "********"
            else:
                sanitized_data[key] = value
        return sanitized_data

    def _should_log_request(self, request):
        return request.user.is_authenticated

    def _is_admin_request(self, request):
        resolver_match = getattr(request, "resolver_match", None)
        if resolver_match and resolver_match.app_name == "admin":
            return True
        return request.path.startswith("/admin/")

    def __call__(self, request):
        response = self.get_response(request)
        try:
            if self._should_log_request(request):
                data_dict = self._sanitize_data(self._extract_data(request))

                if isinstance(data_dict, dict):
                    data_dict.update(
                        {
                            "ip": request.META.get("REMOTE_ADDR"),
                            "user_agent": request.META.get("HTTP_USER_AGENT", ""),
                            "is_admin": self._is_admin_request(request),
                            "status_code": response.status_code,
                        }
                    )

                serialized_data = json.dumps(data_dict)

                UserActivity.objects.create(
                    username=request.user.username,
                    path=request.path,
                    method=request.method,
                    data=serialized_data,
                )
        except Exception as e:  # pragma: no cover - logging should not break request
            logger.exception(e)

        return response
