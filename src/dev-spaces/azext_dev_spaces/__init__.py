# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core import AzCommandsLoader
from azure.cli.core.commands import CliCommandType
from azure.cli.core.commands.parameters import (get_enum_type)
import azext_dev_spaces._help  # pylint: disable=unused-import
import azext_dev_spaces.custom  # pylint: disable=unused-import


class DevspacesExtCommandLoader(AzCommandsLoader):  # pylint:disable=too-few-public-methods

    def __init__(self, cli_ctx=None):
        dev_spaces_custom = CliCommandType(
            operations_tmpl='azext_dev_spaces.custom#{}')
        super(DevspacesExtCommandLoader, self).__init__(cli_ctx=cli_ctx,
                                                        custom_command_type=dev_spaces_custom)

    # Make sure the following 2 functions stay in sync with what's declared in the core ACS component __init__.py
    def load_command_table(self, _):
        dev_spaces_custom = CliCommandType(operations_tmpl='azext_dev_spaces.custom#{}')

        with self.command_group('aks', dev_spaces_custom) as g:
            g.custom_command('use-dev-spaces', 'ads_use_dev_spaces')

        return self.command_table

    def load_arguments(self, _):
        with self.argument_context('aks use-dev-spaces') as c:
            c.argument('cluster_name', options_list=['--name', '-n'])
            c.argument('update', options_list=['--update'], action='store_true')
            c.argument('space_name', options_list=['--space', '-s'])
            c.argument('endpoint_type', get_enum_type(['Public', 'Private', 'None'], default='Public'),
                       options_list=['--endpoint', '-e'])
            c.argument('do_not_prompt', options_list=['--yes', '-y'],
                       action='store_true', help='Do not prompt for confirmation. Requires --space.')


COMMAND_LOADER_CLS = DevspacesExtCommandLoader
