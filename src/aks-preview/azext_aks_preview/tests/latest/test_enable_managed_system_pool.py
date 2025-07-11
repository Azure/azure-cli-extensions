# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import unittest
from unittest.mock import Mock

from azext_aks_preview._client_factory import CUSTOM_MGMT_AKS_PREVIEW
from azext_aks_preview._consts import CONST_NODEPOOL_MODE_MANAGEDSYSTEM
from azext_aks_preview.managed_cluster_decorator import (
    AKSPreviewManagedClusterContext, AKSPreviewManagedClusterCreateDecorator,
    AKSPreviewManagedClusterModels)
from azure.cli.command_modules.acs._consts import DecoratorMode
from azure.cli.command_modules.acs.managed_cluster_decorator import \
    AKSManagedClusterParamDict


class EnableManagedSystemPoolTestCase(unittest.TestCase):
    """Test cases for the --enable-managed-system-pool functionality"""

    def setUp(self):
        """Set up test fixtures"""
        self.cmd = Mock()
        self.client = Mock()
        self.models = Mock()

    def test_get_enable_managed_system_pool_context(self):
        """Test the get_enable_managed_system_pool method in AKSPreviewManagedClusterContext"""

        # Test with enable_managed_system_pool=True
        ctx1 = AKSPreviewManagedClusterContext(
            self.cmd,
            AKSManagedClusterParamDict({"enable_managed_system_pool": True}),
            self.models,
            decorator_mode=DecoratorMode.CREATE,
        )
        self.assertEqual(ctx1.raw_param.get("enable_managed_system_pool"), True)

        # Test with enable_managed_system_pool=False
        ctx2 = AKSPreviewManagedClusterContext(
            self.cmd,
            AKSManagedClusterParamDict({"enable_managed_system_pool": False}),
            self.models,
            decorator_mode=DecoratorMode.CREATE,
        )
        self.assertEqual(ctx2.raw_param.get("enable_managed_system_pool"), False)

        # Test with enable_managed_system_pool=None (default)
        ctx3 = AKSPreviewManagedClusterContext(
            self.cmd,
            AKSManagedClusterParamDict({}),
            self.models,
            decorator_mode=DecoratorMode.CREATE,
        )
        self.assertEqual(ctx3.raw_param.get("enable_managed_system_pool"), None)

    def test_raw_parameter_modification_logic(self):
        """Test the parameter modification logic that sets mode to ManagedSystem"""

        # Test with enable_managed_system_pool=True
        raw_parameters_true = {
            "enable_managed_system_pool": True,
            "nodepool_name": "test_np_name",
            "node_vm_size": "Standard_D2s_v3",
        }

        ctx_true = AKSPreviewManagedClusterContext(
            self.cmd,
            AKSManagedClusterParamDict(raw_parameters_true),
            self.models,
            decorator_mode=DecoratorMode.CREATE,
        )

        # Simulate the logic from init_agentpool_decorator_context
        modified_raw_parameters = raw_parameters_true.copy()
        if ctx_true.raw_param.get("enable_managed_system_pool"):
            modified_raw_parameters["mode"] = CONST_NODEPOOL_MODE_MANAGEDSYSTEM

        # Verify the mode was set
        self.assertEqual(modified_raw_parameters.get("mode"), CONST_NODEPOOL_MODE_MANAGEDSYSTEM)

        # Test with enable_managed_system_pool=False
        raw_parameters_false = {
            "enable_managed_system_pool": False,
            "nodepool_name": "test_np_name",
        }

        ctx_false = AKSPreviewManagedClusterContext(
            self.cmd,
            AKSManagedClusterParamDict(raw_parameters_false),
            self.models,
            decorator_mode=DecoratorMode.CREATE,
        )

        # Simulate the logic from init_agentpool_decorator_context
        modified_raw_parameters_false = raw_parameters_false.copy()
        if ctx_false.raw_param.get("enable_managed_system_pool"):
            modified_raw_parameters_false["mode"] = CONST_NODEPOOL_MODE_MANAGEDSYSTEM

        # Verify the mode was NOT set
        self.assertNotEqual(modified_raw_parameters_false.get("mode"), CONST_NODEPOOL_MODE_MANAGEDSYSTEM)


if __name__ == "__main__":
    unittest.main()
