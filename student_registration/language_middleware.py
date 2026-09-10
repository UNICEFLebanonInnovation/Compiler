"""Interface language that follows the user's explicit choice only."""
from django.conf import settings
from django.middleware.locale import LocaleMiddleware
from django.utils import translation


class ChosenLanguageMiddleware(LocaleMiddleware):
    """Activate the language the user picked in the topbar, else the default.

    The choice is the language cookie written by Django's ``set_language``
    view. Django's stock ``LocaleMiddleware`` would also honour the
    browser's ``Accept-Language`` header; while the Arabic catalogue is still
    partly untranslated, switching someone's whole interface on a browser
    setting they may not know about would give them a mixed-language screen.
    Swap this class for ``django.middleware.locale.LocaleMiddleware`` once the
    catalogue is complete to get automatic detection back.
    """

    def process_request(self, request):
        language = request.COOKIES.get(settings.LANGUAGE_COOKIE_NAME)
        if language not in dict(settings.LANGUAGES):
            language = settings.LANGUAGE_CODE
        translation.activate(language)
        request.LANGUAGE_CODE = translation.get_language()
