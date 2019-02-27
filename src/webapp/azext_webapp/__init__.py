# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=ungrouped-imports
from azure.cli.core import AzCommandsLoader
from azure.cli.command_modules.appservice.commands import ex_handler_factory
from knack.arguments import CLIArgumentType
from azure.cli.core.commands.parameters import (get_enum_type, get_resource_name_completion_list)
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
        sku_arg_type = CLIArgumentType(help='The pricing tiers, e.g., F1(Free), D1(Shared), B1(Basic Small), B2(Basic Medium), B3(Basic Large), S1(Standard Small), P1(Premium Small), P1V2(Premium V2 Small), PC2 (Premium Container Small), PC3 (Premium Container Medium), PC4 (Premium Container Large)',
                                       arg_type=get_enum_type(['F1', 'FREE', 'D1', 'SHARED', 'B1', 'B2', 'B3', 'S1', 'S2', 'S3', 'P1', 'P2', 'P3', 'P1V2', 'P2V2', 'P3V2', 'PC2', 'PC3', 'PC4']))
        webapp_name_arg_type = CLIArgumentType(configured_default='web', options_list=['--name', '-n'], metavar='NAME',
                                               completer=get_resource_name_completion_list('Microsoft.Web/sites'), id_part='name',
                                               help="name of the webapp. You can configure the default using 'az configure --defaults web=<name>'")
        with self.argument_context('webapp up') as c:
            c.argument('name', arg_type=webapp_name_arg_type)
            c.argument('sku', arg_type=sku_arg_type)
            c.argument('dryrun',
                       help="shows summary of the create and deploy operation instead of executing it",
                       default=False, action='store_true')
        with self.argument_context('webapp remote-connection create') as c:
            c.argument('port', options_list=['--port', '-p'],
                       help='Port for the remote connection. Default: Random available port', type=int)
            c.argument('name', options_list=['--name', '-n'], help='Name of the webapp to connect to')


COMMAND_LOADER_CLS = WebappExtCommandLoader
