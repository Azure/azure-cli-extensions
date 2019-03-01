# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core.commands import CliCommandType
from ._client_factory import spatial_anchors_account_factory


def load_command_table(self, _):

    group_name = 'spatial-anchors-account'

    operations_tmpl = 'azext_mixed_reality.vendored_sdks.' \
        + 'mixedreality.operations.spatial_anchors_accounts_operations' \
        + '#SpatialAnchorsAccountsOperations.{}'

    client_factory = spatial_anchors_account_factory

    command_type = CliCommandType(
        operations_tmpl=operations_tmpl,
        client_factory=client_factory,
        client_arg_name='self'
    )

    with self.command_group(group_name, command_type, client_factory=client_factory) as g:
        g.command('create', 'create')
        g.show_command('show', 'get')
        g.custom_command('list', 'list_spatial_anchors_accounts')
        g.command('delete', 'delete')

    group_name = 'spatial-anchors-account key'

    with self.command_group(group_name, command_type, client_factory=client_factory) as g:
        g.command('list', 'get_keys')
        g.custom_command('renew', 'renew_key')
