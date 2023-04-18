# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long
from azure.cli.core.commands import CliCommandType
from azext_aosm._client_factory import cf_aosm


def load_command_table(self, _):

    # TODO: Add command type here
    # aosm_sdk = CliCommandType(
    #    operations_tmpl='<PATH>.operations#None.{}',
    #    client_factory=cf_aosm)

    with self.command_group('aosm') as g:
        g.custom_command('create', 'create_aosm')
        # g.command('delete', 'delete')
        g.custom_command('list', 'list_aosm')
        # g.show_command('show', 'get')
        # g.generic_update_command('update', setter_name='update', custom_func_name='update_aosm')

    with self.command_group('aosm', is_preview=True):
        pass
