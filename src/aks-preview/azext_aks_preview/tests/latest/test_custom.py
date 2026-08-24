# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import unittest
from unittest.mock import Mock, patch

from azext_aks_preview.__init__ import register_aks_preview_resource_type
from azext_aks_preview import ContainerServiceCommandsLoader
from azext_aks_preview._client_factory import CUSTOM_MGMT_AKS_PREVIEW
from azext_aks_preview._consts import CONST_FLEX_NODES
from azext_aks_preview.agentpool_decorator import AKSPreviewAgentPoolModels
from azext_aks_preview.managed_cluster_decorator import (
    AKSPreviewManagedClusterModels,
)
from azext_aks_preview.custom import (
    aks_agentpool_get_bootstrap_data,
    aks_agentpool_upgrade,
    aks_machine_add,
    aks_machine_update,
    aks_stop,
    aks_scale,
    aks_upgrade,
    aks_enable_addons,
    aks_list_vm_skus,
)
from azext_aks_preview.tests.latest.mocks import MockCLI, MockClient, MockCmd
from azure.cli.command_modules.acs._consts import AgentPoolDecoratorMode
from azure.cli.core.azclierror import (
    ClientRequestError,
    InvalidArgumentValueError,
    RequiredArgumentMissingError,
)
from azure.core.exceptions import ResourceNotFoundError
from azext_aks_preview.tests.latest.test_vm_skus import _make_sku, _make_restriction
from knack.util import CLIError


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
        """Managed System Pool clusters return a useful error instead of len(None)."""
        mc = self.models.ManagedCluster(location="test_location")
        mc.agent_pool_profiles = None
        mc.pod_identity_profile = None
        self.client.get = Mock(return_value=mc)

        with self.assertRaisesRegex(CLIError, "no scalable node pools"):
            aks_scale(self.cmd, self.client, "rg", "name", 3, "nodepool1")

    def test_aks_upgrade_node_image_only_skips_machines_mode_pool(self):
        """Machines mode pools must be skipped during --node-image-only to avoid a known client-side error."""
        machines_pool = self.models.ManagedClusterAgentPoolProfile(name="machinespool", mode="Machines", type="VirtualMachines")
        vmss_pool = self.models.ManagedClusterAgentPoolProfile(name="nodepool1", mode="User", type="VirtualMachineScaleSets")
        mc = self.models.ManagedCluster(location="test_location")
        mc.agent_pool_profiles = [machines_pool, vmss_pool]
        mc.pod_identity_profile = None
        mc.kubernetes_version = "1.24.0"
        mc.provisioning_state = "Succeeded"
        mc.max_agent_pools = 10

        self.client.get = Mock(return_value=mc)

        with patch("azext_aks_preview.custom.cf_agent_pools") as mock_cf, \
             patch("azext_aks_preview.custom._upgrade_single_nodepool_image_version") as mock_upgrade:
            mock_agent_pool_client = Mock()
            mock_cf.return_value = mock_agent_pool_client

            aks_upgrade(self.cmd, self.client, "rg", "name", node_image_only=True, yes=True)

            # Only the VMSS pool should be upgraded; the Machines mode pool must be skipped.
            upgraded_pools = [call.args[4] for call in mock_upgrade.call_args_list]
            self.assertNotIn("machinespool", upgraded_pools)
            self.assertIn("nodepool1", upgraded_pools)

    def test_aks_upgrade_node_image_only_skips_flexnodes_pool(self):
        """FlexNodes pools do not support node image-only upgrades."""
        flex_pool = self.models.ManagedClusterAgentPoolProfile(name="flexpool", mode="User", type="FlexNodes")
        vmss_pool = self.models.ManagedClusterAgentPoolProfile(name="nodepool1", mode="User", type="VirtualMachineScaleSets")
        mc = self.models.ManagedCluster(location="test_location")
        mc.agent_pool_profiles = [flex_pool, vmss_pool]
        mc.pod_identity_profile = None
        mc.kubernetes_version = "1.24.0"
        mc.provisioning_state = "Succeeded"
        mc.max_agent_pools = 10

        self.client.get = Mock(return_value=mc)

        with patch("azext_aks_preview.custom.cf_agent_pools") as mock_cf, \
             patch("azext_aks_preview.custom._upgrade_single_nodepool_image_version") as mock_upgrade:
            mock_cf.return_value = Mock()

            aks_upgrade(self.cmd, self.client, "rg", "name", node_image_only=True, yes=True)

            upgraded_pools = [call.args[4] for call in mock_upgrade.call_args_list]
            self.assertNotIn("flexpool", upgraded_pools)
            self.assertIn("nodepool1", upgraded_pools)

    def test_aks_upgrade_kubernetes_version_skips_machines_mode_pool(self):
        """Machines mode pools must be skipped during Kubernetes version upgrade to avoid a known client-side error."""
        machines_pool = self.models.ManagedClusterAgentPoolProfile(name="machinespool", mode="Machines", type="VirtualMachines")
        vmss_pool = self.models.ManagedClusterAgentPoolProfile(name="nodepool1", mode="User", type="VirtualMachineScaleSets")
        mc = self.models.ManagedCluster(location="test_location")
        mc.agent_pool_profiles = [machines_pool, vmss_pool]
        mc.pod_identity_profile = None
        mc.kubernetes_version = "1.24.0"
        mc.provisioning_state = "Succeeded"
        mc.max_agent_pools = 10
        mc.service_principal_profile = None

        self.client.get = Mock(return_value=mc)
        self.client.begin_create_or_update = Mock(return_value=None)

        aks_upgrade(self.cmd, self.client, "rg", "name", kubernetes_version="1.25.0", yes=True)

        # Machines mode pool must not have orchestrator_version set; VMSS pool must be upgraded.
        self.assertIsNone(machines_pool.orchestrator_version)
        self.assertEqual(vmss_pool.orchestrator_version, "1.25.0")

    def test_aks_upgrade_kubernetes_version_updates_flexnodes_pool(self):
        """FlexNodes pools support Kubernetes version upgrades."""
        flex_pool = self.models.ManagedClusterAgentPoolProfile(name="flexpool", mode="User", type="FlexNodes")
        mc = self.models.ManagedCluster(location="test_location")
        mc.agent_pool_profiles = [flex_pool]
        mc.pod_identity_profile = None
        mc.kubernetes_version = "1.24.0"
        mc.provisioning_state = "Succeeded"
        mc.max_agent_pools = 10
        mc.service_principal_profile = None

        self.client.get = Mock(return_value=mc)
        self.client.begin_create_or_update = Mock(return_value=None)

        aks_upgrade(self.cmd, self.client, "rg", "name", kubernetes_version="1.25.0", yes=True)

        self.assertEqual(flex_pool.orchestrator_version, "1.25.0")

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


