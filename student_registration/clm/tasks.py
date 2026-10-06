# -*- coding: utf-8 -*-
"""Background jobs for the Dirasa (Bridging) programme."""
from __future__ import absolute_import, unicode_literals

from student_registration.backends.profile_ids import generate_profile_ids, queue_profile_ids

from .profile_id import BRIDGING_PROFILE_IDS, PROFILE_IDS_EXPORT_TYPE  # noqa: F401  (re-exported)


def _generate_bridging_profile_ids(export_id, registration_ids):
    return generate_profile_ids(export_id, BRIDGING_PROFILE_IDS, registration_ids)


def queue_bridging_profile_ids(export_id, registration_ids):
    """Generate the Dirasa profile IDs PDF in the background."""
    return queue_profile_ids(export_id, BRIDGING_PROFILE_IDS, registration_ids)
