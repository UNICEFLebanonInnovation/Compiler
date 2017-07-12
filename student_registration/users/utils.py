

def user_main_role(user):
    groups = [g.name for g in user.groups.all()]

    if 'PMU' in groups:
        return 'pmu'
    if 'COORDINATOR' in groups:
        return 'coordinator'
    if 'DIRECTOR' in groups or 'ALP_DIRECTOR' in groups:
        return 'director'
    if 'SCHOOL' in groups or 'ALP_SCHOOL' in groups:
        return 'school'
    return 'mehe'


def get_user_token(user_id):
    from rest_framework.authtoken.models import Token
    try:
        token = Token.objects.get(user_id=user_id)
    except Token.DoesNotExist:
        token = Token.objects.create(user_id=user_id)
    return token.key


def force_default_language(request, language='ar-ar'):
    from django.utils import translation
    translation.activate('ar-ar')
    request.session[translation.LANGUAGE_SESSION_KEY] = 'ar-ar'
