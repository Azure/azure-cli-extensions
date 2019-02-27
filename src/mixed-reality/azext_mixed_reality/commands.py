# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core.commands import CliCommandType
from ._client_factory import spatial_anchors_account_factory
from ._exception_handler import mixed_reality_exception_handler


def load_command_table(self, _):
    spatial_anchors_account_util = CliCommandType(
        operations_tmpl='azext_mixed_reality.vendored_sdks.azure-mgmt-mixedreality.operations.spatial_anchors_accounts_operations#SpatialAnchorsAccountsOperations.{}',
        client_factory=spatial_anchors_account_factory,
        client_arg_name='self',
        exception_handler=mixed_reality_exception_handler
    )

    with self.command_group('spatial_anchors_account', spatial_anchors_account_util, client_factory=spatial_anchors_account_factory) as g:
        g.command('create', 'create')
