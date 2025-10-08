"""Testing utilities mirroring DRF's request factory."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict

from django.test import RequestFactory


class APIRequestFactory(RequestFactory):
    """Expose the same interface as DRF's factory while reusing the stub request."""

    def get(self, path: str, data: Dict[str, Any] | None = None, **extra: Any):
        request = super().get(path, data)
        for key, value in extra.items():
            request.META[key] = value
        return request

    def post(self, path: str, data: Any = None, format: str | None = None, **extra: Any):  # noqa: A002 - parity with DRF signature
        content_type = 'application/json' if format == 'json' else extra.get('CONTENT_TYPE')
        request = super().post(path, data, content_type=content_type)
        for key, value in extra.items():
            request.META[key] = value
        return request
