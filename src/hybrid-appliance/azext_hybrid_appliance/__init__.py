# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core import AzCommandsLoader

from azext_hybrid_appliance._help import helps  # pylint: disable=unused-import


class HybridApplianceCommandsLoader(AzCommandsLoader):
    
    def __init__(self, cli_ctx=None):
        from azure.cli.core.commands import CliCommandType

        hybrid_appliance_custom = CliCommandType(operations_tmpl='azext_hybrid_appliance.custom#{}')
        super(HybridApplianceCommandsLoader, self).__init__(cli_ctx=cli_ctx, custom_command_type=hybrid_appliance_custom)

    def load_command_table(self, args):
        from azext_hybrid_appliance.commands import load_command_table
        load_command_table(self, args)
        return self.command_table

    def load_arguments(self, command):
        from azext_hybrid_appliance._params import load_arguments
        load_arguments(self, command)


COMMAND_LOADER_CLS = HybridApplianceCommandsLoader