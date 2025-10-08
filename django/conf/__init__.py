"""Simplified configuration holder used by the compatibility layer."""


class _Settings:
    """Very small settings container.

    Attributes can be freely assigned at runtime. Unknown attributes default to
    ``None`` which keeps the behaviour predictable for optional configuration
    flags accessed by the code under test.
    """

    def __init__(self):
        super().__setattr__('_data', {})

    def __getattr__(self, item):
        return self._data.get(item)

    def __setattr__(self, key, value):
        if key == '_data':
            super().__setattr__(key, value)
        else:
            self._data[key] = value


settings = _Settings()

# Provide sensible defaults for the settings referenced in the tests so that
# accessing them never raises ``AttributeError``.
settings.UNIQUE_ID_API_USERNAME = ''
settings.UNIQUE_ID_API_PASSWORD = ''
settings.UNIQUE_ID_API_TOKEN_URL = 'https://example.invalid/token'
settings.UNIQUE_ID_API_URL = 'https://example.invalid/ids'
settings.UNIQUE_PROGRAMMES_API_URL = 'https://example.invalid/programmes'
settings.AUTH_USER_MODEL = 'auth.User'
