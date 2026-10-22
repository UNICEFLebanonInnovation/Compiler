import re
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from unittest.mock import patch

import pytest

from student_registration.backends.azure_storage import ChunkedAzureStorage
from student_registration.backends.utils import ExportStorage


@pytest.mark.parametrize('backend', [ChunkedAzureStorage, ExportStorage])
def test_large_blob_download_uses_bounded_ranges_and_preserves_all_bytes(backend):
    # Simulate an intermediary that closes any response above 4 MiB. This is
    # larger than the first failed production download, including a final
    # partial range and nonuniform data to detect missing/repeated chunks.
    payload = bytes(range(251)) * 65000
    requested = []

    class BlobHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            value = self.headers.get('x-ms-range') or self.headers.get('Range', '')
            match = re.fullmatch(r'bytes=(\d+)-(\d+)', value)
            start, end = (int(part) for part in match.groups()) if match else (0, len(payload) - 1)
            end = min(end, len(payload) - 1)
            data = payload[start:end + 1]
            requested.append((start, end))
            self.send_response(206)
            self.send_header('Content-Length', str(len(data)))
            self.send_header('Content-Range', 'bytes {}-{}/{}'.format(start, end, len(payload)))
            self.send_header('Content-Type', 'application/octet-stream')
            self.send_header('ETag', '"unchanged-blob"')
            self.send_header('Last-Modified', 'Tue, 20 Oct 2026 12:00:00 GMT')
            self.send_header('x-ms-blob-type', 'BlockBlob')
            self.end_headers()
            self.wfile.write(data[:4 * 1024 * 1024])
            self.close_connection = True

        def log_message(self, *args):
            pass

    server = ThreadingHTTPServer(('127.0.0.1', 0), BlobHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    storage = backend(account_name='localtest', account_key=None, sas_token=None,
                      token_credential=None, connection_string=None, azure_container='exports',
                      custom_domain='127.0.0.1:{}'.format(server.server_port), azure_ssl=False)
    # Use the loopback blob endpoint for both regular and custom-domain clients.
    storage._service_client = storage._get_service_client(use_custom_domain=True)
    try:
        with storage.open('large.bin', 'rb') as source:
            assert source.read() == payload
        assert len(requested) > 1
        assert all(end - start + 1 <= 2 * 1024 * 1024 for start, end in requested)
        assert requested[0][0] == 0
        assert requested[-1][1] == len(payload) - 1
        assert all(left[1] + 1 == right[0] for left, right in zip(requested, requested[1:]))
    finally:
        storage.service_client.close()
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)


def test_connection_string_receives_the_same_download_limits():
    storage = ChunkedAzureStorage(connection_string=(
        'DefaultEndpointsProtocol=https;AccountName=example;AccountKey=dGVzdA=='))
    with patch('student_registration.backends.azure_storage.BlobServiceClient') as factory:
        storage._get_service_client(use_custom_domain=False)
    assert factory.from_connection_string.call_args.kwargs == {
        'max_single_get_size': 2 * 1024 * 1024,
        'max_chunk_get_size': 2 * 1024 * 1024,
    }
