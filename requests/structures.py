"""Stub implementation of ``requests.structures``."""


class CaseInsensitiveDict(dict):
    def __init__(self, data=None, **kwargs):
        super().__init__()
        data = data or {}
        for key, value in {**data, **kwargs}.items():
            self[key] = value

    def __setitem__(self, key, value):
        super().__setitem__(key.lower(), value)

    def __getitem__(self, key):
        return super().__getitem__(key.lower())

    def get(self, key, default=None):
        return super().get(key.lower(), default)
