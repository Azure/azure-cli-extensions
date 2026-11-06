# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import unittest

from azure.cli.core import get_default_cli
from azure.cli.core.aaz._command_ctx import AAZCommandCtx

from azext_workload_manager import WorkloadManagerCommandsLoader
from azext_workload_manager.aaz.latest.workload_manager.workload_space import Create, List, Show, Update, Wait


class WorkloadSpaceResponseTest(unittest.TestCase):

    def _output(self, command_type, schema_builder, response):
        loader = WorkloadManagerCommandsLoader(cli_ctx=get_default_cli())
        command = command_type(loader)
        command.ctx = AAZCommandCtx(command.cli_ctx, command.get_arguments_schema(), {})
        command.ctx.set_var("instance", response, schema_builder=schema_builder)
        return command._output()

    def test_resource_responses_preserve_optional_readiness_state(self):
        commands = (
            (Create, Create.WorkloadSpacesCreateOrUpdate._build_schema_on_200_201),
            (Show, Show.WorkloadSpacesGet._build_schema_on_200),
            (Update, Update.WorkloadSpacesUpdate._build_schema_on_200),
            (Wait, Wait.WorkloadSpacesGet._build_schema_on_200),
        )
        for command_type, schema_builder in commands:
            for state in ("Degraded", None):
                with self.subTest(command=command_type.__name__, state=state):
                    properties = {"provisioningState": "Succeeded"}
                    if state is not None:
                        properties["state"] = state
                    response = {"location": "eastus2", "properties": properties}

                    self.assertEqual(self._output(command_type, schema_builder, response), response)

    def test_list_responses_preserve_readiness_state_and_pagination(self):
        resources = [
            {"location": "eastus2", "properties": {"provisioningState": "Succeeded", "state": "Degraded"}},
            {"location": "eastus2", "properties": {"provisioningState": "Succeeded"}},
        ]
        next_link = "https://management.azure.com/next-page"
        response = {"value": resources, "nextLink": next_link}
        for operation in (List.WorkloadSpacesListByResourceGroup, List.WorkloadSpacesListBySubscription):
            with self.subTest(operation=operation.__name__):
                output, continuation = self._output(List, operation._build_schema_on_200, response)

                self.assertEqual(output, resources)
                self.assertEqual(continuation, next_link)


if __name__ == "__main__":
    unittest.main()
