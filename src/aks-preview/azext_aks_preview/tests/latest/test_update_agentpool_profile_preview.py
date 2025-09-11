# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import unittest
from unittest.mock import Mock, patch

from azext_aks_preview.__init__ import register_aks_preview_resource_type
from azext_aks_preview._client_factory import CUSTOM_MGMT_AKS_PREVIEW
from azext_aks_preview._consts import CONST_NODEPOOL_MODE_MANAGEDSYSTEM
from azext_aks_preview.agentpool_decorator import (
    AKSPreviewAgentPoolModels,
    AKSPreviewAgentPoolUpdateDecorator,
)
from azure.cli.command_modules.acs._consts import (
    CONST_DEFAULT_NODE_OS_TYPE,
    CONST_DEFAULT_NODE_VM_SIZE,
    CONST_NODEPOOL_MODE_SYSTEM,
    CONST_NODEPOOL_MODE_USER,
    CONST_SCALE_DOWN_MODE_DELETE,
    CONST_VIRTUAL_MACHINE_SCALE_SETS,
    AgentPoolDecoratorMode,
    DecoratorMode,
)
from azure.cli.command_modules.acs.agentpool_decorator import AKSAgentPoolParamDict
from azure.cli.command_modules.acs.tests.latest.mocks import (
    MockCLI,
    MockClient,
    MockCmd,
)
from azure.cli.core.azclierror import CLIInternalError


