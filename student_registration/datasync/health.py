"""Bounded, read-only diagnostics for operators without container access."""
import re
from urllib.parse import urlsplit, urlunsplit

from celery import current_app
from django.conf import settings
from django.utils import timezone
import requests

from .client import SyncClient
from .outbox import sync_enabled


def safe_error(error):
    """Keep useful error reasons out of HTML responses without exposing secrets."""
    text = str(error)
    status = re.search(r'BMA-NFE replied (\d{3})', text)
    if status:
        return 'BMA-NFE returned HTTP {}. Check the receiver URL, availability and logs.'.format(status[1])
    for name in ('DATASYNC_TARGET_TOKEN', 'CELERY_BROKER_URL', 'BROKER_URL'):
        value = getattr(settings, name, '')
        if isinstance(value, str) and value:
            text = text.replace(value, '[redacted]')
    text = re.sub(r'(?i)\b(?:rediss?|amqps?|https?)://[^\s<>]+', '[address redacted]', text)
    text = re.sub(r'(?i)\bBearer\s+\S+', 'Bearer [redacted]', text)
    text = re.sub(r'(?i)\b(password|token|secret)(\s*[=:]\s*)[^\s,;]+', r'\1\2[redacted]', text)
    return '{}: {}'.format(type(error).__name__, ' '.join(text.split())[:450])


def safe_target():
    raw = getattr(settings, 'DATASYNC_TARGET_URL', '') or ''
    try:
        parts = urlsplit(raw)
        return urlunsplit((parts.scheme, parts.netloc.rsplit('@', 1)[-1], parts.path, '', ''))
    except ValueError:
        return '(invalid destination URL)'


def check_sync_health():
    """Check configuration, broker, worker replies and the receiver; send no records."""
    checks = []

    def add(component, status, detail):
        checks.append(dict(component=component, status=status, detail=detail))

    add('Compiler sync', 'ok' if sync_enabled() else 'error',
        'Enabled in the web application.' if sync_enabled() else
        'DATASYNC_ENABLED is off in the web application. Check the worker setting too.')
    try:
        with current_app.connection_for_write(connect_timeout=3) as connection:
            connection.ensure_connection(max_retries=0, timeout=3)
            add('Message broker', 'ok', 'Connection succeeded from the web application.')
            driver = connection.transport.driver_type
            if driver not in ('redis', 'amqp'):
                add('Sync worker', 'warning',
                    'This broker does not support browser worker inspection. Check the worker process logs.')
            else:
                try:
                    inspector = current_app.control.inspect(timeout=2, connection=connection)
                    queues = inspector.active_queues() or {}
                    nodes = [node for node, items in queues.items()
                             if any(item.get('name') == 'datasync' for item in items)]
                    if not nodes:
                        add('Sync worker', 'warning',
                            'No responding worker consumes the datasync queue. Check worker startup and broker settings; '
                            'busy workers or disabled remote control can also prevent replies.')
                    else:
                        registered = inspector.registered() or {}
                        current = [node for node in nodes if {
                            'datasync.flush_sync_outbox', 'datasync.worker_health',
                        }.issubset({str(task).split()[0] for task in registered.get(node, [])})]
                        add('Sync worker', 'ok' if current else 'warning',
                            'A worker responds on datasync and has loaded the current sync tasks. '
                            'Check its DATASYNC_ENABLED setting if a request remains waiting.' if current else
                            'A worker responds on datasync, but the current sync tasks were not confirmed. '
                            'Restart or update the worker with the deployed Compiler code.')
                except Exception as error:
                    add('Sync worker', 'warning', safe_error(error))
    except Exception as error:
        add('Message broker', 'error', safe_error(error))
        add('Sync worker', 'warning', 'Worker inspection requires a working broker connection.')

    try:
        with requests.Session() as session:
            info = SyncClient(timeout=4, session=session).ping()
        if info.get('enabled'):
            add('BMA-NFE receiver', 'ok', 'API responds and ingestion is enabled.')
        else:
            add('BMA-NFE receiver', 'error', 'API responds but ingestion is disabled on NFE.')
    except Exception as error:
        add('BMA-NFE receiver', 'error', safe_error(error))
    add('Periodic recovery', 'info',
        'The staging startup must also run Celery beat. A worker response does not confirm that the scheduler is running.')
    return dict(checked_at=timezone.now(), target=safe_target(), checks=checks)
