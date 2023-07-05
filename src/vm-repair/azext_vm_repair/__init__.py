# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core import AzCommandsLoader
import azext_vm_repair._help  # pylint: disable=unused-import


class VmRepairCommandsLoader(AzCommandsLoader):

    def __init__(self, cli_ctx=None):
        from azure.cli.core.commands import CliCommandType
        import os
        prod_env_string = 'AZURE_CLI_VM_REPAIR_PROD'
        # test_env_string = 'AZURE_CLI_VM_REPAIR_TEST'
        os.environ[prod_env_string] = prod_env_string
        custom_type = CliCommandType(operations_tmpl='azext_vm_repair.custom#{}')
        super(VmRepairCommandsLoader, self).__init__(cli_ctx=cli_ctx,
                                                     custom_command_type=custom_type)

    def load_command_table(self, args):
        from .commands import load_command_table
        load_command_table(self, args)
        return self.command_table

    def load_arguments(self, command):
        from ._params import load_arguments
        load_arguments(self, command)


COMMAND_LOADER_CLS = VmRepairCommandsLoader
