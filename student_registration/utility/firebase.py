import os
from firebase_admin import credentials, initialize_app, messaging

_app = None

def _get_app():
    global _app
    if _app:
        return _app
    cred_path = os.environ.get('FIREBASE_CREDENTIALS')
    if cred_path and os.path.exists(cred_path):
        cred = credentials.Certificate(cred_path)
        _app = initialize_app(cred)
    return _app


def send_push(token, title, body, data=None):
    if not token:
        return
    app = _get_app()
    if not app:
        return
    message = messaging.Message(
        notification=messaging.Notification(title=title, body=body),
        token=token,
        data=data or {},
    )
    try:
        messaging.send(message, app=app)
    except Exception:
        pass
