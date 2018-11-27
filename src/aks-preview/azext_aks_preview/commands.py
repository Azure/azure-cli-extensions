# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core.commands import CliCommandType

from ._client_factory import cf_managed_clusters
from ._format import aks_show_table_format


def load_command_table(self, _):

    managed_clusters_sdk = CliCommandType(
        operations_tmpl='azext_aks_preview.vendored_sdks.azure_mgmt_preview_aks.'
                        'operations.managed_clusters_operations#ManagedClustersOperations.{}',
        client_factory=cf_managed_clusters
    )

    # AKS commands
    with self.command_group('aks', managed_clusters_sdk, client_factory=cf_managed_clusters) as g:
        g.custom_command('create', 'aks_create', supports_no_wait=True)
        g.custom_command('update', 'aks_update', supports_no_wait=True)
        g.custom_command('scale', 'aks_scale', supports_no_wait=True)
        g.custom_show_command('show', 'aks_show', table_transformer=aks_show_table_format)
        g.custom_command('upgrade', 'aks_upgrade', supports_no_wait=True,
                         confirmation='Kubernetes may be unavailable during cluster upgrades.\n' +
                         'Are you sure you want to perform this operation?')
        g.wait_command('wait')