class TestAksAgentPoolGetBootstrapData(unittest.TestCase):
    def setUp(self):
        register_aks_preview_resource_type()
        self.cmd = MockCmd(MockCLI())
        self.models = AKSPreviewAgentPoolModels(
            self.cmd,
            CUSTOM_MGMT_AKS_PREVIEW,
            AgentPoolDecoratorMode.STANDALONE,
        )
        self.client = Mock()

    def test_get_bootstrap_data(self):
        bootstrap_data = self.models.PoolBootstrapData(
            networking=self.models.BootstrapNetworkingConfig(
                dns_service_ip="10.0.0.10"
            ),
            node=self.models.BootstrapNodeConfig(
                kubelet=self.models.BootstrapKubeletConfig(
                    cluster_fqdn="cluster.example.com"
                )
            ),
        )
        self.client.list_bootstrap_data.return_value = bootstrap_data

        result = aks_agentpool_get_bootstrap_data(
            self.cmd,
            self.client,
            "rg",
            "cluster",
            "flexpool",
        )

        self.assertEqual(
            result,
            {
                "networking": {"dnsServiceIP": "10.0.0.10"},
                "node": {"kubelet": {"clusterFQDN": "cluster.example.com"}},
            },
        )
        self.client.get.assert_not_called()
        action_args = self.client.list_bootstrap_data.call_args.args
        self.assertEqual(action_args[:3], ("rg", "cluster", "flexpool"))
        self.assertIsInstance(action_args[3], self.models.ListBootstrapDataRequest)
        self.assertEqual(action_args[3].as_dict(), {})
        self.assertEqual(
            self.client.list_bootstrap_data.call_args.kwargs,
            {"logging_enable": False},
        )

    def test_get_bootstrap_data_command_is_sensitive(self):
        loader = ContainerServiceCommandsLoader(self.cmd.cli_ctx)
        loader.load_command_table(["aks", "nodepool", "get-bootstrap-data"])

        command = loader.command_table["aks nodepool get-bootstrap-data"]
        command.load_arguments()

        sensitive_info = command.sensitive_info
        self.assertEqual(
            sensitive_info.sensitive_keys,
            ["bootstrapToken", "caCertData"],
        )
        self.assertNotIn("aks_custom_headers", command.arguments)


