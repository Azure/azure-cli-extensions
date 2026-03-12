# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import unittest

import azext_aks_preview._natgateway as natgateway
from azext_aks_preview.__init__ import register_aks_preview_resource_type
from azext_aks_preview._client_factory import CUSTOM_MGMT_AKS_PREVIEW
from azext_aks_preview.managed_cluster_decorator import (
    AKSPreviewManagedClusterModels,
)
from azext_aks_preview.tests.latest.mocks import MockCLI, MockCmd


class TestCreateNatGatewayProfile(unittest.TestCase):
    def setUp(self):
        # manually register CUSTOM_MGMT_AKS_PREVIEW
        register_aks_preview_resource_type()
        self.cli_ctx = MockCLI()
        self.cmd = MockCmd(self.cli_ctx)
        # store all the models used by nat gateway
        self.nat_gateway_models = AKSPreviewManagedClusterModels(self.cmd, CUSTOM_MGMT_AKS_PREVIEW).nat_gateway_models

    def test_empty_arguments(self):
        profile = natgateway.create_nat_gateway_profile(None, None, models=self.nat_gateway_models)
        self.assertIsNone(profile)

    def test_nonempty_arguments(self):
        managed_outbound_ip_count = 2
        idle_timeout = 30

        profile = natgateway.create_nat_gateway_profile(managed_outbound_ip_count, idle_timeout, models=self.nat_gateway_models)

        self.assertEqual(profile.managed_outbound_ip_profile.count, managed_outbound_ip_count)
        self.assertEqual(profile.idle_timeout_in_minutes, idle_timeout)


class TestUpdateNatGatewayProfile(unittest.TestCase):
    def setUp(self):
        # manually register CUSTOM_MGMT_AKS_PREVIEW
        register_aks_preview_resource_type()
        self.cli_ctx = MockCLI()
        self.cmd = MockCmd(self.cli_ctx)
        # store all the models used by nat gateway
        self.nat_gateway_models = AKSPreviewManagedClusterModels(self.cmd, CUSTOM_MGMT_AKS_PREVIEW).nat_gateway_models

    def test_empty_arguments(self):
        origin_profile = self.nat_gateway_models.ManagedClusterNATGatewayProfile(
            managed_outbound_ip_profile=self.nat_gateway_models.ManagedClusterManagedOutboundIPProfile(
                count=1
            ),
            idle_timeout_in_minutes=4
        )

        profile = natgateway.update_nat_gateway_profile(None, None, origin_profile, models=self.nat_gateway_models)

        self.assertEqual(profile.managed_outbound_ip_profile.count, origin_profile.managed_outbound_ip_profile.count)
        self.assertEqual(profile.idle_timeout_in_minutes, origin_profile.idle_timeout_in_minutes)

    def test_reset_empty_arguments(self):
        origin_profile = self.nat_gateway_models.ManagedClusterNATGatewayProfile(
            managed_outbound_ip_profile=self.nat_gateway_models.ManagedClusterManagedOutboundIPProfile(
                count=1
            ),
            idle_timeout_in_minutes=4
        )

        profile = natgateway.update_nat_gateway_profile(0, None, origin_profile, models=self.nat_gateway_models)

        self.assertEqual(profile.managed_outbound_ip_profile.count, 0)
        self.assertEqual(profile.idle_timeout_in_minutes, origin_profile.idle_timeout_in_minutes)

    def test_nonempty_arguments(self):
        origin_profile = self.nat_gateway_models.ManagedClusterNATGatewayProfile(
            managed_outbound_ip_profile=self.nat_gateway_models.ManagedClusterManagedOutboundIPProfile(
                count=1
            ),
            idle_timeout_in_minutes=4
        )
        new_managed_outbound_ip_count = 2
        new_idle_timeout = 30

        profile = natgateway.update_nat_gateway_profile(new_managed_outbound_ip_count, new_idle_timeout, origin_profile, models=self.nat_gateway_models)

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


