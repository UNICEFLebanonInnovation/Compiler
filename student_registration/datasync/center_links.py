# -*- coding: utf-8 -*-
"""Resolve the BMA-NFE centre a Compiler school's teachers belong to."""

from __future__ import unicode_literals, absolute_import, division

import logging

logger = logging.getLogger(__name__)


def center_for_school(school):
    """Return the centre mapped to ``school``, or ``None``.

    Args:
        school: A ``schools.School`` instance, or ``None``.

    Returns:
        The linked ``locations.Center``, or ``None`` when the school has not
        been mapped yet. An unmapped school is normal on a fresh install and
        only means the replicated teacher arrives without a centre.
    """
    if school is None:
        return None

    from .models import SchoolCenterLink

    link = (
        SchoolCenterLink.objects
        .filter(school=school)
        .select_related('center')
        .first()
    )
    if link is None:
        logger.debug(
            'datasync: school %s has no centre link, teacher will sync without one',
            school.pk,
        )
        return None
    return link.center
