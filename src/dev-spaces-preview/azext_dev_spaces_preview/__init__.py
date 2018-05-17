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
            g.custom_command('use', 'ads_use_dev_spaces')
            g.custom_command('remove', 'ads_remove_dev_spaces')
        return self.command_table

    def load_arguments(self, _):
        with self.argument_context('ads use') as c:
            c.argument('cluster_name', options_list=['--name', '-n'])
            c.argument('resource_group_name', options_list=['--resource-group', '-g'])
            c.argument('space_name', options_list=['--space', '-s'])
            c.argument('parent_space_name', options_list=['--parent-space', '-p'])

        with self.argument_context('ads remove') as c:
            c.argument('cluster_name', options_list=['--name', '-n'])
            c.argument('resource_group_name', options_list=['--resource-group', '-g'])
            c.argument('prompt', options_list=['--yes', '-y'], action='store_true')


COMMAND_LOADER_CLS = DevspacesExtCommandLoader
