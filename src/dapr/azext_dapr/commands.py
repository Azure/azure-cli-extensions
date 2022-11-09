# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long
from azure.cli.core.commands import CliCommandType
from azext_dapr._client_factory import cf_dapr


def load_command_table(self, _):
    #cf_install_dapr_cli(self.cli_ctx)
    # TODO: Add command type here
    # dapr_sdk = CliCommandType(
    #    operations_tmpl='<PATH>.operations#None.{}',
    #    client_factory=cf_dapr)


    with self.command_group('dapr') as g:
        g.custom_command('create', 'create_dapr')
        # g.command('delete', 'delete')
        g.custom_command('list', 'list_dapr')
        g.custom_command('status', 'status_dapr')
        # g.show_command('show', 'get')
        # g.generic_update_command('update', setter_name='update', custom_func_name='update_dapr')


    with self.command_group('dapr', is_preview=True):
        pass