class TestAksFlexNodePoolUpgrade(unittest.TestCase):
    def setUp(self):
        register_aks_preview_resource_type()
        self.cmd = MockCmd(MockCLI())
        self.models = AKSPreviewAgentPoolModels(
            self.cmd,
            CUSTOM_MGMT_AKS_PREVIEW,
            AgentPoolDecoratorMode.STANDALONE,
        )
        self.client = Mock()
        self.client.get.return_value = self.models.UnifiedAgentPoolModel(
            type_properties_type=CONST_FLEX_NODES,
            orchestrator_version="1.32",
            upgrade_settings=self.models.AgentPoolUpgradeSettings(
                max_unavailable="30%",
            ),
        )

    def test_upgrade_flexnodes_pool_uses_regular_path(self):
        with patch(
            "azext_aks_preview._helpers.get_user_supplied_argument_options",
            return_value={
                "kubernetes_version": "--kubernetes-version",
                "max_unavailable": "--max-unavailable",
                "yes": "--yes",
            },
        ):
            aks_agentpool_upgrade(
                self.cmd,
                self.client,
                "rg",
                "cluster",
                "flexpool",
                kubernetes_version="1.33",
                max_unavailable="50%",
                yes=True,
            )

        agentpool = self.client.begin_create_or_update.call_args.args[3]
        self.assertIs(agentpool, self.client.get.return_value)
        self.assertEqual(agentpool.orchestrator_version, "1.33")
        self.assertEqual(agentpool.upgrade_settings.max_unavailable, "50%")

    def test_node_image_only_rejects_flexnodes_pool(self):
        with self.assertRaisesRegex(
            ClientRequestError,
            "Node image-only upgrade is not supported for FlexNodes pools",
        ):
            aks_agentpool_upgrade(
                self.cmd,
                self.client,
                "rg",
                "cluster",
                "flexpool",
                node_image_only=True,
                yes=True,
            )

        self.client.get.assert_called_once_with("rg", "cluster", "flexpool")
        self.client.begin_upgrade_node_image_version.assert_not_called()
        self.client.begin_create_or_update.assert_not_called()

    def test_upgrade_rejects_unsupported_flexnodes_options(self):
        unsupported_options = {
            "max_surge": "50%",
            "drain_timeout": 30,
            "node_soak_duration": 0,
            "upgrade_strategy": "Rolling",
            "drain_batch_size": "10%",
            "drain_timeout_bg": 30,
            "batch_soak_duration": 15,
            "final_soak_duration": 60,
            "undrainable_node_behavior": "Cordon",
            "max_blocked_nodes": "1",
            "snapshot_id": "/subscriptions/000/resourceGroups/rg/providers/Microsoft.ContainerService/snapshots/test",
        }

        supplied_options = {
            name: "--" + name.replace("_", "-") for name in unsupported_options
        }
        with patch(
            "azext_aks_preview._helpers.get_user_supplied_argument_options",
            return_value=supplied_options,
        ), self.assertRaises(InvalidArgumentValueError) as err:
            aks_agentpool_upgrade(
                self.cmd,
                self.client,
                "rg",
                "cluster",
                "flexpool",
                kubernetes_version="1.33",
                yes=True,
                **unsupported_options,
            )

        for option in unsupported_options:
            self.assertIn("--" + option.replace("_", "-"), str(err.exception))
        self.client.begin_create_or_update.assert_not_called()


