"""Very small HTTP response classes that emulate Django's interface."""

from __future__ import annotations

import json
from typing import Any, Iterable


class HttpResponse:
    """Simplified HTTP response object."""

    def __init__(self, content: Any = b"", status: int = 200, content_type: str = "text/html"):
        if isinstance(content, str):
            content = content.encode("utf-8")
        self.content = content or b""
        self.status_code = status
        self.headers = {"Content-Type": content_type}

    def write(self, value: Any) -> bytes:
        if isinstance(value, str):
            value = value.encode("utf-8")
        self.content += value
        return value

    def __setitem__(self, key: str, value: str) -> None:
        self.headers[key] = value

    def __getitem__(self, key: str) -> str:
        return self.headers[key]


class StreamingHttpResponse(HttpResponse):
    """Collect the streaming content eagerly for the purposes of the tests."""

    def __init__(self, streaming_content: Iterable[Any], **kwargs: Any):
        content = b"".join(
            part if isinstance(part, (bytes, bytearray)) else str(part).encode("utf-8")
            for part in streaming_content
        )
        super().__init__(content=content, **kwargs)


class JsonResponse(HttpResponse):
    """Encode ``data`` as JSON and expose the familiar Django API."""

    def __init__(self, data: Any, status: int = 200, safe: bool = True):  # noqa: ARG002 - parity with Django
        content = json.dumps(data)
        super().__init__(content=content, status=status, content_type="application/json")


class HttpResponseBadRequest(HttpResponse):
    def __init__(self, content: Any = b"", **kwargs: Any):
        super().__init__(content=content, status=400, **kwargs)


class HttpResponseForbidden(HttpResponse):
    def __init__(self, content: Any = b"", **kwargs: Any):
        super().__init__(content=content, status=403, **kwargs)


class FileResponse(HttpResponse):
    """Placeholder for :class:`django.http.FileResponse`."""

    def __init__(self, fileobj: Any, **kwargs: Any):
        data = getattr(fileobj, "read", lambda: fileobj)()
        super().__init__(content=data, **kwargs)


class HttpResponseRedirect(HttpResponse):
    def __init__(self, redirect_to: str, status: int = 302):
        super().__init__(content=b"", status=status)
        self['Location'] = redirect_to
