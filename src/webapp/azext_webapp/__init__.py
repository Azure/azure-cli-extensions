# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=unused-import,ungrouped-imports,import-outside-toplevel,super-with-arguments
from azure.cli.core import AzCommandsLoader
from azure.cli.command_modules.appservice.commands import ex_handler_factory
from knack.arguments import CLIArgumentType
from azure.cli.core.commands.parameters import (get_resource_name_completion_list)
import azext_webapp._help


class WebappExtCommandLoader(AzCommandsLoader):
    def __init__(self, cli_ctx=None):
        from azure.cli.core.commands import CliCommandType
        from azure.cli.core.profiles import ResourceType
        webapp_custom = CliCommandType(
            operations_tmpl='azext_webapp.custom#{}')
        super(WebappExtCommandLoader, self).__init__(cli_ctx=cli_ctx,
                                                     custom_command_type=webapp_custom,
                                                     resource_type=ResourceType.MGMT_APPSERVICE)

    def load_command_table(self, _):
        with self.command_group('webapp scan') as g:
            g.custom_command('start', 'start_scan')
            g.custom_command('show-result', 'get_scan_result')
            g.custom_command('track', 'track_scan')
            g.custom_command('list-result', 'get_all_scan_result')
            g.custom_command('stop', 'stop_scan')

        return self.command_table

    def load_arguments(self, _):
        # pylint: disable=line-too-long
        # PARAMETER REGISTRATION

        with self.argument_context('webapp scan') as c:
            c.argument('name', options_list=['--name', '-n'], help='Name of the webapp to connect to')
            c.argument('scan_id', options_list=['--scan-id'], help='Unique scan id')
            c.argument('timeout', options_list=['--timeout'], help='Timeout for operation in milliseconds')
            c.argument('slot', help="Name of the deployment slot to use")


COMMAND_LOADER_CLS = WebappExtCommandLoader
