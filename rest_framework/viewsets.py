"""Simplified ViewSet implementation."""

from typing import Callable, Dict


class GenericViewSet:
    """Provide just enough functionality for the tests."""

    @classmethod
    def as_view(cls, actions: Dict[str, str]) -> Callable:
        def view(request, *args, **kwargs):
            method = request.method.lower()
            handler_name = actions.get(method)
            if handler_name is None:
                raise AttributeError(f'Method {method!r} not allowed')
            self = cls()
            self.request = request
            handler = getattr(self, handler_name)
            return handler(request, *args, **kwargs)
        return view
