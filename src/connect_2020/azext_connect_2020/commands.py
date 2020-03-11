# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long
from azure.cli.core.commands import CliCommandType
from azext_connect_2020._client_factory import cf_connect_2020


def load_command_table(self, _):

    connect_2020_sdk = CliCommandType(
        operations_tmpl='azext_connect_2020.vendored_sdks.operations#ConnectedClusterOperations.{}',
        client_factory=cf_connect_2020)


    with self.command_group('connect_2020', connect_2020_sdk, client_factory=cf_connect_2020) as g:
        g.custom_command('create', 'create_connect_2020')
        g.command('delete', 'delete')
        g.custom_command('list', 'list_connect_2020')
        g.show_command('show', 'get')
        g.generic_update_command('update', setter_name='update', custom_func_name='update_connect_2020')


    with self.command_group('connect_2020', is_preview=True):
        pass

