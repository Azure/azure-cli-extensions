# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long
# from azure.cli.core.commands import CliCommandType


def load_command_table(self, _):

    # TODO: Add command type here
    # hack_sdk = CliCommandType(
    #    operations_tmpl='<PATH>.operations#None.{}',
    #    client_factory=cf_hack)

    with self.command_group('hack') as g:
        g.custom_command('create', 'create_hack')
        # g.command('delete', 'delete')
        # g.custom_command('list', 'list_hack')
        # g.show_command('show', 'get')
        # g.generic_update_command('update', setter_name='update', custom_func_name='update_hack')

    with self.command_group('hack', is_preview=True):
        pass