class TestUpdateAgentPoolProfilePreview(unittest.TestCase):
    """Test class for the update_agentpool_profile_preview method."""

    def setUp(self):
        """Set up test fixtures."""
        # manually register CUSTOM_MGMT_AKS_PREVIEW
        register_aks_preview_resource_type()
        self.cli_ctx = MockCLI()
        self.cmd = MockCmd(self.cli_ctx)
        self.resource_type = CUSTOM_MGMT_AKS_PREVIEW
        self.agentpool_decorator_mode = AgentPoolDecoratorMode.STANDALONE
        self.models = AKSPreviewAgentPoolModels(
            self.cmd, self.resource_type, self.agentpool_decorator_mode
        )
        self.client = MockClient()

    def _create_initialized_agentpool_instance(
        self,
        nodepool_name="nodepool1",
        **kwargs
    ):
        """Helper method to create an initialized AgentPool instance."""
        # Create AgentPool similar to existing test pattern
        if self.agentpool_decorator_mode == AgentPoolDecoratorMode.MANAGED_CLUSTER:
            agentpool = self.models.UnifiedAgentPoolModel(name=nodepool_name)
        else:
            agentpool = self.models.UnifiedAgentPoolModel()
            agentpool.name = nodepool_name

        # Set properties
        for key, value in kwargs.items():
            setattr(agentpool, key, value)

        # Set default values if not provided
        if not hasattr(agentpool, 'vm_size') or agentpool.vm_size is None:
            agentpool.vm_size = kwargs.get("vm_size", CONST_DEFAULT_NODE_VM_SIZE)
        if not hasattr(agentpool, 'os_type') or agentpool.os_type is None:
            agentpool.os_type = kwargs.get("os_type", CONST_DEFAULT_NODE_OS_TYPE)
        if not hasattr(agentpool, 'enable_node_public_ip') or agentpool.enable_node_public_ip is None:
            agentpool.enable_node_public_ip = kwargs.get("enable_node_public_ip", False)
        if not hasattr(agentpool, 'enable_auto_scaling') or agentpool.enable_auto_scaling is None:
            agentpool.enable_auto_scaling = kwargs.get("enable_auto_scaling", False)
        if not hasattr(agentpool, 'count') or agentpool.count is None:
            agentpool.count = kwargs.get("count", 3)
        if not hasattr(agentpool, 'node_taints') or agentpool.node_taints is None:
            agentpool.node_taints = kwargs.get("node_taints", [])
        if not hasattr(agentpool, 'os_disk_size_gb') or agentpool.os_disk_size_gb is None:
            agentpool.os_disk_size_gb = kwargs.get("os_disk_size_gb", 0)
        if not hasattr(agentpool, 'type_properties_type') or agentpool.type_properties_type is None:
            agentpool.type_properties_type = kwargs.get("type_properties_type", CONST_VIRTUAL_MACHINE_SCALE_SETS)
        if not hasattr(agentpool, 'enable_encryption_at_host') or agentpool.enable_encryption_at_host is None:
            agentpool.enable_encryption_at_host = kwargs.get("enable_encryption_at_host", False)
        if not hasattr(agentpool, 'enable_ultra_ssd') or agentpool.enable_ultra_ssd is None:
            agentpool.enable_ultra_ssd = kwargs.get("enable_ultra_ssd", False)
        if not hasattr(agentpool, 'enable_fips') or agentpool.enable_fips is None:
            agentpool.enable_fips = kwargs.get("enable_fips", False)
        if not hasattr(agentpool, 'mode') or agentpool.mode is None:
            agentpool.mode = kwargs.get("mode", CONST_NODEPOOL_MODE_USER)
        if not hasattr(agentpool, 'scale_down_mode') or agentpool.scale_down_mode is None:
            agentpool.scale_down_mode = kwargs.get("scale_down_mode", CONST_SCALE_DOWN_MODE_DELETE)

        return agentpool

    def test_update_agentpool_profile_preview_default_behavior(self):
        """Test the default behavior of update_agentpool_profile_preview."""
        # Arrange
        raw_param_dict = {
            "resource_group_name": "test_rg",
            "cluster_name": "test_cluster",
            "nodepool_name": "test_nodepool",
        }

        decorator = AKSPreviewAgentPoolUpdateDecorator(
            self.cmd,
            self.client,
            raw_param_dict,
            self.resource_type,
            self.agentpool_decorator_mode,
        )

        # Create a regular agentpool
        agentpool = self._create_initialized_agentpool_instance(
            nodepool_name="test_nodepool"
        )

        # Mock the update_agentpool_profile_default method
        decorator.update_agentpool_profile_default = Mock(return_value=agentpool)

        # Mock all the update methods to return the agentpool unchanged
        decorator.update_custom_ca_trust = Mock(return_value=agentpool)
        decorator.update_network_profile = Mock(return_value=agentpool)
        decorator.update_artifact_streaming = Mock(return_value=agentpool)
        decorator.update_secure_boot = Mock(return_value=agentpool)
        decorator.update_vtpm = Mock(return_value=agentpool)
        decorator.update_os_sku = Mock(return_value=agentpool)
        decorator.update_fips_image = Mock(return_value=agentpool)
        decorator.update_ssh_access = Mock(return_value=agentpool)
        decorator.update_localdns_profile = Mock(return_value=agentpool)
        decorator.update_auto_scaler_properties_vms = Mock(return_value=agentpool)
        decorator.update_upgrade_strategy = Mock(return_value=agentpool)
        decorator.update_blue_green_upgrade_settings = Mock(return_value=agentpool)

        # Act
        result = decorator.update_agentpool_profile_preview()

        # Assert
        self.assertEqual(result, agentpool)

        # Verify that update_agentpool_profile_default was called
        decorator.update_agentpool_profile_default.assert_called_once_with(None)

        # Verify that all update methods were called
        decorator.update_custom_ca_trust.assert_called_once_with(agentpool)
        decorator.update_network_profile.assert_called_once_with(agentpool)
        decorator.update_artifact_streaming.assert_called_once_with(agentpool)
        decorator.update_secure_boot.assert_called_once_with(agentpool)
        decorator.update_vtpm.assert_called_once_with(agentpool)
        decorator.update_os_sku.assert_called_once_with(agentpool)
        decorator.update_fips_image.assert_called_once_with(agentpool)
        decorator.update_ssh_access.assert_called_once_with(agentpool)
        decorator.update_localdns_profile.assert_called_once_with(agentpool)
        decorator.update_auto_scaler_properties_vms.assert_called_once_with(agentpool)
        decorator.update_upgrade_strategy.assert_called_once_with(agentpool)
        decorator.update_blue_green_upgrade_settings.assert_called_once_with(agentpool)

    def test_update_agentpool_profile_preview_with_agentpools_parameter(self):
        """Test update_agentpool_profile_preview with agentpools parameter."""
        # Arrange
        raw_param_dict = {
            "resource_group_name": "test_rg",
            "cluster_name": "test_cluster",
            "nodepool_name": "test_nodepool",
        }

        decorator = AKSPreviewAgentPoolUpdateDecorator(
            self.cmd,
            self.client,
            raw_param_dict,
            self.resource_type,
            self.agentpool_decorator_mode,
        )

        # Create a regular agentpool
        agentpool = self._create_initialized_agentpool_instance(
            nodepool_name="test_nodepool"
        )

        agentpools = [agentpool]

        # Mock the update_agentpool_profile_default method
        decorator.update_agentpool_profile_default = Mock(return_value=agentpool)

        # Mock all the update methods to return the agentpool unchanged
        decorator.update_custom_ca_trust = Mock(return_value=agentpool)
        decorator.update_network_profile = Mock(return_value=agentpool)
        decorator.update_artifact_streaming = Mock(return_value=agentpool)
        decorator.update_secure_boot = Mock(return_value=agentpool)
        decorator.update_vtpm = Mock(return_value=agentpool)
        decorator.update_os_sku = Mock(return_value=agentpool)
        decorator.update_fips_image = Mock(return_value=agentpool)
        decorator.update_ssh_access = Mock(return_value=agentpool)
        decorator.update_localdns_profile = Mock(return_value=agentpool)
        decorator.update_auto_scaler_properties_vms = Mock(return_value=agentpool)
        decorator.update_upgrade_strategy = Mock(return_value=agentpool)
        decorator.update_blue_green_upgrade_settings = Mock(return_value=agentpool)

        # Act
        result = decorator.update_agentpool_profile_preview(agentpools)

        # Assert
        self.assertEqual(result, agentpool)

        # Verify that update_agentpool_profile_default was called with agentpools
        decorator.update_agentpool_profile_default.assert_called_once_with(agentpools)

    def test_update_agentpool_profile_preview_managed_system_mode(self):
        """Test update_agentpool_profile_preview with ManagedSystem mode."""
        # Arrange
        raw_param_dict = {
            "resource_group_name": "test_rg",
            "cluster_name": "test_cluster",
            "nodepool_name": "test_nodepool",
        }

        decorator = AKSPreviewAgentPoolUpdateDecorator(
            self.cmd,
            self.client,
            raw_param_dict,
            self.resource_type,
            self.agentpool_decorator_mode,
        )

        # Create a ManagedSystem agentpool with some non-None attributes
        agentpool = self._create_initialized_agentpool_instance(
            nodepool_name="test_nodepool",
            mode=CONST_NODEPOOL_MODE_MANAGEDSYSTEM,
            vm_size="Standard_D2s_v3",
            count=5,
            enable_custom_ca_trust=True,
        )

        # Mock the update_agentpool_profile_default method
        decorator.update_agentpool_profile_default = Mock(return_value=agentpool)

        # Mock all the update methods (they should not be called for ManagedSystem mode)
        decorator.update_custom_ca_trust = Mock()
        decorator.update_network_profile = Mock()
        decorator.update_artifact_streaming = Mock()
        decorator.update_secure_boot = Mock()
        decorator.update_vtpm = Mock()
        decorator.update_os_sku = Mock()
        decorator.update_fips_image = Mock()
        decorator.update_ssh_access = Mock()
        decorator.update_localdns_profile = Mock()
        decorator.update_auto_scaler_properties_vms = Mock()
        decorator.update_upgrade_strategy = Mock()
        decorator.update_blue_green_upgrade_settings = Mock()

        # Act
        result = decorator.update_agentpool_profile_preview()

        # Assert
        self.assertEqual(result.name, "test_nodepool")
        self.assertEqual(result.mode, CONST_NODEPOOL_MODE_MANAGEDSYSTEM)

        # Verify that all other attributes are None (except name, mode, and internal attributes)
        for attr in vars(result):
            if attr != 'name' and attr != 'mode' and not attr.startswith('_'):
                self.assertIsNone(getattr(result, attr), f"Attribute {attr} should be None for ManagedSystem mode")

        # Verify that update_agentpool_profile_default was called
        decorator.update_agentpool_profile_default.assert_called_once_with(None)

        # Verify that none of the update methods were called for ManagedSystem mode
        decorator.update_custom_ca_trust.assert_not_called()
        decorator.update_network_profile.assert_not_called()
        decorator.update_artifact_streaming.assert_not_called()
        decorator.update_secure_boot.assert_not_called()
        decorator.update_vtpm.assert_not_called()
        decorator.update_os_sku.assert_not_called()
        decorator.update_fips_image.assert_not_called()
        decorator.update_ssh_access.assert_not_called()
        decorator.update_localdns_profile.assert_not_called()
        decorator.update_auto_scaler_properties_vms.assert_not_called()
        decorator.update_upgrade_strategy.assert_not_called()
        decorator.update_blue_green_upgrade_settings.assert_not_called()

    def test_update_agentpool_profile_preview_managed_system_mode_with_agentpools(self):
        """Test update_agentpool_profile_preview with ManagedSystem mode and agentpools parameter."""
        # Arrange
        raw_param_dict = {
            "resource_group_name": "test_rg",
            "cluster_name": "test_cluster",
            "nodepool_name": "test_nodepool",
        }

        decorator = AKSPreviewAgentPoolUpdateDecorator(
            self.cmd,
            self.client,
            raw_param_dict,
            self.resource_type,
            self.agentpool_decorator_mode,
        )

        # Create a ManagedSystem agentpool
        agentpool = self._create_initialized_agentpool_instance(
            nodepool_name="test_nodepool",
            mode=CONST_NODEPOOL_MODE_MANAGEDSYSTEM,
        )

        agentpools = [agentpool]

        # Mock the update_agentpool_profile_default method
        decorator.update_agentpool_profile_default = Mock(return_value=agentpool)

        # Act
        result = decorator.update_agentpool_profile_preview(agentpools)

        # Assert
        self.assertEqual(result.name, "test_nodepool")
        self.assertEqual(result.mode, CONST_NODEPOOL_MODE_MANAGEDSYSTEM)

        # Verify that update_agentpool_profile_default was called with agentpools
        decorator.update_agentpool_profile_default.assert_called_once_with(agentpools)

    def test_update_agentpool_profile_preview_system_mode_regular_flow(self):
        """Test update_agentpool_profile_preview with System mode (regular flow)."""
        # Arrange
        raw_param_dict = {
            "resource_group_name": "test_rg",
            "cluster_name": "test_cluster",
            "nodepool_name": "test_nodepool",
            "enable_custom_ca_trust": True,
        }

        decorator = AKSPreviewAgentPoolUpdateDecorator(
            self.cmd,
            self.client,
            raw_param_dict,
            self.resource_type,
            self.agentpool_decorator_mode,
        )

        # Create a System mode agentpool
        agentpool = self._create_initialized_agentpool_instance(
            nodepool_name="test_nodepool",
            mode=CONST_NODEPOOL_MODE_SYSTEM,
        )

        # Mock the update_agentpool_profile_default method
        decorator.update_agentpool_profile_default = Mock(return_value=agentpool)

        # Mock all the update methods to return the agentpool unchanged
        decorator.update_custom_ca_trust = Mock(return_value=agentpool)
        decorator.update_network_profile = Mock(return_value=agentpool)
        decorator.update_artifact_streaming = Mock(return_value=agentpool)
        decorator.update_secure_boot = Mock(return_value=agentpool)
        decorator.update_vtpm = Mock(return_value=agentpool)
        decorator.update_os_sku = Mock(return_value=agentpool)
        decorator.update_fips_image = Mock(return_value=agentpool)
        decorator.update_ssh_access = Mock(return_value=agentpool)
        decorator.update_localdns_profile = Mock(return_value=agentpool)
        decorator.update_auto_scaler_properties_vms = Mock(return_value=agentpool)
        decorator.update_upgrade_strategy = Mock(return_value=agentpool)
        decorator.update_blue_green_upgrade_settings = Mock(return_value=agentpool)

        # Act
        result = decorator.update_agentpool_profile_preview()

        # Assert
        self.assertEqual(result, agentpool)
        self.assertEqual(result.mode, CONST_NODEPOOL_MODE_SYSTEM)

        # Verify that all update methods were called for System mode
        decorator.update_custom_ca_trust.assert_called_once_with(agentpool)
        decorator.update_network_profile.assert_called_once_with(agentpool)
        decorator.update_artifact_streaming.assert_called_once_with(agentpool)
        decorator.update_secure_boot.assert_called_once_with(agentpool)
        decorator.update_vtpm.assert_called_once_with(agentpool)
        decorator.update_os_sku.assert_called_once_with(agentpool)
        decorator.update_fips_image.assert_called_once_with(agentpool)
        decorator.update_ssh_access.assert_called_once_with(agentpool)
        decorator.update_localdns_profile.assert_called_once_with(agentpool)
        decorator.update_auto_scaler_properties_vms.assert_called_once_with(agentpool)
        decorator.update_upgrade_strategy.assert_called_once_with(agentpool)
        decorator.update_blue_green_upgrade_settings.assert_called_once_with(agentpool)

    def test_update_agentpool_profile_preview_execution_order(self):
        """Test that update methods are called in the correct order."""
        # Arrange
        raw_param_dict = {
            "resource_group_name": "test_rg",
            "cluster_name": "test_cluster",
            "nodepool_name": "test_nodepool",
        }

        decorator = AKSPreviewAgentPoolUpdateDecorator(
            self.cmd,
            self.client,
            raw_param_dict,
            self.resource_type,
            self.agentpool_decorator_mode,
        )

        agentpool = self._create_initialized_agentpool_instance(
            nodepool_name="test_nodepool"
        )

        # Mock the update_agentpool_profile_default method
        decorator.update_agentpool_profile_default = Mock(return_value=agentpool)

        # Track the order of method calls
        call_order = []

        def create_mock_update_method(name):
            def mock_method(pool):
                call_order.append(name)
                return pool
            return Mock(side_effect=mock_method)

        decorator.update_custom_ca_trust = create_mock_update_method("update_custom_ca_trust")
        decorator.update_network_profile = create_mock_update_method("update_network_profile")
        decorator.update_artifact_streaming = create_mock_update_method("update_artifact_streaming")
        decorator.update_secure_boot = create_mock_update_method("update_secure_boot")
        decorator.update_vtpm = create_mock_update_method("update_vtpm")
        decorator.update_os_sku = create_mock_update_method("update_os_sku")
        decorator.update_fips_image = create_mock_update_method("update_fips_image")
        decorator.update_ssh_access = create_mock_update_method("update_ssh_access")
        decorator.update_localdns_profile = create_mock_update_method("update_localdns_profile")
        decorator.update_auto_scaler_properties_vms = create_mock_update_method("update_auto_scaler_properties_vms")
        decorator.update_upgrade_strategy = create_mock_update_method("update_upgrade_strategy")
        decorator.update_blue_green_upgrade_settings = create_mock_update_method("update_blue_green_upgrade_settings")

        # Act
        decorator.update_agentpool_profile_preview()

        # Assert
        expected_order = [
            "update_custom_ca_trust",
            "update_network_profile",
            "update_artifact_streaming",
            "update_secure_boot",
            "update_vtpm",
            "update_os_sku",
            "update_fips_image",
            "update_ssh_access",
            "update_localdns_profile",
            "update_auto_scaler_properties_vms",
            "update_upgrade_strategy",
            "update_blue_green_upgrade_settings"
        ]
        self.assertEqual(call_order, expected_order)

    def test_update_agentpool_profile_preview_preserves_agentpool_reference(self):
        """Test that the method preserves agentpool object reference throughout the chain."""
        # Arrange
        raw_param_dict = {
            "resource_group_name": "test_rg",
            "cluster_name": "test_cluster",
            "nodepool_name": "test_nodepool",
        }

        decorator = AKSPreviewAgentPoolUpdateDecorator(
            self.cmd,
            self.client,
            raw_param_dict,
            self.resource_type,
            self.agentpool_decorator_mode,
        )

        original_agentpool = self._create_initialized_agentpool_instance(
            nodepool_name="test_nodepool"
        )

        # Mock the update_agentpool_profile_default method
        decorator.update_agentpool_profile_default = Mock(return_value=original_agentpool)

        # Track the agentpool object passed to each method
        passed_agentpools = []

        def create_tracking_mock(name):
            def track_and_return(pool):
                passed_agentpools.append((name, pool))
                return pool
            return Mock(side_effect=track_and_return)

        decorator.update_custom_ca_trust = create_tracking_mock("update_custom_ca_trust")
        decorator.update_network_profile = create_tracking_mock("update_network_profile")
        decorator.update_artifact_streaming = create_tracking_mock("update_artifact_streaming")
        decorator.update_secure_boot = create_tracking_mock("update_secure_boot")
        decorator.update_vtpm = create_tracking_mock("update_vtpm")
        decorator.update_os_sku = create_tracking_mock("update_os_sku")
        decorator.update_fips_image = create_tracking_mock("update_fips_image")
        decorator.update_ssh_access = create_tracking_mock("update_ssh_access")
        decorator.update_localdns_profile = create_tracking_mock("update_localdns_profile")
        decorator.update_auto_scaler_properties_vms = create_tracking_mock("update_auto_scaler_properties_vms")
        decorator.update_upgrade_strategy = create_tracking_mock("update_upgrade_strategy")
        decorator.update_blue_green_upgrade_settings = create_tracking_mock("update_blue_green_upgrade_settings")        

        # Act
        result = decorator.update_agentpool_profile_preview()

        # Assert
        self.assertEqual(result, original_agentpool)

        # Verify that the same agentpool object was passed to all methods
        for method_name, passed_pool in passed_agentpools:
            self.assertIs(passed_pool, original_agentpool,
                         f"Method {method_name} should receive the same agentpool object")

    def test_update_agentpool_profile_preview_mixed_modes_scenario(self):
        """Test the method with different agentpool modes to ensure proper handling."""
        test_cases = [
            {
                "mode": CONST_NODEPOOL_MODE_USER,
                "expect_update_methods_called": True,
                "description": "User mode should trigger all update methods"
            },
            {
                "mode": CONST_NODEPOOL_MODE_SYSTEM,
                "expect_update_methods_called": True,
                "description": "System mode should trigger all update methods"
            },
            {
                "mode": CONST_NODEPOOL_MODE_MANAGEDSYSTEM,
                "expect_update_methods_called": False,
                "description": "ManagedSystem mode should skip all update methods"
            }
        ]

        for case in test_cases:
            with self.subTest(mode=case["mode"], description=case["description"]):
                # Arrange
                raw_param_dict = {
                    "resource_group_name": "test_rg",
                    "cluster_name": "test_cluster",
                    "nodepool_name": "test_nodepool",
                }

                decorator = AKSPreviewAgentPoolUpdateDecorator(
                    self.cmd,
                    self.client,
                    raw_param_dict,
                    self.resource_type,
                    self.agentpool_decorator_mode,
                )

                agentpool = self._create_initialized_agentpool_instance(
                    nodepool_name="test_nodepool",
                    mode=case["mode"]
                )

                # Mock the update_agentpool_profile_default method
                decorator.update_agentpool_profile_default = Mock(return_value=agentpool)

                # Mock all update methods
                update_methods = [
                    'update_custom_ca_trust', 'update_network_profile', 'update_artifact_streaming',
                    'update_secure_boot', 'update_vtpm', 'update_os_sku', 'update_fips_image',
                    'update_ssh_access', 'update_localdns_profile', 'update_auto_scaler_properties_vms', 
                    'update_upgrade_strategy', 'update_blue_green_upgrade_settings'
                ]

                for method_name in update_methods:
                    setattr(decorator, method_name, Mock(return_value=agentpool))

                # Act
                result = decorator.update_agentpool_profile_preview()

                # Assert
                self.assertEqual(result.mode, case["mode"])

                if case["expect_update_methods_called"]:
                    for method_name in update_methods:
                        getattr(decorator, method_name).assert_called_once_with(agentpool)
                else:
                    for method_name in update_methods:
                        getattr(decorator, method_name).assert_not_called()


