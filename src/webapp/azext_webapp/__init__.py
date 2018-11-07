# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=ungrouped-imports
from azure.cli.core import AzCommandsLoader
from azure.cli.command_modules.appservice.commands import ex_handler_factory
from knack.arguments import CLIArgumentType
from azure.cli.core.commands.parameters import (get_resource_name_completion_list)
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
        # pylint: disable=line-too-long
        # PARAMETER REGISTRATION
        webapp_name_arg_type = CLIArgumentType(configured_default='web', options_list=['--name', '-n'], metavar='NAME',
                                               completer=get_resource_name_completion_list('Microsoft.Web/sites'), id_part='name',
                                               help="name of the webapp. You can configure the default using 'az configure --defaults web=<name>'")
        with self.argument_context('webapp up') as c:
            c.argument('name', arg_type=webapp_name_arg_type)
            c.argument('dryrun',
                       help="shows summary of the create and deploy operation instead of executing it",
                       default=False, action='store_true')
        with self.argument_context('webapp remote-connection create') as c:
            c.argument('port', options_list=['--port', '-p'],
                       help='Port for the remote connection. Default: Random available port', type=int)
            c.argument('name', options_list=['--name', '-n'], help='Name of the webapp to connect to')


COMMAND_LOADER_CLS = WebappExtCommandLoader
