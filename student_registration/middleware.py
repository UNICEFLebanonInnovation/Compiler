# from datetime import datetime, timedelta
# from django.conf import settings
# from django.contrib import auth
#
#
# class AutoLogout(object):
#
#   def __init__(self, get_response=None):
#     self.get_response = get_response
#     super(AutoLogout, self).__init__()
#
#   def __call__(self, request):
#     response = None
#     if hasattr(self, 'process_request'):
#         response = self.process_request(request)
#     if not response:
#         response = self.get_response(request)
#     if hasattr(self, 'process_response'):
#         response = self.process_response(request, response)
#     return response
#
#   def process_request(self, request):
#     if not request.user.is_authenticated:
#       return
#
#     try:
#       if datetime.now().isoformat() - request.session['last_touch'] > timedelta(0, settings.AUTO_LOGOUT_DELAY * 60, 0):
#         auth.logout(request)
#         del request.session['last_touch']
#         return
#     except KeyError:
#       pass
#
#     request.session['last_touch'] = datetime.now().isoformat()


from datetime import datetime, timedelta
from django.conf import settings
from django.contrib import auth
from django.shortcuts import redirect


class AutoLogout:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.process_request(request)
        if response is not None:
            return response
        response = self.get_response(request)
        return self.process_response(request, response)

    def process_request(self, request):
        if not request.user.is_authenticated:
            return

        last_touch_str = request.session.get('last_touch')
        if last_touch_str:
            try:
                last_touch = datetime.fromisoformat(last_touch_str)
                if datetime.now() - last_touch > timedelta(minutes=settings.AUTO_LOGOUT_DELAY):
                    auth.logout(request)
                    request.session.flush()  # Clears the session completely
                    return
            except ValueError:
                # Invalid date format — reset session
                request.session.flush()
                return

        request.session['last_touch'] = datetime.now().isoformat()

    def process_response(self, request, response):
        return response


import json
import logging
from django.utils.deprecation import MiddlewareMixin
from student_registration.backends.models import HttpRequestLog

logger = logging.getLogger(__name__)


class HttpRequestMonitoringMiddleware(MiddlewareMixin):
    """Middleware to log all incoming HTTP requests."""

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
                except Exception:
                    return {}
            return request.POST.copy()
        return request.GET.copy()

    def __call__(self, request):
        response = self.get_response(request)
        try:
            data = self._extract_data(request)
            if hasattr(data, "lists"):
                data_dict = dict(data.lists())
            else:
                data_dict = data

            # Extract headers
            headers = {k: v for k, v in request.META.items() if k.startswith('HTTP_')}

            HttpRequestLog.objects.create(
                path=request.get_full_path(),
                method=request.method,
                headers=json.dumps(headers),
                body=json.dumps(data_dict),
                status_code=response.status_code,
            )
        except Exception as e:
            logger.exception(e)

        return response
