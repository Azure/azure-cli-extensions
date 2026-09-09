# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=unused-argument
# pylint: disable=too-many-locals

import ipaddress

from azure.cli.core.azclierror import InvalidArgumentValueError, ResourceNotFoundError
from azure.cli.core.commands.client_factory import get_mgmt_service_client
from azure.core.exceptions import HttpResponseError, ResourceNotFoundError as SdkResourceNotFoundError
from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.containerservice import ContainerServiceClient
from azure.mgmt.core.tools import parse_resource_id
from azure.mgmt.network import NetworkManagementClient
from azure.mgmt.network.models import Delegation, Subnet
from knack.log import get_logger

from ..vendored_sdks.models import Extension, PatchExtension, Scope, ScopeCluster
from .DefaultExtension import DefaultExtension, user_confirmation_factory

logger = get_logger(__name__)

MIN_CPU_CORES = 4
MIN_MEM_GB = 16
ACI_SUBNET_PREFIX = 16
RELEASE_NAMESPACE = "vn-system"  # release unique namespace
ACI_SUBNET_NAME = "virtualnodes-aci-subnet"
ACI_DELEGATION_SERVICE_NAME = "Microsoft.ContainerInstance/containerGroups"
ALLOWED_CONFIG_SETTINGS_KEYS = [
    "replicaCount",
    "admissionControllerReplicaCount",
    "podAnnotations",
    "nodeSelector",
    "tolerations",
    "affinity",
    "zones",
    "nodeLabels",
]


class VirtualNodes(DefaultExtension):
    def __init__(self):
        pass

    def Create(self, cmd, client, resource_group_name, cluster_name, name, cluster_type, cluster_rp,
               extension_type, scope, auto_upgrade_minor_version, auto_upgrade_mode, release_train,
               version, target_namespace, release_namespace, configuration_settings,
               configuration_protected_settings, configuration_settings_file,
               configuration_protected_settings_file, plan_name, plan_publisher, plan_product):
        logger.info("Validating parameters and AKS cluster configuration for Microsoft.virtualnodes extension...")

        if scope is not None and scope.lower() == "namespace":
            raise InvalidArgumentValueError(
                "Invalid scope '{}'.  This extension can be installed only at 'cluster' scope.".format(scope)
            )

        if cluster_type is not None and cluster_type.lower() != "managedclusters":
            raise InvalidArgumentValueError(
                "Invalid cluster type '{}'. This extension can be installed only on AKS clusters "
                "(cluster type 'managedClusters').".format(cluster_type)
            )

        if release_namespace is not None and release_namespace != RELEASE_NAMESPACE:
            raise InvalidArgumentValueError(
                f"The '--release-namespace' argument is not configurable for Microsoft.virtualnodes extension. "
                f"The extension must be installed in the '{RELEASE_NAMESPACE}' namespace."
            )

        aks_client = get_mgmt_service_client(cmd.cli_ctx, ContainerServiceClient)
        try:
            cluster = aks_client.managed_clusters.get(resource_group_name, cluster_name)
        except SdkResourceNotFoundError as e:
            raise ResourceNotFoundError(
                f"AKS cluster '{cluster_name}' was not found in resource group '{resource_group_name}'."
            ) from e
        except HttpResponseError as e:
            raise InvalidArgumentValueError(
                f"Failed to get AKS cluster '{cluster_name}' in resource group '{resource_group_name}': {e.message}"
            ) from e

        if configuration_settings is None:
            configuration_settings = {}
        validate_configuration(configuration_settings, configuration_protected_settings, extension_type)
        validate_node_pools(cmd, cluster)
        check_aks_cluster_network_config(cluster)

        logger.info("Validation successful. Proceeding with creating subnet and delegating it for the ACI CGs.")

        add_and_delegate_aci_subnet(cmd, cluster, resource_group_name)

        logger.info("Subnet created and delegated successfully. Proceeding with extension creation.")

        scope_cluster = ScopeCluster(release_namespace=RELEASE_NAMESPACE)
        ext_scope = Scope(cluster=scope_cluster, namespace=None)

        create_identity = True
        extension = Extension(
            extension_type=extension_type,
            auto_upgrade_minor_version=auto_upgrade_minor_version,
            auto_upgrade_mode=auto_upgrade_mode,
            release_train=release_train,
            version=version,
            scope=ext_scope,
            configuration_settings=configuration_settings,
            configuration_protected_settings=configuration_protected_settings,
        )
        return extension, name, create_identity

    def Update(self, cmd, resource_group_name, cluster_name, auto_upgrade_minor_version, auto_upgrade_mode,
               release_train, version, configuration_settings, configuration_protected_settings,
               original_extension, yes=False):
        validate_allowed_keys(configuration_settings, original_extension.extension_type)
        validate_allowed_keys(configuration_protected_settings, original_extension.extension_type)

        return PatchExtension(
            auto_upgrade_minor_version=auto_upgrade_minor_version,
            auto_upgrade_mode=auto_upgrade_mode,
            release_train=release_train,
            version=version,
            configuration_settings=configuration_settings,
            configuration_protected_settings=configuration_protected_settings,
        )

    def Delete(self, cmd, client, resource_group_name, cluster_name, name, cluster_type, cluster_rp, yes):
        user_confirmation_factory(cmd, yes)


def validate_allowed_keys(config_dict, extension_type):
    if not config_dict:
        return
    for key in config_dict:
        if key not in ALLOWED_CONFIG_SETTINGS_KEYS:
            raise InvalidArgumentValueError(
                f"Unsupported configuration setting: '{key}'. "
                f"Only {ALLOWED_CONFIG_SETTINGS_KEYS} are allowed for extensions of type {extension_type}."
            )


