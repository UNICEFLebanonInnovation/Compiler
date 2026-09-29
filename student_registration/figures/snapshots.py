"""Building and reading the stored snapshots.

``refresh(programme, year)`` counts in the database (engine.py) and stores the result; the Celery
task runs it at night and, when NeuroDB asks for a snapshot older than FIGURES_MAX_AGE_HOURS, once
in the background (a cache lock keeps a second request from starting a second count).
"""

from __future__ import annotations

import datetime
import logging
import time

from django.conf import settings
from django.core.cache import cache
from django.utils import timezone

from .models import FiguresSnapshot

logger = logging.getLogger(__name__)

KEEP = 3  # snapshots kept per programme and year
LOCK_SECONDS = 30 * 60


def programmes():
    from . import education

    return education.PROGRAMMES


def refresh(programme, year=None):
    """Count ``programme`` for ``year`` (its current year when None) and store the snapshot."""
    definition = programmes()[programme]
    year = year or definition.current_year()
    if year is None:
        return None
    started = time.monotonic()
    payload = definition.build(year)
    snapshot = FiguresSnapshot.objects.create(
        programme=programme,
        year=str(payload['year']),
        seconds=round(time.monotonic() - started, 1),
        payload=payload,
    )
    old = FiguresSnapshot.objects.filter(programme=programme, year=snapshot.year).order_by('-created_at')[KEEP:]
    FiguresSnapshot.objects.filter(id__in=[s.id for s in old]).delete()
    logger.info('figures %s %s counted in %ss', programme, snapshot.year, snapshot.seconds)
    return snapshot


def latest(programme, year):
    return (
        FiguresSnapshot.objects.filter(programme=programme, year=str(year)).order_by('-created_at').first()
    )


def is_stale(snapshot):
    """Missing, older than FIGURES_MAX_AGE_HOURS, or counted in an older payload format (after an
    upgrade it is counted again at once, not at night)."""
    from .education import FORMAT_VERSION

    if snapshot is None or (snapshot.payload or {}).get('format') != FORMAT_VERSION:
        return True
    hours = int(getattr(settings, 'FIGURES_MAX_AGE_HOURS', 26))
    return snapshot.created_at < timezone.now() - datetime.timedelta(hours=hours)


def request_refresh(programme, year):
    """Queue one background count of ``programme``/``year`` unless one was queued recently."""
    key = 'figures-refresh:%s:%s' % (programme, year)
    if not cache.add(key, '1', LOCK_SECONDS):
        return False
    from .tasks import refresh_figures

    refresh_figures.delay(programme, str(year))
    return True