class TestAksFlexNodeMachine(unittest.TestCase):
    def setUp(self):
        register_aks_preview_resource_type()
        self.cmd = MockCmd(MockCLI())
        self.models = AKSPreviewAgentPoolModels(
            self.cmd,
            CUSTOM_MGMT_AKS_PREVIEW,
            AgentPoolDecoratorMode.STANDALONE,
        )
        self.client = Mock()
        self.client.get.side_effect = ResourceNotFoundError("not found")
        self.client.begin_create_or_update.return_value = None

    def test_add_flexnode_machine_uses_minimal_payload(self):
        flex_pool = self.models.UnifiedAgentPoolModel(type_properties_type=CONST_FLEX_NODES)
        with patch("azext_aks_preview.custom.cf_agent_pools") as mock_cf, patch(
            "azext_aks_preview._helpers.get_user_supplied_argument_options",
            return_value={
                "kubernetes_version": "--kubernetes-version",
                "labels": "--labels",
                "node_taints": "--node-taints",
                "max_pods": "--max-pods",
            },
        ):
            mock_cf.return_value.get.return_value = flex_pool
            aks_machine_add(
                self.cmd,
                self.client,
                "rg",
                "cluster",
                "flexpool",
                machine_name="flexnode01",
                kubernetes_version="1.35.5",
                labels={"role": "edge"},
                node_taints="dedicated=edge:NoSchedule",
                max_pods=75,
            )

        machine = self.client.begin_create_or_update.call_args.args[4]
        self.assertEqual(
            machine.as_dict(),
            {
                "properties": {
                    "kubernetes": {
                        "nodeLabels": {"role": "edge"},
                        "orchestratorVersion": "1.35.5",
                        "nodeTaints": ["dedicated=edge:NoSchedule"],
                        "maxPods": 75,
                    }
                }
            },
        )

    def test_add_flexnode_machine_requires_machine_name(self):
        flex_pool = self.models.UnifiedAgentPoolModel(type_properties_type=CONST_FLEX_NODES)
        with patch("azext_aks_preview.custom.cf_agent_pools") as mock_cf:
            mock_cf.return_value.get.return_value = flex_pool
            with self.assertRaisesRegex(
                RequiredArgumentMissingError,
                "Please specify --machine-name",
            ):
                aks_machine_add(
                    self.cmd,
                    self.client,
                    "rg",
                    "cluster",
                    "flexpool",
                    kubernetes_version="1.35.5",
                )

        self.client.begin_create_or_update.assert_not_called()

    def test_add_flexnode_machine_rejects_unsupported_options(self):
        flex_pool = self.models.UnifiedAgentPoolModel(type_properties_type=CONST_FLEX_NODES)
        with patch("azext_aks_preview.custom.cf_agent_pools") as mock_cf, patch(
            "azext_aks_preview._helpers.get_user_supplied_argument_options",
            return_value={"vm_size": "--vm-size", "zones": "--zones"},
        ):
            mock_cf.return_value.get.return_value = flex_pool
            with self.assertRaisesRegex(InvalidArgumentValueError, "--vm-size, --zones"):
                aks_machine_add(
                    self.cmd,
                    self.client,
                    "rg",
                    "cluster",
                    "flexpool",
                    machine_name="flexnode01",
                    kubernetes_version="1.35.5",
                    vm_size="Standard_D4s_v3",
                    zones=["1"],
                )

    def test_regular_machine_add_rejects_flexnode_only_options(self):
        regular_pool = self.models.UnifiedAgentPoolModel(type_properties_type="VirtualMachines")
        with patch("azext_aks_preview.custom.cf_agent_pools") as mock_cf, patch(
            "azext_aks_preview.custom.get_user_supplied_argument_options",
            return_value={
                "labels": "--labels",
                "node_taints": "--node-taints",
                "max_pods": "--max-pods",
            },
        ):
            mock_cf.return_value.get.return_value = regular_pool
            with self.assertRaisesRegex(
                InvalidArgumentValueError,
                "--labels, --max-pods, --node-taints",
            ):
                aks_machine_add(
                    self.cmd,
                    self.client,
                    "rg",
                    "cluster",
                    "machinepool",
                    machine_name="machine01",
                    vm_size="Standard_D4s_v3",
                    labels={"role": "edge"},
                    node_taints="dedicated=edge:NoSchedule",
                    max_pods=75,
                )

    def test_update_flexnode_machine_preserves_immutable_fields(self):
        existing = self.models.Machine(
            properties=self.models.MachineProperties(
                kubernetes=self.models.MachineKubernetesProfile(
                    orchestrator_version="1.35.5",
                    max_pods=75,
                    node_labels={"role": "edge"},
                    node_taints=["dedicated=edge:NoSchedule"],
                )
            )
        )
        self.client.get.side_effect = None
        self.client.get.return_value = existing
        with patch(
            "azext_aks_preview._helpers.get_user_supplied_argument_options",
            return_value={
                "labels": "--labels",
                "node_taints": "--node-taints",
                "kubernetes_version": "--kubernetes-version",
            },
        ):
            aks_machine_update(
                self.cmd,
                self.client,
                "rg",
                "cluster",
                "flexpool",
                machine_name="flexnode01",
                labels=["role=updated"],
                node_taints="dedicated=updated:NoSchedule",
                kubernetes_version="1.36.1",
            )

        machine = self.client.begin_create_or_update.call_args.args[4]
        self.assertEqual(machine.properties.kubernetes.orchestrator_version, "1.36.1")
        self.assertEqual(machine.properties.kubernetes.max_pods, 75)
        self.assertEqual(machine.properties.kubernetes.node_labels, {"role": "updated"})
        self.assertEqual(machine.properties.kubernetes.node_taints, ["dedicated=updated:NoSchedule"])

    def test_regular_machine_rejects_kubernetes_version_update(self):
        existing = self.models.Machine(
            properties=self.models.MachineProperties(
                hardware=self.models.MachineHardwareProfile(vm_size="Standard_D4s_v3"),
                kubernetes=self.models.MachineKubernetesProfile(orchestrator_version="1.35.5")
            )
        )
        self.client.get.side_effect = None
        self.client.get.return_value = existing
        with self.assertRaisesRegex(
            InvalidArgumentValueError,
            "only supported for FlexNode machines",
        ):
            aks_machine_update(
                self.cmd,
                self.client,
                "rg",
                "cluster",
                "machinepool",
                machine_name="machine01",
                kubernetes_version="1.36.1",
            )

    def test_machine_update_argument_surface(self):
        loader = ContainerServiceCommandsLoader(self.cmd.cli_ctx)
        loader.load_command_table(["aks", "machine", "update"])
        command = loader.command_table["aks machine update"]
        command.load_arguments()

        self.assertIn("kubernetes_version", command.arguments)
        self.assertIn("labels", command.arguments)
        self.assertIn("node_taints", command.arguments)
        self.assertNotIn("max_pods", command.arguments)

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
