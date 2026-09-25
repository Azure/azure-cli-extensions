# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from azext_connectedvmware.custom import create_from_machines


class CreateFromMachinesTest(unittest.TestCase):
    @patch('azext_connectedvmware.custom.get_logger')
    @patch('azext_connectedvmware.custom.get_resources_client')
    @patch('azext_connectedvmware.custom.cf_machine')
    @patch('azext_connectedvmware.custom.cf_resource_graph')
    def test_cross_subscription_machines(
        self,
        mock_cf_resource_graph,
        mock_cf_machine,
        mock_get_resources_client,
        _,
    ):
        machine_sub = "11111111-1111-1111-1111-111111111111"
        vcenter_sub = "22222222-2222-2222-2222-222222222222"
        machine_id = (
            f"/subscriptions/{machine_sub}/resourceGroups/machine-rg/"
            "providers/Microsoft.HybridCompute/machines/machine-1"
        )
        vcenter_id = (
            f"/subscriptions/{vcenter_sub}/resourceGroups/vcenter-rg/"
            "providers/Microsoft.ConnectedVMwareVsphere/vcenters/vcenter-1"
        )

        cmd = SimpleNamespace(cli_ctx=MagicMock())
        cmd.cli_ctx.data = {"subscription_id": machine_sub}
        vcenter = SimpleNamespace(
            id=vcenter_id,
            name="vcenter-1",
            kind="VMware",
            location="eastus",
            extended_location=SimpleNamespace(name="custom-location"),
        )
        mock_get_resources_client.return_value.get_by_id.return_value = vcenter

        query_response = SimpleNamespace(
            data=[{
                "machineId": machine_id,
                "name": "machine-1",
                "resourceGroup": "machine-rg",
                "kind": "",
                "inventoryId": f"{vcenter_id}/InventoryItems/vm-1",
                "managedResourceId": "",
                "biosId": "bios-1",
            }],
            skip_token=None,
        )
        arg_client = mock_cf_resource_graph.return_value
        arg_client.resources.return_value = query_response

        machine_client = mock_cf_machine.return_value
        vm_client = MagicMock()

        create_from_machines(
            cmd,
            vm_client,
            vcenter_id,
            rg_name="machine-rg",
            resource_name="machine-1",
        )

        query_request = arg_client.resources.call_args.args[0]
        self.assertEqual(
            query_request.subscriptions,
            [machine_sub, vcenter_sub],
        )
        self.assertIn(
            f"subscriptionId =~ '{machine_sub}'",
            query_request.query,
        )
        self.assertIn(machine_id, query_request.query)
        mock_get_resources_client.assert_called_once_with(
            cmd.cli_ctx, vcenter_sub
        )
        mock_cf_machine.assert_called_once_with(cmd.cli_ctx)
        machine_client.update.assert_called_once()
        vm_client.begin_create_or_update.assert_called_once()


if __name__ == '__main__':
    unittest.main()
