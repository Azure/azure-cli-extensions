# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core import AzCommandsLoader
from azure.cli.core.commands import CliCommandType
import azext_dev_spaces._help  # pylint: disable=unused-import
import azext_dev_spaces.custom  # pylint: disable=unused-import


class DevspacesExtCommandLoader(AzCommandsLoader):  # pylint:disable=too-few-public-methods

    def __init__(self, cli_ctx=None):
        dev_spaces_custom = CliCommandType(
            operations_tmpl='azure.cli.command_modules.acs.custom#{}')
        super(DevspacesExtCommandLoader, self).__init__(cli_ctx=cli_ctx,
                                                        custom_command_type=dev_spaces_custom)

    def load_command_table(self, _):
        dev_spaces_custom = CliCommandType(operations_tmpl='azure.cli.command_modules.acs.custom#{}')

        with self.command_group('aks', dev_spaces_custom) as g:
            g.custom_command('use-dev-spaces', 'aks_use_dev_spaces')

        return self.command_table


COMMAND_LOADER_CLS = DevspacesExtCommandLoader
