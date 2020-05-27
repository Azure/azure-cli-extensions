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

    from ._client_factory import cf_custom_resource_provider
    custom_providers_custom_resource_provider = CliCommandType(
        operations_tmpl='azext_custom_providers.vendored_sdks.customproviders.operations._custom_resource_provider_operations#CustomResourceProviderOperations.{}',
        client_factory=cf_custom_resource_provider)
    with self.command_group('custom-providers resource-provider', custom_providers_custom_resource_provider, client_factory=cf_custom_resource_provider, is_experimental=True) as g:
        g.custom_command('create', 'create_custom_providers_custom_resource_provider', supports_no_wait=True)
        g.custom_command('update', 'update_custom_providers_custom_resource_provider')
        g.custom_command('delete', 'delete_custom_providers_custom_resource_provider', supports_no_wait=True, confirmation=True)
        g.custom_show_command('show', 'get_custom_providers_custom_resource_provider')
        g.custom_command('list', 'list_custom_providers_custom_resource_provider')
