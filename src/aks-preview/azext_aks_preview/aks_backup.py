# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""Helpers that delegate AKS backup enablement to the dataprotection CLI extension.

The actual orchestration (vault, policy, storage account, extension install,
trusted access, role assignments, backup instance) lives in the
``dataprotection`` extension. This module is a thin shim that:

* loads that extension's path lazily (so ``az aks`` works without it),
* raises an actionable error if the extension is not installed,
* derives the AKS datasource ARM id from the resource group + cluster name.
"""

from azure.cli.core.azclierror import UnknownError
from azure.cli.core.commands.client_factory import get_subscription_id


def enable_aks_backup(cmd, resource_group_name, cluster_name,  # pylint: disable=too-many-positional-arguments
                      backup_strategy, backup_configuration_file, yes):
    """Enable Azure Backup for an AKS cluster by delegating to the
    ``dataprotection`` extension.

    Raises ``UnknownError`` if the extension is not installed.
    """
    try:
        from azure.cli.core.extension.operations import add_extension_to_path
        add_extension_to_path("dataprotection")
        from azext_dataprotection.manual.aks.aks_helper import (
            dataprotection_enable_backup_helper,
        )
    except ImportError:
        raise UnknownError(  # pylint: disable=raise-missing-from
            "Please add CLI extension `dataprotection` to use --enable-backup with "
            "'az aks create' / 'az aks update'.\n"
            "Run command `az extension add --name dataprotection`."
        )

    subscription_id = get_subscription_id(cmd.cli_ctx)
    datasource_id = (
        f"/subscriptions/{subscription_id}/resourceGroups/{resource_group_name}"
        f"/providers/Microsoft.ContainerService/managedClusters/{cluster_name}"
    )
    dataprotection_enable_backup_helper(
        cmd,
        datasource_id,
        backup_strategy or "Week",
        backup_configuration_file or {},
        yes=yes,
    )