def validate_configuration(configuration_settings, configuration_protected_settings, extension_type):
    validate_allowed_keys(configuration_settings, extension_type)
    validate_allowed_keys(configuration_protected_settings, extension_type)

    configuration_settings["aciSubnetName"] = ACI_SUBNET_NAME


def validate_node_pools(cmd, cluster):
    compute_client = get_mgmt_service_client(cmd.cli_ctx, ComputeManagementClient)
    location = cluster.location
    vm_sizes = compute_client.virtual_machine_sizes.list(location)
    vm_size_dict = {vm.name: vm for vm in vm_sizes}

    for pool in cluster.agent_pool_profiles:
        vm_size = pool.vm_size
        vm_info = vm_size_dict.get(vm_size)
        if vm_info and vm_info.number_of_cores >= MIN_CPU_CORES and vm_info.memory_in_mb / 1024 >= MIN_MEM_GB:
            return

    raise InvalidArgumentValueError(
        f"Nodes selected for AKS must be at least {MIN_CPU_CORES} CPU and {MIN_MEM_GB} GB RAM "
        f"to accommodate virtual nodes being run on them, though they can be larger. "
        f"No node pool in cluster '{cluster.name}' meets the minimum requirements."
    )


def check_aks_cluster_network_config(cluster):
    network_profile = cluster.network_profile
    plugin = (network_profile.network_plugin or "").lower()
    plugin_mode = (network_profile.network_plugin_mode or "").lower()
    policy = (network_profile.network_policy or "").lower()

    if plugin != "azure" or plugin_mode not in ("", "none"):
        raise InvalidArgumentValueError(
            "VirtualNode requires Azure CNI Node Subnet as network configuration. "
            "This cluster does not meet the requirements."
        )

    if policy != "calico":
        raise InvalidArgumentValueError(
            f"Calico network policy is not enabled for this AKS cluster. "
            f"It is instead: {network_profile.network_policy}."
        )

    node_rg = (cluster.node_resource_group or "").lower()
    for pool in cluster.agent_pool_profiles or []:
        vnet_subnet_id = getattr(pool, "vnet_subnet_id", None)
        if not vnet_subnet_id:
            continue
        parsed = parse_resource_id(vnet_subnet_id)
        subnet_rg = (parsed.get("resource_group") or "").lower()
        if subnet_rg != node_rg:
            raise InvalidArgumentValueError(
                f"Microsoft.Virtualnodes extension type requires the cluster VNET to be in the node resource group "
                f"('{cluster.node_resource_group}'), but agent pool '{pool.name}' uses a subnet in resource group "
                f"'{parsed.get('resource_group')}'. BYO VNETs outside the node resource group are not supported."
            )


def add_and_delegate_aci_subnet(cmd, cluster, resource_group_name):
    vnet_rg = cluster.node_resource_group
    network_client = get_mgmt_service_client(cmd.cli_ctx, NetworkManagementClient)

    vnets = list(network_client.virtual_networks.list(vnet_rg))
    if not vnets:
        raise ResourceNotFoundError(f"No VNET found in node resource group '{vnet_rg}'.")
    if len(vnets) > 1:
        raise InvalidArgumentValueError(
            f"Expected exactly one VNET in node resource group '{vnet_rg}', found {len(vnets)}."
        )
    vnet = vnets[0]
    vnet_name = vnet.name

    existing = next((s for s in (vnet.subnets or []) if s.name == ACI_SUBNET_NAME), None)
    if existing is not None:
        delegated = any(
            (d.service_name or "").lower() == ACI_DELEGATION_SERVICE_NAME.lower()
            for d in (existing.delegations or [])
        )
        if not delegated:
            raise InvalidArgumentValueError(
                f"Subnet '{ACI_SUBNET_NAME}' already exists in VNET '{vnet_name}' but is not delegated to "
                f"'{ACI_DELEGATION_SERVICE_NAME}'."
            )
        logger.info(
            "Reusing existing subnet '%s' in VNET '%s' (resource group '%s') that is already delegated to ACI.",
            ACI_SUBNET_NAME, vnet_name, vnet_rg,
        )
        return

    new_cidr = _find_free_subnet_cidr(vnet, new_prefix=ACI_SUBNET_PREFIX)
    if new_cidr is None:
        raise InvalidArgumentValueError(
            f"Could not find a free /{ACI_SUBNET_PREFIX} in VNET '{vnet_name}' to create subnet '{ACI_SUBNET_NAME}'."
        )

    subnet_params = Subnet(
        address_prefix=str(new_cidr),
        delegations=[
            Delegation(
                name="aci-delegation",
                service_name=ACI_DELEGATION_SERVICE_NAME,
            )
        ],
    )

    logger.info(
        "Creating subnet '%s' (%s) in VNET '%s' (resource group '%s') delegated to ACI...",
        ACI_SUBNET_NAME, new_cidr, vnet_name, vnet_rg,
    )
    network_client.subnets.begin_create_or_update(
        vnet_rg, vnet_name, ACI_SUBNET_NAME, subnet_params
    ).result()


def _find_free_subnet_cidr(vnet, new_prefix):
    used = []
    for s in (vnet.subnets or []):
        for p in ([s.address_prefix] if s.address_prefix else []) + list(s.address_prefixes or []):
            try:
                used.append(ipaddress.ip_network(p, strict=False))
            except ValueError:
                continue

    for space in (vnet.address_space.address_prefixes or []):
        try:
            vnet_net = ipaddress.ip_network(space, strict=False)
        except ValueError:
            continue
        if vnet_net.prefixlen > new_prefix:
            continue
        for candidate in vnet_net.subnets(new_prefix=new_prefix):
            if not any(candidate.overlaps(u) for u in used):
                return candidate
    return None
