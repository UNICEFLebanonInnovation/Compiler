"""Simple shortcut helpers."""

from django.http import HttpResponseRedirect, HttpResponse


def redirect(to, *args, **kwargs):
    return HttpResponseRedirect(str(to))


def render(request, template_name, context=None, content_type=None, status=200):
    body = f"Rendered {template_name}".encode('utf-8')
    return HttpResponse(body, status=status, content_type=content_type or 'text/html')
