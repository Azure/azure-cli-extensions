# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core.azclierror import InvalidArgumentValueError, MutuallyExclusiveArgumentError

from azext_aks_preview.azuremanagedlustre._consts import (
    CONST_AML_ARM64_UNSUPPORTED_OS_SKUS,
    CONST_AML_UNSUPPORTED_OS_SKUS,
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


def validate_azure_managed_lustre_node_compatibility(cmd, cluster):
    pools = cluster.agent_pool_profiles or []
    architecture_sensitive_pools = []

    for pool in pools:
        os_sku = (pool.os_sku or "").lower()
        if os_sku in CONST_AML_UNSUPPORTED_OS_SKUS:
            continue
        if os_sku in CONST_AML_ARM64_UNSUPPORTED_OS_SKUS:
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
        "Azure Managed Lustre extension version 0.6.0. Flatcar, Ubuntu 26.04, and Azure Linux 3 "
        "on ARM64 node pools aren't supported."
    )
