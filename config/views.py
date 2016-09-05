
import environ
from django.http import HttpResponse

env = environ.Env()


def acme_view(request, slug):
    return HttpResponse(env('ACME_CODE', default='NOT_SET'))
