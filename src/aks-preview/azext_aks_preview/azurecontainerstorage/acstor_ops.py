# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import random
import string

from azure.cli.core.azclierror import UnknownError
from azure.cli.core.commands import LongRunningOperation
from azure.cli.command_modules.resource.custom import register_provider
from azure.cli.command_modules.acs._roleassignments import (
    add_role_assignment,
    build_role_scope,
    delete_role_assignments,
)
from azext_aks_preview.azurecontainerstorage._consts import (
    CONST_STORAGE_POOL_TYPE_AZURE_DISK,
    CONST_STORAGE_POOL_TYPE_EPHEMERAL_DISK,
    CONST_STORAGE_POOL_NAME_PREFIX,
    CONST_STORAGE_POOL_OPTION_NVME,
    CONST_STORAGE_POOL_OPTION_TEMP,
    CONST_STORAGE_POOL_RANDOM_LENGTH,
)
from knack.prompting import prompt_y_n

def perform_enable_azure_container_storage(
    cmd,
    subscription_id,
    resource_group,
    cluster_name,
    node_resource_group,
    kubelet_identity_object_id,
    storage_pool_name,
    storage_pool_type,
    storage_pool_size,
    storage_pool_sku,
    storage_pool_option,
    nodepool_name,
):
    # Step 1: Register the dependent providers i.e.
    # 1. Microsoft.Kubernetes
    # 2. Microsoft.KubernetesConfiguration
    # 3. Microsoft.ExtendedLocation
    _register_dependent_rps(cmd)

    # Step 2: Grant AKS cluster's node identity the following 
    # roles on the AKS managed resource group:
    # 1. Reader
    # 2. Network Contributor
    # 3. Elastic SAN Owner
    # 4. Elastic SAN Volume Group Owner
    _perform_role_operations_on_managed_rg(cmd, subscription_id, node_resource_group, kubelet_identity_object_id, True)

    if storage_pool_type is None:
        storage_pool_type = CONST_STORAGE_POOL_TYPE_AZURE_DISK

    # Step 3: Install the k8s_extension 'microsoft.azurecontainerstorage'
    if storage_pool_name is None:
        storage_pool_name = _generate_random_storage_pool_name()
    config_settings = [
        {"cli.storagePool.poolName": storage_pool_name},
        {"cli.storagePool.poolSize": storage_pool_size},
        {"cli.storagePool.poolType": storage_pool_type},
        {"cli.node.nodepools": nodepool_name},
    ]

    if storage_pool_type == CONST_STORAGE_POOL_TYPE_AZURE_DISK:
        config_settings.append({"cli.storagePool.azureDiskPoolSku": storage_pool_sku})
    if storage_pool_type == CONST_STORAGE_POOL_TYPE_EPHEMERAL_DISK:
        pool_option = CONST_STORAGE_POOL_OPTION_TEMP
        if storage_pool_option == CONST_STORAGE_POOL_OPTION_NVME:
            pool_option = "nvme"
        config_settings.append({"cli.storagePool.ephemeralPoolOption": pool_option})

    from azext_k8s_extension._client_factory import cf_k8s_extension_operation
    from azext_k8s_extension.custom import create_k8s_extension

    client = cf_k8s_extension_operation(cmd.cli_ctx)
    result = create_k8s_extension(
        cmd,
        client,
        resource_group,
        cluster_name,
        "azurecontainerstorage",
        "managedClusters",
        "microsoft.azstor",
        auto_upgrade_minor_version=True,
        release_train="logtest",
        scope="cluster",
        release_namespace="acstor",
        configuration_settings=config_settings,
    )

    arc_result = LongRunningOperation(cmd.cli_ctx)(result)

    print (op)

def perform_disable_azure_container_storage(
    cmd,
    subscription_id,
    resource_group,
    cluster_name,
    node_resource_group,
    kubelet_identity_object_id,
):
    from azext_k8s_extension._client_factory import cf_k8s_extension_operation
    client = cf_k8s_extension_operation(cmd.cli_ctx)
    # Step 1: Check if show_k8s_extension returns an extension already installed
    from azext_k8s_extension.custom import show_k8s_extension
    try:
        extension = show_k8s_extension(
            client,
            resource_group,
            cluster_name,
            "azurecontainerstorage",
            "managedClusters",
        )

        extension_type = extension.extension_type.lower()
        print (extension_type)
        if extension_type != "microsoft.azstor":
            raise UnknownError('The extension returned is not of the type microsoft.azurecontainerstorage')
    except:
        raise UnknownError('Extension type microsoft.azurecontainerstorage not installed on cluster')

    # Step 2: Add a prompt to ensure if we want to skip validation of existing storagepool
    msg = 'Disabling Azure Container Storage will delete all the storagepools on the cluster. Do you want to validate before disabling?'
    if not prompt_y_n(msg, default="y"):
        config_settings = [{"cli.storagePool.validateBeforeUninstall": False}]
        from azext_k8s_extension.custom import update_k8s_extension
        update_k8s_extension(
            cmd,
            client,
            resource_group,
            cluster_name,
            "azurecontainerstorage",
            "managedClusters",
            configuration_settings=config_settings,
            ignore_warning_msg=True,
        )

    # Step 3: If the extension is installed, call delete_k8s_extension
    from azext_k8s_extension.custom import delete_k8s_extension
    result = delete_k8s_extension(
        cmd,
        client,
        resource_group,
        cluster_name,
        "azurecontainerstorage",
        "managedClusters",
    )
    arc_result = LongRunningOperation(cmd.cli_ctx)(result)
    print (op)

    # Revoke AKS cluster's node identity the following 
    # roles on the AKS managed resource group:
    # 1. Reader
    # 2. Network Contributor
    # 3. Elastic SAN Owner
    # 4. Elastic SAN Volume Group Owner
    _perform_role_operations_on_managed_rg(cmd, subscription_id, node_resource_group, kubelet_identity_object_id, False)

def _register_dependent_rps(cmd):
    register_provider(cmd, 'Microsoft.Kubernetes', wait=True)
    register_provider(cmd, 'Microsoft.KubernetesConfiguration', wait=True)
    register_provider(cmd, 'Microsoft.ExtendedLocation', wait=True)

def _perform_role_operations_on_managed_rg(cmd, subscription_id, node_resource_group, kubelet_identity_object_id, assign):
    managed_rg_role_scope = build_role_scope(node_resource_group, None, subscription_id)
    roles = ["Reader", "Network Contributor", "Elastic SAN Owner", "Elastic SAN Volume Group Owner"]

    for role in roles:
        if assign:
            add_role_assignment(
                cmd,
                role,
                kubelet_identity_object_id,
                scope=managed_rg_role_scope,
            )
        else:
            delete_role_assignments(
                cmd,
                role,
                kubelet_identity_object_id,
                scope=managed_rg_role_scope,
            )


def _generate_random_storage_pool_name():
    random_name = CONST_STORAGE_POOL_NAME_PREFIX + ''.join(random.choices(string.ascii_letters, k=CONST_STORAGE_POOL_RANDOM_LENGTH))
    return random_name