class TestUpdateAgentPoolProfilePreviewManagedClusterMode(TestUpdateAgentPoolProfilePreview):
    """Test class for update_agentpool_profile_preview in ManagedCluster mode."""

    def setUp(self):
        """Set up test fixtures for ManagedCluster mode."""
        super().setUp()
        self.agentpool_decorator_mode = AgentPoolDecoratorMode.MANAGED_CLUSTER
        self.models = AKSPreviewAgentPoolModels(
            self.cmd, self.resource_type, self.agentpool_decorator_mode
        )

    def test_update_agentpool_profile_preview_managed_cluster_mode(self):
        """Test update_agentpool_profile_preview in ManagedCluster mode."""
        # This test verifies that the method works correctly in ManagedCluster mode
        # The core logic should be the same, but the decorator mode affects how
        # the context and models are initialized

        # Arrange
        raw_param_dict = {
            "resource_group_name": "test_rg",
            "name": "test_cluster",  # Note: 'name' instead of 'cluster_name' for ManagedCluster mode
        }

        decorator = AKSPreviewAgentPoolUpdateDecorator(
            self.cmd,
            self.client,
            raw_param_dict,
            self.resource_type,
            self.agentpool_decorator_mode,
        )

        agentpool = self._create_initialized_agentpool_instance(
            nodepool_name="test_nodepool"
        )

        agentpools = [agentpool]

        # Mock the update_agentpool_profile_default method
        decorator.update_agentpool_profile_default = Mock(return_value=agentpool)

        # Mock all the update methods
        decorator.update_custom_ca_trust = Mock(return_value=agentpool)
        decorator.update_network_profile = Mock(return_value=agentpool)
        decorator.update_artifact_streaming = Mock(return_value=agentpool)
        decorator.update_secure_boot = Mock(return_value=agentpool)
        decorator.update_vtpm = Mock(return_value=agentpool)
        decorator.update_os_sku = Mock(return_value=agentpool)
        decorator.update_fips_image = Mock(return_value=agentpool)
        decorator.update_ssh_access = Mock(return_value=agentpool)
        decorator.update_localdns_profile = Mock(return_value=agentpool)
        decorator.update_auto_scaler_properties_vms = Mock(return_value=agentpool)
        decorator.update_upgrade_strategy = Mock(return_value=agentpool)
        decorator.update_blue_green_upgrade_settings = Mock(return_value=agentpool)

        # Act
        result = decorator.update_agentpool_profile_preview(agentpools)

        # Assert
        self.assertEqual(result, agentpool)
        decorator.update_agentpool_profile_default.assert_called_once_with(agentpools)


if __name__ == "__main__":
    unittest.main()
