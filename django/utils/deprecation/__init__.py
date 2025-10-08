"""Compatibility helpers for middleware."""


class MiddlewareMixin:
    """Match Django's ``MiddlewareMixin`` API surface."""

    def __init__(self, get_response=None):
        self.get_response = get_response

    def __call__(self, request):  # pragma: no cover - passthrough behaviour
        return self.get_response(request)
