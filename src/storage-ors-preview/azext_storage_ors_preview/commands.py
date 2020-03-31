# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core.commands import CliCommandType

from ._client_factory import cf_ors_policy
from .profiles import CUSTOM_MGMT_STORAGE_ORS
from ._validators import validate_ors_policy


def load_command_table(self, _):

    ors_policy_sdk = CliCommandType(
        operations_tmpl='azext_storage_ors_preview.vendored_sdks.azure_mgmt_storage.operations'
                        '#ObjectReplicationPoliciesOperations.{}',
        client_factory=cf_ors_policy,
        resource_type=CUSTOM_MGMT_STORAGE_ORS
    )

    ors_policy_custom_type = CliCommandType(
        operations_tmpl='azext_storage_ors_preview.operations.account#{}',
        client_factory=cf_ors_policy)

    with self.command_group('storage account ors-policy', ors_policy_sdk, is_preview=True,
                            resource_type=CUSTOM_MGMT_STORAGE_ORS, min_api='2019-06-01',
                            custom_command_type=ors_policy_custom_type) as g:
        g.show_command('show', 'get')
        g.command('list', 'list')
        g.custom_command('create', 'create_ors_policy', validator=validate_ors_policy)
        g.generic_update_command('update', setter_name='update_ors_policy', setter_type=ors_policy_custom_type)
        g.command('delete', 'delete')

    with self.command_group('storage account ors-policy rule', ors_policy_sdk, is_preview=True,
                            resource_type=CUSTOM_MGMT_STORAGE_ORS, min_api='2019-06-01',
                            custom_command_type=ors_policy_custom_type) as g:
        g.custom_show_command('show', 'get_ors_rule')
        g.custom_command('list', 'list_ors_rules')
        g.custom_command('add', 'add_ors_rule')
        g.custom_command('update', 'update_ors_rule')
        g.custom_command('remove', 'remove_ors_rule')
