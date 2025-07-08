import json
import logging
from django.utils import timezone

from student_registration.users.models import User
from student_registration.backends.models import UserActivity

logger = logging.getLogger(__name__)


class UserActivityMiddleware:
    """Persist the timestamp of the user's last authenticated activity and
    log request details for auditing."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        user = getattr(request, "user", None)
        if user:
            is_auth = getattr(user, "is_authenticated", False)
            if callable(is_auth):
                is_auth = is_auth()
            if is_auth:
                User.objects.filter(pk=user.pk).update(last_activity=timezone.now())
                try:
                    if request.method == "POST":
                        data = request.POST.copy()
                    else:
                        data = request.GET.copy()

                    if not request.path.startswith('/admin'):
                        serialized_data = json.dumps(dict(data.lists()))
                        UserActivity.objects.create(
                            username=user,
                            path=request.path,
                            method=request.method,
                            data=serialized_data,
                        )
                except Exception:  # pragma: no cover - don't break request on log failure
                    logger.exception('Failed to log user activity')
        return response
