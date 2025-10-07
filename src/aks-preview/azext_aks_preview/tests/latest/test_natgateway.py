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


if __name__ == '__main__':
    unittest.main()