class TestCreateNatGatewayV2Profile(unittest.TestCase):
    def setUp(self):
        register_aks_preview_resource_type()
        self.cli_ctx = MockCLI()
        self.cmd = MockCmd(self.cli_ctx)
        self.nat_gateway_models = AKSPreviewManagedClusterModels(self.cmd, CUSTOM_MGMT_AKS_PREVIEW).nat_gateway_models

    def test_v2_with_managed_outbound_ipv6_count(self):
        profile = natgateway.create_nat_gateway_profile(
            2, 30, models=self.nat_gateway_models,
            managed_outbound_ipv6_count=4,
        )
        self.assertEqual(profile.managed_outbound_ip_profile.count, 2)
        self.assertEqual(profile.managed_outbound_ip_profile.count_i_pv6, 4)
        self.assertEqual(profile.idle_timeout_in_minutes, 30)

    def test_v2_with_outbound_ip_ids(self):
        ip_ids = ["/subscriptions/sub1/resourceGroups/rg1/providers/Microsoft.Network/publicIPAddresses/ip1"]
        profile = natgateway.create_nat_gateway_profile(
            None, None, models=self.nat_gateway_models,
            outbound_ip_ids=ip_ids,
        )
        self.assertIsNotNone(profile)
        self.assertEqual(len(profile.outbound_i_ps.public_i_ps), 1)
        self.assertEqual(profile.outbound_i_ps.public_i_ps[0], ip_ids[0])

    def test_v2_with_outbound_ip_prefix_ids(self):
        prefix_ids = ["/subscriptions/sub1/resourceGroups/rg1/providers/Microsoft.Network/publicIPPrefixes/prefix1"]
        profile = natgateway.create_nat_gateway_profile(
            None, None, models=self.nat_gateway_models,
            outbound_ip_prefix_ids=prefix_ids,
        )
        self.assertIsNotNone(profile)
        self.assertEqual(len(profile.outbound_ip_prefixes.public_ip_prefixes), 1)
        self.assertEqual(profile.outbound_ip_prefixes.public_ip_prefixes[0], prefix_ids[0])

    def test_v2_only_ipv6_count(self):
        profile = natgateway.create_nat_gateway_profile(
            None, None, models=self.nat_gateway_models,
            managed_outbound_ipv6_count=8,
        )
        self.assertIsNotNone(profile)
        self.assertEqual(profile.managed_outbound_ip_profile.count_i_pv6, 8)


class TestUpdateNatGatewayV2Profile(unittest.TestCase):
    def setUp(self):
        register_aks_preview_resource_type()
        self.cli_ctx = MockCLI()
        self.cmd = MockCmd(self.cli_ctx)
        self.nat_gateway_models = AKSPreviewManagedClusterModels(self.cmd, CUSTOM_MGMT_AKS_PREVIEW).nat_gateway_models

    def test_v2_update_with_ipv6_count(self):
        origin_profile = self.nat_gateway_models.ManagedClusterNATGatewayProfile(
            managed_outbound_ip_profile=self.nat_gateway_models.ManagedClusterManagedOutboundIPProfile(count=1),
            idle_timeout_in_minutes=4,
        )
        profile = natgateway.update_nat_gateway_profile(
            None, None, origin_profile, models=self.nat_gateway_models,
            managed_outbound_ipv6_count=4,
        )
        self.assertEqual(profile.managed_outbound_ip_profile.count, 1)
        self.assertEqual(profile.managed_outbound_ip_profile.count_i_pv6, 4)

    def test_v2_update_with_outbound_ip_ids(self):
        origin_profile = self.nat_gateway_models.ManagedClusterNATGatewayProfile(idle_timeout_in_minutes=4)
        ip_ids = ["/subscriptions/sub1/resourceGroups/rg1/providers/Microsoft.Network/publicIPAddresses/ip1"]
        profile = natgateway.update_nat_gateway_profile(
            None, None, origin_profile, models=self.nat_gateway_models,
            outbound_ip_ids=ip_ids,
        )
        self.assertEqual(len(profile.outbound_i_ps.public_i_ps), 1)

    def test_v2_empty_v2_params_returns_original(self):
        origin_profile = self.nat_gateway_models.ManagedClusterNATGatewayProfile(
            managed_outbound_ip_profile=self.nat_gateway_models.ManagedClusterManagedOutboundIPProfile(count=2),
            idle_timeout_in_minutes=10,
        )
        profile = natgateway.update_nat_gateway_profile(
            None, None, origin_profile, models=self.nat_gateway_models,
        )
        self.assertEqual(profile.managed_outbound_ip_profile.count, 2)
        self.assertEqual(profile.idle_timeout_in_minutes, 10)


class TestIsNatGatewayV2ProfileProvided(unittest.TestCase):
    def test_only_ipv6_count(self):
        result = natgateway.is_nat_gateway_profile_provided(None, None, managed_outbound_ipv6_count=4)
        self.assertTrue(result)

    def test_only_outbound_ip_ids(self):
        result = natgateway.is_nat_gateway_profile_provided(None, None, outbound_ip_ids=["/sub/ip1"])
        self.assertTrue(result)

    def test_only_outbound_ip_prefix_ids(self):
        result = natgateway.is_nat_gateway_profile_provided(None, None, outbound_ip_prefix_ids=["/sub/prefix1"])
        self.assertTrue(result)

    def test_all_none(self):
        result = natgateway.is_nat_gateway_profile_provided(None, None, None, None, None)
        self.assertFalse(result)


if __name__ == '__main__':
    unittest.main()
