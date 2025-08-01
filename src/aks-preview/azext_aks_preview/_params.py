# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=too-many-statements,too-many-lines
import os.path
import platform

from argcomplete.completers import FilesCompleter
from azure.cli.command_modules.acs._consts import (
    CONST_OUTBOUND_TYPE_LOAD_BALANCER,
    CONST_OUTBOUND_TYPE_MANAGED_NAT_GATEWAY,
    CONST_OUTBOUND_TYPE_USER_ASSIGNED_NAT_GATEWAY,
    CONST_OUTBOUND_TYPE_USER_DEFINED_ROUTING,
)
from azure.cli.command_modules.acs._validators import (
    validate_image_cleaner_enable_disable_mutually_exclusive,
    validate_load_balancer_idle_timeout,
    validate_load_balancer_outbound_ip_prefixes,
    validate_load_balancer_outbound_ips,
    validate_load_balancer_outbound_ports,
    validate_nat_gateway_idle_timeout,
    validate_nat_gateway_managed_outbound_ip_count,
)
from azure.cli.core.commands.parameters import (
    edge_zone_type,
    file_type,
    get_enum_type,
    get_resource_name_completion_list,
    get_three_state_flag,
    name_type,
    tags_type,
    zones_type,
)
from azext_aks_preview._client_factory import CUSTOM_MGMT_AKS_PREVIEW
from azext_aks_preview._completers import (
    get_k8s_upgrades_completion_list,
    get_k8s_versions_completion_list,
    get_vm_size_completion_list,
)
from azext_aks_preview._consts import (
    CONST_ABSOLUTEMONTHLY_MAINTENANCE_SCHEDULE,
    CONST_AZURE_KEYVAULT_NETWORK_ACCESS_PRIVATE,
    CONST_AZURE_KEYVAULT_NETWORK_ACCESS_PUBLIC,
    CONST_NAMESPACE_ADOPTION_POLICY_NEVER,
    CONST_NAMESPACE_ADOPTION_POLICY_IFIDENTICAL,
    CONST_NAMESPACE_ADOPTION_POLICY_ALWAYS,
    CONST_NAMESPACE_NETWORK_POLICY_RULE_DENYALL,
    CONST_NAMESPACE_NETWORK_POLICY_RULE_ALLOWALL,
    CONST_NAMESPACE_NETWORK_POLICY_RULE_ALLOWSAMENAMESPACE,
    CONST_NAMESPACE_DELETE_POLICY_KEEP,
    CONST_NAMESPACE_DELETE_POLICY_DELETE,
    CONST_CREDENTIAL_FORMAT_AZURE,
    CONST_CREDENTIAL_FORMAT_EXEC,
    CONST_DAILY_MAINTENANCE_SCHEDULE,
    CONST_DISK_DRIVER_V1,
    CONST_DISK_DRIVER_V2,
    CONST_GPU_DRIVER_INSTALL,
    CONST_GPU_DRIVER_NONE,
    CONST_GPU_INSTANCE_PROFILE_MIG1_G,
    CONST_GPU_INSTANCE_PROFILE_MIG2_G,
    CONST_GPU_INSTANCE_PROFILE_MIG3_G,
    CONST_GPU_INSTANCE_PROFILE_MIG4_G,
    CONST_GPU_INSTANCE_PROFILE_MIG7_G,
    CONST_LOAD_BALANCER_SKU_BASIC,
    CONST_LOAD_BALANCER_SKU_STANDARD,
    CONST_MANAGED_CLUSTER_SKU_TIER_FREE,
    CONST_MANAGED_CLUSTER_SKU_TIER_STANDARD,
    CONST_MANAGED_CLUSTER_SKU_TIER_PREMIUM,
    CONST_NETWORK_DATAPLANE_AZURE,
    CONST_NETWORK_DATAPLANE_CILIUM,
    CONST_NETWORK_PLUGIN_AZURE,
    CONST_NETWORK_PLUGIN_KUBENET,
    CONST_NETWORK_PLUGIN_MODE_OVERLAY,
    CONST_NETWORK_PLUGIN_NONE,
    CONST_NETWORK_POD_IP_ALLOCATION_MODE_DYNAMIC_INDIVIDUAL,
    CONST_NETWORK_POD_IP_ALLOCATION_MODE_STATIC_BLOCK,
    CONST_NODE_IMAGE_UPGRADE_CHANNEL,
    CONST_NODE_OS_CHANNEL_NODE_IMAGE,
    CONST_NODE_OS_CHANNEL_NONE,
    CONST_NODE_OS_CHANNEL_SECURITY_PATCH,
    CONST_NODE_OS_CHANNEL_UNMANAGED,
    CONST_NODEPOOL_MODE_SYSTEM,
    CONST_NODEPOOL_MODE_USER,
    CONST_NODEPOOL_MODE_GATEWAY,
    CONST_NODEPOOL_MODE_MANAGEDSYSTEM,
    CONST_NONE_UPGRADE_CHANNEL,
    CONST_NRG_LOCKDOWN_RESTRICTION_LEVEL_READONLY,
    CONST_NRG_LOCKDOWN_RESTRICTION_LEVEL_UNRESTRICTED,
    CONST_OS_DISK_TYPE_EPHEMERAL,
    CONST_OS_DISK_TYPE_MANAGED,
    CONST_OS_SKU_AZURELINUX,
    CONST_OS_SKU_CBLMARINER,
    CONST_OS_SKU_MARINER,
    CONST_OS_SKU_UBUNTU,
    CONST_OS_SKU_UBUNTU2204,
    CONST_OS_SKU_UBUNTU2404,
    CONST_OS_SKU_WINDOWS2019,
    CONST_OS_SKU_WINDOWS2022,
    CONST_OS_SKU_WINDOWSANNUAL,
    CONST_PATCH_UPGRADE_CHANNEL,
    CONST_RAPID_UPGRADE_CHANNEL,
    CONST_RELATIVEMONTHLY_MAINTENANCE_SCHEDULE,
    CONST_SCALE_DOWN_MODE_DEALLOCATE,
    CONST_SCALE_DOWN_MODE_DELETE,
    CONST_SCALE_SET_PRIORITY_REGULAR,
    CONST_SCALE_SET_PRIORITY_SPOT,
    CONST_SPOT_EVICTION_POLICY_DEALLOCATE,
    CONST_SPOT_EVICTION_POLICY_DELETE,
    CONST_STABLE_UPGRADE_CHANNEL,
    CONST_WEEKINDEX_FIRST,
    CONST_WEEKINDEX_FOURTH,
    CONST_WEEKINDEX_LAST,
    CONST_SAFEGUARDSLEVEL_OFF,
    CONST_SAFEGUARDSLEVEL_WARNING,
    CONST_SAFEGUARDSLEVEL_ENFORCEMENT,
    CONST_AZURE_SERVICE_MESH_INGRESS_MODE_EXTERNAL,
    CONST_AZURE_SERVICE_MESH_INGRESS_MODE_INTERNAL,
    CONST_AZURE_SERVICE_MESH_DEFAULT_EGRESS_NAMESPACE,
    CONST_WEEKINDEX_SECOND,
    CONST_WEEKINDEX_THIRD,
    CONST_WEEKLY_MAINTENANCE_SCHEDULE,
    CONST_WORKLOAD_RUNTIME_KATA_MSHV_VM_ISOLATION,
    CONST_WORKLOAD_RUNTIME_KATA_CC_ISOLATION,
    CONST_WORKLOAD_RUNTIME_OCI_CONTAINER,
    CONST_WORKLOAD_RUNTIME_WASM_WASI,
    CONST_NODE_PROVISIONING_MODE_MANUAL,
    CONST_NODE_PROVISIONING_MODE_AUTO,
    CONST_NODE_PROVISIONING_DEFAULT_POOLS_AUTO,
    CONST_NODE_PROVISIONING_DEFAULT_POOLS_NONE,
    CONST_MANAGED_CLUSTER_SKU_NAME_BASE,
    CONST_MANAGED_CLUSTER_SKU_NAME_AUTOMATIC,
    CONST_SSH_ACCESS_LOCALUSER,
    CONST_SSH_ACCESS_DISABLED,
    CONST_CLUSTER_SERVICE_HEALTH_PROBE_MODE_SERVICE_NODE_PORT,
    CONST_CLUSTER_SERVICE_HEALTH_PROBE_MODE_SHARED,
    CONST_ARTIFACT_SOURCE_DIRECT,
    CONST_ARTIFACT_SOURCE_CACHE,
    CONST_OUTBOUND_TYPE_NONE,
    CONST_OUTBOUND_TYPE_BLOCK,
    CONST_APP_ROUTING_ANNOTATION_CONTROLLED_NGINX,
    CONST_APP_ROUTING_EXTERNAL_NGINX,
    CONST_APP_ROUTING_INTERNAL_NGINX,
    CONST_APP_ROUTING_NONE_NGINX,
    CONST_GPU_DRIVER_TYPE_CUDA,
    CONST_GPU_DRIVER_TYPE_GRID,
    CONST_ADVANCED_NETWORKPOLICIES_NONE,
    CONST_ADVANCED_NETWORKPOLICIES_FQDN,
    CONST_ADVANCED_NETWORKPOLICIES_L7,
    CONST_TRANSIT_ENCRYPTION_TYPE_NONE,
    CONST_TRANSIT_ENCRYPTION_TYPE_WIREGUARD
)

from azext_aks_preview._validators import (
    validate_acr,
    validate_namespace_name,
    validate_resource_quota,
    validate_addon,
    validate_addons,
    validate_agent_pool_name,
    validate_allowed_host_ports,
    validate_apiserver_subnet_id,
    validate_application_security_groups,
    validate_assign_identity,
    validate_assign_kubelet_identity,
    validate_azure_keyvault_kms_key_id,
    validate_azure_keyvault_kms_key_vault_resource_id,
    validate_azuremonitorworkspaceresourceid,
    validate_cluster_id,
    validate_cluster_snapshot_id,
    validate_create_parameters,
    validate_crg_id,
    validate_custom_ca_trust_certificates,
    validate_defender_config_parameter,
    validate_defender_disable_and_enable_parameters,
    validate_disable_windows_outbound_nat,
    validate_asm_egress_name,
    validate_enable_custom_ca_trust,
    validate_eviction_policy,
    validate_grafanaresourceid,
    validate_host_group_id,
    validate_ip_ranges,
    validate_k8s_version,
    validate_linux_host_name,
    validate_load_balancer_backend_pool_type,
    validate_load_balancer_sku,
    validate_max_surge,
    validate_message_of_the_day,
    validate_node_public_ip_tags,
    validate_nodepool_id,
    validate_nodepool_labels,
    validate_nodepool_taints,
    validate_nodepool_name,
    validate_nodepool_tags,
    validate_nodes_count,
    validate_os_sku,
    validate_pod_identity_pod_labels,
    validate_pod_identity_resource_name,
    validate_pod_identity_resource_namespace,
    validate_pod_subnet_id,
    validate_pod_ip_allocation_mode,
    validate_priority,
    validate_sku_tier,
    validate_snapshot_id,
    validate_snapshot_name,
    validate_spot_max_price,
    validate_ssh_key,
    validate_ssh_key_for_update,
    validate_start_date,
    validate_start_time,
    validate_user,
    validate_utc_offset,
    validate_vm_set_type,
    validate_vnet_subnet_id,
    validate_force_upgrade_disable_and_enable_parameters,
    validate_azure_service_mesh_revision,
    validate_artifact_streaming,
    validate_custom_endpoints,
    validate_bootstrap_container_registry_resource_id,
    validate_gateway_prefix_size,
    validate_max_unavailable,
    validate_max_blocked_nodes,
    validate_resource_group_parameter,
    validate_location_resource_group_cluster_parameters,
)
from azext_aks_preview.azurecontainerstorage._consts import (
    CONST_ACSTOR_ALL,
    CONST_DISK_TYPE_EPHEMERAL_VOLUME_ONLY,
    CONST_DISK_TYPE_PV_WITH_ANNOTATION,
    CONST_EPHEMERAL_NVME_PERF_TIER_BASIC,
    CONST_EPHEMERAL_NVME_PERF_TIER_PREMIUM,
    CONST_EPHEMERAL_NVME_PERF_TIER_STANDARD,
    CONST_STORAGE_POOL_TYPE_AZURE_DISK,
    CONST_STORAGE_POOL_TYPE_EPHEMERAL_DISK,
    CONST_STORAGE_POOL_TYPE_ELASTIC_SAN,
    CONST_STORAGE_POOL_SKU_PREMIUM_LRS,
    CONST_STORAGE_POOL_SKU_STANDARD_LRS,
    CONST_STORAGE_POOL_SKU_STANDARDSSD_LRS,
    CONST_STORAGE_POOL_SKU_ULTRASSD_LRS,
    CONST_STORAGE_POOL_SKU_PREMIUM_ZRS,
    CONST_STORAGE_POOL_SKU_PREMIUMV2_LRS,
    CONST_STORAGE_POOL_SKU_STANDARDSSD_ZRS,
    CONST_STORAGE_POOL_OPTION_NVME,
    CONST_STORAGE_POOL_OPTION_SSD,
)

