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
from azext_workload_manager.aaz.latest.workload_manager.workload_space.capability import Create


class CapabilityCreateTest(unittest.TestCase):

    def test_cli_accepts_and_serializes_capability_kinds(self):
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
            content = command.CapabilitiesCreateOrUpdate(ctx=ctx).content
            requests.append(content)
            return content

        cases = (
            ("AgentSandbox", "AgentSandbox"),
            ("PodSnapshotRestore", "PodSnapshotRestore"),
            ("podsnapshotrestore", "PodSnapshotRestore"),
        )
        with patch.object(MainCommandsLoader, "load_command_table", load_workload_commands), patch.object(
                Create, "_handler", autospec=True, side_effect=serialize_request), patch(
                "socket.socket.connect", side_effect=AssertionError("Unexpected network request")):
            for kind, expected_kind in cases:
                with self.subTest(kind=kind):
                    requests.clear()
                    cli = get_default_cli()
                    arguments = [
                        "workload-manager", "workload-space", "capability", "create",
                        "-g", "workload-rg", "--space-name", "workload-space", "-n", "capability",
                        "-l", "eastus2", "--kind", kind, "--version-policy", "ServiceManaged",
                        "--only-show-errors", "-o", "none",
                    ]
                    self.assertEqual(cli.invoke(arguments, out_file=io.StringIO()), 0)
                    self.assertEqual(len(requests), 1)
                    self.assertEqual(requests[0]["kind"], expected_kind)
                    self.assertEqual(requests[0]["properties"]["versionPolicy"], "ServiceManaged")


if __name__ == "__main__":
    unittest.main()
