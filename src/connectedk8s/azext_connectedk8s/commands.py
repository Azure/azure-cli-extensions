# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long
from azure.cli.core.commands import CliCommandType
from azext_connectedk8s._client_factory import (cf_connectedk8s, cf_connected_cluster, cf_connectedk8s_prev_2022_10_01, cf_connected_cluster_prev_2022_10_01)
from ._format import connectedk8s_show_table_format
from ._format import connectedk8s_list_table_format


def load_command_table(self, _):

    connectedk8s_sdk = CliCommandType(
        operations_tmpl='azext_connectedk8s.vendored_sdks.operations#ConnectedClusterOperations.{}',
        client_factory=cf_connectedk8s
    )
    connectedk8s_sdk_prev = CliCommandType(
        operations_tmpl='azext_connectedk8s.vendored_sdks.preview_2022_10_01.operations#ConnectedClusterOperations.{}',
        client_factory=cf_connectedk8s_prev_2022_10_01
    )
    with self.command_group('connectedk8s', connectedk8s_sdk, client_factory=cf_connected_cluster) as g:
        g.custom_command('connect', 'create_connectedk8s', supports_no_wait=True)
        g.custom_command('update', 'update_connected_cluster')
        g.custom_command('upgrade', 'upgrade_agents')
        g.custom_command('delete', 'delete_connectedk8s', supports_no_wait=True)
        g.custom_command('enable-features', 'enable_features', is_preview=True)
        g.custom_command('disable-features', 'disable_features', is_preview=True)
        g.custom_command('list', 'list_connectedk8s', table_transformer=connectedk8s_list_table_format)
        g.custom_show_command('show', 'get_connectedk8s', table_transformer=connectedk8s_show_table_format)
        g.custom_command('proxy', 'client_side_proxy_wrapper')
        g.custom_command('troubleshoot', 'troubleshoot', is_preview=True)

    with self.command_group('connectedk8s', connectedk8s_sdk_prev, client_factory=cf_connected_cluster_prev_2022_10_01) as g:
        pass
        # use this block for using preview sdk client for a command