from .action import (
    AddConfigurationSettings,
    AddConfigurationProtectedSettings,
)

from knack.arguments import CLIArgumentType

# candidates for enumeration
# consts for AgentPool
node_priorities = [CONST_SCALE_SET_PRIORITY_REGULAR, CONST_SCALE_SET_PRIORITY_SPOT]
node_eviction_policies = [
    CONST_SPOT_EVICTION_POLICY_DELETE,
    CONST_SPOT_EVICTION_POLICY_DEALLOCATE,
]
node_os_disk_types = [CONST_OS_DISK_TYPE_MANAGED, CONST_OS_DISK_TYPE_EPHEMERAL]
node_mode_types = [
    CONST_NODEPOOL_MODE_SYSTEM,
    CONST_NODEPOOL_MODE_USER,
    CONST_NODEPOOL_MODE_GATEWAY,
    CONST_NODEPOOL_MODE_MANAGEDSYSTEM,
]
node_os_skus_create = [
    CONST_OS_SKU_AZURELINUX,
    CONST_OS_SKU_UBUNTU,
    CONST_OS_SKU_CBLMARINER,
    CONST_OS_SKU_MARINER,
    CONST_OS_SKU_UBUNTU2204,
    CONST_OS_SKU_UBUNTU2404,
]
node_os_skus = node_os_skus_create + [
    CONST_OS_SKU_WINDOWS2019,
    CONST_OS_SKU_WINDOWS2022,
    CONST_OS_SKU_WINDOWSANNUAL,
]
node_os_skus_update = [
    CONST_OS_SKU_AZURELINUX,
    CONST_OS_SKU_UBUNTU,
    CONST_OS_SKU_UBUNTU2204,
    CONST_OS_SKU_UBUNTU2404,
]
scale_down_modes = [CONST_SCALE_DOWN_MODE_DELETE, CONST_SCALE_DOWN_MODE_DEALLOCATE]
workload_runtimes = [
    CONST_WORKLOAD_RUNTIME_OCI_CONTAINER,
    CONST_WORKLOAD_RUNTIME_WASM_WASI,
    CONST_WORKLOAD_RUNTIME_KATA_MSHV_VM_ISOLATION,
    CONST_WORKLOAD_RUNTIME_KATA_CC_ISOLATION,
]
gpu_instance_profiles = [
    CONST_GPU_INSTANCE_PROFILE_MIG1_G,
    CONST_GPU_INSTANCE_PROFILE_MIG2_G,
    CONST_GPU_INSTANCE_PROFILE_MIG3_G,
    CONST_GPU_INSTANCE_PROFILE_MIG4_G,
    CONST_GPU_INSTANCE_PROFILE_MIG7_G,
]
gpu_driver_install_modes = [
    CONST_GPU_DRIVER_INSTALL,
    CONST_GPU_DRIVER_NONE
]
pod_ip_allocation_modes = [
    CONST_NETWORK_POD_IP_ALLOCATION_MODE_DYNAMIC_INDIVIDUAL,
    CONST_NETWORK_POD_IP_ALLOCATION_MODE_STATIC_BLOCK,
]

# consts for ManagedCluster
load_balancer_skus = [CONST_LOAD_BALANCER_SKU_BASIC, CONST_LOAD_BALANCER_SKU_STANDARD]
sku_names = [
    CONST_MANAGED_CLUSTER_SKU_NAME_BASE,
    CONST_MANAGED_CLUSTER_SKU_NAME_AUTOMATIC,
]
sku_tiers = [
    CONST_MANAGED_CLUSTER_SKU_TIER_FREE,
    CONST_MANAGED_CLUSTER_SKU_TIER_STANDARD,
    CONST_MANAGED_CLUSTER_SKU_TIER_PREMIUM,
]
network_plugins = [
    CONST_NETWORK_PLUGIN_KUBENET,
    CONST_NETWORK_PLUGIN_AZURE,
    CONST_NETWORK_PLUGIN_NONE,
]
network_plugin_modes = [CONST_NETWORK_PLUGIN_MODE_OVERLAY]
advanced_networkpolicies = [
    CONST_ADVANCED_NETWORKPOLICIES_NONE,
    CONST_ADVANCED_NETWORKPOLICIES_FQDN,
    CONST_ADVANCED_NETWORKPOLICIES_L7,
]
transit_encryption_types = [
    CONST_TRANSIT_ENCRYPTION_TYPE_NONE,
    CONST_TRANSIT_ENCRYPTION_TYPE_WIREGUARD,
]
network_dataplanes = [CONST_NETWORK_DATAPLANE_AZURE, CONST_NETWORK_DATAPLANE_CILIUM]
disk_driver_versions = [CONST_DISK_DRIVER_V1, CONST_DISK_DRIVER_V2]
outbound_types = [
    CONST_OUTBOUND_TYPE_LOAD_BALANCER,
    CONST_OUTBOUND_TYPE_USER_DEFINED_ROUTING,
    CONST_OUTBOUND_TYPE_MANAGED_NAT_GATEWAY,
    CONST_OUTBOUND_TYPE_USER_ASSIGNED_NAT_GATEWAY,
    CONST_OUTBOUND_TYPE_NONE,
    CONST_OUTBOUND_TYPE_BLOCK,
]
auto_upgrade_channels = [
    CONST_RAPID_UPGRADE_CHANNEL,
    CONST_STABLE_UPGRADE_CHANNEL,
    CONST_PATCH_UPGRADE_CHANNEL,
    CONST_NODE_IMAGE_UPGRADE_CHANNEL,
    CONST_NONE_UPGRADE_CHANNEL,
]
node_os_upgrade_channels = [
    CONST_NODE_OS_CHANNEL_NODE_IMAGE,
    CONST_NODE_OS_CHANNEL_NONE,
    CONST_NODE_OS_CHANNEL_SECURITY_PATCH,
    CONST_NODE_OS_CHANNEL_UNMANAGED,
]

nrg_lockdown_restriction_levels = [
    CONST_NRG_LOCKDOWN_RESTRICTION_LEVEL_READONLY,
    CONST_NRG_LOCKDOWN_RESTRICTION_LEVEL_UNRESTRICTED,
]

# consts for managed namespace
network_policy_rule = [
    CONST_NAMESPACE_NETWORK_POLICY_RULE_DENYALL,
    CONST_NAMESPACE_NETWORK_POLICY_RULE_ALLOWALL,
    CONST_NAMESPACE_NETWORK_POLICY_RULE_ALLOWSAMENAMESPACE,
]

adoption_policy = [
    CONST_NAMESPACE_ADOPTION_POLICY_NEVER,
    CONST_NAMESPACE_ADOPTION_POLICY_IFIDENTICAL,
    CONST_NAMESPACE_ADOPTION_POLICY_ALWAYS,
]

delete_policy = [
    CONST_NAMESPACE_DELETE_POLICY_KEEP,
    CONST_NAMESPACE_DELETE_POLICY_DELETE,
]

# consts for maintenance configuration
schedule_types = [
    CONST_DAILY_MAINTENANCE_SCHEDULE,
    CONST_WEEKLY_MAINTENANCE_SCHEDULE,
    CONST_ABSOLUTEMONTHLY_MAINTENANCE_SCHEDULE,
    CONST_RELATIVEMONTHLY_MAINTENANCE_SCHEDULE,
]

week_indexes = [
    CONST_WEEKINDEX_FIRST,
    CONST_WEEKINDEX_SECOND,
    CONST_WEEKINDEX_THIRD,
    CONST_WEEKINDEX_FOURTH,
    CONST_WEEKINDEX_LAST,
]

# consts for credential
credential_formats = [CONST_CREDENTIAL_FORMAT_AZURE, CONST_CREDENTIAL_FORMAT_EXEC]

keyvault_network_access_types = [
    CONST_AZURE_KEYVAULT_NETWORK_ACCESS_PUBLIC,
    CONST_AZURE_KEYVAULT_NETWORK_ACCESS_PRIVATE,
]

# consts for Safeguards level
safeguards_levels = [
    CONST_SAFEGUARDSLEVEL_OFF,
    CONST_SAFEGUARDSLEVEL_WARNING,
    CONST_SAFEGUARDSLEVEL_ENFORCEMENT,
]

# azure service mesh
ingress_gateway_types = [
    CONST_AZURE_SERVICE_MESH_INGRESS_MODE_EXTERNAL,
    CONST_AZURE_SERVICE_MESH_INGRESS_MODE_INTERNAL,
]

# azure container storage
storage_pool_types = [
    CONST_STORAGE_POOL_TYPE_AZURE_DISK,
    CONST_STORAGE_POOL_TYPE_EPHEMERAL_DISK,
    CONST_STORAGE_POOL_TYPE_ELASTIC_SAN,
]

disable_storage_pool_types = [
    CONST_STORAGE_POOL_TYPE_AZURE_DISK,
    CONST_STORAGE_POOL_TYPE_EPHEMERAL_DISK,
    CONST_STORAGE_POOL_TYPE_ELASTIC_SAN,
    CONST_ACSTOR_ALL,
]

storage_pool_skus = [
    CONST_STORAGE_POOL_SKU_PREMIUM_LRS,
    CONST_STORAGE_POOL_SKU_STANDARD_LRS,
    CONST_STORAGE_POOL_SKU_STANDARDSSD_LRS,
    CONST_STORAGE_POOL_SKU_ULTRASSD_LRS,
    CONST_STORAGE_POOL_SKU_PREMIUM_ZRS,
    CONST_STORAGE_POOL_SKU_PREMIUMV2_LRS,
    CONST_STORAGE_POOL_SKU_STANDARDSSD_ZRS,
]

storage_pool_options = [
    CONST_STORAGE_POOL_OPTION_NVME,
    CONST_STORAGE_POOL_OPTION_SSD,
]

disable_storage_pool_options = [
    CONST_STORAGE_POOL_OPTION_NVME,
    CONST_STORAGE_POOL_OPTION_SSD,
    CONST_ACSTOR_ALL,
]

ephemeral_disk_volume_types = [
    CONST_DISK_TYPE_EPHEMERAL_VOLUME_ONLY,
    CONST_DISK_TYPE_PV_WITH_ANNOTATION,
]

ephemeral_disk_nvme_perf_tiers = [
    CONST_EPHEMERAL_NVME_PERF_TIER_BASIC,
    CONST_EPHEMERAL_NVME_PERF_TIER_PREMIUM,
    CONST_EPHEMERAL_NVME_PERF_TIER_STANDARD,
]

node_provisioning_modes = [
    CONST_NODE_PROVISIONING_MODE_MANUAL,
    CONST_NODE_PROVISIONING_MODE_AUTO,
]

node_provisioning_default_pools = [
    CONST_NODE_PROVISIONING_DEFAULT_POOLS_AUTO,
    CONST_NODE_PROVISIONING_DEFAULT_POOLS_NONE,
]

ssh_accesses = [
    CONST_SSH_ACCESS_LOCALUSER,
    CONST_SSH_ACCESS_DISABLED,
]

health_probe_modes = [
    CONST_CLUSTER_SERVICE_HEALTH_PROBE_MODE_SERVICE_NODE_PORT,
    CONST_CLUSTER_SERVICE_HEALTH_PROBE_MODE_SHARED,
]

bootstrap_artifact_source_types = [
    CONST_ARTIFACT_SOURCE_DIRECT,
    CONST_ARTIFACT_SOURCE_CACHE,
]

# consts for app routing add-on
app_routing_nginx_configs = [
    CONST_APP_ROUTING_ANNOTATION_CONTROLLED_NGINX,
    CONST_APP_ROUTING_EXTERNAL_NGINX,
    CONST_APP_ROUTING_INTERNAL_NGINX,
    CONST_APP_ROUTING_NONE_NGINX
]

gpu_driver_types = [
    CONST_GPU_DRIVER_TYPE_CUDA,
    CONST_GPU_DRIVER_TYPE_GRID,
]


