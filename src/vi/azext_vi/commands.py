# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long
from azure.cli.core.commands import CliCommandType
from azext_vi._client_factory import cf_vi


def load_command_table(self, _):

    # TODO: Add command type here
    # vi_sdk = CliCommandType(
    #    operations_tmpl='<PATH>.operations#None.{}',
    #    client_factory=cf_vi)


    with self.command_group('vi') as g:
        g.custom_command('create', 'create_vi')
        # g.command('delete', 'delete')
        g.custom_command('list', 'list_vi')
        # g.show_command('show', 'get')
        # g.generic_update_command('update', setter_name='update', custom_func_name='update_vi')


    with self.command_group('vi', is_preview=True):
        pass

