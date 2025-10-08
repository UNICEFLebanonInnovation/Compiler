"""Testing helpers used by the exercises."""

from __future__ import annotations

from typing import Any, Dict
from urllib.parse import parse_qs, urlsplit


class _QueryMapping(dict):
    def __init__(self, initial=None):
        super().__init__(initial or {})

    def copy(self):
        return _QueryMapping(super().copy())

    def lists(self):
        for key, value in self.items():
            if isinstance(value, list):
                yield key, value
            else:
                yield key, [value]

    def get(self, key, default=None):  # noqa: D401 - mimic QueryDict behaviour
        if key not in self:
            return default
        value = super().get(key)
        if isinstance(value, list):
            return value[0]
        return value


class _Request:
    def __init__(self, method: str, path: str, data: Dict[str, Any] | None = None, *, content_type: str | None = None):
        self.method = method.upper()
        self.path = urlsplit(path).path
        self.encoding = 'utf-8'
        self.META: Dict[str, Any] = {
            'CONTENT_TYPE': content_type or 'application/x-www-form-urlencoded',
            'REMOTE_ADDR': '127.0.0.1',
            'HTTP_USER_AGENT': 'stub-client',
        }
        data = data or {}
        if self.method == 'GET':
            query = parse_qs(urlsplit(path).query)
            if isinstance(data, dict):
                query.update({key: [value] if not isinstance(value, list) else value for key, value in data.items()})
            self.GET = _QueryMapping({key: values for key, values in query.items()})
            self.POST = _QueryMapping()
            self.body = b''
        else:
            self.GET = _QueryMapping()
            if isinstance(data, dict):
                self.POST = _QueryMapping({key: value for key, value in data.items()})
                payload = ''
            else:
                self.POST = _QueryMapping()
                payload = data
            if isinstance(payload, str):
                payload = payload.encode('utf-8')
            elif not isinstance(payload, (bytes, bytearray)):
                payload = str(payload).encode('utf-8')
            self.body = payload
        self.user = None

    def get_full_path(self):
        if self.method == 'GET' and self.GET:
            query = '&'.join(f"{key}={value[0]}" for key, value in self.GET.items())
            return f"{self.path}?{query}"
        return self.path


class RequestFactory:
    def get(self, path: str, data: Dict[str, Any] | None = None):
        return _Request('GET', path, data)

    def post(self, path: str, data: Any = None, content_type: str | None = None):
        payload = data
        if isinstance(data, dict):
            payload = {key: value for key, value in data.items()}
        return _Request('POST', path, payload, content_type=content_type)
