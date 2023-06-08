# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long
from azure.cli.core.commands import CliCommandType
from azext_copilot._client_factory import cf_copilot


def load_command_table(self, _):

    # TODO: Add command type here
    # copilot_sdk = CliCommandType(
    #    operations_tmpl='<PATH>.operations#None.{}',
    #    client_factory=cf_copilot)


    with self.command_group('copilot') as g:
        g.custom_command('', 'create_copilot')
        # g.custom_command('create', 'create_copilot')
        # g.command('delete', 'delete')
        g.custom_command('list', 'list_copilot')
        # g.show_command('show', 'get')
        # g.generic_update_command('update', setter_name='update', custom_func_name='update_copilot')


    with self.command_group('copilot', is_preview=True):
        pass

