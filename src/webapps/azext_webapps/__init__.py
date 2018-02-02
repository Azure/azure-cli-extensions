# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core import AzCommandsLoader

# pylint: disable=unused-import

import azext_webapps._help


class WebappsExtCommandLoader(AzCommandsLoader):

    def __init__(self, cli_ctx=None):
        from azure.cli.core.commands import CliCommandType
        webapps_custom = CliCommandType(
            operations_tmpl='azext_webapps.custom#{}')
        super(WebappsExtCommandLoader, self).__init__(cli_ctx=cli_ctx,
                                                      custom_command_type=webapps_custom,
                                                      min_profile="2017-03-10-profile")

    def load_command_table(self, _):
        with self.command_group('webapp') as g:
            g.custom_command('quickstart', 'create_deploy_webapp')
        return self.command_table

    def load_arguments(self, _):
        with self.argument_context('webapp quickstart') as c:
            c.argument('name', options_list=['--name', '-n'], help='name of the new webapp')
            c.argument('dryrun',
                       help="shows summary of the create and deploy operation instead of executing it",
                       default=False, action='store_true')


COMMAND_LOADER_CLS = WebappsExtCommandLoader
