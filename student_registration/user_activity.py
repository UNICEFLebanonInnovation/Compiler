# middleware/user_activity.py
import json
import logging
from django.utils.deprecation import MiddlewareMixin

from student_registration.backends.models import UserActivity

logger = logging.getLogger(__name__)


class UserActivityMiddleware(MiddlewareMixin):
    def __init__(self, get_response=None):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        try:
            if request.user.is_authenticated:
                if request.method == "POST":
                    data = request.POST.copy()
                else:
                    data = request.GET.copy()

                if request.path.startswith('/admin'):
                   return response

                # Serialize to JSON string (handle complex data manually if needed)
                serialized_data = json.dumps(dict(data.lists()))

                UserActivity.objects.create(
                    username=request.user,
                    path=request.path,
                    method=request.method,
                    data=serialized_data
                )
        except Exception as e:
            logger.exception(e)
            pass  # Optional: log the error to avoid breaking the app

        return response
