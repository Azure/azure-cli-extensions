# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long
# pylint: disable=too-many-lines
# pylint: disable=too-many-statements
# pylint: disable=too-many-locals
from azure.cli.core.commands import CliCommandType


def load_command_table(self, _):

    from ._client_factory import cf_operations
    mixed_reality_operations = CliCommandType(
        operations_tmpl='azext_mixed_reality.vendored_sdks.mixedreality.operations._operations_operations#OperationsOperations.{}',
        client_factory=cf_operations)
    with self.command_group('mixed-reality', mixed_reality_operations, client_factory=cf_operations) as g:
        g.custom_command('list', 'list_mixed_reality')

    from ._client_factory import cf_mixed_reality
    mixed_reality_ = CliCommandType(
        operations_tmpl='azext_mixed_reality.vendored_sdks.mixedreality.operations.__operations#Operations.{}',
        client_factory=cf_mixed_reality)
    with self.command_group('mixed-reality check-name-availability', mixed_reality_, client_factory=cf_mixed_reality) as g:
        g.custom_command('check_name_availability_local', 'check_name_availability_local_mixed_reality_check_name_availability')

    from ._client_factory import cf_spatial_anchors_accounts
    mixed_reality_spatial_anchors_accounts = CliCommandType(
        operations_tmpl='azext_mixed_reality.vendored_sdks.mixedreality.operations._spatial_anchors_accounts_operations#SpatialAnchorsAccountsOperations.{}',
        client_factory=cf_spatial_anchors_accounts)
    with self.command_group('mixed-reality', mixed_reality_spatial_anchors_accounts, client_factory=cf_spatial_anchors_accounts) as g:
        g.custom_command('create', 'create_mixed_reality')
        g.custom_command('update', 'update_mixed_reality')
        g.custom_command('delete', 'delete_mixed_reality')
        g.custom_command('show', 'get_mixed_reality')
        g.custom_command('list', 'list_mixed_reality')
        g.custom_command('regenerate_keys', 'regenerate_keys_mixed_reality')
        g.custom_command('get_keys', 'get_keys_mixed_reality')
