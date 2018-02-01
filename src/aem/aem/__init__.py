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
        with self.command_group('vm aem') as g:
            g.custom_command('set', 'set_aem')
            g.custom_command('delete', 'delete_aem')
            g.custom_command('verify', 'verify_aem')

        return self.command_table

    def load_arguments(self, _):
        with self.argument_context('vm aem') as c:
            c.argument('skip_storage_check', action='store_true',
                       help='Disables the test for table content')
            c.argument('wait_time_in_minutes', type=int,
                       help='Time that should be waited for the Strorage Metrics or Diagnostics data to be available in minutes')


COMMAND_LOADER_CLS = AEMCommandsLoader
