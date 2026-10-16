# TODO: Remove Temporary access
# Exceptional access to partner 3's Dirasa registrations by governorate.
TEMPORARY_BRIDGING_GOVERNORATES = {7: (7,), 107: (1,), 29: (3, 5)}


def temporary_bridging_governorates(user):
    return TEMPORARY_BRIDGING_GOVERNORATES.get(user.partner_id, ())


def has_temporary_bridging_access(user, registration):
    governorate_ids = temporary_bridging_governorates(user)
    return bool(
        governorate_ids
        and registration
        and registration.partner_id == 3
        and registration.governorate_id in governorate_ids
    )
