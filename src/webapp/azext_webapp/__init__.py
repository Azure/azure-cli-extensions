# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core import AzCommandsLoader
from azure.cli.command_modules.appservice.commands import ex_handler_factory

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
            g.custom_command('up', 'create_deploy_webapp', exception_handler=ex_handler_factory())
            g.custom_command('remote-connection create', 'create_tunnel')
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


COMMAND_LOADER_CLS = WebappExtCommandLoader
