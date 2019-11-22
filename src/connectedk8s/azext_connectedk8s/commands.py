# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long
from azure.cli.core.commands import CliCommandType
from azext_connectedk8s._client_factory import (cf_connectedk8s,cf_connected_cluster)


def load_command_table(self, _):

    connectedk8s_sdk = CliCommandType(
        operations_tmpl='azext_connectedk8s.vendored_sdks.operations#ConnectedClusterOperations.{}',
        client_factory=cf_connectedk8s)


    with self.command_group('connectedk8s', connectedk8s_sdk, client_factory=cf_connected_cluster) as g:
        g.custom_command('create', 'create_connectedk8s')
        g.custom_command('delete', 'delete_connectedk8s')
        g.custom_command('list', 'list_connectedk8s')
        g.custom_show_command('show', 'get_connectedk8s')
        g.generic_update_command('update', setter_name='update', custom_func_name='update_connectedk8s')


    with self.command_group('connectedk8s', is_preview=True):
        pass

