# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import unittest
from azure.cli.core.azclierror import InvalidArgumentValueError, CLIInternalError
from azure.cli.core import AzCommandsLoader
from azure.cli.core.commands import AzCliCommand
from azure.cli.core.mock import DummyCli

from azext_connectedvmware.vmware_utils import get_resource_id


class TestGetResourceId(unittest.TestCase):
    @staticmethod
    def _get_test_cmd():
        cli_ctx = DummyCli()
        cli_ctx.data["subscription_id"] = "00000000-0000-0000-0000-000000000000"  # type: ignore
        loader = AzCommandsLoader(cli_ctx)
        cmd = AzCliCommand(loader, "test", None)
        cmd.cli_ctx = cli_ctx
        return cmd

    def test_get_resource_id_no_name_no_children(self):
        cmd = self._get_test_cmd()

        result = get_resource_id(
            cmd, "contoso-rg", "Microsoft.HybridCompute", "Machines", None
        )

        self.assertIsNone(result)

    def test_get_resource_id_invalid_resource_name(self):
        cmd = self._get_test_cmd()

        with self.assertRaises(InvalidArgumentValueError):
            get_resource_id(
                cmd,
                "contoso-rg",
                "Microsoft.HybridCompute",
                "Machines",
                "invalid/resource",
            )

    def test_get_resource_id_with_child1_id_and_diff_rg(self):
        cmd = self._get_test_cmd()

        res_id = (
            "/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/contoso-rg"
            "/providers/Microsoft.HybridCompute/Machines/contoso-machine"
            "/providers/Microsoft.ConnectedVMwarevSphere/VirtualMachineInstances/default"
        )
        result = get_resource_id(
            cmd,
            "contoso-parent-rg",
            "Microsoft.HybridCompute",
            "Machines",
            None,
            child_type_1="VirtualMachineInstances",
            child_name_1=res_id,
        )

        expected_result = res_id
        assert result is not None
        self.assertEqual(result, expected_result)

    def test_get_resource_id_with_child2_id_and_diff_sub_id(self):
        cmd = self._get_test_cmd()

        res_id = (
            "/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/contoso-rg"
            "/providers/Microsoft.HybridCompute/Machines/contoso-machine"
            "/providers/Microsoft.ConnectedVMwarevSphere/VirtualMachineInstances/default/guestagents/default"
        )

        result = get_resource_id(
            cmd,
            "contoso-rg",
            "Microsoft.HybridCompute",
            "Machines",
            "contoso-machine",
            child_namespace_1="Microsoft.ConnectedVMwarevSphere",
            child_type_1="VirtualMachineInstances",
            child_name_1="default",
            child_type_2="guestagents",
            child_name_2="default",
        )

        expected_result = res_id
        assert result is not None
        self.assertEqual(result.lower(), expected_result.lower())

    def test_get_resource_id_with_intermediate_id_and_diff_sub_id(self):
        cmd = self._get_test_cmd()

        inter_res_id = (
            "/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/contoso-rg"
            "/providers/Microsoft.HybridCompute/Machines/contoso-machine"
            "/providers/Microsoft.ConnectedVMwarevSphere/VirtualMachineInstances/default"
        )

        result = get_resource_id(
            cmd,
            "contoso-rg",
            "Microsoft.HybridCompute",
            "Machines",
            None,
            child_type_1="VirtualMachineInstances",
            child_name_1=inter_res_id,
            child_type_2="guestagents",
            child_name_2="default",
        )

        expected_result = f"{inter_res_id}/guestagents/default"
        assert result is not None
        self.assertEqual(result.lower(), expected_result.lower())

    def test_get_resource_id_with_multiple_id(self):
        cmd = self._get_test_cmd()

        inter_res_id = (
            "/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/contoso-rg"
            "/providers/Microsoft.HybridCompute/Machines/contoso-machine"
            "/providers/Microsoft.ConnectedVMwarevSphere/VirtualMachineInstances/default"
        )

        res_id = f"{inter_res_id}/guestagents/default"

        result = get_resource_id(
            cmd,
            "contoso-rg",
            "Microsoft.HybridCompute",
            "Machines",
            None,
            child_type_1="VirtualMachineInstances",
            child_name_1=inter_res_id,
            child_type_2="guestagents",
            child_name_2=res_id,
        )

        expected_result = res_id
        assert result is not None
        self.assertEqual(result.lower(), expected_result.lower())

    def test_get_resource_id_with_final_child_none(self):
        cmd = self._get_test_cmd()

        res_id = (
            "/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/contoso-rg"
            "/providers/Microsoft.HybridCompute/Machines/contoso-machine"
            "/providers/Microsoft.SCVMM/VirtualMachineInstances/default"
        )

        result = get_resource_id(
            cmd,
            "contoso-rg",
            "Microsoft.HybridCompute",
            "Machines",
            "contoso-machine",
            child_namespace_1="Microsoft.SCVMM",
            child_type_1="VirtualMachineInstances",
            child_name_1=res_id,
            child_type_2="guestagents",
            child_name_2=None,
        )

        self.assertIsNone(result)

    def test_get_resource_id_with_invalid_child_type(self):
        cmd = self._get_test_cmd()

        inter_res_id = (
            "/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/contoso-rg"
            "/providers/Microsoft.HybridCompute/Machines/contoso-machine"
            "/providers/Microsoft.ConnectedVMwarevSphere/VirtualMachines/default"
        )

        with self.assertRaises(InvalidArgumentValueError):
            get_resource_id(
                cmd,
                "contoso-rg",
                "Microsoft.HybridCompute",
                "Machines",
                None,
                child_type_1="VirtualMachineInstances",
                child_name_1=inter_res_id,
                child_type_2="guestagents",
                child_name_2="default",
            )

    def test_get_resource_id_with_invalid_resource_id(self):
        cmd = self._get_test_cmd()

        # Contains extra slash
        inter_res_id = (
            "/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/contoso-rg"
            "/providers/Microsoft.HybridCompute/Machines/contoso-machine"
            "/providers/Microsoft.ConnectedVMwarevSphere//VirtualMachineInstances/default"
        )

        with self.assertRaises(InvalidArgumentValueError):
            get_resource_id(
                cmd,
                "contoso-rg",
                "Microsoft.HybridCompute",
                "Machines",
                None,
                child_type_1="VirtualMachineInstances",
                child_name_1=inter_res_id,
                child_type_2="guestagents",
                child_name_2="default",
            )

    def test_get_resource_id_with_type_none(self):
        cmd = self._get_test_cmd()

        with self.assertRaises(CLIInternalError):
            get_resource_id(
                cmd,
                "contoso-rg",
                "Microsoft.HybridCompute",
                "Machines",
                "contoso-machine",
                child_type_1=None,
                child_name_1="VirtualMachineInstances/default",
            )

    def test_get_resource_id_with_namespace_dangling(self):
        cmd = self._get_test_cmd()

        with self.assertRaises(CLIInternalError):
            get_resource_id(
                cmd,
                "contoso-rg",
                "Microsoft.HybridCompute",
                "Machines",
                "contoso-machine",
                child_namespace_1="Microsoft.ConnectedVMwarevSphere",
            )

    def test_get_resource_id_with_namespace_none(self):
        cmd = self._get_test_cmd()

        with self.assertRaises(CLIInternalError):
            get_resource_id(
                cmd,
                "contoso-rg",
                "Microsoft.HybridCompute",
                "Machines",
                "contoso-machine",
                child_type_1="VirtualMachineInstances",
                child_name_1="default",
                child_namespace_1=None,
            )

    def test_get_resource_id_with_name_missing(self):
        cmd = self._get_test_cmd()

        with self.assertRaises(CLIInternalError):
            get_resource_id(
                cmd,
                "contoso-rg",
                "Microsoft.HybridCompute",
                "Machines",
                "contoso-machine",
                child_type_1="VirtualMachineInstances",
            )


if __name__ == "__main__":
    unittest.main()
