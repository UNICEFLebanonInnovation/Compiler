from datetime import datetime, timedelta
from django.conf import settings
from django.contrib import auth


class AutoLogout(object):

  def __init__(self, get_response=None):
    self.get_response = get_response
    super(AutoLogout, self).__init__()

  def __call__(self, request):
    response = None
    if hasattr(self, 'process_request'):
        response = self.process_request(request)
    if not response:
        response = self.get_response(request)
    if hasattr(self, 'process_response'):
        response = self.process_response(request, response)
    return response

  def process_request(self, request):

    print("PRRTLT")
    if not request.user.is_authenticated() :
      #Can't log out if not logged in
      return

    try:
      if datetime.now() - request.session['last_touch'] > timedelta( 0, settings.AUTO_LOGOUT_DELAY * 60, 0):
        auth.logout(request)
        del request.session['last_touch']
        return
    except KeyError:
      pass

    request.session['last_touch'] = datetime.now()
