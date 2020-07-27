# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long
from azure.cli.core.commands import CliCommandType
from azext_init-preview._client_factory import cf_init-preview


def load_command_table(self, _):

    # TODO: Add command type here
    # init-preview_sdk = CliCommandType(
    #    operations_tmpl='<PATH>.operations#None.{}',
    #    client_factory=cf_init-preview)


    with self.command_group('init-preview') as g:
        g.custom_command('create', 'create_init-preview')
        # g.command('delete', 'delete')
        g.custom_command('list', 'list_init-preview')
        # g.show_command('show', 'get')
        # g.generic_update_command('update', setter_name='update', custom_func_name='update_init-preview')


    with self.command_group('init-preview', is_preview=True):
        pass

