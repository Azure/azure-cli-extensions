# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import io
import unittest
from unittest.mock import Mock, patch

from azure.cli.core import MainCommandsLoader, get_default_cli
from azure.cli.core.aaz._command_ctx import AAZCommandCtx

from azext_workload_manager import WorkloadManagerCommandsLoader
from azext_workload_manager.aaz.latest.workload_manager.workload_space.runtime_link import Create


class RuntimeLinkCreateTest(unittest.TestCase):

    _RESOURCE_GROUP_ID = "/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/workload-rg"
    _SPACE_ID = f"{_RESOURCE_GROUP_ID}/providers/Microsoft.Compute/workloadSpaces/workload-space"
    _SUBNET_ID = f"{_RESOURCE_GROUP_ID}/providers/Microsoft.Network/virtualNetworks/workload-vnet/subnets/mvnp"
    _IDENTITY_ID = f"{_RESOURCE_GROUP_ID}/providers/Microsoft.ManagedIdentity/userAssignedIdentities/integration"

    def test_cli_serializes_optional_subnet_and_preserves_existing_properties(self):
        requests = []

        def load_workload_commands(main_loader, args):
            loader = WorkloadManagerCommandsLoader(cli_ctx=main_loader.cli_ctx)
            main_loader.command_table = loader.load_command_table(args)
            main_loader.cmd_to_loader_map = {name: [loader] for name in main_loader.command_table}
            for command in main_loader.command_table.values():
                command.command_source = "workload-manager"
            return main_loader.command_table

        def serialize_request(command, command_args):
            ctx = AAZCommandCtx(command.cli_ctx, command.get_arguments_schema(), command_args)
            ctx.format_args()
            ctx.get_http_client = Mock(return_value=Mock())
            content = command.RuntimeLinksCreateOrUpdate(ctx=ctx).content
            requests.append(content)
            return content

        with patch.object(MainCommandsLoader, "load_command_table", load_workload_commands), patch.object(
                Create, "_handler", autospec=True, side_effect=serialize_request), patch(
                "socket.socket.connect", side_effect=AssertionError("Unexpected network request")):
            for subnet in (None, self._SUBNET_ID):
                with self.subTest(subnet=subnet):
                    requests.clear()
                    cli = get_default_cli()
                    arguments = [
                        "workload-manager", "workload-space", "runtime-link", "create",
                        "-g", "workload-rg", "--space-name", "workload-space", "-n", "link",
                        "-l", "eastus2",
                        "--orchestrator-binding", f"{self._SPACE_ID}/runtimeBindings/aks",
                        "--execution-binding", f"{self._SPACE_ID}/runtimeBindings/aci",
                        "--capacity-profile", "{minimum-nodes:1,maximum-nodes:100}",
                        "--integration-profile", f"{{managed-identity-resource-id:{self._IDENTITY_ID}}}",
                        "--tags", "environment=test", "--only-show-errors", "-o", "none",
                    ]
                    properties = {
                        "orchestratorBindingResourceId": f"{self._SPACE_ID}/runtimeBindings/aks",
                        "executionBindingResourceId": f"{self._SPACE_ID}/runtimeBindings/aci",
                        "capacityProfile": {"minimumNodes": 1, "maximumNodes": 100},
                        "integrationProfile": {"managedIdentityResourceId": self._IDENTITY_ID},
                    }
                    if subnet is not None:
                        arguments.extend(["--subnet-resource-id", subnet])
                        properties["subnetResourceId"] = subnet

                    self.assertEqual(cli.invoke(arguments, out_file=io.StringIO()), 0)
                    self.assertEqual(requests, [{
                        "location": "eastus2",
                        "tags": {"environment": "test"},
                        "properties": properties,
                    }])


if __name__ == "__main__":
    unittest.main()
