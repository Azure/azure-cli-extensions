# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core.azclierror import InvalidArgumentValueError, MutuallyExclusiveArgumentError

from azext_aks_preview._client_factory import cf_managed_clusters
from azext_aks_preview.azuremanagedlustre._consts import (
    CONST_AMLFS_ARM64_UNSUPPORTED_OS_SKUS,
    CONST_AMLFS_UNSUPPORTED_OS_SKUS,
)


def validate_azure_managed_lustre_params(enable, disable, is_extension_installed=None):
    if enable and disable:
        raise MutuallyExclusiveArgumentError(
            "Cannot set --enable-azure-managed-lustre and --disable-azure-managed-lustre together."
        )
    if disable and is_extension_installed is False:
        raise InvalidArgumentValueError(
            "Cannot set --disable-azure-managed-lustre. Azure Managed Lustre is not enabled in the cluster."
        )


def _get_vm_sku_architectures(cli_ctx, location):
    from azure.cli.command_modules.vm.aaz.latest.vm import ListSkus as VMListSkus

    def is_in_location(sku):
        return not location or any(location.lower() == value.lower() for value in sku.get("locations", []))

    architectures = {}
    for sku in VMListSkus(cli_ctx=cli_ctx)(command_args={}):
        if sku.get("resourceType", "").lower() != "virtualmachines" or not is_in_location(sku):
            continue
        for capability in sku.get("capabilities", []):
            if capability.get("name", "").lower() == "cpuarchitecturetype":
                architectures[sku.get("name", "").lower()] = capability.get("value", "").lower()
                break
    return architectures


def _resolve_os_sku(os_sku, kubernetes_version):
    version_parts = str(kubernetes_version).lstrip("v").split(".")
    try:
        version = (int(version_parts[0]), int(version_parts[1].split("-")[0]))
    except (IndexError, ValueError) as ex:
        raise InvalidArgumentValueError(
            f"Cannot resolve OS SKU '{os_sku}' for Kubernetes version '{kubernetes_version}'. "
            "Specify a valid --kubernetes-version."
        ) from ex
    if os_sku == "azurelinux":
        return "azurelinux3" if version >= (1, 32) else "azurelinux"
    if version >= (1, 35):
        return "ubuntu2404"
    return "ubuntu2204" if version >= (1, 25) else "ubuntu2004"


def _get_default_kubernetes_version(cmd, location):
    versions = cf_managed_clusters(cmd.cli_ctx).list_kubernetes_versions(location)
    defaults = [version.version for version in versions.values_property or [] if version.is_default]
    if len(defaults) != 1 or not defaults[0]:
        raise InvalidArgumentValueError(
            "Cannot determine the default Kubernetes version for Azure Managed Lustre node compatibility. "
            "Specify --kubernetes-version."
        )
    return defaults[0]


def validate_azure_managed_lustre_node_compatibility(cmd, cluster):
    pools = cluster.agent_pool_profiles or []
    architecture_sensitive_pools = []
    default_kubernetes_version = None

    for pool in pools:
        os_sku = (pool.os_sku or "Ubuntu").lower()
        if os_sku in ("ubuntu", "azurelinux"):
            kubernetes_version = (
                getattr(pool, "orchestrator_version", None) or getattr(cluster, "kubernetes_version", None)
            )
            if not kubernetes_version:
                if default_kubernetes_version is None:
                    default_kubernetes_version = _get_default_kubernetes_version(cmd, cluster.location)
                kubernetes_version = default_kubernetes_version
            os_sku = _resolve_os_sku(os_sku, kubernetes_version)
        if os_sku in CONST_AMLFS_UNSUPPORTED_OS_SKUS:
            continue
        if os_sku in CONST_AMLFS_ARM64_UNSUPPORTED_OS_SKUS:
            architecture_sensitive_pools.append(pool)
            continue
        return

    if architecture_sensitive_pools:
        architectures = _get_vm_sku_architectures(cmd.cli_ctx, cluster.location)
        unknown_vm_sizes = []
        for pool in architecture_sensitive_pools:
            vm_size = (pool.vm_size or "").lower()
            architecture = architectures.get(vm_size)
            if architecture and architecture != "arm64":
                return
            if not architecture:
                unknown_vm_sizes.append(pool.vm_size or "<unknown>")
        if unknown_vm_sizes:
            raise InvalidArgumentValueError(
                "Cannot enable Azure Managed Lustre because the architecture couldn't be determined for "
                f"node pool VM size(s): {', '.join(unknown_vm_sizes)}."
            )

    raise InvalidArgumentValueError(
        "Cannot enable Azure Managed Lustre because none of the cluster's node pools support "
        "the Azure Managed Lustre extension. Flatcar and Ubuntu 26.04 aren't supported; "
        "Ubuntu 22.04 and Azure Linux 3 on ARM64 aren't supported."
    )
