"""Decorators compatible with DRF's public API."""

from typing import Callable, Iterable, Optional


def api_view(http_method_names: Iterable[str]):  # noqa: D401 - mimic DRF signature
    """Return a decorator that simply passes through the wrapped function."""

    def decorator(func: Callable) -> Callable:
        func.allowed_methods = [method.upper() for method in http_method_names]
        return func

    return decorator


def action(detail: bool = False, methods: Optional[Iterable[str]] = None, url_path: Optional[str] = None):  # noqa: D401
    """Attach metadata to the wrapped method so ``ViewSet.as_view`` can dispatch."""

    methods = [method.lower() for method in (methods or ['get'])]

    def decorator(func: Callable) -> Callable:
        func.detail = detail
        func.mapping = {method: func.__name__ for method in methods}
        func.url_path = url_path or func.__name__
        return func

    return decorator
