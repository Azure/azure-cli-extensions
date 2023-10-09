# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import random
import string

from azure.cli.core.azclierror import (
    UnknownError,
    CLIInternalError,
)
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
    CONST_ACSTOR_K8S_EXTENSION_NAME,
    CONST_EXT_INSTALLATION_NAME,
    CONST_K8S_EXTENSION_NAME,
    CONST_K8S_EXTENSION_CLIENT_FACTORY_MOD_NAME,
    CONST_K8S_EXTENSION_CUSTOM_MOD_NAME,
)
from knack.log import get_logger
from knack.prompting import prompt_y_n

logger = get_logger(__name__)


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
        {"cli.storagePool.name": storage_pool_name},
        {"cli.storagePool.size": storage_pool_size},
        {"cli.storagePool.type": storage_pool_type},
        {"cli.node.nodepools": nodepool_name},
    ]

    if storage_pool_type == CONST_STORAGE_POOL_TYPE_AZURE_DISK:
        config_settings.append({"cli.storagePool.azureDiskSku": storage_pool_sku})
    if storage_pool_type == CONST_STORAGE_POOL_TYPE_EPHEMERAL_DISK:
        pool_option = CONST_STORAGE_POOL_OPTION_TEMP
        if storage_pool_option == CONST_STORAGE_POOL_OPTION_NVME:
            pool_option = "nvme"
        config_settings.append({"cli.storagePool.ephemeralDiskOption": pool_option})

    client_factory = _get_k8s_extension_module(CONST_K8S_EXTENSION_CLIENT_FACTORY_MOD_NAME)
    client = client_factory.cf_k8s_extension_operation(cmd.cli_ctx)

    k8s_extension_custom_mod = _get_k8s_extension_module(CONST_K8S_EXTENSION_CUSTOM_MOD_NAME)
    result = k8s_extension_custom_mod.create_k8s_extension(
        cmd,
        client,
        resource_group,
        cluster_name,
        CONST_EXT_INSTALLATION_NAME,
        "managedClusters",
        CONST_ACSTOR_K8S_EXTENSION_NAME,
        auto_upgrade_minor_version=True,
        release_train="logtest",
        scope="cluster",
        release_namespace="acstor",
        configuration_settings=config_settings,
    )

    return LongRunningOperation(cmd.cli_ctx)(result)


def perform_disable_azure_container_storage(
    cmd,
    subscription_id,
    resource_group,
    cluster_name,
    node_resource_group,
    kubelet_identity_object_id,
):
    client_factory = _get_k8s_extension_module(CONST_K8S_EXTENSION_CLIENT_FACTORY_MOD_NAME)
    client = client_factory.cf_k8s_extension_operation(cmd.cli_ctx)
    # Step 1: Check if show_k8s_extension returns an extension already installed
    k8s_extension_custom_mod = _get_k8s_extension_module(CONST_K8S_EXTENSION_CUSTOM_MOD_NAME)
    try:
        extension = k8s_extension_custom_mod.show_k8s_extension(
            client,
            resource_group,
            cluster_name,
            CONST_EXT_INSTALLATION_NAME,
            "managedClusters",
        )

        extension_type = extension.extension_type.lower()
        if extension_type != CONST_ACSTOR_K8S_EXTENSION_NAME:
            raise UnknownError("The extension returned is not of the type {}. Aborting operation.".format(CONST_ACSTOR_K8S_EXTENSION_NAME))
    except:
        raise UnknownError("Extension type {} not installed on cluster.".format(CONST_ACSTOR_K8S_EXTENSION_NAME))

    # Step 2: Add a prompt to ensure if we want to skip validation of existing storagepool
    msg = 'Disabling Azure Container Storage will delete all the storagepools on the cluster. Do you want to validate before disabling?'
    if not prompt_y_n(msg, default="y"):
        config_settings = [{"cli.storagePool.validateBeforeUninstall": False}]
        from azext_k8s_extension.custom import update_k8s_extension
        update_result = k8s_extension_custom_mod.update_k8s_extension(
            cmd,
            client,
            resource_group,
            cluster_name,
            CONST_EXT_INSTALLATION_NAME,
            "managedClusters",
            configuration_settings=config_settings,
            yes=True,
            no_wait=False,
        )

        update_long_op_result = LongRunningOperation(cmd.cli_ctx)(update_result)

        if update_long_op_result.provisioning_state == "Succeeded":
            logger.info("Azure Container Storage successfully installed")
        else:
            if update_long_op_result.error_info is None:
                logger.error("Error setting up Azure Container Storage")
            else:
                logger.error(
                    "Azure Container Storage failed to uninstall "
                    "with the following error in updating ", update_long_op_result.error_info
                )
            raise UnknownError("Azure Container Storage failed to uninstall.")

    # Step 3: If the extension is installed, call delete_k8s_extension
    from azext_k8s_extension.custom import delete_k8s_extension
    delete_result = delete_k8s_extension(
        cmd,
        client,
        resource_group,
        cluster_name,
        CONST_EXT_INSTALLATION_NAME,
        "managedClusters",
        yes=True,
        no_wait=False,
    )

    delete_long_op_result = LongRunningOperation(cmd.cli_ctx)(delete_result)
    if delete_long_op_result is not None:
        logger.error("Uninstallation of {} failed".CONST_EXT_INSTALLATION_NAME)
        raise UnknownError("Azure Container Storage failed to uninstall.")

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
            # NOTE: delete_role_assignments accepts cli_ctx
            # instead of cmd unlike add_role_assignment.
            delete_role_assignments(
                cmd.cli_ctx,
                role,
                kubelet_identity_object_id,
                scope=managed_rg_role_scope,
            )


def _generate_random_storage_pool_name():
    random_name = CONST_STORAGE_POOL_NAME_PREFIX + ''.join(random.choices(string.ascii_lowercase, k=CONST_STORAGE_POOL_RANDOM_LENGTH))
    return random_name


def _get_k8s_extension_module(module_name):
    try:
        # adding the installed extension in the path
        from azure.cli.core.extension.operations import add_extension_to_path
        add_extension_to_path(CONST_K8S_EXTENSION_NAME)
        # import the extension module
        from importlib import import_module
        azext_custom = import_module(module_name)
        return azext_custom
    except ImportError as ie:
        raise CLIInternalError(ie) from ie
