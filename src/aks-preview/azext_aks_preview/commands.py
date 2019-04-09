# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core.commands import CliCommandType

from ._client_factory import cf_managed_clusters
from ._client_factory import cf_agent_pools
from ._format import aks_show_table_format
from ._format import aks_agentpool_show_table_format


def load_command_table(self, _):

    managed_clusters_sdk = CliCommandType(
        operations_tmpl='azext_aks_preview.vendored_sdks.azure_mgmt_preview_aks.'
                        'operations.managed_clusters_operations#ManagedClustersOperations.{}',
        client_factory=cf_managed_clusters
    )

    agent_pools_sdk = CliCommandType(
        operations_tmpl='azext_aks_preview.vendored_sdks.azure_mgmt_preview_aks.'
                        'operations.agent_pools_operations#AgentPoolsOperations.{}',
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

    # AKS agent pool commands
    with self.command_group('aks nodepool', agent_pools_sdk, client_factory=cf_agent_pools) as g:
        g.custom_command('list', 'aks_agentpool_list')
        g.custom_show_command('show', 'aks_agentpool_show', table_transformer=aks_agentpool_show_table_format)
        g.custom_command('add', 'aks_agentpool_add', supports_no_wait=True)
        g.custom_command('scale', 'aks_agentpool_scale', supports_no_wait=True)
        g.custom_command('upgrade', 'aks_agentpool_upgrade', supports_no_wait=True)
        g.custom_command('delete', 'aks_agentpool_delete', supports_no_wait=True)
