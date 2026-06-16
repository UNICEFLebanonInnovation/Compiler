from unittest.mock import MagicMock, patch

from django.test import TestCase

from student_registration.backends.utils import send_push_to_web
from student_registration.users.models import User, WebPushToken


class SendPushToWebTests(TestCase):
    def test_send_push_returns_false_when_firebase_send_fails(self):
        user = User.objects.create_user(username="export-user")
        WebPushToken.objects.create(user=user, token="token-1")

        firebase_admin = MagicMock()
        firebase_admin._apps = {"default": object()}
        messaging = MagicMock()
        messaging.send.side_effect = Exception("invalid_grant: Invalid JWT Signature.")

        with patch.dict("sys.modules", {"firebase_admin": firebase_admin}):
            with patch("firebase_admin.credentials"):
                with patch("firebase_admin.messaging", messaging):
                    result = send_push_to_web(
                        user,
                        "Makani export ready",
                        "Your export is ready to download.",
                        data={"type": "mscc_export_ready", "count": 1},
                    )

        self.assertFalse(result)
        messaging.Message.assert_called_once()
        self.assertEqual(messaging.Message.call_args.kwargs["data"]["count"], "1")

    def test_send_push_returns_false_when_firebase_initialization_fails(self):
        user = User.objects.create_user(username="init-failure-user")
        WebPushToken.objects.create(user=user, token="token-2")

        firebase_admin = MagicMock()
        firebase_admin._apps = {}
        firebase_admin.initialize_app.side_effect = Exception(
            "invalid_grant: Invalid JWT Signature."
        )

        with patch.dict("sys.modules", {"firebase_admin": firebase_admin}):
            with patch("firebase_admin.credentials") as credentials:
                with patch("firebase_admin.messaging"):
                    result = send_push_to_web(
                        user,
                        "Makani export ready",
                        "Your export is ready to download.",
                    )

        self.assertFalse(result)
        credentials.Certificate.assert_called_once()
