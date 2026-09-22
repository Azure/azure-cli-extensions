# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core.azclierror import UnknownError
from azure.cli.core.commands import LongRunningOperation
from knack.log import get_logger

from azext_aks_preview.azuremanagedlustre._consts import (
    CONST_AML_EXT_INSTALLATION_NAME,
    CONST_AML_K8S_EXTENSION_NAME,
    CONST_AML_RELEASE_TRAIN,
    CONST_AML_VERSION,
)
from azext_aks_preview.azuremanagedlustre._helpers import get_azure_managed_lustre_extension_client

logger = get_logger(__name__)


def perform_enable_azure_managed_lustre(cmd, resource_group, cluster_name):
    client, custom_module = get_azure_managed_lustre_extension_client(cmd)
    result = custom_module.create_k8s_extension(
        cmd,
        client,
        resource_group,
        cluster_name,
        CONST_AML_EXT_INSTALLATION_NAME,
        "managedClusters",
        CONST_AML_K8S_EXTENSION_NAME,
        version=CONST_AML_VERSION,
        release_train=CONST_AML_RELEASE_TRAIN,
        scope="cluster",
        auto_upgrade_minor_version=False,
    )
    extension = LongRunningOperation(cmd.cli_ctx)(result)
    if extension is None or extension.provisioning_state != "Succeeded":
        raise UnknownError("Azure Managed Lustre extension installation did not succeed.")
    logger.warning("Azure Managed Lustre successfully installed.")


def perform_disable_azure_managed_lustre(cmd, resource_group, cluster_name):
    client, custom_module = get_azure_managed_lustre_extension_client(cmd)
    result = custom_module.delete_k8s_extension(
        cmd,
        client,
        resource_group,
        cluster_name,
        CONST_AML_EXT_INSTALLATION_NAME,
        "managedClusters",
        yes=True,
    )
    # The delegated delete returns None when it cannot retrieve the extension.
    if result is None:
        raise UnknownError("Azure Managed Lustre extension could not be retrieved for deletion.")
    LongRunningOperation(cmd.cli_ctx)(result)
    logger.warning("Azure Managed Lustre has been disabled.")
