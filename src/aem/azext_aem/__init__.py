# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core import AzCommandsLoader

import azext_aem._help  # pylint: disable=unused-import


class AEMCommandsLoader(AzCommandsLoader):

    def __init__(self, cli_ctx=None):
        from azure.cli.core.commands import CliCommandType
        aem_custom = CliCommandType(
            operations_tmpl='azext_aem.custom#{}')
        super(AEMCommandsLoader, self).__init__(cli_ctx=cli_ctx,
                                                custom_command_type=aem_custom)

    def load_command_table(self, _):
        with self.command_group('vm aem', min_api='2016-04-30-preview') as g:
            g.custom_command('set', 'set_aem')
            g.custom_command('delete', 'delete_aem')
            g.custom_command('verify', 'verify_aem')

        return self.command_table

    def load_arguments(self, _):
        # pylint: disable=line-too-long
        from knack.arguments import CLIArgumentType
        from azure.cli.core.commands.parameters import get_resource_name_completion_list
        name_arg_type = CLIArgumentType(options_list=['--name', '-n'], metavar='NAME')
        existing_vm_name = CLIArgumentType(overrides=name_arg_type,
                                           configured_default='vm',
                                           help="The name of the Virtual Machine. You can configure the default using `az configure --defaults vm=<name>`",
                                           completer=get_resource_name_completion_list('Microsoft.Compute/virtualMachines'), id_part='name')

        with self.argument_context('vm aem') as c:
            c.argument('vm_name', existing_vm_name)
            c.argument('skip_storage_check', action='store_true',
                       help='Disables the test for table content')
            c.argument('skip_storage_analytics', action='store_true',
                       help='skip enabling analytics on storage accounts')
            c.argument('wait_time_in_minutes', type=int,
                       help='Maximum minutes to wait for the storage metrics to be available')


COMMAND_LOADER_CLS = AEMCommandsLoader
