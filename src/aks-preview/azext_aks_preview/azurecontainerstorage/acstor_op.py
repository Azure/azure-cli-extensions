# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import random
import string

from azure.cli.command_modules.resource.custom import register_provider
from azure.cli.command_modules.acs._roleassignments import (
    add_role_assignment,
    build_role_scope,
    delete_role_assignments,
)
from azext_k8s_extension.custom import (
    create_k8s_extension,
    delete_k8s_extension,
    show_k8s_extension,
)
from azext_aks_preview.azurecontainerstorage._consts import (
    CONST_STORAGE_POOL_TYPE_AZURE_DISK,
    CONST_STORAGE_POOL_TYPE_AZURE_DISK
    CONST_STORAGE_POOL_NAME_PREFIX,
    CONST_STORAGE_POOL_OPTION_NVME,
    CONST_STORAGE_POOL_OPTION_TEMP,
)

from knack.prompting import prompt_y_n

def perform_enable_azure_container_storage(
    cmd,
    client,
    cluster,
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
    _perform_role_operations_on_managed_rg(cmd, cluster, True)

    # Step 3: Install the k8s_extension 'microsoft.azurecontainerstorage'
    if storage_pool_name is None:
    	storage_pool_name = _generate_random_storage_pool_name()
    config_settings = [
        {".cli.poolName": storage_pool_name},
        {"cli.poolSize": storage_pool_size},
        {"cli.poolType": storage_pool_type},
        {"cli.nodepools": nodepool_name},
    ]

    if storage_pool_type == CONST_STORAGE_POOL_TYPE_AZURE_DISK:
        config_settings.append({"cli.azureDiskPoolSku": storage_pool_sku})
    if storage_pool_type == CONST_STORAGE_POOL_TYPE_EPHEMERAL_DISK:
        pool_option = CONST_STORAGE_POOL_OPTION_TEMP
        if storage_pool_option == CONST_STORAGE_POOL_OPTION_NVME:
            pool_option = "nvme"
        config_settings.append({"cli.ephemeralPoolOption": pool_option})

    create_k8s_extension(
        cmd,
        client,
        cluster.context.get_resource_group_name(),
        cluster.context.get_name(),
        "azurecontainerstorage",
        "managedClusters",
        "microsoft.azurecontainerstorage",
        auto_upgrade_minor_version=True,
        release_train="stable",
        scope="cluster",
        release_namespace="acstor",
        configuration_settings=config_settings,
    )

def perform_disable_azure_container_storage(
    cmd,
    client,
    cluster,
):
    # Step 1: Check if show_k8s_extension returns an extension already installed
    try:
        extension = show_k8s_extension(
            client,
            cluster.context.get_resource_group_name(),
            cluster.context.get_name(),
            "azurecontainerstorage",
            "managedClusters",
        )

        extension_type = extension.extension_type.lower()
        if extension_type != "microsoft.azurecontainerstorage":
            logger.debug("The extension returned is not of the type microsoft.azurecontainerstorage")
            return
    except:
        logger.debug("Extension type microsoft.azurecontainerstorage not installed on cluster")
        return

    # Step 2: Add a prompt to ensure if we want to skip validation of existing storagepool
    msg = 'Disabling Azure Container Storage will delete all the storagepools on the cluster. Do you want to validate before disabling?'
    if not prompt_y_n(msg, default="y"):
        config_settings = [{"cli.validateBeforeUninstall": False}]
        update_k8s_extension(
            cmd,
            client,
            cluster.context.get_resource_group_name(),
            cluster.context.get_name(),
            "azurecontainerstorage",
            "managedClusters",
            configuration_settings=config_settings,
            ignore_warning_msg=True,
        )

    # Step 3: If the extension is installed, call delete_k8s_extension
    delete_k8s_extension(
        cmd,
        client,
        cluster.context.get_resource_group_name(),
        cluster.context.get_name(),
        "azurecontainerstorage",
        "managedClusters",
    )

    # Revoke AKS cluster's node identity the following 
    # roles on the AKS managed resource group:
    # 1. Reader
    # 2. Network Contributor
    # 3. Elastic SAN Owner
    # 4. Elastic SAN Volume Group Owner
    _perform_role_operations_on_managed_rg(cmd, cluster, False)

def _register_dependent_rps(cmd):
    register_provider(cmd, 'Microsoft.Kubernetes', wait=True)
    register_provider(cmd, 'Microsoft.KubernetesConfiguration', wait=True)
    register_provider(cmd, 'Microsoft.ExtendedLocation', wait=True)

def _perform_role_operations_on_managed_rg(cmd, cluster, assign):
    managed_resource_group = cluster.context.get_node_resource_group()
    managed_rg_role_scope = build_role_scope(managed_resource_group)
    assignee, is_service_principal = cluster.context.get_assignee_from_identity_or_sp_profile()
    if assign:
        add_role_assignment(
            cmd,
            "Reader",
            assignee,
            scope=managed_rg_role_scope,
            is_service_principal = is_service_principal,
        )

        add_role_assignment(
            cmd,
            "Network Contributor",
            assignee,
            scope=managed_rg_role_scope,
            is_service_principal = is_service_principal,
        )

        add_role_assignment(
            cmd,
            "Elastic SAN Owner",
            assignee,
            scope=managed_rg_role_scope,
            is_service_principal = is_service_principal,
        )

        add_role_assignment(
            cmd,
            "Elastic SAN Volume Group Owner",
            assignee,
            scope=managed_rg_role_scope,
            is_service_principal = is_service_principal,
        )

    else:
        delete_role_assignments(
            cmd,
            "Reader",
            assignee,
            scope=managed_rg_role_scope,
            is_service_principal = is_service_principal,
        )

        delete_role_assignments(
            cmd,
            "Network Contributor",
            assignee,
            scope=managed_rg_role_scope,
            is_service_principal = is_service_principal,
        )

        delete_role_assignments(
            cmd,
            "Elastic SAN Owner",
            assignee,
            scope=managed_rg_role_scope,
            is_service_principal = is_service_principal,
        )

        delete_role_assignments(
            cmd,
            "Elastic SAN Volume Group Owner",
            assignee,
            scope=managed_rg_role_scope,
            is_service_principal = is_service_principal,
        )


def _generate_random_storage_pool_name():
	random_name = CONST_STORAGE_POOL_NAME_PREFIX + ''.join(random.choices(string.ascii_letters, k=N))
	return random_name