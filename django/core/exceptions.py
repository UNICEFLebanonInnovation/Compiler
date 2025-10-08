"""Core exceptions used by the minimal Django test doubles."""


class ValidationError(Exception):
    """Match Django's ``ValidationError`` interface closely enough for tests."""

    def __init__(self, message):
        super().__init__(message)
        self.message = message

    def __str__(self):  # pragma: no cover - mirrors Django's API
        return str(self.message)