def load_arguments(self, _):
    acr_arg_type = CLIArgumentType(metavar="ACR_NAME_OR_RESOURCE_ID")
    k8s_support_plans = self.get_models(
        "KubernetesSupportPlan",
        resource_type=CUSTOM_MGMT_AKS_PREVIEW,
        operation_group="managed_clusters",
    )

    # AKS command argument configuration
    with self.argument_context("aks") as c:
        c.argument(
            "resource_name",
            name_type,
            help="Name of the managed cluster.",
            completer=get_resource_name_completion_list(
                "Microsoft.ContainerService/ManagedClusters"
            ),
        )
        c.argument(
            "name",
            name_type,
            help="Name of the managed cluster.",
            completer=get_resource_name_completion_list(
                "Microsoft.ContainerService/ManagedClusters"
            ),
        )
        c.argument(
            "kubernetes_version",
            options_list=["--kubernetes-version", "-k"],
            validator=validate_k8s_version,
        )
        c.argument("node_count", options_list=["--node-count", "-c"], type=int)
        c.argument("tags", tags_type)

    with self.argument_context("aks create") as c:
        # managed cluster paramerters
        c.argument("name", validator=validate_linux_host_name)
        c.argument("kubernetes_version", completer=get_k8s_versions_completion_list)
        c.argument("dns_name_prefix", options_list=["--dns-name-prefix", "-p"])
        c.argument(
            "node_osdisk_diskencryptionset_id",
            options_list=["--node-osdisk-diskencryptionset-id", "-d"],
        )
        c.argument("disable_local_accounts", action="store_true")
        c.argument("disable_rbac", action="store_true")
        c.argument("edge_zone", edge_zone_type)
        c.argument(
            "admin_username",
            options_list=["--admin-username", "-u"],
            default="azureuser",
        )
        c.argument(
            "generate_ssh_keys",
            action="store_true",
            validator=validate_create_parameters,
        )
        c.argument(
            "ssh_key_value",
            required=False,
            type=file_type,
            default=os.path.join("~", ".ssh", "id_rsa.pub"),
            completer=FilesCompleter(),
            validator=validate_ssh_key,
        )
        c.argument("no_ssh_key", options_list=["--no-ssh-key", "-x"])
        c.argument("dns_service_ip")
        c.argument(
            "docker_bridge_address",
            deprecate_info=c.deprecate(target="--docker-bridge-address", hide=True),
        )
        c.argument("pod_cidrs")
        c.argument("service_cidrs")
        c.argument(
            "load_balancer_sku",
            arg_type=get_enum_type(load_balancer_skus),
            validator=validate_load_balancer_sku,
        )
        c.argument("load_balancer_managed_outbound_ip_count", type=int)
        c.argument(
            "load_balancer_outbound_ips", validator=validate_load_balancer_outbound_ips
        )
        c.argument(
            "load_balancer_outbound_ip_prefixes",
            validator=validate_load_balancer_outbound_ip_prefixes,
        )
        c.argument(
            "load_balancer_outbound_ports",
            type=int,
            validator=validate_load_balancer_outbound_ports,
        )
        c.argument(
            "load_balancer_idle_timeout",
            type=int,
            validator=validate_load_balancer_idle_timeout,
        )
        c.argument(
            "load_balancer_backend_pool_type",
            validator=validate_load_balancer_backend_pool_type,
        )
        c.argument(
            "nrg_lockdown_restriction_level",
            arg_type=get_enum_type(nrg_lockdown_restriction_levels),
        )
        c.argument(
            "nat_gateway_managed_outbound_ip_count",
            type=int,
            validator=validate_nat_gateway_managed_outbound_ip_count,
        )
        c.argument(
            "nat_gateway_idle_timeout",
            type=int,
            validator=validate_nat_gateway_idle_timeout,
        )
        c.argument("outbound_type", arg_type=get_enum_type(outbound_types))
        c.argument("network_plugin", arg_type=get_enum_type(network_plugins))
        c.argument("network_plugin_mode", arg_type=get_enum_type(network_plugin_modes))
        c.argument("network_policy")
        c.argument("network_dataplane", arg_type=get_enum_type(network_dataplanes))
        c.argument("kube_proxy_config")
        c.argument(
            "auto_upgrade_channel", arg_type=get_enum_type(auto_upgrade_channels)
        )
        c.argument(
            "node_os_upgrade_channel", arg_type=get_enum_type(node_os_upgrade_channels)
        )
        c.argument(
            "cluster_autoscaler_profile",
            nargs="+",
            options_list=["--cluster-autoscaler-profile", "--ca-profile"],
            help=(
                "Space-separated list of key=value pairs for configuring cluster autoscaler. "
                "Pass an empty string to clear the profile."
            ),
        )
        c.argument(
            "sku", is_preview=True, arg_type=get_enum_type(sku_names)
        )
        c.argument(
            "tier", arg_type=get_enum_type(sku_tiers), validator=validate_sku_tier
        )
        c.argument("fqdn_subdomain")
        c.argument("api_server_authorized_ip_ranges", validator=validate_ip_ranges)
        c.argument("enable_private_cluster", action="store_true")
        c.argument("private_dns_zone")
        c.argument("disable_public_fqdn", action="store_true")
        c.argument("service_principal")
        c.argument("client_secret")
        c.argument("enable_managed_identity", action="store_true")
        c.argument("assign_identity", validator=validate_assign_identity)
        c.argument(
            "assign_kubelet_identity", validator=validate_assign_kubelet_identity
        )
        c.argument("enable_aad", action="store_true")
        c.argument("enable_azure_rbac", action="store_true")
        c.argument("aad_tenant_id")
        c.argument("aad_admin_group_object_ids")
        c.argument("enable_oidc_issuer", action="store_true")
        c.argument("windows_admin_username")
        c.argument("windows_admin_password")
        c.argument("enable_ahub")
        c.argument("enable_windows_gmsa", action="store_true")
        c.argument("gmsa_dns_server")
        c.argument("gmsa_root_domain_name")
        c.argument("attach_acr", acr_arg_type)
        c.argument("skip_subnet_role_assignment", action="store_true")
        c.argument("node_resource_group")
        c.argument("k8s_support_plan", arg_type=get_enum_type(k8s_support_plans))
        c.argument("enable_defender", action="store_true")
        c.argument("defender_config", validator=validate_defender_config_parameter)
        c.argument("disk_driver_version", arg_type=get_enum_type(disk_driver_versions))
        c.argument("disable_disk_driver", action="store_true")
        c.argument("disable_file_driver", action="store_true")
        c.argument("enable_blob_driver", action="store_true")
        c.argument("disable_snapshot_controller", action="store_true")
        c.argument("enable_azure_keyvault_kms", action="store_true")
        c.argument(
            "azure_keyvault_kms_key_id", validator=validate_azure_keyvault_kms_key_id
        )
        c.argument(
            "azure_keyvault_kms_key_vault_network_access",
            arg_type=get_enum_type(keyvault_network_access_types),
            default=CONST_AZURE_KEYVAULT_NETWORK_ACCESS_PUBLIC,
        )
        c.argument(
            "azure_keyvault_kms_key_vault_resource_id",
            validator=validate_azure_keyvault_kms_key_vault_resource_id,
        )
        c.argument("http_proxy_config")
        c.argument(
            "bootstrap_artifact_source",
            arg_type=get_enum_type(bootstrap_artifact_source_types),
            default=CONST_ARTIFACT_SOURCE_DIRECT,
            is_preview=True,
        )
        c.argument(
            "bootstrap_container_registry_resource_id",
            validator=validate_bootstrap_container_registry_resource_id,
            is_preview=True,
        )
        # addons
        c.argument(
            "enable_addons",
            options_list=["--enable-addons", "-a"],
            validator=validate_addons,
        )
        c.argument("workspace_resource_id")
        c.argument(
            "enable_msi_auth_for_monitoring",
            arg_type=get_three_state_flag(),
            is_preview=True,
        )
        c.argument("enable_syslog", arg_type=get_three_state_flag(), is_preview=True)
        c.argument("data_collection_settings", is_preview=True)
        c.argument("enable_high_log_scale_mode", arg_type=get_three_state_flag(), is_preview=True)
        c.argument("ampls_resource_id", is_preview=True)
        c.argument("aci_subnet_name")
        c.argument("appgw_name", arg_group="Application Gateway")
        c.argument("appgw_subnet_cidr", arg_group="Application Gateway")
        c.argument("appgw_id", arg_group="Application Gateway")
        c.argument("appgw_subnet_id", arg_group="Application Gateway")
        c.argument("appgw_watch_namespace", arg_group="Application Gateway")
        c.argument("enable_secret_rotation", action="store_true")
        c.argument("rotation_poll_interval")
        c.argument("enable_sgxquotehelper", action="store_true")
        c.argument("enable_app_routing", action="store_true", is_preview=True)
        c.argument(
            "app_routing_default_nginx_controller",
            arg_type=get_enum_type(app_routing_nginx_configs),
            options_list=["--app-routing-default-nginx-controller", "--ardnc"]
        )
        # nodepool paramerters
        c.argument(
            "nodepool_name",
            default="nodepool1",
            help="Node pool name, upto 12 alphanumeric characters",
            validator=validate_nodepool_name,
        )
        c.argument(
            "node_vm_size",
            options_list=["--node-vm-size", "-s"],
            completer=get_vm_size_completion_list,
        )
        c.argument(
            "os_sku",
            arg_type=get_enum_type(node_os_skus_create),
            validator=validate_os_sku,
        )
        c.argument("snapshot_id", validator=validate_snapshot_id)
        c.argument("vnet_subnet_id", validator=validate_vnet_subnet_id)
        c.argument("pod_subnet_id", validator=validate_pod_subnet_id)
        c.argument(
            "pod_ip_allocation_mode",
            arg_type=get_enum_type(pod_ip_allocation_modes),
            validator=validate_pod_ip_allocation_mode,
        )
        c.argument("enable_node_public_ip", action="store_true")
        c.argument("node_public_ip_prefix_id")
        c.argument("enable_cluster_autoscaler", action="store_true")
        c.argument("min_count", type=int, validator=validate_nodes_count)
        c.argument("max_count", type=int, validator=validate_nodes_count)
        c.argument(
            "nodepool_tags",
            nargs="*",
            validator=validate_nodepool_tags,
            help='space-separated tags: key[=value] [key[=value] ...]. Use "" to clear existing tags.',
        )
        c.argument(
            "nodepool_labels",
            nargs="*",
            validator=validate_nodepool_labels,
            help=(
                "space-separated labels: key[=value] [key[=value] ...]. "
                "See https://aka.ms/node-labels for syntax of labels."
            ),
        )
        c.argument("nodepool_taints", validator=validate_nodepool_taints)
        c.argument(
            "nodepool_initialization_taints",
            options_list=["--nodepool-initialization-taints", "--node-init-taints"],
            is_preview=True,
            validator=validate_nodepool_taints,
            help=(
                "Comma-separated taints: <key1>=<value1>:<effect1>,<key2>=<value2>:<effect2>. "
                "Pass \"\" to clear existing taints."
            ),
        )
        c.argument("node_osdisk_type", arg_type=get_enum_type(node_os_disk_types))
        c.argument("node_osdisk_size", type=int)
        c.argument("max_pods", type=int, options_list=["--max-pods", "-m"])
        c.argument("vm_set_type", validator=validate_vm_set_type)
        c.argument(
            "enable_vmss",
            action="store_true",
            help="To be deprecated. Use vm_set_type instead.",
            deprecate_info=c.deprecate(redirect="--vm-set-type", hide=True),
        )
        c.argument(
            "zones",
            zones_type,
            options_list=["--zones", "-z"],
            help="Space-separated list of availability zones where agent nodes will be placed.",
        )
        c.argument("ppg")
        c.argument("enable_encryption_at_host", action="store_true")
        c.argument("enable_ultra_ssd", action="store_true")
        c.argument("enable_fips_image", action="store_true")
        c.argument("kubelet_config")
        c.argument("linux_os_config")
        c.argument("host_group_id", validator=validate_host_group_id)
        c.argument(
            "gpu_instance_profile", arg_type=get_enum_type(gpu_instance_profiles)
        )
        # misc
        c.argument(
            "yes",
            options_list=["--yes", "-y"],
            help="Do not prompt for confirmation.",
            action="store_true",
        )
        c.argument("aks_custom_headers")
        # extensions
        # managed cluster
        c.argument("ip_families")
        c.argument("pod_cidrs")
        c.argument("service_cidrs")
        c.argument("load_balancer_managed_outbound_ipv6_count", type=int)
        c.argument("enable_pod_identity", action="store_true")
        c.argument("enable_pod_identity_with_kubenet", action="store_true")
        c.argument("enable_workload_identity", action="store_true")
        c.argument("enable_image_cleaner", action="store_true")
        c.argument(
            "enable_azure_service_mesh",
            options_list=["--enable-azure-service-mesh", "--enable-asm"],
            action="store_true",
        )
        c.argument("revision", validator=validate_azure_service_mesh_revision)
        c.argument("image_cleaner_interval_hours", type=int)
        c.argument(
            "cluster_snapshot_id",
            validator=validate_cluster_snapshot_id,
            is_preview=True,
        )
        c.argument(
            "enable_apiserver_vnet_integration", action="store_true", is_preview=True
        )
        c.argument(
            "apiserver_subnet_id",
            validator=validate_apiserver_subnet_id,
            is_preview=True,
        )
        c.argument(
            "dns_zone_resource_id",
            deprecate_info=c.deprecate(
                target="--dns-zone-resource-id",
                redirect="--dns-zone-resource-ids",
                hide=True,
            ),
        )
        c.argument("dns_zone_resource_ids", is_preview=True)
        c.argument('disable_run_command', action='store_true')
        c.argument("enable_keda", action="store_true", is_preview=True)
        c.argument(
            "enable_vpa",
            action="store_true",
            is_preview=True,
            help="enable vertical pod autoscaler for cluster",
        )
        c.argument(
            "enable_optimized_addon_scaling",
            action="store_true",
            is_preview=True,
            help="enable optimized addon scaling for cluster",
        )
        c.argument(
            "enable_cilium_dataplane",
            action="store_true",
            is_preview=True,
            deprecate_info=c.deprecate(
                target="--enable-cilium-dataplane",
                redirect="--network-dataplane",
                hide=True,
            ),
        )
        c.argument(
            "enable_acns",
            action="store_true",
        )
        c.argument(
            "disable_acns_observability",
            action="store_true",
        )
        c.argument(
            "disable_acns_security",
            action="store_true",
        )
        c.argument(
            "acns_advanced_networkpolicies",
            is_preview=True,
            arg_type=get_enum_type(advanced_networkpolicies),
        )
        c.argument(
            "acns_transit_encryption_type",
            is_preview=True,
            arg_type=get_enum_type(transit_encryption_types),
            help="Specify the transit encryption type for ACNS. Available values are 'None' and 'WireGuard'.",
        )
        c.argument(
            "enable_retina_flow_logs",
            action="store_true",
        )
        c.argument(
            "custom_ca_trust_certificates",
            options_list=["--custom-ca-trust-certificates", "--ca-certs"],
            is_preview=True,
            help="path to file containing list of new line separated CAs",
        )
        # nodepool
        c.argument("crg_id", validator=validate_crg_id, is_preview=True)
        # no validation for aks create because it already only supports Linux.
        c.argument("message_of_the_day")
        c.argument(
            "workload_runtime",
            arg_type=get_enum_type(workload_runtimes),
            default=CONST_WORKLOAD_RUNTIME_OCI_CONTAINER,
        )
        # no validation for aks create because it already only supports Linux.
        c.argument("enable_custom_ca_trust", action="store_true")
        c.argument(
            "nodepool_allowed_host_ports",
            validator=validate_allowed_host_ports,
            is_preview=True,
            help="allowed host ports for agentpool",
        )
        c.argument(
            "nodepool_asg_ids",
            validator=validate_application_security_groups,
            is_preview=True,
            help="application security groups for agentpool",
        )
        c.argument(
            "node_public_ip_tags",
            arg_type=tags_type,
            validator=validate_node_public_ip_tags,
            help="space-separated tags: key[=value] [key[=value] ...].",
        )
        c.argument(
            "safeguards_level",
            arg_type=get_enum_type(safeguards_levels),
            is_preview=True,
        )
        c.argument(
            "safeguards_version",
            type=str,
            help="The deployment safeguards version",
            is_preview=True,
        )
        c.argument(
            "safeguards_excluded_ns",
            type=str,
            is_preview=True
        )
        # azure monitor profile
        c.argument(
            "enable_azuremonitormetrics",
            action="store_true",
            deprecate_info=c.deprecate(
                target="--enable-azuremonitormetrics",
                redirect="--enable-azure-monitor-metrics",
                hide=True,
            ),
        )
        c.argument("enable_azure_monitor_metrics", action="store_true")
        c.argument(
            "azure_monitor_workspace_resource_id",
            validator=validate_azuremonitorworkspaceresourceid,
        )
        c.argument("ksm_metric_labels_allow_list")
        c.argument("ksm_metric_annotations_allow_list")
        c.argument("grafana_resource_id", validator=validate_grafanaresourceid)
        c.argument("enable_windows_recording_rules", action="store_true")
        c.argument("enable_azure_monitor_app_monitoring", is_preview=True, action="store_true")
        c.argument("enable_cost_analysis", action="store_true")
        c.argument('enable_ai_toolchain_operator', is_preview=True, action='store_true')
        # azure container storage
        c.argument(
            "enable_azure_container_storage",
            arg_type=get_enum_type(storage_pool_types),
            help="enable azure container storage and define storage pool type",
        )
        c.argument(
            "storage_pool_name",
            help="set storage pool name for azure container storage",
        )
        c.argument(
            "storage_pool_size",
            help="set storage pool size for azure container storage",
        )
        c.argument(
            "storage_pool_sku",
            arg_type=get_enum_type(storage_pool_skus),
            help="set azure disk type storage pool sku for azure container storage",
        )
        c.argument(
            "storage_pool_option",
            arg_type=get_enum_type(storage_pool_options),
            help="set ephemeral disk storage pool option for azure container storage",
        )
        c.argument(
            "ephemeral_disk_volume_type",
            arg_type=get_enum_type(ephemeral_disk_volume_types),
            help="set ephemeral disk volume type for azure container storage",
        )
        c.argument(
            "ephemeral_disk_nvme_perf_tier",
            arg_type=get_enum_type(ephemeral_disk_nvme_perf_tiers),
            help="set ephemeral disk volume type for azure container storage",
        )
        c.argument(
            "node_provisioning_mode",
            is_preview=True,
            arg_type=get_enum_type(node_provisioning_modes),
            help=(
                'Set the node provisioning mode of the cluster. Valid values are "Auto" and "Manual". '
                'For more information on "Auto" mode see aka.ms/aks/nap.'
            )
        )
        c.argument(
            "node_provisioning_default_pools",
            is_preview=True,
            arg_type=get_enum_type(node_provisioning_default_pools),
            help=(
                'The set of default Karpenter NodePools configured for node provisioning. '
                'Valid values are "Auto" and "None". Auto: A standard set of Karpenter NodePools are provisioned. '
                'None: No Karpenter NodePools are provisioned. '
                'WARNING: Changing this from Auto to None on an existing cluster will cause the default Karpenter '
                'NodePools to be deleted, which will in turn drain and delete the nodes associated with those pools. '
                'It is strongly recommended to not do this unless there are idle nodes ready to take the pods evicted '
                'by that action.'
            )
        )
        # in creation scenario, use "localuser" as default
        c.argument(
            'ssh_access',
            arg_type=get_enum_type(ssh_accesses),
            default=CONST_SSH_ACCESS_LOCALUSER,
            is_preview=True,
        )
        # trusted launch
        c.argument(
            "enable_secure_boot",
            is_preview=True,
            action="store_true"
        )
        c.argument(
            "enable_vtpm",
            is_preview=True,
            action="store_true"
        )
        c.argument("enable_static_egress_gateway", is_preview=True, action="store_true")

        c.argument(
            "cluster_service_load_balancer_health_probe_mode",
            is_preview=True,
            arg_type=get_enum_type(health_probe_modes),
        )
        c.argument("if_match")
        c.argument("if_none_match")
        # virtual machines
        c.argument("vm_sizes", is_preview=True)
        c.argument("enable_imds_restriction", action="store_true", is_preview=True)
        c.argument("enable_managed_system_pool", action="store_true", is_preview=True)

    with self.argument_context("aks update") as c:
        # managed cluster paramerters
        c.argument("disable_local_accounts", action="store_true")
        c.argument("enable_local_accounts", action="store_true")
        c.argument(
            "load_balancer_sku",
            arg_type=get_enum_type([CONST_LOAD_BALANCER_SKU_STANDARD]),
            validator=validate_load_balancer_sku,
        )
        c.argument("load_balancer_managed_outbound_ip_count", type=int)
        c.argument(
            "load_balancer_outbound_ips", validator=validate_load_balancer_outbound_ips
        )
        c.argument(
            "load_balancer_outbound_ip_prefixes",
            validator=validate_load_balancer_outbound_ip_prefixes,
        )
        c.argument(
            "load_balancer_outbound_ports",
            type=int,
            validator=validate_load_balancer_outbound_ports,
        )
        c.argument(
            "load_balancer_idle_timeout",
            type=int,
            validator=validate_load_balancer_idle_timeout,
        )
        c.argument(
            "load_balancer_backend_pool_type",
            validator=validate_load_balancer_backend_pool_type,
        )
        c.argument(
            "nrg_lockdown_restriction_level",
            arg_type=get_enum_type(nrg_lockdown_restriction_levels),
        )
        c.argument(
            "nat_gateway_managed_outbound_ip_count",
            type=int,
            validator=validate_nat_gateway_managed_outbound_ip_count,
        )
        c.argument(
            "nat_gateway_idle_timeout",
            type=int,
            validator=validate_nat_gateway_idle_timeout,
        )
        c.argument("network_dataplane", arg_type=get_enum_type(network_dataplanes))
        c.argument("network_policy")
        c.argument("network_plugin", arg_type=get_enum_type(network_plugins))
        c.argument("ip_families")
        c.argument("kube_proxy_config")
        c.argument(
            "auto_upgrade_channel", arg_type=get_enum_type(auto_upgrade_channels)
        )
        c.argument(
            "node_os_upgrade_channel", arg_type=get_enum_type(node_os_upgrade_channels)
        )
        c.argument(
            "disable_force_upgrade",
            action="store_true",
            validator=validate_force_upgrade_disable_and_enable_parameters,
        )
        c.argument(
            "enable_force_upgrade",
            action="store_true",
            validator=validate_force_upgrade_disable_and_enable_parameters,
        )
        c.argument("upgrade_override_until", is_preview=True)
        c.argument(
            "cluster_autoscaler_profile",
            nargs="+",
            options_list=["--cluster-autoscaler-profile", "--ca-profile"],
            help=(
                "Space-separated list of key=value pairs for configuring cluster autoscaler. "
                "Pass an empty string to clear the profile."
            ),
        )
        c.argument(
            "sku", is_preview=True, arg_type=get_enum_type(sku_names)
        )
        c.argument(
            "tier", arg_type=get_enum_type(sku_tiers), validator=validate_sku_tier
        )
        c.argument("api_server_authorized_ip_ranges", validator=validate_ip_ranges)
        c.argument("enable_public_fqdn", action="store_true")
        c.argument("disable_public_fqdn", action="store_true")
        c.argument("enable_managed_identity", action="store_true")
        c.argument("assign_identity", validator=validate_assign_identity)
        c.argument(
            "assign_kubelet_identity", validator=validate_assign_kubelet_identity
        )
        c.argument("enable_aad", action="store_true")
        c.argument("enable_azure_rbac", action="store_true")
        c.argument("disable_azure_rbac", action="store_true")
        c.argument("aad_tenant_id")
        c.argument("aad_admin_group_object_ids")
        c.argument("enable_oidc_issuer", action="store_true")
        c.argument("k8s_support_plan", arg_type=get_enum_type(k8s_support_plans))
        c.argument("windows_admin_password")
        c.argument("enable_ahub")
        c.argument("disable_ahub")
        c.argument("enable_windows_gmsa", action="store_true")
        c.argument("gmsa_dns_server")
        c.argument("gmsa_root_domain_name")
        c.argument("attach_acr", acr_arg_type, validator=validate_acr)
        c.argument("detach_acr", acr_arg_type, validator=validate_acr)
        c.argument(
            "disable_defender",
            action="store_true",
            validator=validate_defender_disable_and_enable_parameters,
        )
        c.argument("enable_defender", action="store_true")
        c.argument("defender_config", validator=validate_defender_config_parameter)
        c.argument("enable_disk_driver", action="store_true")
        c.argument("disk_driver_version", arg_type=get_enum_type(disk_driver_versions))
        c.argument("disable_disk_driver", action="store_true")
        c.argument("enable_file_driver", action="store_true")
        c.argument("disable_file_driver", action="store_true")
        c.argument("enable_blob_driver", action="store_true")
        c.argument("disable_blob_driver", action="store_true")
        c.argument("enable_snapshot_controller", action="store_true")
        c.argument("disable_snapshot_controller", action="store_true")
        c.argument("enable_azure_keyvault_kms", action="store_true")
        c.argument("disable_azure_keyvault_kms", action="store_true")
        c.argument(
            "azure_keyvault_kms_key_id", validator=validate_azure_keyvault_kms_key_id
        )
        c.argument(
            "azure_keyvault_kms_key_vault_network_access",
            arg_type=get_enum_type(keyvault_network_access_types),
        )
        c.argument(
            "azure_keyvault_kms_key_vault_resource_id",
            validator=validate_azure_keyvault_kms_key_vault_resource_id,
        )
        c.argument("http_proxy_config")
        c.argument(
            "bootstrap_artifact_source",
            arg_type=get_enum_type(bootstrap_artifact_source_types),
            is_preview=True,
        )
        c.argument(
            "bootstrap_container_registry_resource_id",
            validator=validate_bootstrap_container_registry_resource_id,
            is_preview=True,
        )
        # addons
        c.argument("enable_secret_rotation", action="store_true")
        c.argument("disable_secret_rotation", action="store_true")
        c.argument("rotation_poll_interval")
        # nodepool paramerters
        c.argument(
            "enable_cluster_autoscaler",
            options_list=["--enable-cluster-autoscaler", "-e"],
            action="store_true",
        )
        c.argument(
            "disable_cluster_autoscaler",
            options_list=["--disable-cluster-autoscaler", "-d"],
            action="store_true",
        )
        c.argument(
            "update_cluster_autoscaler",
            options_list=["--update-cluster-autoscaler", "-u"],
            action="store_true",
        )
        c.argument("min_count", type=int, validator=validate_nodes_count)
        c.argument("max_count", type=int, validator=validate_nodes_count)
        c.argument(
            "nodepool_labels",
            nargs="*",
            validator=validate_nodepool_labels,
            help=(
                "space-separated labels: key[=value] [key[=value] ...]. "
                "See https://aka.ms/node-labels for syntax of labels."
            )
        )
        c.argument("nodepool_taints", validator=validate_nodepool_taints)
        c.argument(
            "nodepool_initialization_taints",
            options_list=["--nodepool-initialization-taints", "--node-init-taints"],
            is_preview=True,
            validator=validate_nodepool_taints,
            help=(
                "Comma-separated taints: <key1>=<value1>:<effect1>,<key2>=<value2>:<effect2>. "
                "Pass \"\" to clear existing taints."
            ),
        )
        # misc
        c.argument(
            "yes",
            options_list=["--yes", "-y"],
            help="Do not prompt for confirmation.",
            action="store_true",
        )
        c.argument("aks_custom_headers")
        c.argument("if_match")
        c.argument("if_none_match")
        # extensions
        # managed cluster
        c.argument(
            "ssh_key_value",
            type=file_type,
            completer=FilesCompleter(),
            validator=validate_ssh_key_for_update,
        )
        c.argument("load_balancer_managed_outbound_ipv6_count", type=int)
        c.argument("outbound_type", arg_type=get_enum_type(outbound_types))
        c.argument("enable_pod_identity", action="store_true")
        c.argument("enable_pod_identity_with_kubenet", action="store_true")
        c.argument("disable_pod_identity", action="store_true")
        c.argument("enable_workload_identity", action="store_true")
        c.argument("disable_workload_identity", action="store_true")
        c.argument("enable_image_cleaner", action="store_true")
        c.argument(
            "disable_image_cleaner",
            action="store_true",
            validator=validate_image_cleaner_enable_disable_mutually_exclusive,
        )
        c.argument("image_cleaner_interval_hours", type=int)
        c.argument("disable_image_integrity", action="store_true", is_preview=True)
        c.argument(
            "enable_apiserver_vnet_integration", action="store_true", is_preview=True
        )
        c.argument(
            "apiserver_subnet_id",
            validator=validate_apiserver_subnet_id,
            is_preview=True,
        )
        c.argument('enable_run_command', action='store_true')
        c.argument('disable_run_command', action='store_true')
        c.argument("enable_keda", action="store_true", is_preview=True)
        c.argument("disable_keda", action="store_true", is_preview=True)
        c.argument(
            "enable_private_cluster",
            action="store_true",
            is_preview=True,
            help="enable private cluster for apiserver vnet integration",
        )
        c.argument(
            "disable_private_cluster",
            action="store_true",
            is_preview=True,
            help="disable private cluster for apiserver vnet integration",
        )
        c.argument("private_dns_zone", is_preview=True)
        c.argument(
            "enable_azuremonitormetrics",
            action="store_true",
            deprecate_info=c.deprecate(
                target="--enable-azuremonitormetrics",
                redirect="--enable-azure-monitor-metrics",
                hide=True,
            ),
        )
        c.argument("enable_azure_monitor_metrics", action="store_true")
        c.argument(
            "azure_monitor_workspace_resource_id",
            validator=validate_azuremonitorworkspaceresourceid,
        )
        c.argument("ksm_metric_labels_allow_list")
        c.argument("ksm_metric_annotations_allow_list")
        c.argument("grafana_resource_id", validator=validate_grafanaresourceid)
        c.argument("enable_windows_recording_rules", action="store_true")
        c.argument(
            "disable_azuremonitormetrics",
            action="store_true",
            deprecate_info=c.deprecate(
                target="--disable-azuremonitormetrics",
                redirect="--disable-azure-monitor-metrics",
                hide=True,
            ),
        )
        c.argument("disable_azure_monitor_metrics", action="store_true")
        c.argument("enable_azure_monitor_app_monitoring", action="store_true", is_preview=True)
        c.argument("disable_azure_monitor_app_monitoring", action="store_true", is_preview=True)
        c.argument(
            "enable_vpa",
            action="store_true",
            is_preview=True,
            help="enable vertical pod autoscaler for cluster",
        )
        c.argument(
            "disable_vpa",
            action="store_true",
            is_preview=True,
            help="disable vertical pod autoscaler for cluster",
        )
        c.argument(
            "enable_optimized_addon_scaling",
            action="store_true",
            is_preview=True,
            help="enable optimized addon scaling for cluster",
        )
        c.argument(
            "disable_optimized_addon_scaling",
            action="store_true",
            is_preview=True,
            help="disable optimized addon scaling for cluster",
        )
        c.argument(
            "cluster_snapshot_id",
            validator=validate_cluster_snapshot_id,
            is_preview=True,
        )
        c.argument(
            "custom_ca_trust_certificates",
            options_list=["--custom-ca-trust-certificates", "--ca-certs"],
            validator=validate_custom_ca_trust_certificates,
            is_preview=True,
            help="path to file containing list of new line separated CAs",
        )
        c.argument(
            "safeguards_level",
            arg_type=get_enum_type(safeguards_levels),
            is_preview=True,
        )
        c.argument(
            "safeguards_version",
            help="The deployment safeguards version",
            is_preview=True
        )
        c.argument(
            "safeguards_excluded_ns",
            is_preview=True
        )
        c.argument(
            "enable_acns",
            action="store_true",
        )
        c.argument(
            "disable_acns",
            action="store_true",
        )
        c.argument(
            "disable_acns_observability",
            action="store_true",
        )
        c.argument(
            "disable_acns_security",
            action="store_true",
        )
        c.argument(
            "acns_advanced_networkpolicies",
            is_preview=True,
            arg_type=get_enum_type(advanced_networkpolicies),
        )
        c.argument(
            "acns_transit_encryption_type",
            is_preview=True,
            arg_type=get_enum_type(transit_encryption_types),
            help="Specify the transit encryption type for ACNS. Available values are 'None' and 'WireGuard'.",
        )
        c.argument(
            "enable_retina_flow_logs",
            action="store_true",
        )
        c.argument(
            "disable_retina_flow_logs",
            action="store_true",
        )
        c.argument("enable_cost_analysis", action="store_true")
        c.argument("disable_cost_analysis", action="store_true")
        c.argument('enable_ai_toolchain_operator', is_preview=True, action='store_true')
        c.argument('disable_ai_toolchain_operator', is_preview=True, action='store_true')
        # azure container storage
        c.argument(
            "enable_azure_container_storage",
            arg_type=get_enum_type(storage_pool_types),
            help="enable azure container storage and define storage pool type",
        )
        c.argument(
            "disable_azure_container_storage",
            arg_type=get_enum_type(disable_storage_pool_types),
            help="disable azure container storage or any one of the storage pool types",
        )
        c.argument(
            "storage_pool_name",
            help="set storage pool name for azure container storage",
        )
        c.argument(
            "storage_pool_size",
            help="set storage pool size for azure container storage",
        )
        c.argument(
            "storage_pool_sku",
            arg_type=get_enum_type(storage_pool_skus),
            help="set azure disk type storage pool sku for azure container storage",
        )
        c.argument(
            "storage_pool_option",
            arg_type=get_enum_type(disable_storage_pool_options),
            help="set ephemeral disk storage pool option for azure container storage",
        )
        c.argument(
            "azure_container_storage_nodepools",
            help="define the comma separated nodepool list to install azure container storage",
        )
        c.argument(
            "ephemeral_disk_volume_type",
            arg_type=get_enum_type(ephemeral_disk_volume_types),
            help="set ephemeral disk volume type for azure container storage",
        )
        c.argument(
            "ephemeral_disk_nvme_perf_tier",
            arg_type=get_enum_type(ephemeral_disk_nvme_perf_tiers),
            help="set ephemeral disk volume type for azure container storage",
        )
        c.argument(
            "node_provisioning_mode",
            is_preview=True,
            arg_type=get_enum_type(node_provisioning_modes),
            help=(
                'Set the node provisioning mode of the cluster. Valid values are "Auto" and "Manual". '
                'For more information on "Auto" mode see aka.ms/aks/nap.'
            )
        )
        c.argument(
            "node_provisioning_default_pools",
            is_preview=True,
            arg_type=get_enum_type(node_provisioning_default_pools),
            help=(
                'The set of default Karpenter NodePools configured for node provisioning. '
                'Valid values are "Auto" and "None". Auto: A standard set of Karpenter NodePools are provisioned. '
                'None: No Karpenter NodePools are provisioned. '
                'WARNING: Changing this from Auto to None on an existing cluster will cause the default Karpenter '
                'NodePools to be deleted, which will in turn drain and delete the nodes associated with those pools. '
                'It is strongly recommended to not do this unless there are idle nodes ready to take the pods evicted '
                'by that action.'
            )
        )
        c.argument('enable_static_egress_gateway', is_preview=True, action='store_true')
        c.argument('disable_static_egress_gateway', is_preview=True, action='store_true')
        c.argument("enable_imds_restriction", action="store_true", is_preview=True)
        c.argument("disable_imds_restriction", action="store_true", is_preview=True)

        c.argument(
            "cluster_service_load_balancer_health_probe_mode",
            is_preview=True,
            arg_type=get_enum_type(health_probe_modes),
        )

        c.argument('migrate_vmas_to_vms', is_preview=True, action='store_true')
        c.argument("disable_http_proxy", action="store_true", is_preview=True)
        c.argument("enable_http_proxy", action="store_true", is_preview=True)

    with self.argument_context("aks upgrade") as c:
        c.argument("kubernetes_version", completer=get_k8s_upgrades_completion_list)
        c.argument(
            "cluster_snapshot_id",
            validator=validate_cluster_snapshot_id,
            is_preview=True,
        )
        c.argument(
            "yes",
            options_list=["--yes", "-y"],
            help="Do not prompt for confirmation.",
            action="store_true",
        )
        c.argument('enable_force_upgrade', action='store_true')
        c.argument(
            'disable_force_upgrade', action='store_true',
            validator=validate_force_upgrade_disable_and_enable_parameters
        )
        c.argument('upgrade_override_until')

    with self.argument_context("aks scale") as c:
        c.argument(
            "nodepool_name",
            help="Node pool name, upto 12 alphanumeric characters",
            validator=validate_nodepool_name,
        )

    # managed namespace
    with self.argument_context("aks namespace") as c:
        c.argument("cluster_name", help="The cluster name.")
        c.argument(
            "name",
            validator=validate_namespace_name,
            help="The managed namespace name.",
        )

    for scope in [
        "aks namespace add",
        "aks namespace update",
    ]:
        with self.argument_context(scope) as c:
            c.argument("tags", tags_type, help="The tags to set to the managed namespace")
            c.argument("labels", nargs="*", help="Labels set to the managed namespace")
            c.argument(
                "annotations",
                nargs="*",
                help="Annotations set to the managed namespace",
            )
            c.argument("cpu_request", validator=validate_resource_quota)
            c.argument("cpu_limit", validator=validate_resource_quota)
            c.argument("memory_request", validator=validate_resource_quota)
            c.argument("memory_limit", validator=validate_resource_quota)
            c.argument("ingress_policy", arg_type=get_enum_type(network_policy_rule))
            c.argument("egress_policy", arg_type=get_enum_type(network_policy_rule))
            c.argument("adoption_policy", arg_type=get_enum_type(adoption_policy))
            c.argument("delete_policy", arg_type=get_enum_type(delete_policy))
            c.argument("aks_custom_headers")
            c.argument("no_wait", help="Do not wait for the long-running operation to finish")

    with self.argument_context("aks namespace get-credentials") as c:
        c.argument(
            "context_name",
            options_list=["--context"],
            help="If specified, overwrite the default context name.",
        )
        c.argument(
            "path",
            options_list=["--file", "-f"],
            type=file_type,
            completer=FilesCompleter(),
            default=os.path.join(os.path.expanduser("~"), ".kube", "config"),
        )

    with self.argument_context("aks nodepool") as c:
        c.argument("cluster_name", help="The cluster name.")
        c.argument(
            "nodepool_name",
            options_list=["--nodepool-name", "--name", "-n"],
            validator=validate_nodepool_name,
            help="The node pool name.",
        )

    with self.argument_context("aks nodepool wait") as c:
        c.argument(
            "resource_name", options_list=["--cluster-name"], help="The cluster name."
        )
        # the option name '--agent-pool-name' is depracated, left for compatibility only
        c.argument(
            "agent_pool_name",
            options_list=[
                "--nodepool-name",
                "--name",
                "-n",
                c.deprecate(
                    target="--agent-pool-name", redirect="--nodepool-name", hide=True
                ),
            ],
            validator=validate_agent_pool_name,
            help="The node pool name.",
        )

    with self.argument_context("aks nodepool add") as c:
        c.argument(
            "node_vm_size",
            options_list=["--node-vm-size", "-s"],
            completer=get_vm_size_completion_list,
        )
        c.argument("os_type")
        c.argument(
            "os_sku", arg_type=get_enum_type(node_os_skus), validator=validate_os_sku
        )
        c.argument("snapshot_id", validator=validate_snapshot_id)
        c.argument("vnet_subnet_id", validator=validate_vnet_subnet_id)
        c.argument("pod_subnet_id", validator=validate_pod_subnet_id)
        c.argument(
            "pod_ip_allocation_mode",
            arg_type=get_enum_type(pod_ip_allocation_modes),
            validator=validate_pod_ip_allocation_mode,
        )
        c.argument("enable_node_public_ip", action="store_true")
        c.argument("node_public_ip_prefix_id")
        c.argument(
            "enable_cluster_autoscaler",
            options_list=["--enable-cluster-autoscaler", "-e"],
            action="store_true",
        )
        c.argument("min_count", type=int, validator=validate_nodes_count)
        c.argument("max_count", type=int, validator=validate_nodes_count)
        c.argument(
            "priority",
            arg_type=get_enum_type(node_priorities),
            validator=validate_priority,
        )
        c.argument(
            "eviction_policy",
            arg_type=get_enum_type(node_eviction_policies),
            validator=validate_eviction_policy,
        )
        c.argument("spot_max_price", type=float, validator=validate_spot_max_price)
        c.argument("labels", nargs="*", validator=validate_nodepool_labels)
        c.argument("tags", tags_type)
        c.argument("node_taints", validator=validate_nodepool_taints)
        c.argument("node_osdisk_type", arg_type=get_enum_type(node_os_disk_types))
        c.argument("node_osdisk_size", type=int)
        c.argument("max_surge", validator=validate_max_surge)
        c.argument("drain_timeout", type=int)
        c.argument("node_soak_duration", type=int)
        c.argument("undrainable_node_behavior")
        c.argument("max_unavailable", validator=validate_max_unavailable)
        c.argument("max_blocked_nodes", validator=validate_max_blocked_nodes)
        c.argument("mode", arg_type=get_enum_type(node_mode_types))
        c.argument("scale_down_mode", arg_type=get_enum_type(scale_down_modes))
        c.argument("max_pods", type=int, options_list=["--max-pods", "-m"])
        c.argument(
            "zones",
            zones_type,
            options_list=["--zones", "-z"],
            help="Space-separated list of availability zones where agent nodes will be placed.",
        )
        c.argument("ppg")
        c.argument("vm_set_type", validator=validate_vm_set_type)
        c.argument("enable_encryption_at_host", action="store_true")
        c.argument("enable_ultra_ssd", action="store_true")
        c.argument("enable_fips_image", action="store_true")
        c.argument("kubelet_config")
        c.argument("linux_os_config")
        c.argument("host_group_id", validator=validate_host_group_id)
        c.argument(
            "gpu_instance_profile", arg_type=get_enum_type(gpu_instance_profiles)
        )
        # misc
        c.argument("aks_custom_headers")
        # extensions
        c.argument("crg_id", validator=validate_crg_id, is_preview=True)
        c.argument("message_of_the_day", validator=validate_message_of_the_day)
        c.argument(
            "workload_runtime",
            arg_type=get_enum_type(workload_runtimes),
            default=CONST_WORKLOAD_RUNTIME_OCI_CONTAINER,
        )
        c.argument(
            "enable_custom_ca_trust",
            action="store_true",
            validator=validate_enable_custom_ca_trust,
        )
        c.argument(
            "disable_windows_outbound_nat",
            action="store_true",
            validator=validate_disable_windows_outbound_nat,
        )
        c.argument(
            "allowed_host_ports", validator=validate_allowed_host_ports, is_preview=True
        )
        c.argument(
            "asg_ids", validator=validate_application_security_groups, is_preview=True
        )
        c.argument(
            "enable_artifact_streaming",
            action="store_true",
            validator=validate_artifact_streaming,
            is_preview=True,
        )
        c.argument(
            "node_public_ip_tags",
            arg_type=tags_type,
            validator=validate_node_public_ip_tags,
            help="space-separated tags: key[=value] [key[=value] ...].",
        )
        c.argument(
            "skip_gpu_driver_install",
            action="store_true",
            is_preview=True,
            deprecate_info=c.deprecate(
                target="--skip-gpu-driver-install",
                redirect="--gpu-driver",
                hide=True
            )
        )
        c.argument(
            "gpu_driver",
            arg_type=get_enum_type(gpu_driver_install_modes)
        )
        c.argument(
            "driver_type",
            arg_type=get_enum_type(gpu_driver_types),
            is_preview=True,
        )
        # in creation scenario, use "localuser" as default
        c.argument(
            'ssh_access',
            arg_type=get_enum_type(ssh_accesses),
            default=CONST_SSH_ACCESS_LOCALUSER,
            is_preview=True,
        )
        # trusted launch
        c.argument(
            "enable_secure_boot",
            is_preview=True,
            action="store_true"
        )
        c.argument(
            "enable_vtpm",
            is_preview=True,
            action="store_true"
        )
        c.argument("if_match")
        c.argument("if_none_match")
        c.argument(
            "gateway_prefix_size",
            type=int,
            validator=validate_gateway_prefix_size,
            is_preview=True,
        )
        # virtual machines
        c.argument("vm_sizes", is_preview=True)
        # local DNS
        c.argument(
            'localdns_config',
            help='Path to a JSON file to configure the local DNS profile for a new nodepool.'
        )

    with self.argument_context("aks nodepool update") as c:
        c.argument(
            "enable_cluster_autoscaler",
            options_list=["--enable-cluster-autoscaler", "-e"],
            action="store_true",
        )
        c.argument(
            "disable_cluster_autoscaler",
            options_list=["--disable-cluster-autoscaler", "-d"],
            action="store_true",
        )
        c.argument(
            "update_cluster_autoscaler",
            options_list=["--update-cluster-autoscaler", "-u"],
            action="store_true",
        )
        c.argument("min_count", type=int, validator=validate_nodes_count)
        c.argument("max_count", type=int, validator=validate_nodes_count)
        c.argument("labels", nargs="*", validator=validate_nodepool_labels)
        c.argument("tags", tags_type)
        c.argument("node_taints", validator=validate_nodepool_taints)
        c.argument("max_surge", validator=validate_max_surge)
        c.argument("drain_timeout", type=int)
        c.argument("node_soak_duration", type=int)
        c.argument("undrainable_node_behavior")
        c.argument("max_unavailable", validator=validate_max_unavailable)
        c.argument("max_blocked_nodes", validator=validate_max_blocked_nodes)
        c.argument("mode", arg_type=get_enum_type(node_mode_types))
        c.argument("scale_down_mode", arg_type=get_enum_type(scale_down_modes))
        # extensions
        c.argument(
            "enable_custom_ca_trust",
            action="store_true",
            validator=validate_enable_custom_ca_trust,
        )
        c.argument(
            "disable_custom_ca_trust",
            options_list=["--disable-custom-ca-trust", "--dcat"],
            action="store_true",
        )
        c.argument(
            "allowed_host_ports", validator=validate_allowed_host_ports, is_preview=True
        )
        c.argument(
            "asg_ids", validator=validate_application_security_groups, is_preview=True
        )
        c.argument(
            "enable_artifact_streaming",
            action="store_true",
            validator=validate_artifact_streaming,
            is_preview=True,
        )
        c.argument(
            "os_sku",
            arg_type=get_enum_type(node_os_skus_update),
            validator=validate_os_sku,
        )
        # In update scenario, use emtpy str as default.
        c.argument('ssh_access', arg_type=get_enum_type(ssh_accesses), is_preview=True)
        c.argument('yes', options_list=['--yes', '-y'], help='Do not prompt for confirmation.', action='store_true')
        # trusted launch
        c.argument(
            "enable_secure_boot",
            is_preview=True,
            action="store_true"
        )
        c.argument(
            "disable_secure_boot",
            is_preview=True,
            action="store_true"
        )
        c.argument(
            "enable_vtpm",
            is_preview=True,
            action="store_true"
        )
        c.argument(
            "disable_vtpm",
            is_preview=True,
            action="store_true"
        )
        c.argument("if_match")
        c.argument("if_none_match")
        c.argument(
            "enable_fips_image",
            action="store_true"
        )
        c.argument(
            "disable_fips_image",
            action="store_true"
        )
        # local DNS
        c.argument(
            'localdns_config',
            help='Path to a JSON file to configure the local DNS profile for an existing nodepool.',
        )

    with self.argument_context("aks nodepool upgrade") as c:
        c.argument("max_surge", validator=validate_max_surge)
        c.argument("drain_timeout", type=int)
        c.argument("node_soak_duration", type=int)
        c.argument("undrainable_node_behavior")
        c.argument("max_unavailable", validator=validate_max_unavailable)
        c.argument("max_blocked_nodes", validator=validate_max_blocked_nodes)
        c.argument("snapshot_id", validator=validate_snapshot_id)
        c.argument(
            "yes",
            options_list=["--yes", "-y"],
            help="Do not prompt for confirmation.",
            action="store_true",
        )
        c.argument("aks_custom_headers")

    with self.argument_context("aks nodepool delete") as c:
        c.argument(
            "ignore_pod_disruption_budget",
            options_list=["--ignore-pod-disruption-budget", "-i"],
            action=get_three_state_flag(),
            is_preview=True,
            help="delete an AKS nodepool by ignoring PodDisruptionBudget setting",
        )
        c.argument("if_match")

    with self.argument_context("aks nodepool delete-machines") as c:
        c.argument(
            "machine_names",
            nargs="+",
            required=True,
            help="Space-separated machine names to delete.",
        )

    with self.argument_context("aks nodepool manual-scale add") as c:
        c.argument("vm_sizes", is_preview=True)

    with self.argument_context("aks nodepool manual-scale update") as c:
        c.argument("current_vm_sizes", is_preview=True)
        c.argument("vm_sizes", is_preview=True)

    with self.argument_context("aks nodepool manual-scale delete") as c:
        c.argument("current_vm_sizes", is_preview=True)

    with self.argument_context("aks machine") as c:
        c.argument("cluster_name", help="The cluster name.")
        c.argument(
            "nodepool_name",
            validator=validate_nodepool_name,
            help="The node pool name.",
        )

    with self.argument_context("aks machine show") as c:
        c.argument(
            "machine_name", help="to display specific information for all machines."
        )

    with self.argument_context("aks operation") as c:
        c.argument(
            "nodepool_name",
            required=False,
            validator=validate_nodepool_name,
            default="",
        )

    with self.argument_context("aks maintenanceconfiguration") as c:
        c.argument("cluster_name", help="The cluster name.")

    for scope in [
        "aks maintenanceconfiguration add",
        "aks maintenanceconfiguration update",
    ]:
        with self.argument_context(scope) as c:
            c.argument(
                "config_name", options_list=["--name", "-n"], help="The config name."
            )
            c.argument("config_file", help="The config json file.")
            c.argument(
                "weekday", help="Weekday on which maintenance can happen. e.g. Monday"
            )
            c.argument(
                "start_hour",
                type=int,
                help="Maintenance start hour of 1 hour window on the weekday. e.g. 1 means 1:00am - 2:00am",
            )
            c.argument(
                "schedule_type",
                arg_type=get_enum_type(schedule_types),
                help="Schedule type for non-default maintenance configuration.",
            )
            c.argument(
                "interval_days",
                type=int,
                help="The number of days between each set of occurrences for Daily schedule.",
            )
            c.argument(
                "interval_weeks",
                type=int,
                help="The number of weeks between each set of occurrences for Weekly schedule.",
            )
            c.argument(
                "interval_months",
                type=int,
                help=(
                    "The number of months between each set of occurrences for AbsoluteMonthly or "
                    "RelativeMonthly schedule."
                )
            )
            c.argument(
                "day_of_week",
                help="Specify on which day of the week the maintenance occurs for Weekly or RelativeMonthly schedule.",
            )
            c.argument(
                "day_of_month",
                help="Specify on which date of the month the maintenance occurs for AbsoluteMonthly schedule.",
            )
            c.argument(
                "week_index",
                arg_type=get_enum_type(week_indexes),
                help=(
                    "Specify on which instance of the weekday specified in --day-of-week "
                    "the maintenance occurs for RelativeMonthly schedule."
                )
            )
            c.argument(
                "duration_hours",
                options_list=["--duration"],
                type=int,
                help="The length of maintenance window. The value ranges from 4 to 24 hours.",
            )
            c.argument(
                "utc_offset",
                validator=validate_utc_offset,
                help="The UTC offset in format +/-HH:mm. e.g. -08:00 or +05:30.",
            )
            c.argument(
                "start_date",
                validator=validate_start_date,
                help="The date the maintenance window activates. e.g. 2023-01-01.",
            )
            c.argument(
                "start_time",
                validator=validate_start_time,
                help="The start time of the maintenance window. e.g. 09:30.",
            )

    for scope in [
        "aks maintenanceconfiguration show",
        "aks maintenanceconfiguration delete",
    ]:
        with self.argument_context(scope) as c:
            c.argument(
                "config_name", options_list=["--name", "-n"], help="The config name."
            )

    with self.argument_context("aks addon show") as c:
        c.argument("addon", options_list=["--addon", "-a"], validator=validate_addon)

    with self.argument_context("aks addon enable") as c:
        c.argument("addon", options_list=["--addon", "-a"], validator=validate_addon)
        c.argument("subnet_name", options_list=["--subnet-name", "-s"])
        c.argument("enable_sgxquotehelper", action="store_true")
        c.argument("osm_mesh_name", options_list=["--osm-mesh-name"])
        c.argument(
            "appgw_name", options_list=["--appgw-name"], arg_group="Application Gateway"
        )
        c.argument(
            "appgw_subnet_prefix",
            options_list=["--appgw-subnet-prefix"],
            arg_group="Application Gateway",
            deprecate_info=c.deprecate(redirect="--appgw-subnet-cidr", hide=True),
        )
        c.argument(
            "appgw_subnet_cidr",
            options_list=["--appgw-subnet-cidr"],
            arg_group="Application Gateway",
        )
        c.argument(
            "appgw_id", options_list=["--appgw-id"], arg_group="Application Gateway"
        )
        c.argument(
            "appgw_subnet_id",
            options_list=["--appgw-subnet-id"],
            arg_group="Application Gateway",
        )
        c.argument(
            "appgw_watch_namespace",
            options_list=["--appgw-watch-namespace"],
            arg_group="Application Gateway",
        )
        c.argument("enable_secret_rotation", action="store_true")
        c.argument("rotation_poll_interval")
        c.argument("workspace_resource_id")
        c.argument(
            "enable_msi_auth_for_monitoring",
            arg_type=get_three_state_flag(),
            is_preview=True,
        )
        c.argument("enable_syslog", arg_type=get_three_state_flag(), is_preview=True)
        c.argument("data_collection_settings", is_preview=True)
        c.argument("enable_high_log_scale_mode", arg_type=get_three_state_flag(), is_preview=True)
        c.argument("ampls_resource_id", is_preview=True)
        c.argument(
            "dns_zone_resource_id",
            deprecate_info=c.deprecate(
                target="--dns-zone-resource-id",
                redirect="--dns-zone-resource-ids",
                hide=True,
            ),
        )
        c.argument("dns_zone_resource_ids", is_preview=True)

    with self.argument_context("aks addon disable") as c:
        c.argument("addon", options_list=["--addon", "-a"], validator=validate_addon)

    with self.argument_context("aks addon update") as c:
        c.argument("addon", options_list=["--addon", "-a"], validator=validate_addon)
        c.argument("subnet_name", options_list=["--subnet-name", "-s"])
        c.argument("enable_sgxquotehelper", action="store_true")
        c.argument("osm_mesh_name", options_list=["--osm-mesh-name"])
        c.argument(
            "appgw_name", options_list=["--appgw-name"], arg_group="Application Gateway"
        )
        c.argument(
            "appgw_subnet_prefix",
            options_list=["--appgw-subnet-prefix"],
            arg_group="Application Gateway",
            deprecate_info=c.deprecate(redirect="--appgw-subnet-cidr", hide=True),
        )
        c.argument(
            "appgw_subnet_cidr",
            options_list=["--appgw-subnet-cidr"],
            arg_group="Application Gateway",
        )
        c.argument(
            "appgw_id", options_list=["--appgw-id"], arg_group="Application Gateway"
        )
        c.argument(
            "appgw_subnet_id",
            options_list=["--appgw-subnet-id"],
            arg_group="Application Gateway",
        )
        c.argument(
            "appgw_watch_namespace",
            options_list=["--appgw-watch-namespace"],
            arg_group="Application Gateway",
        )
        c.argument("enable_secret_rotation", action="store_true")
        c.argument("rotation_poll_interval")
        c.argument("workspace_resource_id")
        c.argument(
            "enable_msi_auth_for_monitoring",
            arg_type=get_three_state_flag(),
            is_preview=True,
        )
        c.argument("enable_syslog", arg_type=get_three_state_flag(), is_preview=True)
        c.argument("data_collection_settings", is_preview=True)
        c.argument("enable_high_log_scale_mode", arg_type=get_three_state_flag(), is_preview=True)
        c.argument("ampls_resource_id", is_preview=True)
        c.argument(
            "dns_zone_resource_id",
            deprecate_info=c.deprecate(
                target="--dns-zone-resource-id",
                redirect="--dns-zone-resource-ids",
                hide=True,
            ),
        )
        c.argument("dns_zone_resource_ids", is_preview=True)

    with self.argument_context("aks disable-addons") as c:
        c.argument("addons", options_list=["--addons", "-a"], validator=validate_addons)

    with self.argument_context("aks enable-addons") as c:
        c.argument("addons", options_list=["--addons", "-a"], validator=validate_addons)
        c.argument("subnet_name", options_list=["--subnet-name", "-s"])
        c.argument("enable_sgxquotehelper", action="store_true")
        c.argument("osm_mesh_name")
        c.argument("appgw_name", arg_group="Application Gateway")
        c.argument(
            "appgw_subnet_prefix",
            arg_group="Application Gateway",
            deprecate_info=c.deprecate(redirect="--appgw-subnet-cidr", hide=True),
        )
        c.argument("appgw_subnet_cidr", arg_group="Application Gateway")
        c.argument("appgw_id", arg_group="Application Gateway")
        c.argument("appgw_subnet_id", arg_group="Application Gateway")
        c.argument("appgw_watch_namespace", arg_group="Application Gateway")
        c.argument("enable_secret_rotation", action="store_true")
        c.argument("rotation_poll_interval")
        c.argument("workspace_resource_id")
        c.argument(
            "enable_msi_auth_for_monitoring",
            arg_type=get_three_state_flag(),
            is_preview=True,
        )
        c.argument("enable_syslog", arg_type=get_three_state_flag(), is_preview=True)
        c.argument("data_collection_settings", is_preview=True)
        c.argument("enable_high_log_scale_mode", arg_type=get_three_state_flag(), is_preview=True)
        c.argument("ampls_resource_id", is_preview=True)
        c.argument(
            "dns_zone_resource_id",
            deprecate_info=c.deprecate(
                target="--dns-zone-resource-id",
                redirect="--dns-zone-resource-ids",
                hide=True,
            ),
        )
        c.argument("dns_zone_resource_ids", is_preview=True)

    with self.argument_context("aks get-credentials") as c:
        c.argument("admin", options_list=["--admin", "-a"], default=False)
        c.argument(
            "context_name",
            options_list=["--context"],
            help="If specified, overwrite the default context name.",
        )
        c.argument(
            "user",
            options_list=["--user", "-u"],
            default="clusterUser",
            validator=validate_user,
        )
        c.argument(
            "path",
            options_list=["--file", "-f"],
            type=file_type,
            completer=FilesCompleter(),
            default=os.path.join(os.path.expanduser("~"), ".kube", "config"),
        )
        c.argument("public_fqdn", default=False, action="store_true")
        c.argument(
            "credential_format",
            options_list=["--format"],
            arg_type=get_enum_type(credential_formats),
        )

    with self.argument_context("aks pod-identity") as c:
        c.argument("cluster_name", help="The cluster name.")
        c.argument(
            "aks_custom_headers",
            help="Send custom headers. When specified, format should be Key1=Value1,Key2=Value2.",
        )

    with self.argument_context("aks pod-identity add") as c:
        c.argument(
            "identity_name",
            options_list=["--name", "-n"],
            default=None,
            required=False,
            help="The pod identity name. Generate if not specified.",
            validator=validate_pod_identity_resource_name(
                "identity_name", required=False
            ),
        )
        c.argument(
            "identity_namespace",
            options_list=["--namespace"],
            help="The pod identity namespace.",
        )
        c.argument(
            "identity_resource_id",
            options_list=["--identity-resource-id"],
            help="Resource id of the identity to use.",
        )
        c.argument(
            "binding_selector",
            options_list=["--binding-selector"],
            help="Optional binding selector to use.",
        )

    with self.argument_context("aks pod-identity delete") as c:
        c.argument(
            "identity_name",
            options_list=["--name", "-n"],
            default=None,
            required=True,
            help="The pod identity name.",
            validator=validate_pod_identity_resource_name(
                "identity_name", required=True
            ),
        )
        c.argument(
            "identity_namespace",
            options_list=["--namespace"],
            help="The pod identity namespace.",
        )

    with self.argument_context("aks pod-identity exception add") as c:
        c.argument(
            "exc_name",
            options_list=["--name", "-n"],
            default=None,
            required=False,
            help="The pod identity exception name. Generate if not specified.",
            validator=validate_pod_identity_resource_name("exc_name", required=False),
        )
        c.argument(
            "exc_namespace",
            options_list=["--namespace"],
            required=True,
            help="The pod identity exception namespace.",
            validator=validate_pod_identity_resource_namespace,
        )
        c.argument(
            "pod_labels",
            nargs="*",
            required=True,
            help="space-separated labels: key=value [key=value ...].",
            validator=validate_pod_identity_pod_labels,
        )

    with self.argument_context("aks pod-identity exception delete") as c:
        c.argument(
            "exc_name",
            options_list=["--name", "-n"],
            required=True,
            help="The pod identity exception name to remove.",
            validator=validate_pod_identity_resource_name("exc_name", required=True),
        )
        c.argument(
            "exc_namespace",
            options_list=["--namespace"],
            required=True,
            help="The pod identity exception namespace to remove.",
            validator=validate_pod_identity_resource_namespace,
        )

    with self.argument_context("aks pod-identity exception update") as c:
        c.argument(
            "exc_name",
            options_list=["--name", "-n"],
            required=True,
            help="The pod identity exception name to remove.",
            validator=validate_pod_identity_resource_name("exc_name", required=True),
        )
        c.argument(
            "exc_namespace",
            options_list=["--namespace"],
            required=True,
            help="The pod identity exception namespace to remove.",
            validator=validate_pod_identity_resource_namespace,
        )
        c.argument(
            "pod_labels",
            nargs="*",
            required=True,
            help="pod labels in key=value [key=value ...].",
            validator=validate_pod_identity_pod_labels,
        )

    for scope in ["aks nodepool snapshot create"]:
        with self.argument_context(scope) as c:
            c.argument(
                "snapshot_name",
                options_list=["--name", "-n"],
                required=True,
                help="The nodepool snapshot name.",
                validator=validate_snapshot_name,
            )
            c.argument("tags", tags_type)
            c.argument(
                "nodepool_id",
                required=True,
                help="The nodepool id.",
                validator=validate_nodepool_id,
            )
            c.argument("aks_custom_headers")

    with self.argument_context("aks nodepool snapshot update") as c:
        c.argument(
            "snapshot_name",
            options_list=["--name", "-n"],
            help="The nodepool snapshot name.",
            validator=validate_snapshot_name,
        )
        c.argument("tags", tags_type, help="The tags to set to the snapshot.")

    for scope in ["aks nodepool snapshot show", "aks nodepool snapshot delete"]:
        with self.argument_context(scope) as c:
            c.argument(
                "snapshot_name",
                options_list=["--name", "-n"],
                required=True,
                help="The nodepool snapshot name.",
                validator=validate_snapshot_name,
            )
            c.argument(
                "yes",
                options_list=["--yes", "-y"],
                help="Do not prompt for confirmation.",
                action="store_true",
            )

    for scope in ["aks snapshot create"]:
        with self.argument_context(scope) as c:
            c.argument(
                "snapshot_name",
                options_list=["--name", "-n"],
                required=True,
                help="The cluster snapshot name.",
                validator=validate_snapshot_name,
            )
            c.argument("tags", tags_type)
            c.argument(
                "cluster_id",
                required=True,
                validator=validate_cluster_id,
                help="The cluster id.",
            )
            c.argument("aks_custom_headers")

    for scope in ["aks snapshot show", "aks snapshot delete"]:
        with self.argument_context(scope) as c:
            c.argument(
                "snapshot_name",
                options_list=["--name", "-n"],
                required=True,
                help="The cluster snapshot name.",
                validator=validate_snapshot_name,
            )
            c.argument(
                "yes",
                options_list=["--yes", "-y"],
                help="Do not prompt for confirmation.",
                action="store_true",
            )

    with self.argument_context("aks mesh enable-ingress-gateway") as c:
        c.argument(
            "ingress_gateway_type", arg_type=get_enum_type(ingress_gateway_types)
        )

    with self.argument_context("aks mesh disable-ingress-gateway") as c:
        c.argument(
            "ingress_gateway_type", arg_type=get_enum_type(ingress_gateway_types)
        )

    with self.argument_context("aks mesh enable-egress-gateway") as c:
        c.argument(
            "istio_egressgateway_name",
            validator=validate_asm_egress_name,
            required=True,
            options_list=["--istio-egressgateway-name", "--istio-eg-gtw-name"]
        )
        c.argument(
            "istio_egressgateway_namespace",
            required=False,
            default=CONST_AZURE_SERVICE_MESH_DEFAULT_EGRESS_NAMESPACE,
            options_list=["--istio-egressgateway-namespace", "--istio-eg-gtw-ns"]
        )
        c.argument(
            "gateway_configuration_name",
            required=True,
            options_list=["--gateway-configuration-name", "--gtw-config-name"]
        )

    with self.argument_context("aks mesh disable-egress-gateway") as c:
        c.argument(
            "istio_egressgateway_name",
            validator=validate_asm_egress_name,
            required=True,
            options_list=["--istio-egressgateway-name", "--istio-eg-gtw-name"]
        )
        c.argument(
            "istio_egressgateway_namespace",
            required=False,
            default=CONST_AZURE_SERVICE_MESH_DEFAULT_EGRESS_NAMESPACE,
            options_list=["--istio-egressgateway-namespace", "--istio-eg-gtw-ns"]
        )

    with self.argument_context("aks mesh enable") as c:
        c.argument("revision", validator=validate_azure_service_mesh_revision)
        c.argument("key_vault_id")
        c.argument("ca_cert_object_name")
        c.argument("ca_key_object_name")
        c.argument("root_cert_object_name")
        c.argument("cert_chain_object_name")

    with self.argument_context("aks mesh get-revisions") as c:
        c.argument(
            "location",
            required=True,
            help="Location in which to discover available Azure Service Mesh revisions.",
        )

    with self.argument_context("aks mesh upgrade start") as c:
        c.argument(
            "revision", validator=validate_azure_service_mesh_revision, required=True
        )

    with self.argument_context("aks mesh upgrade rollback") as c:
        c.argument(
            "yes",
            options_list=["--yes", "-y"],
            help="Do not prompt for confirmation.",
            action="store_true"
        )

    with self.argument_context("aks mesh upgrade complete") as c:
        c.argument(
            "yes",
            options_list=["--yes", "-y"],
            help="Do not prompt for confirmation.",
            action="store_true"
        )

    with self.argument_context("aks approuting enable") as c:
        c.argument("enable_kv", action="store_true")
        c.argument("keyvault_id", options_list=["--attach-kv"])
        c.argument("nginx", arg_type=get_enum_type(app_routing_nginx_configs))

    with self.argument_context("aks approuting update") as c:
        c.argument("keyvault_id", options_list=["--attach-kv"])
        c.argument("enable_kv", action="store_true")
        c.argument("nginx", arg_type=get_enum_type(app_routing_nginx_configs))

    with self.argument_context("aks approuting zone add") as c:
        c.argument("dns_zone_resource_ids", options_list=["--ids"], required=True)
        c.argument("attach_zones")

    with self.argument_context("aks approuting zone delete") as c:
        c.argument("dns_zone_resource_ids", options_list=["--ids"], required=True)

    with self.argument_context("aks approuting zone update") as c:
        c.argument("dns_zone_resource_ids", options_list=["--ids"], required=True)
        c.argument("attach_zones")

    with self.argument_context('aks check-network outbound') as c:
        c.argument('cluster_name', options_list=['--name', '-n'],
                   required=True, help='Name of the managed cluster.')
        c.argument('node_name', help='Name of the node to perform the connectivity check.')
        c.argument('custom_endpoints',
                   nargs="+",
                   help='Space-separated additional endpoint(s) to perform the connectivity check.',
                   validator=validate_custom_endpoints)

    # Reference: https://learn.microsoft.com/en-us/cli/azure/k8s-extension?view=azure-cli-latest
    with self.argument_context('aks extension') as c:
        c.argument('resource_group_name',
                   options_list=['--resource-group', '-g'],
                   help='Name of resource group.')
        c.argument('name',
                   options_list=['--name', '-n'],
                   help='Name of the extension instance')
        c.argument('extension_type',
                   options_list=['--extension-type', '-t'],
                   help='Name of the extension type.')
        c.argument('cluster_name',
                   options_list=['--cluster-name', '-c'],
                   help='Name of the Kubernetes cluster')
        c.argument('scope',
                   arg_type=get_enum_type(['cluster', 'namespace']),
                   help='Specify the extension scope.')
        c.argument('configuration_settings',
                   arg_group="Configuration",
                   options_list=['--configuration-settings', '--config'],
                   action=AddConfigurationSettings,
                   nargs='+',
                   help='Configuration Settings as key=value pair.'
                   + 'Repeat parameter for each setting.'
                   + 'Do not use this for secrets, as this value is returned in response.')
        c.argument('configuration_protected_settings',
                   arg_group="Configuration",
                   options_list=['--config-protected-settings', '--config-protected'],
                   action=AddConfigurationProtectedSettings,
                   nargs='+',
                   help='Configuration Protected Settings as key=value pair. '
                   + 'Repeat parameter for each setting. Only the key is returned in response, the value is not.')
        c.argument('configuration_settings_file',
                   arg_group="Configuration",
                   options_list=['--config-settings-file', '--config-file'],
                   help='JSON file path for configuration-settings')
        c.argument('configuration_protected_settings_file',
                   arg_group="Configuration",
                   options_list=['--config-protected-settings-file', '--config-protected-file'],
                   help='JSON file path for configuration-protected-settings')
        c.argument('release_namespace',
                   help='Specify the namespace to install the extension release.')
        c.argument('target_namespace',
                   help='Specify the target namespace to install to for the extension instance. This'
                   ' parameter is required if extension scope is set to \'namespace\'')

    with self.argument_context("aks extension update") as c:
        c.argument('yes',
                   options_list=['--yes', '-y'],
                   help='Ignore confirmation prompts')

    with self.argument_context("aks extension delete") as c:
        c.argument('yes',
                   options_list=['--yes', '-y'],
                   help='Ignore confirmation prompts')
        c.argument('force',
                   help='Specify whether to force delete the extension from the cluster.')

    # Reference: https://learn.microsoft.com/en-us/cli/azure/k8s-extension/extension-types?view=azure-cli-latest
    with self.argument_context("aks extension type") as c:
        c.argument('resource_group_name',
                   options_list=['--resource-group', '-g'],
                   validator=validate_resource_group_parameter,
                   help='Name of resource group.')
        c.argument('cluster_name',
                   options_list=['--cluster-name', '-c'],
                   validator=validate_location_resource_group_cluster_parameters,
                   help='Name of the Kubernetes cluster')
        c.argument('extension_type',
                   options_list=['--extension-type', '-t'],
                   help='Name of the extension type.')
        c.argument('location',
                   options_list=['--location', '-l'],
                   validator=validate_location_resource_group_cluster_parameters,
                   help='Name of the location. Values from: `az account list-locations`')

    # Reference: https://learn.microsoft.com/en-us/cli/azure/k8s-extension/extension-types?view=azure-cli-latest
    with self.argument_context("aks extension type version") as c:
        c.argument('resource_group_name',
                   options_list=['--resource-group', '-g'],
                   validator=validate_resource_group_parameter,
                   help='Name of resource group.')
        c.argument('cluster_name',
                   options_list=['--cluster-name', '-c'],
                   validator=validate_location_resource_group_cluster_parameters,
                   help='Name of the Kubernetes cluster')
        c.argument('extension_type',
                   options_list=['--extension-type', '-t'],
                   help='Name of the extension type.')
        c.argument('location',
                   options_list=['--location', '-l'],
                   validator=validate_location_resource_group_cluster_parameters,
                   help='Name of the location. Values from: `az account list-locations`')
        c.argument('version',
                   help='Version for the extension type.')
        c.argument('major_version',
                   help='Filter results by only the major version of an extension type.'
                   + 'For example if 1 is specified, all versions with major version 1 (1.1, 1.1.2) will be shown.'
                   + 'The default value is None')
        c.argument('release_train',
                   arg_group="Version",
                   help='Specify the release train for the extension type.')
        c.argument('show_latest',
                   arg_type=get_three_state_flag(),
                   help='Filter results by only the latest version.'
                   + 'For example, if this flag is used the latest version of the extensionType will be shown.')

    # AKS loadbalancer command parameter configuration
    with self.argument_context("aks loadbalancer add") as c:
        c.argument(
            "name",
            options_list=["--name", "-n"],
            help="Name of the load balancer configuration. Required.",
        )
        c.argument(
            "primary_agent_pool_name",
            options_list=["--primary-agent-pool-name", "-p"],
            help=(
                "Name of the primary agent pool for this load balancer. "
                "All nodes in this pool will be added to the load balancer. Required."
            ),
        )
        c.argument(
            "allow_service_placement",
            options_list=["--allow-service-placement", "-a"],
            arg_type=get_three_state_flag(),
            help="Whether to automatically place services on the load balancer. Default is true.",
        )
        c.argument(
            "aks_custom_headers",
            help="Send custom headers. When specified, format should be Key1=Value1,Key2=Value2.",
        )
        c.argument(
            "service_label_selector",
            options_list=["--service-label-selector", "-l"],
            help=(
                "Only services that match this selector can be placed on this load balancer. "
                "Format: key1=value1,key2=value2 for simple selectors, "
                "or key1 In val1 val2,key2 Exists for advanced expressions."
            ),
        )
        c.argument(
            "service_namespace_selector",
            options_list=["--service-namespace-selector", "-s"],
            help=(
                "Services created in namespaces that match the selector can be placed on this load balancer. "
                "Format: key1=value1,key2=value2 for simple selectors, "
                "or key1 In val1 val2,key2 Exists for advanced expressions."
            ),
        )
        c.argument(
            "node_selector",
            options_list=["--node-selector", "-d"],
            help=(
                "Nodes that match this selector will be possible members of this load balancer. "
                "Format: key1=value1,key2=value2 for simple selectors, "
                "or key1 In val1 val2,key2 Exists for advanced expressions."
            ),
        )

    with self.argument_context("aks loadbalancer rebalance-nodes") as c:
        c.argument(
            "resource_group_name",
            options_list=["--resource-group", "-g"],
            help="Name of resource group.",
            id_part="resource_group",
            configured_default="aks",
        )
        c.argument(
            "cluster_name",
            options_list=["--name", "-n"],
            help="Name of the managed cluster.",
        )
        c.argument(
            "load_balancer_names",
            options_list=["--load-balancer-names", "--lb-names"],
            nargs="+",
            help=(
                "Space-separated list of load balancer names to rebalance. "
                "If not specified, all load balancers will be rebalanced."
            ),
        )
        c.argument(
            "no_wait", help="Do not wait for the long-running operation to finish."
        )

    with self.argument_context("aks loadbalancer update") as c:
        c.argument(
            "name",
            options_list=["--name", "-n"],
            help="Name of the public load balancer. Required.",
        )
        c.argument(
            "primary_agent_pool_name",
            options_list=["--primary-agent-pool-name", "-p"],
            help=(
                "Name of the primary agent pool for this load balancer. "
                "All nodes in this pool will be added to the load balancer."
            ),
        )
        c.argument(
            "allow_service_placement",
            options_list=["--allow-service-placement", "-a"],
            arg_type=get_three_state_flag(),
            help="Whether to automatically place services on the load balancer. Default is true.",
        )
        c.argument(
            "aks_custom_headers",
            help="Send custom headers. When specified, format should be Key1=Value1,Key2=Value2.",
        )
        c.argument(
            "service_label_selector",
            options_list=["--service-label-selector", "-l"],
            help=(
                "Only services that match this selector can be placed on this load balancer. "
                "Format: key1=value1,key2=value2 for simple selectors, "
                "or key1 In val1 val2,key2 Exists for advanced expressions."
            ),
        )
        c.argument(
            "service_namespace_selector",
            options_list=["--service-namespace-selector", "-s"],
            help=(
                "Services created in namespaces that match the selector can be placed on this load balancer. "
                "Format: key1=value1,key2=value2 for simple selectors, "
                "or key1 In val1 val2,key2 Exists for advanced expressions."
            ),
        )
        c.argument(
            "node_selector",
            options_list=["--node-selector", "-d"],
            help=(
                "Nodes that match this selector will be possible members of this load balancer. "
                "Format: key1=value1,key2=value2 for simple selectors, "
                "or key1 In val1 val2,key2 Exists for advanced expressions."
            ),
        )

    # Define parameters for show and delete commands
    for scope in [
        "aks loadbalancer show",
        "aks loadbalancer delete",
    ]:
        with self.argument_context(scope) as c:
            c.argument(
                "name",
                options_list=["--name", "-n"],
                help="Name of the load balancer configuration. Required.",
            )

    with self.argument_context("aks bastion") as c:
        c.argument("bastion")
        c.argument("port", type=int)
        c.argument("admin", action="store_true")
        c.argument(
            "yes",
            options_list=["--yes", "-y"],
            help="Do not prompt for confirmation.",
            action="store_true",
        )


def _get_default_install_location(exe_name):
    system = platform.system()
    if system == "Windows":
        home_dir = os.environ.get("USERPROFILE")
        if not home_dir:
            return None
        install_location = os.path.join(
            home_dir, f".azure-{exe_name}\\{exe_name}.exe"
        )
    elif system in ("Linux", "Darwin"):
        install_location = f"/usr/local/bin/{exe_name}"
    else:
        install_location = None
    return install_location
