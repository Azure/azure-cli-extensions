# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long
from azure.cli.core.commands import CliCommandType
from azext_nginx._client_factory import cf_nginx


def load_command_table(self, _):

    # TODO: Add command type here
    # nginx_sdk = CliCommandType(
    #    operations_tmpl='<PATH>.operations#None.{}',
    #    client_factory=cf_nginx)


    with self.command_group('nginx') as g:
        g.custom_command('create', 'create_nginx')
        # g.command('delete', 'delete')
        g.custom_command('list', 'list_nginx')
        # g.show_command('show', 'get')
        # g.generic_update_command('update', setter_name='update', custom_func_name='update_nginx')


    with self.command_group('nginx', is_preview=True):
        pass

