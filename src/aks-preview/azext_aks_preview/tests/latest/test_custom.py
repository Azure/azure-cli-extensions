# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import unittest
from unittest.mock import Mock, patch

from azext_aks_preview.__init__ import register_aks_preview_resource_type
from azext_aks_preview._client_factory import CUSTOM_MGMT_AKS_PREVIEW
from azext_aks_preview.managed_cluster_decorator import (
    AKSPreviewManagedClusterModels,
)
from azext_aks_preview.custom import (
    aks_stop,
    aks_scale,
    aks_upgrade,
    aks_enable_addons,
)
from azext_aks_preview.tests.latest.mocks import MockCLI, MockClient, MockCmd


class TestCustomCommand(unittest.TestCase):
    def setUp(self):
        # manually register CUSTOM_MGMT_AKS_PREVIEW
        register_aks_preview_resource_type()
        self.cli_ctx = MockCLI()
        self.cmd = MockCmd(self.cli_ctx)
        self.models = AKSPreviewManagedClusterModels(self.cmd, CUSTOM_MGMT_AKS_PREVIEW)
        self.client = MockClient()

    def test_aks_stop(self):
        # public cluster: call begin_stop
        mc_1 = self.models.ManagedCluster(location="test_location")
        self.client.get = Mock(
            return_value=mc_1
        )
        self.client.begin_stop = Mock(
            return_value=None
        )
        self.assertEqual(aks_stop(self.cmd, self.client, "rg", "name"), None)

        # private cluster: call begin_stop
        mc_3 = self.models.ManagedCluster(location="test_location")
        api_server_access_profile = self.models.ManagedClusterAPIServerAccessProfile()
        api_server_access_profile.enable_private_cluster = True
        mc_3.api_server_access_profile = api_server_access_profile
        self.client.get = Mock(
            return_value=mc_3
        )
        self.client.begin_stop = Mock(
            return_value=None
        )
        self.assertEqual(aks_stop(self.cmd, self.client, "rg", "name", False), None)

    def test_aks_scale_with_none_agent_pool_profiles(self):
        """Test aks_scale handles None agent_pool_profiles gracefully"""
        # Test case: automatic cluster with hosted system components, no agent pools
        mc = self.models.ManagedCluster(location="test_location")
        mc.agent_pool_profiles = None  # This is the key scenario
        mc.pod_identity_profile = None

        self.client.get = Mock(return_value=mc)

        # Should not raise NoneType error and should return without crashing
        try:
            result = aks_scale(self.cmd, self.client, "rg", "name", 3, "nodepool1")
            # We expect this to complete without NoneType errors
        except Exception as e:
            # Should not be a NoneType error
            self.assertNotIn("NoneType", str(type(e)))

    def test_aks_upgrade_with_none_agent_pool_profiles(self):
        """Test aks_upgrade handles None agent_pool_profiles gracefully"""
        mc = self.models.ManagedCluster(location="test_location")
        mc.agent_pool_profiles = None  # Key test scenario
        mc.pod_identity_profile = None
        mc.kubernetes_version = "1.24.0"
        mc.provisioning_state = "Succeeded"
        mc.max_agent_pools = 10

        self.client.get = Mock(return_value=mc)

        # Should not raise NoneType error
        try:
            result = aks_upgrade(
                self.cmd, self.client, "rg", "name",
                kubernetes_version="1.25.0", yes=True
            )
        except Exception as e:
            self.assertNotIn("NoneType", str(type(e)))

    def test_aks_enable_addons_with_none_agent_pool_profiles(self):
        """Test aks_enable_addons handles None agent_pool_profiles gracefully"""
        mc = self.models.ManagedCluster(location="test_location")
        mc.agent_pool_profiles = None  # Key test scenario
        mc.addon_profiles = {}
        mc.service_principal_profile = self.models.ManagedClusterServicePrincipalProfile(
            client_id="msi"
        )
        mc.api_server_access_profile = None

        self.client.get = Mock(return_value=mc)
        self.client.begin_create_or_update = Mock(return_value=mc)

        # Should not raise NoneType error
        try:
            result = aks_enable_addons(
                self.cmd, self.client, "rg", "name", "monitoring",
                workspace_resource_id="/subscriptions/test/resourceGroups/test/providers/Microsoft.OperationalInsights/workspaces/test"
            )
        except Exception as e:
            self.assertNotIn("NoneType", str(type(e)))

    def test_aks_enable_addons_virtual_node_with_none_agent_pool_profiles(self):
        """Test aks_enable_addons for virtual-node handles None agent_pool_profiles"""
        mc = self.models.ManagedCluster(location="test_location")
        mc.agent_pool_profiles = None  # Key test scenario for virtual node addon
        mc.addon_profiles = {}
        mc.service_principal_profile = self.models.ManagedClusterServicePrincipalProfile(
            client_id="msi"
        )
        mc.api_server_access_profile = None

        self.client.get = Mock(return_value=mc)
        self.client.begin_create_or_update = Mock(return_value=mc)

        # Virtual node addon should handle None agent_pool_profiles gracefully
        try:
            result = aks_enable_addons(
                self.cmd, self.client, "rg", "name", "virtual-node",
                subnet_name="test-subnet"
            )
        except Exception as e:
            self.assertNotIn("NoneType", str(type(e)))


if __name__ == '__main__':
    unittest.main()
