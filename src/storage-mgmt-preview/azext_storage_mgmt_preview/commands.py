# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core.commands import CliCommandType

from ._client_factory import cf_mgmt_file_services
from .profiles import CUSTOM_MGMT_STORAGE


def load_command_table(self, _):

    file_service_mgmt_sdk = CliCommandType(
        operations_tmpl='azext_storage_mgmt_preview.vendored_sdks.azure_mgmt_storage.operations'
                        '#FileServicesOperations.{}',
        client_factory=cf_mgmt_file_services,
        resource_type=CUSTOM_MGMT_STORAGE
    )

    def get_custom_sdk(custom_module, client_factory, resource_type=CUSTOM_MGMT_STORAGE):
        """Returns a CliCommandType instance with specified operation template based on the given custom module name.
        This is useful when the command is not defined in the default 'custom' module but instead in a module under
        'operations' package."""
        return CliCommandType(
            operations_tmpl='azext_storage_mgmt_preview.operations.{}#'.format(
                custom_module) + '{}',
            client_factory=client_factory,
            resource_type=resource_type
        )

    with self.command_group('storage account file-service-properties', file_service_mgmt_sdk,
                            custom_command_type=get_custom_sdk('account', client_factory=cf_mgmt_file_services,
                                                               resource_type=CUSTOM_MGMT_STORAGE),
                            resource_type=CUSTOM_MGMT_STORAGE, min_api='2019-06-01', is_preview=True) as g:
        g.show_command('show', 'get_service_properties')
        g.generic_update_command('update',
                                 getter_name='get_service_properties',
                                 setter_name='set_service_properties',
                                 custom_func_name='update_file_service_properties')
