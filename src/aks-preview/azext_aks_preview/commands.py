# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core.commands import CliCommandType

from ._client_factory import cf_managed_clusters
from ._client_factory import cf_maintenance_configurations
from ._client_factory import cf_agent_pools
from ._client_factory import cf_nodepool_snapshots
from ._client_factory import cf_mc_snapshots
from ._format import aks_show_table_format
from ._format import aks_addon_list_available_table_format, aks_addon_list_table_format, aks_addon_show_table_format
from ._format import aks_agentpool_show_table_format
from ._format import aks_agentpool_list_table_format
from ._format import aks_versions_table_format
from ._format import aks_upgrades_table_format
from ._format import aks_pod_identities_table_format
from ._format import aks_pod_identity_exceptions_table_format
from ._format import aks_show_nodepool_snapshot_table_format
from ._format import aks_list_nodepool_snapshot_table_format
from ._format import aks_show_snapshot_table_format
from ._format import aks_list_snapshot_table_format


def load_command_table(self, _):

    managed_clusters_sdk = CliCommandType(
        operations_tmpl='azext_aks_preview.vendored_sdks.azure_mgmt_preview_aks.'
                        'operations._managed_clusters_operations#ManagedClustersOperations.{}',
        operation_group='managed_clusters',
        client_factory=cf_managed_clusters
    )

    agent_pools_sdk = CliCommandType(
        operations_tmpl='azext_aks_preview.vendored_sdks.azure_mgmt_preview_aks.'
                        'operations._agent_pools_operations#AgentPoolsOperations.{}',
        client_factory=cf_managed_clusters
    )

    maintenance_configuration_sdk = CliCommandType(
        operations_tmpl='azext_aks_preview.vendored_sdks.azure_mgmt_preview_aks.'
                        'operations._maintenance_configurations_operations#MaintenanceConfigurationsOperations.{}',
        client_factory=cf_maintenance_configurations
    )

    nodepool_snapshot_sdk = CliCommandType(
        operations_tmpl='azext_aks_preview.vendored_sdks.azure_mgmt_preview_aks.'
                        'operations._snapshots_operations#SnapshotsOperations.{}',
        client_factory=cf_nodepool_snapshots
    )

    mc_snapshot_sdk = CliCommandType(
        operations_tmpl='azext_aks_preview.vendored_sdks.azure_mgmt_preview_aks.'
                        'operations._managed_clusters_snapshots_operations#ManagedClusterSnapshotsOperations.{}',
        client_factory=cf_mc_snapshots)

    # AKS managed cluster commands
    with self.command_group('aks', managed_clusters_sdk, client_factory=cf_managed_clusters) as g:
        g.custom_command('kollect', 'aks_kollect')
        g.custom_command('kanalyze', 'aks_kanalyze')
        g.custom_command('browse', 'aks_browse')
        g.custom_command('create', 'aks_create', supports_no_wait=True)
        g.custom_command('update', 'aks_update', supports_no_wait=True)
        g.command('delete', 'begin_delete',
                  supports_no_wait=True, confirmation=True)
        g.custom_command('scale', 'aks_scale', supports_no_wait=True)
        g.custom_command('disable-addons', 'aks_disable_addons',
                         supports_no_wait=True)
        g.custom_command('enable-addons', 'aks_enable_addons',
                         supports_no_wait=True)
        g.custom_command('get-credentials', 'aks_get_credentials')
        g.custom_show_command('show', 'aks_show',
                              table_transformer=aks_show_table_format)
        g.custom_command('upgrade', 'aks_upgrade', supports_no_wait=True)
        g.command('get-upgrades', 'get_upgrade_profile',
                  table_transformer=aks_upgrades_table_format)
        g.custom_command('rotate-certs', 'aks_rotate_certs', supports_no_wait=True,
                         confirmation='Kubernetes will be unavailable during certificate rotation process.\n' +
                         'Are you sure you want to perform this operation?')
        g.wait_command('wait')
        g.command('stop', 'begin_stop', supports_no_wait=True)
        g.command('start', 'begin_start', supports_no_wait=True)
        g.custom_command('get-os-options', 'aks_get_os_options')

    # AKS maintenance configuration commands
    with self.command_group('aks maintenanceconfiguration', maintenance_configuration_sdk, client_factory=cf_maintenance_configurations) as g:
        g.custom_command('list', 'aks_maintenanceconfiguration_list')
        g.custom_show_command('show', 'aks_maintenanceconfiguration_show')
        g.custom_command('add', 'aks_maintenanceconfiguration_add')
        g.custom_command('update', 'aks_maintenanceconfiguration_update')
        g.custom_command('delete', 'aks_maintenanceconfiguration_delete')

    # AKS addon commands
    with self.command_group('aks addon', managed_clusters_sdk, client_factory=cf_managed_clusters) as g:
        g.custom_command('list-available', 'aks_addon_list_available',
                         table_transformer=aks_addon_list_available_table_format)
        g.custom_command('list', 'aks_addon_list',
                         table_transformer=aks_addon_list_table_format)
        g.custom_show_command('show', 'aks_addon_show',
                              table_transformer=aks_addon_show_table_format)
        g.custom_command('enable', 'aks_addon_enable', supports_no_wait=True)
        g.custom_command('disable', 'aks_addon_disable', supports_no_wait=True)
        g.custom_command('update', 'aks_addon_update', supports_no_wait=True)

    # AKS agent pool commands
    with self.command_group('aks nodepool', agent_pools_sdk, client_factory=cf_agent_pools) as g:
        g.custom_command('list', 'aks_agentpool_list',
                         table_transformer=aks_agentpool_list_table_format)
        g.custom_show_command('show', 'aks_agentpool_show',
                              table_transformer=aks_agentpool_show_table_format)
        g.custom_command('add', 'aks_agentpool_add', supports_no_wait=True)
        g.custom_command('scale', 'aks_agentpool_scale', supports_no_wait=True)
        g.custom_command('upgrade', 'aks_agentpool_upgrade',
                         supports_no_wait=True)
        g.custom_command('update', 'aks_agentpool_update',
                         supports_no_wait=True)
        g.custom_command('delete', 'aks_agentpool_delete',
                         supports_no_wait=True)
        g.custom_command('get-upgrades', 'aks_agentpool_get_upgrade_profile')
        g.custom_command('stop', 'aks_agentpool_stop', supports_no_wait=True)
        g.custom_command('start', 'aks_agentpool_start', supports_no_wait=True)

    # AKS draft commands
    with self.command_group('aks draft', managed_clusters_sdk, client_factory=cf_managed_clusters) as g:
        g.custom_command('create', 'aks_draft_create')
        g.custom_command('setup-gh', 'aks_draft_setup_gh')
        g.custom_command('generate-workflow', 'aks_draft_generate_workflow')
        g.custom_command('up', 'aks_draft_up')
        g.custom_command('update', 'aks_draft_update')

    # AKS pod identity commands
    with self.command_group('aks pod-identity', managed_clusters_sdk, client_factory=cf_managed_clusters) as g:
        g.custom_command('add', 'aks_pod_identity_add')
        g.custom_command('delete', 'aks_pod_identity_delete')
        g.custom_command('list', 'aks_pod_identity_list',
                         table_transformer=aks_pod_identities_table_format)

    # AKS pod identity exception commands
    with self.command_group('aks pod-identity exception', managed_clusters_sdk, client_factory=cf_managed_clusters) as g:
        g.custom_command('add', 'aks_pod_identity_exception_add')
        g.custom_command('delete', 'aks_pod_identity_exception_delete')
        g.custom_command('update', 'aks_pod_identity_exception_update')
        g.custom_command('list', 'aks_pod_identity_exception_list',
                         table_transformer=aks_pod_identity_exceptions_table_format)

    # AKS egress commands
    with self.command_group('aks egress-endpoints', managed_clusters_sdk, client_factory=cf_managed_clusters) as g:
        g.custom_command('list', 'aks_egress_endpoints_list')

    # AKS nodepool snapshot commands
    with self.command_group('aks nodepool snapshot', nodepool_snapshot_sdk, client_factory=cf_nodepool_snapshots) as g:
        g.custom_command('list', 'aks_nodepool_snapshot_list',
                         table_transformer=aks_list_nodepool_snapshot_table_format)
        g.custom_show_command('show', 'aks_nodepool_snapshot_show',
                              table_transformer=aks_show_nodepool_snapshot_table_format)
        g.custom_command('create', 'aks_nodepool_snapshot_create',
                         supports_no_wait=True)
        g.custom_command('delete', 'aks_nodepool_snapshot_delete',
                         supports_no_wait=True)

    # AKS mc snapshot commands
    with self.command_group('aks snapshot', mc_snapshot_sdk, client_factory=cf_mc_snapshots) as g:
        g.custom_command('list', 'aks_snapshot_list',
                         table_transformer=aks_list_snapshot_table_format)
        g.custom_show_command('show', 'aks_snapshot_show',
                              table_transformer=aks_show_snapshot_table_format)
        g.custom_command('create', 'aks_snapshot_create',
                         supports_no_wait=True)
        g.custom_command('delete', 'aks_snapshot_delete',
                         supports_no_wait=True)
