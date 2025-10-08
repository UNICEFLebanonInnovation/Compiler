"""Minimal template library used in tests."""


class Library:
    def __init__(self):
        self.tags = {}

    def simple_tag(self, func=None, *args, **kwargs):
        def decorator(inner):
            self.tags[inner.__name__] = inner
            return inner

        if func is not None:
            return decorator(func)
        return decorator

    def filter(self, func=None, *args, **kwargs):  # pragma: no cover - parity stub
        return self.simple_tag(func, *args, **kwargs)


def LibraryFactory():  # pragma: no cover - compatibility helper
    return Library()


library = Library()
