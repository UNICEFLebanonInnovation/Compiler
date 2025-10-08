"""Minimal class-based view infrastructure used in tests."""

from typing import Any, Callable

from django.http import HttpResponse


class View:
    """Basic approximation of :class:`django.views.generic.base.View`."""

    http_method_names = {'get', 'post'}

    def dispatch(self, request, *args, **kwargs):
        handler_name = request.method.lower()
        handler = getattr(self, handler_name, None)
        if handler is None:
            return self.http_method_not_allowed(request, *args, **kwargs)
        return handler(request, *args, **kwargs)

    def http_method_not_allowed(self, request, *args, **kwargs):  # pragma: no cover - mirrors Django API
        return HttpResponse(status=405)

    @classmethod
    def as_view(cls, **initkwargs) -> Callable:
        def view(request, *args, **kwargs):
            self = cls(**initkwargs)
            return self.dispatch(request, *args, **kwargs)
        return view


class TemplateView(View):
    pass


class ListView(View):
    pass


class DetailView(View):
    pass


class RedirectView(View):
    url = '/'  # pragma: no cover - compatibility default


class UpdateView(View):
    pass


class FormView(View):
    pass
