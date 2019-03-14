# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core.commands import CliCommandType
from azext_mixed_reality._client_factory import spatial_anchors_account_factory


def load_command_table(self, _):

    command_type = CliCommandType(
        operations_tmpl='azext_mixed_reality.vendored_sdks.mixedreality.operations.spatial_anchors_accounts_operations#SpatialAnchorsAccountsOperations.{}'  # pylint: disable=line-too-long
    )

    with self.command_group('spatial-anchors-account', command_type, client_factory=spatial_anchors_account_factory) as g:  # pylint: disable=line-too-long
        g.custom_command('create', 'create_spatial_anchors_account')
        g.show_command('show', 'get')
        g.custom_command('list', 'list_spatial_anchors_accounts')
        g.command('delete', 'delete')

    with self.command_group('spatial-anchors-account key', command_type, client_factory=spatial_anchors_account_factory) as g:  # pylint: disable=line-too-long
        g.show_command('show', 'get_keys')
        g.custom_command('renew', 'renew_key')
