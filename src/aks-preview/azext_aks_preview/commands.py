# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core.commands import CliCommandType

from ._client_factory import cf_managed_clusters
from ._client_factory import cf_maintenance_configurations
from ._client_factory import cf_container_services
from ._client_factory import cf_agent_pools
from ._format import aks_show_table_format
from ._format import aks_agentpool_show_table_format
from ._format import aks_agentpool_list_table_format
from ._format import aks_versions_table_format
from ._format import aks_upgrades_table_format
from ._format import aks_pod_identities_table_format
from ._format import aks_pod_identity_exceptions_table_format
from ._format import aks_run_command_result_format


def load_command_table(self, _):

    managed_clusters_sdk = CliCommandType(
        operations_tmpl='azext_aks_preview.vendored_sdks.azure_mgmt_preview_aks.'
                        'operations._managed_clusters_operations#ManagedClustersOperations.{}',
        client_factory=cf_managed_clusters
    )

    container_services_sdk = CliCommandType(
        operations_tmpl='azext_aks_preview.vendored_sdks.azure_mgmt_preview_aks.'
                        'operations.container_service_operations#ContainerServicesOperations.{}',
        client_factory=cf_container_services
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

    # AKS managed cluster commands
    with self.command_group('aks', managed_clusters_sdk, client_factory=cf_managed_clusters) as g:
        g.custom_command('kollect', 'aks_kollect')
        g.custom_command('kanalyze', 'aks_kanalyze')
        g.custom_command('browse', 'aks_browse')
        g.custom_command('create', 'aks_create', supports_no_wait=True)
        g.custom_command('update', 'aks_update', supports_no_wait=True)
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
        g.command('stop', 'stop', supports_no_wait=True)
        g.command('start', 'start', supports_no_wait=True)
        g.custom_command('get-os-options', 'aks_get_os_options')

    # AKS container service commands
    with self.command_group('aks', container_services_sdk, client_factory=cf_container_services) as g:
        g.custom_command('get-versions', 'aks_get_versions',
                         table_transformer=aks_versions_table_format)

    with self.command_group('aks command', managed_clusters_sdk, client_factory=cf_managed_clusters) as g:
        g.custom_command('invoke', 'aks_runcommand', supports_no_wait=True,
                         table_transformer=aks_run_command_result_format)
        g.custom_command('result', 'aks_command_result',
                         supports_no_wait=False, table_transformer=aks_run_command_result_format)

    # AKS maintenance configuration commands
    with self.command_group('aks maintenanceconfiguration', maintenance_configuration_sdk, client_factory=cf_maintenance_configurations) as g:
        g.custom_command('list', 'aks_maintenanceconfiguration_list')
        g.custom_show_command('show', 'aks_maintenanceconfiguration_show')
        g.custom_command('add', 'aks_maintenanceconfiguration_add')
        g.custom_command('update', 'aks_maintenanceconfiguration_update')
        g.custom_command('delete', 'aks_maintenanceconfiguration_delete')

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
