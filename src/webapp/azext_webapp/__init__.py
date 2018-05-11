# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core import AzCommandsLoader

# pylint: disable=unused-import

import azext_webapp._help


class WebappExtCommandLoader(AzCommandsLoader):

    def __init__(self, cli_ctx=None):
        from azure.cli.core.commands import CliCommandType
        webapp_custom = CliCommandType(
            operations_tmpl='azext_webapp.custom#{}')
        super(WebappExtCommandLoader, self).__init__(cli_ctx=cli_ctx,
                                                     custom_command_type=webapp_custom,
                                                     min_profile="2017-03-10-profile")

    def load_command_table(self, _):
        with self.command_group('webapp') as g:
            g.custom_command('up', 'create_deploy_webapp')
            g.custom_command('remote-connection create', 'create_tunnel')
            g.custom_command('config snapshot list', 'list_webapp_snapshots')
            g.custom_command('config snapshot restore', 'restore_webapp_snapshot')
        return self.command_table

    def load_arguments(self, _):
        with self.argument_context('webapp up') as c:
            c.argument('name', options_list=['--name', '-n'], help='name of the webapp to be created')
            c.argument('dryrun',
                       help="shows summary of the create and deploy operation instead of executing it",
                       default=False, action='store_true')
        with self.argument_context('webapp remote-connection create') as c:
            c.argument('port', options_list=['--port', '-p'],
                       help='Port for the remote connection. Default: Random available port', type=int)
            c.argument('name', options_list=['--name', '-n'], help='Name of the webapp to connect to')
        with self.argument_context('webapp config snapshot list') as c:
            c.argument('resource_group', options_list=['--resource-group', '-g'], help='Name of resource group.')
            c.argument('name', options_list=['--webapp-name', '-n'], help='Name of the webapp.')
            c.argument('slot', options_list=['--slot', '-s'], help='Name of the webapp slot.')
        with self.argument_context('webapp config snapshot restore') as c:
            c.argument('resource_group', options_list=['--resource-group', '-g'],
                       help='Name of resource group to restore to.')
            c.argument('name', options_list=['--webapp-name', '-n'], help='Name of the webapp to restore to.')
            c.argument('time', options_list=['--time', '-t'], help='Timestamp of the snapshot to restore.')
            c.argument('slot', options_list=['--slot', '-s'], help='Name of the webapp slot to restore to.')
            c.argument('restore_config', options_list=['--restore-config'],
                       help='Restore the previous configuration along with web app content.')
            c.argument('source_resource_group', options_list=['--source-resource-group'],
                       help='Name of the resource group to retrieve snapshot from.')
            c.argument('source_name', options_list=['--source-webapp-name'],
                       help='Name of the webapp to retrieve snapshot from.')
            c.argument('source_slot', options_list=['--source-slot'],
                       help='Name of the webapp slot to retrieve snapshot from.')


COMMAND_LOADER_CLS = WebappExtCommandLoader
