"""Very small subset of the ``requests`` API for the tests."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional

from .structures import CaseInsensitiveDict  # noqa: F401
from . import auth  # noqa: F401


@dataclass
class _Response:
    text: str = '{}'
    status_code: int = 200

    def json(self):  # pragma: no cover - helper parity
        import json as _json
        return _json.loads(self.text)


def post(url: str, data: Any = None, headers: Optional[Dict[str, Any]] = None, auth: Any = None):  # noqa: D401 - mimic requests
    return _Response()


def get(url: str, headers: Optional[Dict[str, Any]] = None, params: Optional[Dict[str, Any]] = None, auth: Any = None):  # noqa: D401
    return _Response()
