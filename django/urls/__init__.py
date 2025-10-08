"""Simple helpers mimicking ``django.urls`` behaviour for tests."""


def reverse(viewname, kwargs=None, args=None):  # noqa: D401 - mimic Django signature
    """Return a predictable, human-readable URL for ``viewname``."""

    suffix = ''
    if kwargs:
        suffix = '/' + '/'.join(str(value) for value in kwargs.values()) + '/'
    return '/' + viewname.replace(':', '/') + suffix


def reverse_lazy(viewname, kwargs=None, args=None):  # noqa: D401 - mimic Django signature
    return reverse(viewname, kwargs=kwargs, args=args)


class _ResolvedURL:
    def __init__(self, view_name):
        self.view_name = view_name


def resolve(path):  # noqa: D401 - mimic Django signature
    """Return an object exposing ``view_name`` similar to Django's resolve."""

    view_name = path.strip('/').replace('/', ':') or ''
    return _ResolvedURL(view_name)
