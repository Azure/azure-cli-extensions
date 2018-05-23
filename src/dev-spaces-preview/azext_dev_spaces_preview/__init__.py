# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core import AzCommandsLoader

import azext_dev_spaces_preview._help  # pylint: disable=unused-import
import azext_dev_spaces_preview.custom  # pylint: disable=unused-import


class DevspacesExtCommandLoader(AzCommandsLoader):

    def __init__(self, cli_ctx=None):
        from azure.cli.core.commands import CliCommandType
        dev_spaces_custom = CliCommandType(
            operations_tmpl='azext_dev_spaces_preview.custom#{}')
        super(DevspacesExtCommandLoader, self).__init__(cli_ctx=cli_ctx,
                                                        custom_command_type=dev_spaces_custom,
                                                        min_profile='2017-03-10-profile')

    def load_command_table(self, _):
        with self.command_group('ads') as g:
            g.custom_command('upgrade-tools', 'ads_upgrade_dev_spaces_tools')
        return self.command_table


COMMAND_LOADER_CLS = DevspacesExtCommandLoader
