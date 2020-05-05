# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core.commands import CliCommandType

from ._client_factory import cf_or_policy
from .profiles import CUSTOM_MGMT_STORAGE_ORS
from ._validators import validate_or_policy


def load_command_table(self, _):

    or_policy_sdk = CliCommandType(
        operations_tmpl='azext_storage_ors_preview.vendored_sdks.azure_mgmt_storage.operations'
                        '#ObjectReplicationPoliciesOperations.{}',
        client_factory=cf_or_policy,
        resource_type=CUSTOM_MGMT_STORAGE_ORS
    )

    or_policy_custom_type = CliCommandType(
        operations_tmpl='azext_storage_ors_preview.operations.account#{}',
        client_factory=cf_or_policy)

    with self.command_group('storage account or-policy', or_policy_sdk, is_preview=True,
                            resource_type=CUSTOM_MGMT_STORAGE_ORS, min_api='2019-06-01',
                            custom_command_type=or_policy_custom_type) as g:
        g.show_command('show', 'get')
        g.command('list', 'list')
        g.custom_command('create', 'create_or_policy', validator=validate_or_policy)
        g.generic_update_command('update', setter_name='update_or_policy', setter_type=or_policy_custom_type)
        g.command('delete', 'delete')

    with self.command_group('storage account or-policy rule', or_policy_sdk, is_preview=True,
                            resource_type=CUSTOM_MGMT_STORAGE_ORS, min_api='2019-06-01',
                            custom_command_type=or_policy_custom_type) as g:
        g.custom_show_command('show', 'get_or_rule')
        g.custom_command('list', 'list_or_rules')
        g.custom_command('add', 'add_or_rule')
        g.custom_command('update', 'update_or_rule')
        g.custom_command('remove', 'remove_or_rule')
