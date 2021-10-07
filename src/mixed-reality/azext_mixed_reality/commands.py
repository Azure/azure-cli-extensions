# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core.commands import CliCommandType
from ._client_factory import cf_spatial_anchor_account, cf_remote_rendering_account


# pylint: disable=line-too-long
def load_command_table(self, _):

    spatial_anchor_account = CliCommandType(
        operations_tmpl='azext_mixed_reality.vendored_sdks.mixedreality.operations._spatial_anchors_accounts_operations#SpatialAnchorsAccountsOperations.{}',
        client_factory=cf_spatial_anchor_account
    )

    remote_rendering_account = CliCommandType(
        operations_tmpl='azext_mixed_reality.vendored_sdks.mixedreality.operations._remote_rendering_accounts_operations#RemoteRenderingAccountsOperations.{}',
        client_factory=cf_remote_rendering_account
    )

    with self.command_group('spatial-anchors-account', spatial_anchor_account, is_preview=True) as g:
        g.custom_command('create', 'spatial_anchor_account_create')
        g.custom_command('list', 'spatial_anchor_account_list')
        g.custom_show_command('show', 'spatial_anchor_account_show')
        g.generic_update_command('update', setter_name='update', custom_func_name='spatial_anchor_account_update', setter_arg_name='spatial_anchors_account')
        g.custom_command('delete', 'spatial_anchor_account_delete')

    with self.command_group('spatial-anchors-account key', spatial_anchor_account, is_preview=True) as g:
        g.custom_show_command('show', 'spatial_anchor_account_list_key')
        g.custom_command('renew', 'spatial_anchor_account_regenerate_key')

    with self.command_group('remote-rendering-account', remote_rendering_account, is_preview=True) as g:
        g.custom_command('create', 'remote_rendering_account_create')
        g.custom_command('update', 'remote_rendering_account_update')
        g.custom_command('list', 'remote_rendering_account_list')
        g.custom_show_command('show', 'remote_rendering_account_show')
        g.custom_command('delete', 'remote_rendering_account_delete')

    with self.command_group('remote-rendering-account key', remote_rendering_account, is_preview=True) as g:
        g.custom_show_command('show', 'remote_rendering_account_list_key')
        g.custom_command('renew', 'remote_rendering_account_regenerate_key')
