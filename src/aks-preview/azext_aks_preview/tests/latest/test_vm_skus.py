# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import unittest
from unittest.mock import Mock

from azext_aks_preview.vm_skus_util import _aks_is_vm_sku_available


def _make_sku(name, location="eastus", zones=None, restrictions=None):
    """Build a minimal ResourceSku-like Mock for testing.

    :param name: SKU name, e.g. "Standard_D4s_v3".
    :param location: The location string stored in location_info[0].location.
    :param zones: List of zone strings, e.g. ["1", "2", "3"].  None means no
                  zone support at all (location_info[0].zones is None).
    :param restrictions: List of restriction Mock objects, or None for no
                         restrictions.
    """
    sku = Mock()
    sku.name = name
    sku.restrictions = restrictions or []

    loc_info = Mock()
    loc_info.location = location
    loc_info.zones = zones
    sku.location_info = [loc_info]

    return sku


def _make_restriction(restriction_type, reason_code="NotAvailableForSubscription",
                      locations=None, zones=None):
    """Build a ResourceSkuRestrictions-like Mock.

    :param restriction_type: "Location" or "Zone".
    :param reason_code: Defaults to "NotAvailableForSubscription".
    :param locations: List of location strings for a Location restriction.
    :param zones: List of zone strings for a Zone restriction.
    """
    restriction = Mock()
    restriction.type = restriction_type
    restriction.reason_code = reason_code

    info = Mock()
    info.locations = locations or []
    info.zones = zones or []
    restriction.restriction_info = info

    return restriction


class TestAksIsVmSkuAvailable(unittest.TestCase):
    """Unit tests for the _aks_is_vm_sku_available helper."""

    def test_no_restrictions_returns_true(self):
        sku = _make_sku("Standard_D4s_v3", restrictions=[])
        self.assertTrue(_aks_is_vm_sku_available(sku, zone=False))

    def test_none_restrictions_returns_true(self):
        sku = _make_sku("Standard_D4s_v3")
        sku.restrictions = None
        self.assertTrue(_aks_is_vm_sku_available(sku, zone=False))

    def test_irrelevant_reason_code_is_ignored(self):
        # A restriction with a different reason_code should not affect availability.
        restriction = _make_restriction("Location", reason_code="ManuallyExcluded",
                                        locations=["eastus"])
        sku = _make_sku("Standard_D4s_v3", location="eastus",
                        restrictions=[restriction])
        self.assertTrue(_aks_is_vm_sku_available(sku, zone=False))

    def test_location_restriction_matching_location_returns_false(self):
        restriction = _make_restriction("Location", locations=["eastus"])
        sku = _make_sku("Standard_D4s_v3", location="eastus",
                        restrictions=[restriction])
        self.assertFalse(_aks_is_vm_sku_available(sku, zone=False))

    def test_location_restriction_non_matching_location_returns_true(self):
        restriction = _make_restriction("Location", locations=["westus"])
        sku = _make_sku("Standard_D4s_v3", location="eastus",
                        restrictions=[restriction])
        self.assertTrue(_aks_is_vm_sku_available(sku, zone=False))

    def test_zone_restriction_all_zones_restricted_with_zone_flag_returns_false(self):
        # All three zones are restricted and caller requests zone-aware filtering.
        restriction = _make_restriction("Zone", zones=["1", "2", "3"])
        sku = _make_sku("Standard_D4s_v3", zones=["1", "2", "3"],
                        restrictions=[restriction])
        self.assertFalse(_aks_is_vm_sku_available(sku, zone=True))

    def test_zone_restriction_partial_zones_restricted_returns_true(self):
        # Only zones 1 and 2 are restricted, but zone 3 is still available.
        restriction = _make_restriction("Zone", zones=["1", "2"])
        sku = _make_sku("Standard_D4s_v3", zones=["1", "2", "3"],
                        restrictions=[restriction])
        self.assertTrue(_aks_is_vm_sku_available(sku, zone=True))

    def test_zone_restriction_ignored_when_zone_flag_false(self):
        # Even if all zones are restricted, without --zone the SKU is available.
        restriction = _make_restriction("Zone", zones=["1", "2", "3"])
        sku = _make_sku("Standard_D4s_v3", zones=["1", "2", "3"],
                        restrictions=[restriction])
        self.assertTrue(_aks_is_vm_sku_available(sku, zone=False))

    def test_location_restriction_with_empty_locations_list_returns_true(self):
        # restriction_info.locations is present but empty – current region is not listed.
        restriction = _make_restriction("Location", locations=[])
        sku = _make_sku("Standard_D4s_v3", location="eastus",
                        restrictions=[restriction])
        self.assertTrue(_aks_is_vm_sku_available(sku, zone=False))

    def test_multiple_restrictions_one_location_match_returns_false(self):
        # One restriction is unrelated; the second blocks the current location.
        r1 = _make_restriction("Zone", zones=["1"])
        r2 = _make_restriction("Location", locations=["eastus"])
        sku = _make_sku("Standard_D4s_v3", location="eastus",
                        zones=["1", "2", "3"], restrictions=[r1, r2])
        self.assertFalse(_aks_is_vm_sku_available(sku, zone=False))

    def test_none_restriction_info_is_handled_gracefully(self):
        restriction = _make_restriction("Location", locations=["eastus"])
        restriction.restriction_info = None
        sku = _make_sku("Standard_D4s_v3", location="eastus",
                        restrictions=[restriction])
        # With restriction_info=None the locations list defaults to [], so no match.
        self.assertTrue(_aks_is_vm_sku_available(sku, zone=False))


if __name__ == '__main__':
    unittest.main()
