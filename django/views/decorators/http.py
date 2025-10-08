"""HTTP method decorators."""


def require_POST(view_func):
    def wrapper(request, *args, **kwargs):
        if request.method.upper() != 'POST':  # pragma: no cover - parity with Django
            raise ValueError('POST required')
        return view_func(request, *args, **kwargs)

    return wrapper
