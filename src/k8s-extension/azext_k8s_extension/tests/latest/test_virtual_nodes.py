# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import unittest
from types import SimpleNamespace
from unittest.mock import patch

from azure.cli.core.azclierror import InvalidArgumentValueError

from azext_k8s_extension.partner_extensions.VirtualNodes import validate_node_pools


class TestVirtualNodes(unittest.TestCase):

    @patch("azure.cli.command_modules.vm.operations.vm.VMListSizes")
    def test_validate_node_pools_accepts_qualifying_pool(self, vm_list_sizes):
        vm_list_sizes.return_value.return_value = [
            {
                "name": "Standard_D2s_v5",
                "numberOfCores": 2,
                "memoryInMB": 8192,
            },
            {
                "name": "Standard_D8s_v5",
                "numberOfCores": 8,
                "memoryInMB": 32768,
            },
        ]
        cmd = SimpleNamespace(cli_ctx=object())
        cluster = SimpleNamespace(
            location="westus2",
            name="test-cluster",
            agent_pool_profiles=[
                SimpleNamespace(vm_size="Standard_D2s_v5"),
                SimpleNamespace(vm_size="Standard_D8s_v5"),
            ],
        )

        validate_node_pools(cmd, cluster)

        vm_list_sizes.assert_called_once_with(cli_ctx=cmd.cli_ctx)
        vm_list_sizes.return_value.assert_called_once_with(command_args={"location": "westus2"})

    @patch("azure.cli.command_modules.vm.operations.vm.VMListSizes")
    def test_validate_node_pools_rejects_non_qualifying_pools(self, vm_list_sizes):
        vm_list_sizes.return_value.return_value = [
            {
                "name": "Standard_D2s_v5",
                "numberOfCores": 2,
                "memoryInMB": 8192,
            },
        ]
        cmd = SimpleNamespace(cli_ctx=object())
        cluster = SimpleNamespace(
            location="westus2",
            name="test-cluster",
            agent_pool_profiles=[
                SimpleNamespace(vm_size="Standard_D2s_v5"),
                SimpleNamespace(vm_size="Unknown_Size"),
            ],
        )

        with self.assertRaisesRegex(
                InvalidArgumentValueError,
                "No node pool in cluster 'test-cluster' meets the minimum requirements"):
            validate_node_pools(cmd, cluster)
