# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from azure.cli.core.commands import CliCommandType
from ._client_factory import is_azure_stack_profile, cf_mhsm, cf_mhsm_region
from .profiles import CUSTOM_MGMT_KEYVAULT


def load_command_table(self, _):
    managed_hsm_sdk = CliCommandType(
        operations_tmpl='azext_keyvault_preview.vendored_sdks.azure_mgmt_keyvault.operations#'
                        'ManagedHsmsOperations.{}',
        client_factory=cf_mhsm,
        resource_type=CUSTOM_MGMT_KEYVAULT
    )
    managed_hsm_custom = CliCommandType(
        operations_tmpl='azext_keyvault_preview.custom#{}',
        client_factory=cf_mhsm,
        resource_type=CUSTOM_MGMT_KEYVAULT
    )
    mhsm_region_sdk = CliCommandType(
        operations_tmpl='azext_keyvault_preview.vendored_sdks.azure_mgmt_keyvault.operations#'
                        'MHSMRegionsOperations.{}',
        client_factory=cf_mhsm,
        resource_type=CUSTOM_MGMT_KEYVAULT
    )

    with self.command_group('keyvault', managed_hsm_sdk, min_api='2021-12-01-preview') as g:
        g.generic_update_command('update-hsm', custom_func_name='update_hsm', supports_no_wait=True,
                                 setter_name='update_hsm_setter', setter_type=managed_hsm_custom)

    with self.command_group('keyvault region', mhsm_region_sdk, client_factory=cf_mhsm_region,
                            min_api='2021-12-01-preview', is_preview=True) as g:
        g.command('list', 'list_by_resource', client_factory=cf_mhsm_region)

    with self.command_group('keyvault region', managed_hsm_sdk, client_factory=cf_mhsm,
                            min_api='2021-12-01-preview', is_preview=True) as g:
        g.custom_command('add', 'add_hsm_region', supports_no_wait=True)
        g.custom_command('remove', 'remove_hsm_region', supports_no_wait=True)
        g.wait_command('wait')
