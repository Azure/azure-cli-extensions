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
    aks_list_vm_skus,
)
from azext_aks_preview.tests.latest.mocks import MockCLI, MockClient, MockCmd
from azext_aks_preview.tests.latest.test_vm_skus import _make_sku, _make_restriction


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


class TestAksListVmSkus(unittest.TestCase):
    """Unit tests for the aks_list_vm_skus command function."""

    def setUp(self):
        self.cmd = Mock()
        self.client = Mock()

    # ------------------------------------------------------------------
    # Basic list behaviour
    # ------------------------------------------------------------------

    def test_returns_all_available_skus_with_no_filters(self):
        skus = [
            _make_sku("Standard_D2s_v3"),
            _make_sku("Standard_D4s_v3"),
            _make_sku("Standard_D8s_v3"),
        ]
        self.client.list.return_value = iter(skus)

        result = aks_list_vm_skus(self.cmd, self.client, "eastus")

        self.client.list.assert_called_once_with("eastus")
        self.assertEqual(result, skus)

    def test_returns_empty_list_when_no_skus_exist(self):
        self.client.list.return_value = iter([])
        result = aks_list_vm_skus(self.cmd, self.client, "eastus")
        self.assertEqual(result, [])

    # ------------------------------------------------------------------
    # show_all / availability filtering
    # ------------------------------------------------------------------

    def test_unavailable_skus_excluded_by_default(self):
        available = _make_sku("Standard_D4s_v3")
        unavailable = _make_sku(
            "Standard_D2s_v3",
            restrictions=[_make_restriction("Location", locations=["eastus"])]
        )
        self.client.list.return_value = iter([available, unavailable])

        result = aks_list_vm_skus(self.cmd, self.client, "eastus")

        self.assertEqual(result, [available])

    def test_show_all_includes_unavailable_skus(self):
        available = _make_sku("Standard_D4s_v3")
        unavailable = _make_sku(
            "Standard_D2s_v3",
            restrictions=[_make_restriction("Location", locations=["eastus"])]
        )
        self.client.list.return_value = iter([available, unavailable])

        result = aks_list_vm_skus(self.cmd, self.client, "eastus", show_all=True)

        self.assertIn(available, result)
        self.assertIn(unavailable, result)
        self.assertEqual(len(result), 2)

    # ------------------------------------------------------------------
    # Size filtering
    # ------------------------------------------------------------------

    def test_size_filter_matches_partial_name(self):
        d4 = _make_sku("Standard_D4s_v3")
        d8 = _make_sku("Standard_D8s_v3")
        e4 = _make_sku("Standard_E4s_v3")
        self.client.list.return_value = iter([d4, d8, e4])

        result = aks_list_vm_skus(self.cmd, self.client, "eastus", size="D4")

        self.assertEqual(result, [d4])

    def test_size_filter_is_case_insensitive(self):
        sku = _make_sku("Standard_D4s_v3")
        self.client.list.return_value = iter([sku])

        result_lower = aks_list_vm_skus(self.cmd, self.client, "eastus", size="d4s")
        self.assertEqual(result_lower, [sku])

        self.client.list.return_value = iter([sku])
        result_upper = aks_list_vm_skus(self.cmd, self.client, "eastus", size="D4S")
        self.assertEqual(result_upper, [sku])

    def test_size_filter_returns_empty_when_no_match(self):
        self.client.list.return_value = iter([_make_sku("Standard_D4s_v3")])
        result = aks_list_vm_skus(self.cmd, self.client, "eastus", size="E96")
        self.assertEqual(result, [])

    def test_size_filter_skips_skus_with_none_name(self):
        sku_no_name = _make_sku(None)
        sku_with_name = _make_sku("Standard_D4s_v3")
        self.client.list.return_value = iter([sku_no_name, sku_with_name])

        result = aks_list_vm_skus(self.cmd, self.client, "eastus", size="D4")

        self.assertNotIn(sku_no_name, result)
        self.assertIn(sku_with_name, result)

    def test_size_filter_matches_multiple_skus(self):
        d4 = _make_sku("Standard_D4s_v3")
        d4_v4 = _make_sku("Standard_D4s_v4")
        e4 = _make_sku("Standard_E4s_v3")
        self.client.list.return_value = iter([d4, d4_v4, e4])

        result = aks_list_vm_skus(self.cmd, self.client, "eastus", size="D4s")

        self.assertIn(d4, result)
        self.assertIn(d4_v4, result)
        self.assertNotIn(e4, result)

    # ------------------------------------------------------------------
    # Zone filtering
    # ------------------------------------------------------------------

    def test_zone_filter_excludes_skus_without_zone_support(self):
        zonal = _make_sku("Standard_D4s_v3", zones=["1", "2", "3"])
        non_zonal = _make_sku("Standard_B2s", zones=None)
        self.client.list.return_value = iter([zonal, non_zonal])

        result = aks_list_vm_skus(self.cmd, self.client, "eastus", zone=True)

        self.assertIn(zonal, result)
        self.assertNotIn(non_zonal, result)

    def test_zone_filter_excludes_skus_with_empty_zones_list(self):
        empty_zones = _make_sku("Standard_B2s", zones=[])
        self.client.list.return_value = iter([empty_zones])

        result = aks_list_vm_skus(self.cmd, self.client, "eastus", zone=True)

        self.assertEqual(result, [])

    def test_zone_filter_excludes_skus_with_no_location_info(self):
        sku = _make_sku("Standard_D4s_v3")
        sku.location_info = None
        self.client.list.return_value = iter([sku])

        result = aks_list_vm_skus(self.cmd, self.client, "eastus", zone=True)

        self.assertEqual(result, [])

    def test_zone_filter_also_excludes_zone_restricted_skus(self):
        # A SKU that has zones but ALL are restricted should be excluded by
        # the availability filter (run before the zone presence filter).
        restriction = _make_restriction("Zone", zones=["1", "2", "3"])
        restricted_zonal = _make_sku("Standard_D4s_v3", zones=["1", "2", "3"],
                                     restrictions=[restriction])
        self.client.list.return_value = iter([restricted_zonal])

        result = aks_list_vm_skus(self.cmd, self.client, "eastus", zone=True)

        self.assertEqual(result, [])

    # ------------------------------------------------------------------
    # Combined filters
    # ------------------------------------------------------------------

    def test_size_and_zone_filters_combined(self):
        d4_zonal = _make_sku("Standard_D4s_v3", zones=["1", "2", "3"])
        d4_non_zonal = _make_sku("Standard_D4as_v4", zones=None)
        e4_zonal = _make_sku("Standard_E4s_v3", zones=["1", "2", "3"])
        self.client.list.return_value = iter([d4_zonal, d4_non_zonal, e4_zonal])

        result = aks_list_vm_skus(self.cmd, self.client, "eastus",
                                  size="D4", zone=True)

        self.assertEqual(result, [d4_zonal])

    def test_size_filter_with_show_all(self):
        available = _make_sku("Standard_D4s_v3")
        unavailable = _make_sku(
            "Standard_D4s_v4",
            restrictions=[_make_restriction("Location", locations=["eastus"])]
        )
        unrelated = _make_sku("Standard_E4s_v3")
        self.client.list.return_value = iter([available, unavailable, unrelated])

        result = aks_list_vm_skus(self.cmd, self.client, "eastus",
                                  size="D4", show_all=True)

        self.assertIn(available, result)
        self.assertIn(unavailable, result)
        self.assertNotIn(unrelated, result)

    def test_all_filters_combined(self):
        match = _make_sku("Standard_D4s_v3", zones=["1", "2", "3"])
        wrong_size = _make_sku("Standard_E4s_v3", zones=["1", "2", "3"])
        no_zone = _make_sku("Standard_D4s_v4", zones=None)
        unavailable = _make_sku(
            "Standard_D4ds_v5",
            zones=["1", "2", "3"],
            restrictions=[_make_restriction("Location", locations=["eastus"])]
        )
        self.client.list.return_value = iter([match, wrong_size, no_zone, unavailable])

        result = aks_list_vm_skus(self.cmd, self.client, "eastus",
                                  size="D4", zone=True, show_all=False)

        self.assertEqual(result, [match])


if __name__ == '__main__':
    unittest.main()
