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
                    self._flush_session_safely(request)
                    return
            except ValueError:
                # Invalid date format — reset session
                self._flush_session_safely(request)
                return

        request.session['last_touch'] = datetime.now().isoformat()

    def process_response(self, request, response):
        return response

    def _flush_session_safely(self, request):
        """Flush the current session while ensuring Django's cache is initialised."""
        session = getattr(request, "session", None)
        if session is None:
            return

        # ``SessionStore`` instances should expose ``_session_cache``. In Django
        # 5.2, some third-party backends may not initialise it until ``load`` is
        # called. Accessing ``flush()`` without the attribute raises an
        # ``AttributeError``. Guard against that situation by initialising the
        # cache before flushing so that ``flush`` can run safely.
        if not hasattr(session, "_session_cache"):
            try:
                session._session_cache = session.load()
            except Exception:  # pragma: no cover - best effort initialisation
                session._session_cache = {}

        session.flush()
