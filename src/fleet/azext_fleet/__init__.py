# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core import AzCommandsLoader
from azure.cli.core.profiles import register_resource_type, SDKProfile

# pylint: disable=unused-import
from azext_fleet._help import helps
from azext_fleet._client_factory import CUSTOM_MGMT_FLEET


def register_fleet_resource_type():
    register_resource_type(
        "latest",
        CUSTOM_MGMT_FLEET,
        SDKProfile("2024-02-02-preview"),
    )


class FleetCommandsLoader(AzCommandsLoader):

    def __init__(self, cli_ctx=None):
        from azure.cli.core.commands import CliCommandType
        register_fleet_resource_type()

        fleet_custom = CliCommandType(operations_tmpl='azext_fleet.custom#{}')
        super().__init__(cli_ctx=cli_ctx,
                         resource_type=CUSTOM_MGMT_FLEET,
                         custom_command_type=fleet_custom)

    def load_command_table(self, args):
        from azext_fleet.commands import load_command_table
        load_command_table(self, args)
        return self.command_table

    def load_arguments(self, command):
        from azext_fleet._params import load_arguments
        load_arguments(self, command)


COMMAND_LOADER_CLS = FleetCommandsLoader
