
import json
import datetime
import os
import io
import re
import logging
import warnings

from pathlib import Path
from time import mktime

from django.http import FileResponse, HttpResponse, Http404
from django.urls import reverse
from storages.backends.azure_storage import AzureStorage

logger = logging.getLogger(__name__)


class MyEncoder(json.JSONEncoder):

    def default(self, obj):
        if isinstance(obj, datetime.datetime) or isinstance(obj, datetime.date):
            return int(mktime(obj.timetuple()))

        return json.JSONEncoder.default(self, obj)

    def decode(self, obj):
        if isinstance(obj, datetime.datetime):
            return int(mktime(obj.timetuple()))

        return json.JSONEncoder.default(self, obj)


class ExportStorage(AzureStorage):
    """Azure storage backend dedicated for exported files."""
    location = "export"

    # Export filenames are UUID-based, so collisions are not expected. Allowing
    # overwrites skips django-storages' pre-upload existence check, which avoids
    # noisy Azure SDK ``HEAD`` requests that return 404 before a new blob is
    # created.
    overwrite_files = True


# Archives holding children's photographs. They may only be downloaded by the
# user who requested the completed export, whichever endpoint serves them.
PHOTO_EXPORT_PREFIXES = ('mscc_photo_export_', 'bridging_photo_export_')


def download_file(file_name, returned_file_name, content_type="application/octet-stream", delete_after=True,
                  *, request=None):
    """Retrieve a file from Azure storage and return it as an HTTP response."""

    if file_name.startswith(PHOTO_EXPORT_PREFIXES):
        # Several modules share this storage/download utility. Photo archives
        # must not be readable through an older module's unscoped alias.
        from student_registration.backends.models import ExportHistory
        if request is None:
            raise Http404('Export not found.')
        if file_name.startswith('mscc_photo_export_'):
            from student_registration.mscc.export_access import user_can_export
            allowed = user_can_export(request.user)
        else:
            from student_registration.clm.bridging_exports import user_can_export_bridging
            allowed = user_can_export_bridging(request.user)
        if not allowed:
            raise Http404('Export not found.')
        if not ExportHistory.objects.filter(
            created_by=request.user, status='done',
            file_url=reverse('mscc:export_download', args=[file_name]),
        ).exists():
            raise Http404('Export not found.')

    storage = ExportStorage()
    try:
        with storage.open(file_name, "rb") as fh:
            file_stream = io.BytesIO(fh.read())
            file_stream.seek(0)
            response = FileResponse(file_stream, content_type=content_type)
            response["Content-Disposition"] = f'attachment; filename="{returned_file_name}"'
            if file_name.startswith(PHOTO_EXPORT_PREFIXES):
                response['Cache-Control'] = 'private, no-store'
    except Exception as exc:  # pragma: no cover - logged for debugging purposes
        logger.exception("Error reading file %s", file_name)
        response = HttpResponse(f"Error reading file: {exc}")
    # if delete_after:
    #     storage.delete(file_name)
    return response


def is_valid_filename(filename, extension):
    pattern = rf'^[a-zA-Z0-9-_]+\.{extension}$'
    return re.match(pattern, filename) is not None


def send_push_to_web_0(user, title, body, data=None):
    """Send a web push notification via Firebase Cloud Messaging.

    Parameters
    ----------
    user: ``django.contrib.auth.models.User``
        Recipient of the notification. All tokens stored for this user will
        receive the message.
    title: str
        Title shown in the web push notification.
    body: str
        Body text of the notification.
    data: dict, optional
        Extra data to include in the notification payload. Values are
        converted to strings as required by FCM.

    Returns
    -------
    bool
        ``True`` when at least one message has been successfully sent,
        otherwise ``False``.
    """

    # Import locally to avoid loading heavy dependencies when unused.
    from pathlib import Path

    import firebase_admin
    from firebase_admin import credentials, messaging

    from student_registration.users.models import WebPushToken

    # Collect all tokens registered for the user.
    tokens = list(
        WebPushToken.objects.filter(user=user).values_list("token", flat=True)
    )
    if not tokens:
        return False

    # Initialise the Firebase app if this hasn't happened yet.  The
    # credentials file lives in ``utility/firebase-creds.json`` relative to the
    # project root.
    if not firebase_admin._apps:  # pragma: no cover - simple initialisation
        project_root = Path(__file__).resolve().parents[2]
        cred_path = project_root / "utility" / "firebase-creds.json"
        cred = credentials.Certificate(str(cred_path))
        firebase_admin.initialize_app(cred)

    # FCM requires payload data values to be strings.
    payload_data = {k: str(v) for k, v in (data or {}).items()}

    message = messaging.MulticastMessage(
        tokens=tokens,
        notification=messaging.Notification(title=title, body=body),
        data=payload_data,
    )

    # Send the notification to all tokens.
    response = messaging.send_multicast(message)
    return response.success_count > 0


def send_push_to_web(user, title, body, data=None):
    """Send a web push notification without failing the caller's workflow.

    Firebase errors (for example an expired or mismatched service-account key
    causing ``invalid_grant: Invalid JWT Signature``) should not mark exports as
    failed after the export file has already been generated and uploaded.  These
    failures are intentionally silent because exports are still available from
    the export history/download endpoint.
    """
    warnings.filterwarnings(
        "ignore",
        message="You are using a Python version.*google.api_core.*",
        category=FutureWarning,
    )
    import firebase_admin
    from firebase_admin import credentials, messaging

    from student_registration.users.models import WebPushToken

    token_obj = (
        WebPushToken.objects.filter(user=user)
        .order_by("-pk")
        .first()
    )
    if token_obj is None:
        logger.warning(
            "No web push token registered for user %s; call the save_fcm_token endpoint to register one before sending.",
            user.pk,
        )
        return False

    # Tokens are registered from the client via the save_fcm_token view
    # (``/api/save-fcm-token/``).  If a user has never visited the app with
    # notifications enabled there will be no token to use here.
    root_dirt = Path(__file__).parents[2]
    firebase_credentials_file = os.path.join(str(root_dirt / "utility"), 'firebase-creds.json')

    try:
        if not firebase_admin._apps:
            cred = credentials.Certificate(firebase_credentials_file)
            firebase_admin.initialize_app(cred)

        # FCM requires all data payload values to be strings.
        payload_data = {k: str(v) for k, v in (data or {}).items()}

        message = messaging.Message(
            notification=messaging.Notification(
                title=title,
                body=body,
            ),
            webpush=messaging.WebpushConfig(
                headers={"Urgency": "high"},
                notification=messaging.WebpushNotification(
                    title=title,
                    body=body,
                    icon="/static/images/logo.png",
                ),
            ),
            token=token_obj.token,
            data=payload_data,
        )
        return messaging.send(message)
    except Exception:
        return False
