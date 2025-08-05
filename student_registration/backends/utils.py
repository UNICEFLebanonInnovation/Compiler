
import json
import datetime

from time import mktime


class MyEncoder(json.JSONEncoder):

    def default(self, obj):
        if isinstance(obj, datetime.datetime) or isinstance(obj, datetime.date):
            return int(mktime(obj.timetuple()))

        return json.JSONEncoder.default(self, obj)

    def decode(self, obj):
        if isinstance(obj, datetime.datetime):
            return int(mktime(obj.timetuple()))

        return json.JSONEncoder.default(self, obj)


def post_data(protocol, url, apifunc, token, data):

    params = json.dumps(data, cls=MyEncoder)

    headers = {"Content-type": "application/json", "Authorization": token, "HTTP_REFERER": url, "Cookie": "token="+token}

    # if protocol == 'HTTPS':
    #     conn = httplib.HTTPSConnection(url)
    # else:
    #     conn = httplib.HTTPConnection(url)
    # conn.request('POST', apifunc, params, headers)
    # response = conn.getresponse()
    # result = response.read()
    #
    # if not response.status == 201:
    #     if response.status == 400:
    #         raise Exception(str(response.status) + response.reason + response.read())
    #     else:
    #         raise Exception(str(response.status) + response.reason)
    #
    # conn.close()
    #
    # return result


import io
import re
import logging
from django.http import FileResponse, HttpResponse
from storages.backends.azure_storage import AzureStorage

logger = logging.getLogger(__name__)


class ExportStorage(AzureStorage):
    """Azure storage backend dedicated for exported files."""

    location = "export"


def download_file(file_name, returned_file_name, content_type="application/octet-stream", delete_after=True):
    """Retrieve a file from Azure storage and return it as an HTTP response."""

    storage = ExportStorage()
    try:
        with storage.open(file_name, "rb") as fh:
            file_stream = io.BytesIO(fh.read())
            file_stream.seek(0)
            response = FileResponse(file_stream, content_type=content_type)
            response["Content-Disposition"] = f'attachment; filename="{returned_file_name}"'
    except Exception as exc:  # pragma: no cover - logged for debugging purposes
        logger.exception("Error reading file %s", file_name)
        response = HttpResponse(f"Error reading file: {exc}")
    if delete_after:
        storage.delete(file_name)
    return response


def is_valid_filename(filename, extension):
    pattern = rf'^[a-zA-Z0-9-_]+\.{extension}$'
    return re.match(pattern, filename) is not None


def send_push_to_web(user, title, body, data=None):
    """Placeholder for sending web push notifications."""

    from student_registration.users.models import WebPushToken

    try:
        WebPushToken.objects.get(user=user)
    except WebPushToken.DoesNotExist:
        return False
    return False
