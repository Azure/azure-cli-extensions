# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import unittest
import azext_aks_preview._natgateway as natgateway
from azext_aks_preview.vendored_sdks.azure_mgmt_preview_aks.v2021_08_01.models import ManagedClusterNATGatewayProfile
from azext_aks_preview.vendored_sdks.azure_mgmt_preview_aks.v2021_08_01.models import ManagedClusterManagedOutboundIPProfile

class TestCreateNatGatewayProfile(unittest.TestCase):
    def test_empty_arguments(self):
        profile = natgateway.create_nat_gateway_profile(None, None)
        self.assertIsNone(profile)

    def test_nonempty_arguments(self):
        managed_outbound_ip_count = 2
        idle_timeout = 30

        profile = natgateway.create_nat_gateway_profile(managed_outbound_ip_count, idle_timeout)

        self.assertEqual(profile.managed_outbound_ip_profile.count, managed_outbound_ip_count)
        self.assertEqual(profile.idle_timeout_in_minutes, idle_timeout)


class TestUpdateNatGatewayProfile(unittest.TestCase):
    def test_empty_arguments(self):
        origin_profile = ManagedClusterNATGatewayProfile(
            managed_outbound_ip_profile=ManagedClusterManagedOutboundIPProfile(
                count=1
            ),
            idle_timeout_in_minutes=4
        )

        profile = natgateway.update_nat_gateway_profile(None, None, origin_profile)

        self.assertEqual(profile.managed_outbound_ip_profile.count, origin_profile.managed_outbound_ip_profile.count)
        self.assertEqual(profile.idle_timeout_in_minutes, origin_profile.idle_timeout_in_minutes)

    def test_nonempty_arguments(self):
        origin_profile = ManagedClusterNATGatewayProfile(
            managed_outbound_ip_profile=ManagedClusterManagedOutboundIPProfile(
                count=1
            ),
            idle_timeout_in_minutes=4
        )
        new_managed_outbound_ip_count = 2
        new_idle_timeout = 30

        profile = natgateway.update_nat_gateway_profile(new_managed_outbound_ip_count, new_idle_timeout, origin_profile)

        self.assertEqual(profile.managed_outbound_ip_profile.count, new_managed_outbound_ip_count)
        self.assertEqual(profile.idle_timeout_in_minutes, new_idle_timeout)


class TestIsNatGatewayProfileProvided(unittest.TestCase):
    def test_empty_arguments(self):
        result = natgateway.is_nat_gateway_profile_provided(None, None)
        self.assertFalse(result)

    def test_nonempty_managed_outbound_ip_count(self):
        result = natgateway.is_nat_gateway_profile_provided(1, None)
        self.assertTrue(result)

    def test_nonempty_idle_timeout(self):
        result = natgateway.is_nat_gateway_profile_provided(None, 4)
        self.assertTrue(result)

    def test_nonempty_arguments(self):
        result = natgateway.is_nat_gateway_profile_provided(1, 4)
        self.assertTrue(result)
