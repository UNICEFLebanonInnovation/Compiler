# -*- coding: utf-8 -*-
"""HTTP client for BMA-NFE's replication endpoint."""

from __future__ import unicode_literals, absolute_import, division

import json
import logging
import os
import threading
import time

import requests
from django.conf import settings

from .constants import CONTRACT_VERSION, SOURCE_SYSTEM_COMPILER

logger = logging.getLogger(__name__)
_connections = threading.local()


def _new_session():
    session = requests.Session()
    adapter = requests.adapters.HTTPAdapter(pool_connections=4, pool_maxsize=1,
                                            pool_block=True, max_retries=0)
    session.mount('https://', adapter)
    session.mount('http://', adapter)
    return session


def pooled_session():
    # Never share a mutable Session between threads or inherit a live pool
    # across Celery's process fork.
    if getattr(_connections, 'pid', None) != os.getpid():
        _connections.session = _new_session()
        _connections.pid = os.getpid()
    return _connections.session


class SyncTransportError(Exception):
    """BMA-NFE could not be reached, or answered with an error status.

    Always retryable: the events in the failed batch stay in the outbox.
    """


class SyncConfigurationError(Exception):
    """Replication is switched on but not configured."""


class SyncClient(object):
    """Posts batches of events to BMA-NFE.

    Args:
        url (str): Endpoint URL; defaults to ``DATASYNC_TARGET_URL``.
        token (str): DRF token of the BMA-NFE service account; defaults to
            ``DATASYNC_TARGET_TOKEN``.
        timeout (int): Request timeout in seconds.
    """

    def __init__(self, url=None, token=None, timeout=None, session=None):
        self.url = (url or getattr(settings, 'DATASYNC_TARGET_URL', '') or '').strip()
        self.token = (token or getattr(settings, 'DATASYNC_TARGET_TOKEN', '') or '').strip()
        self.timeout = timeout or getattr(settings, 'DATASYNC_TIMEOUT', 30)
        self.verify = getattr(settings, 'DATASYNC_VERIFY_TLS', True)
        self.session = session if session is not None else pooled_session()

    def worker_copy(self):
        client = type(self)(url=self.url, token=self.token, timeout=self.timeout,
                            session=_new_session())
        client.verify = self.verify
        return client

    def close(self):
        self.session.close()

    def photo_reuse_supported(self):
        if not getattr(settings, 'DATASYNC_PHOTO_REUSE_ENABLED', True):
            return False
        key = (self.url, self.token)
        cache = getattr(self.session, '_datasync_capabilities', {})
        previous = cache.get(key)
        if previous and time.monotonic() - previous[0] < 60:
            return previous[1]
        supported = bool(self.ping().get('child_photo_sync', {}).get('verified_reuse'))
        cache[key] = (time.monotonic(), supported)
        self.session._datasync_capabilities = cache
        return supported

    def _check(self):
        """Raise when the endpoint or credentials are missing."""
        if not self.url:
            raise SyncConfigurationError(
                'DATASYNC_TARGET_URL is not set; nothing can be replicated.'
            )
        if not self.token:
            raise SyncConfigurationError(
                'DATASYNC_TARGET_TOKEN is not set; BMA-NFE would reject the push.'
            )

    @property
    def headers(self):
        """Return the headers every request carries."""
        return {
            'Authorization': 'Token {}'.format(self.token),
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        }

    def ping(self):
        """Ask BMA-NFE what it accepts, to verify URL and credentials.

        Returns:
            dict: The endpoint's capability document.

        Raises:
            SyncConfigurationError: When the URL or token is missing.
            SyncTransportError: When the endpoint is unreachable or unhappy.
        """
        self._check()
        try:
            response = self.session.get(
                self.url, headers=self.headers, timeout=self.timeout, verify=self.verify,
                allow_redirects=False,
            )
        except requests.RequestException as error:
            raise SyncTransportError('cannot reach {}: {}'.format(self.url, error))
        return self._decode(response)

    def check_ready(self):
        """Initial imports require the same complete-event contract on NFE."""
        capabilities = self.ping()
        if not capabilities.get('enabled'):
            raise SyncConfigurationError('NFE synchronization is disabled')
        if not capabilities.get('child_photo_sync', {}).get('atomic_with_registration'):
            raise SyncConfigurationError('Deploy the unified record/photo receiver on NFE first')
        return capabilities

    def push(self, events, attachments=None):
        """Send a batch of events and return BMA-NFE's per-event outcome.

        Args:
            events (list): Event dictionaries built by :mod:`.dispatch`.

        Returns:
            dict: The decoded response body.

        Raises:
            SyncConfigurationError: When the URL or token is missing.
            SyncTransportError: On a transport error or a non-2xx reply.
        """
        self._check()
        body = {
            'source_system': SOURCE_SYSTEM_COMPILER,
            'contract_version': CONTRACT_VERSION,
            'events': events,
        }
        try:
            if attachments:
                headers = {key: value for key, value in self.headers.items() if key != 'Content-Type'}
                response = self.session.post(
                    self.url, headers=headers, data={'envelope': json.dumps(body, default=str)},
                    files={key: ('photo', stream, 'application/octet-stream')
                           for key, stream in attachments.items()},
                    timeout=getattr(settings, 'DATASYNC_PHOTO_TIMEOUT', self.timeout),
                    verify=self.verify, allow_redirects=False,
                )
            else:
                response = self.session.post(
                    self.url, headers=self.headers, data=json.dumps(body, default=str),
                    timeout=self.timeout, verify=self.verify, allow_redirects=False,
                )
        except requests.RequestException as error:
            raise SyncTransportError('cannot reach {}: {}'.format(self.url, error))
        return self._decode(response)

    def _decode(self, response):
        """Return the JSON body, or raise a descriptive transport error."""
        if response.status_code >= 400:
            raise SyncTransportError(
                'BMA-NFE replied {}: {}'.format(
                    response.status_code, (response.text or '')[:500]
                )
            )
        try:
            return response.json()
        except ValueError:
            raise SyncTransportError(
                'BMA-NFE replied {} with a non-JSON body: {}'.format(
                    response.status_code, (response.text or '')[:500]
                )
            )
