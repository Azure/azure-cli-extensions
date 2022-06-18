# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core import AzCommandsLoader
from azure.cli.core.profiles import ResourceType

import azext_aem._help  # pylint: disable=unused-import


class AEMCommandsLoader(AzCommandsLoader):

    def __init__(self, cli_ctx=None):
        from azure.cli.core.commands import CliCommandType
        aem_custom = CliCommandType(
            operations_tmpl='azext_aem.custom#{}')
        super(AEMCommandsLoader, self).__init__(cli_ctx=cli_ctx,
                                                custom_command_type=aem_custom)

    def load_command_table(self, _):
        with self.command_group('vm aem', min_api='2016-04-30-preview', resource_type=ResourceType.MGMT_COMPUTE) as g:
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

        proxy_arg_type = CLIArgumentType(options_list=['--proxy-uri', '-p'])
        proxy_uri = CLIArgumentType(overrides=proxy_arg_type,
                                    help="Set the proxy URI that should be used to access external resources e.g. the Azure API. Example: http://proxyhost:8080")

        with self.argument_context('vm aem') as c:
            c.argument('vm_name', existing_vm_name)
            c.argument('proxy_uri', proxy_uri)
            c.argument('skip_storage_check', action='store_true',
                       help='Disables the test for table content')
            c.argument('skip_storage_analytics', action='store_true',
                       help='skip enabling analytics on storage accounts')
            c.argument('install_new_extension', action='store_true',
                       options_list=['--install-new-extension', '-i'],
                       help='Install the new VM Extension for SAP.')
            c.argument('set_access_to_individual_resources', action='store_true',
                       options_list=['--set-access-to-individual-resources', '-s'],
                       help='Set the access of the VM identity to the individual resources, e.g. data disks instead of the complete resource group.')
            c.argument('wait_time_in_minutes', type=int,
                       help='Maximum minutes to wait for the storage metrics to be available')
            c.argument('debug_extension', action='store_true',
                       help='Enable debug mode on the VM Extension for SAP.')


COMMAND_LOADER_CLS = AEMCommandsLoader
