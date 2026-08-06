# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
"""Helpers for the `az aks list-vm-skus` command."""


def _aks_is_vm_sku_available(sku, zone):
    """Return True if the SKU is available for the current subscription.

    A SKU is considered unavailable when:
    1. It has a Location restriction that covers this region, or
    2. The --zone flag is set AND all availability zones in the region are restricted.
    """
    if not sku.restrictions:
        return True

    for restriction in sku.restrictions:
        if restriction.reason_code != "NotAvailableForSubscription":
            continue

        restriction_type = restriction.type
        restriction_info = restriction.restriction_info

        if restriction_type == "Location":
            restricted_locations = (restriction_info.locations or []) if restriction_info else []
            location_info = sku.location_info[0] if sku.location_info else None
            if location_info and location_info.location in restricted_locations:
                return False

        if restriction_type == "Zone" and zone:
            location_info = sku.location_info[0] if sku.location_info else None
            if location_info:
                available_zones = set(location_info.zones or [])
                restricted_zones = set(
                    (restriction_info.zones or []) if restriction_info else []
                )
                # If all zones are restricted, the SKU is unavailable
                if not (available_zones - restricted_zones):
                    return False

    return True
