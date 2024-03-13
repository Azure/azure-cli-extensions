# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core.azclierror import UnknownError
from azure.cli.core.commands import LongRunningOperation
from azext_aks_preview.azurecontainerstorage._consts import (
    CONST_ACSTOR_K8S_EXTENSION_NAME,
    CONST_EXT_INSTALLATION_NAME,
    CONST_K8S_EXTENSION_CLIENT_FACTORY_MOD_NAME,
    CONST_K8S_EXTENSION_CUSTOM_MOD_NAME,
    CONST_STORAGE_POOL_DEFAULT_SIZE,
    CONST_STORAGE_POOL_DEFAULT_SIZE_ESAN,
    CONST_STORAGE_POOL_OPTION_NVME,
    CONST_STORAGE_POOL_OPTION_SSD,
    CONST_STORAGE_POOL_SKU_PREMIUM_LRS,
    CONST_ACSTOR_ALL,
    CONST_STORAGE_POOL_TYPE_AZURE_DISK,
    CONST_STORAGE_POOL_TYPE_ELASTIC_SAN,
    CONST_STORAGE_POOL_TYPE_EPHEMERAL_DISK,
)
from azext_aks_preview.azurecontainerstorage._helpers import (
    get_k8s_extension_module,
    get_current_resource_value_args,
    get_desired_resource_value_args,
    get_initial_resource_value_args,
    perform_role_operations_on_managed_rg,
    validate_storagepool_creation,
)
from knack.log import get_logger

logger = get_logger(__name__)


def perform_enable_azure_container_storage( # pylint: disable=too-many-statements,too-many-locals
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
    acstor_nodepool_skus,
    is_cluster_create,
    is_extension_installed=False,
    is_azureDisk_enabled=False,
    is_elasticSan_enabled=False,
    is_ephemeralDisk_localssd_enabled=False,
    is_ephemeralDisk_nvme_enabled=False,
    current_core_value=None,
):
    # Step 1: Validate if storagepool could be created.
    # Depends on the following:
    #   1a: Grant AKS cluster's node identity the following
    #       roles on the AKS managed resource group:
    #       1. Reader
    #       2. Network Contributor
    #       3. Elastic SAN Owner
    #       4. Elastic SAN Volume Group Owner
    #       Azure Container Storage Operator (replace)
    #       Ensure grant was successful if creation of
    #       Elastic SAN storagepool is requested.
    validate_storagepool_creation(
        cmd,
        subscription_id,
        node_resource_group,
        kubelet_identity_object_id,
        storage_pool_type,
    )

    # Step 2: Configure the storagepool parameters
    config_settings = []
    if storage_pool_name is None:
        storage_pool_name = storage_pool_type.lower()
        if storage_pool_type == CONST_STORAGE_POOL_TYPE_EPHEMERAL_DISK:
            storage_pool_name = storage_pool_type.lower() + "-" + storage_pool_option.lower()
    if storage_pool_size is None:
        storage_pool_size = CONST_STORAGE_POOL_DEFAULT_SIZE_ESAN if \
            storage_pool_type == CONST_STORAGE_POOL_TYPE_ELASTIC_SAN else \
            CONST_STORAGE_POOL_DEFAULT_SIZE

    # If enabling of storagepool type in Azure Container Storage failed,
    # define the existing resource values for ioEngine and hugepages for
    # resetting the cluster state.
    default_resource_args = get_current_resource_value_args(
        is_azureDisk_enabled,
        is_elasticSan_enabled,
        is_ephemeralDisk_localssd_enabled,
        is_ephemeralDisk_nvme_enabled,
        current_core_value,
    )

    default_cluster_settings = _get_cluster_state_fields(
        is_elasticSan_enabled,
        is_azureDisk_enabled,
        is_ephemeralDisk_localssd_enabled,
        is_ephemeralDisk_nvme_enabled,
    )

    if storage_pool_type == CONST_STORAGE_POOL_TYPE_EPHEMERAL_DISK:
        if storage_pool_option == CONST_STORAGE_POOL_OPTION_NVME:
            is_ephemeralDisk_nvme_enabled = True
        elif storage_pool_option == CONST_STORAGE_POOL_OPTION_SSD:
            is_ephemeralDisk_localssd_enabled = True
        config_settings.append({"global.cli.storagePool.install.diskType": storage_pool_option.lower()})
    else:
        if storage_pool_sku is None:
            storage_pool_sku = CONST_STORAGE_POOL_SKU_PREMIUM_LRS
        if storage_pool_type == CONST_STORAGE_POOL_TYPE_ELASTIC_SAN:
            config_settings.append({"global.cli.storagePool.elasticSan.sku": storage_pool_sku})
            is_elasticSan_enabled = True
        elif storage_pool_type == CONST_STORAGE_POOL_TYPE_AZURE_DISK:
            config_settings.append({"global.cli.storagePool.azureDisk.sku": storage_pool_sku})
            is_azureDisk_enabled = True
        config_settings.append({"global.cli.storagePool.install.diskType": ""})

    config_settings.extend(
        [
            {"global.cli.activeControl": True},
            {"global.cli.storagePool.install.create": True},
            {"global.cli.storagePool.install.name": storage_pool_name},
            {"global.cli.storagePool.install.size": storage_pool_size},
            {"global.cli.storagePool.install.type": storage_pool_type},
            # Always set cli.storagePool.disable.type to empty
            # and cli.storagePool.disable.validation to False
            # during enable operation so that any older disable
            # operation doesn't interfere with the current state.
            {"global.cli.storagePool.disable.validation": False},
            {"global.cli.storagePool.disable.type": ""},
            {"global.cli.storagePool.disable.active": False},
        ]
    )

    config_settings.extend(
        _get_cluster_state_fields(
            is_elasticSan_enabled,
            is_azureDisk_enabled,
            is_ephemeralDisk_localssd_enabled,
            is_ephemeralDisk_nvme_enabled,
        )
    )

    # Step 5: Install the k8s_extension 'microsoft.azurecontainerstorage'
    client_factory = get_k8s_extension_module(CONST_K8S_EXTENSION_CLIENT_FACTORY_MOD_NAME)
    client = client_factory.cf_k8s_extension_operation(cmd.cli_ctx)
    k8s_extension_custom_mod = get_k8s_extension_module(CONST_K8S_EXTENSION_CUSTOM_MOD_NAME)
    update_settings = [
        {"global.cli.activeControl": True},
        {"global.cli.storagePool.install.create": False},
        {"global.cli.storagePool.install.name": ""},
        {"global.cli.storagePool.install.size": ""},
        {"global.cli.storagePool.install.type": ""},
        {"global.cli.storagePool.install.diskType": ""},
    ]
    update_post_enable = False
    try:
        if is_extension_installed:
            config_settings.extend(
                get_desired_resource_value_args(
                    storage_pool_type,
                    storage_pool_option,
                    current_core_value,
                    is_azureDisk_enabled,
                    is_elasticSan_enabled,
                    is_ephemeralDisk_localssd_enabled,
                    is_ephemeralDisk_nvme_enabled,
                    acstor_nodepool_skus,
                    True,
                )
            )
            result = k8s_extension_custom_mod.update_k8s_extension(
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
            op_text = "Azure Container Storage successfully updated"
        else:
            config_settings.extend(
                get_initial_resource_value_args(
                    storage_pool_type,
                    storage_pool_option,
                    acstor_nodepool_skus,
                )
            )
            result = k8s_extension_custom_mod.create_k8s_extension(
                cmd,
                client,
                resource_group,
                cluster_name,
                CONST_EXT_INSTALLATION_NAME,
                "managedClusters",
                CONST_ACSTOR_K8S_EXTENSION_NAME,
                auto_upgrade_minor_version=True,
                release_train="stable",
                scope="cluster",
                release_namespace="acstor",
                configuration_settings=config_settings,
            )
            op_text = "Azure Container Storage successfully installed"

        long_op_result = LongRunningOperation(cmd.cli_ctx)(result)
        if long_op_result.provisioning_state == "Succeeded":
            logger.warning(op_text)
            update_post_enable = True
    except Exception as ex:  # pylint: disable=broad-except
        if is_cluster_create:
            logger.error("Azure Container Storage failed to install.\nError: %s", ex)
            logger.warning(
                "AKS cluster is created. "
                "Please run `az aks update` along with `--enable-azure-container-storage` "
                "to enable Azure Container Storage."
            )
        elif is_extension_installed:
            logger.error(
                "AKS update to enable Azure Container Storage pool type %s failed.\n"
                "Error: %s. Resetting cluster state.", storage_pool_type, ex
            )

            update_settings.extend(default_resource_args)
            update_settings.extend(default_cluster_settings)
            update_post_enable = True
        else:
            logger.error("AKS update to enable Azure Container Storage failed.\nError: %s", ex)

    if update_post_enable:
        k8s_extension_custom_mod.update_k8s_extension(
            cmd,
            client,
            resource_group,
            cluster_name,
            CONST_EXT_INSTALLATION_NAME,
            "managedClusters",
            configuration_settings=update_settings,
            yes=True,
            no_wait=True,
        )


def perform_disable_azure_container_storage( # pylint: disable=too-many-statements,too-many-locals
    cmd,
    subscription_id,
    resource_group,
    cluster_name,
    node_resource_group,
    kubelet_identity_object_id,
    perform_validation,
    storage_pool_type,
    storage_pool_option,
    is_elasticSan_enabled,
    is_azureDisk_enabled,
    is_ephemeralDisk_localssd_enabled,
    is_ephemeralDisk_nvme_enabled,
    current_core_value,
):
    client_factory = get_k8s_extension_module(CONST_K8S_EXTENSION_CLIENT_FACTORY_MOD_NAME)
    client = client_factory.cf_k8s_extension_operation(cmd.cli_ctx)
    k8s_extension_custom_mod = get_k8s_extension_module(CONST_K8S_EXTENSION_CUSTOM_MOD_NAME)
    no_wait_delete_op = False

    # Step 1: Perform validation if accepted by user
    if perform_validation:
        _perform_validations_before_disable(
            cmd,
            client,
            k8s_extension_custom_mod,
            resource_group,
            cluster_name,
            storage_pool_type,
            storage_pool_option,
            is_elasticSan_enabled,
            is_azureDisk_enabled,
            is_ephemeralDisk_localssd_enabled,
            is_ephemeralDisk_nvme_enabled,
        )
        # Since, pre uninstall validation will ensure deletion of storagepools,
        # we don't need to long wait while performing the delete operation.
        # Setting no_wait_delete_op = True.
        # Only relevant when we are uninstalling Azure Container Storage completely.
        if storage_pool_type == CONST_ACSTOR_ALL:
            no_wait_delete_op = True

    # Step 2: If the extension is installed and validation succeeded or skipped,
    # if we want to uninstall Azure Container Storage completely, then call
    # delete_k8s_extension. Else, if we want to disable a storagepool type,
    # we will perform another update_k8s_extension operation on the cluster.

    if storage_pool_type == CONST_ACSTOR_ALL:
        # Uninstallation operation
        try:
            result = k8s_extension_custom_mod.delete_k8s_extension(
                cmd,
                client,
                resource_group,
                cluster_name,
                CONST_EXT_INSTALLATION_NAME,
                "managedClusters",
                yes=True,
                no_wait=no_wait_delete_op,
            )

            if not no_wait_delete_op:
                LongRunningOperation(cmd.cli_ctx)(result)
        except Exception as delete_ex:
            raise UnknownError(
                "Failure observed while disabling Azure Container Storage."
            ) from delete_ex

        logger.warning("Azure Container Storage has been disabled.")

        # Revoke role assignments irrespective of whether ElasticSAN
        # type was enabled on the cluster to handle older clusters where
        # the role assignments were done for all storagepool type during
        # installation of Azure Container Storage.
        perform_role_operations_on_managed_rg(
            cmd,
            subscription_id,
            node_resource_group,
            kubelet_identity_object_id,
            False
        )
    else:
        # If disabling type of storagepool in Azure Container Storage failed,
        # define the existing resource values for ioEngine and hugepages for
        # resetting the cluster state.
        default_resource_args = get_current_resource_value_args(
            is_azureDisk_enabled,
            is_elasticSan_enabled,
            is_ephemeralDisk_localssd_enabled,
            is_ephemeralDisk_nvme_enabled,
            current_core_value,
        )

        default_cluster_settings = _get_cluster_state_fields(
            is_elasticSan_enabled,
            is_azureDisk_enabled,
            is_ephemeralDisk_localssd_enabled,
            is_ephemeralDisk_nvme_enabled,
        )

        config_settings = [
            {"global.cli.storagePool.disable.validation": False},
            {"global.cli.storagePool.disable.type": storage_pool_type},
            {"global.cli.storagePool.disable.active": True},
            # Ensure that all the install storagepool fields are turned off.
            {"global.cli.activeControl": True},
            {"global.cli.storagePool.install.create": False},
            {"global.cli.storagePool.install.name": ""},
            {"global.cli.storagePool.install.size": ""},
            {"global.cli.storagePool.install.type": ""},
            {"global.cli.storagePool.install.diskType": ""},
        ]

        # Disabling a particular type of storagepool.
        if storage_pool_type == CONST_STORAGE_POOL_TYPE_AZURE_DISK:
            config_settings.append({"global.cli.storagePool.disable.diskType": ""})
            is_azureDisk_enabled = False
        elif storage_pool_type == CONST_STORAGE_POOL_TYPE_ELASTIC_SAN:
            config_settings.append({"global.cli.storagePool.disable.diskType": ""})
            is_elasticSan_enabled = False
        elif storage_pool_type == CONST_STORAGE_POOL_TYPE_EPHEMERAL_DISK:
            if storage_pool_option is None:
                if is_ephemeralDisk_nvme_enabled:
                    is_ephemeralDisk_nvme_enabled = False
                    config_settings.append(
                        {"global.cli.storagePool.disable.diskType": CONST_STORAGE_POOL_OPTION_NVME.lower()}
                    )
                elif is_ephemeralDisk_localssd_enabled:
                    is_ephemeralDisk_localssd_enabled = False
                    config_settings.append(
                        {"global.cli.storagePool.disable.diskType": CONST_STORAGE_POOL_OPTION_SSD.lower()}
                    )
            elif storage_pool_option == CONST_STORAGE_POOL_OPTION_NVME:
                is_ephemeralDisk_nvme_enabled = False
                config_settings.append(
                    {"global.cli.storagePool.disable.diskType": CONST_STORAGE_POOL_OPTION_NVME.lower()}
                )
            elif storage_pool_option == CONST_STORAGE_POOL_OPTION_SSD:
                is_ephemeralDisk_localssd_enabled = False
                config_settings.append(
                    {"global.cli.storagePool.disable.diskType": CONST_STORAGE_POOL_OPTION_SSD.lower()}
                )
            elif storage_pool_option == CONST_ACSTOR_ALL:
                is_ephemeralDisk_nvme_enabled = False
                is_ephemeralDisk_localssd_enabled = False
                config_settings.append(
                    {"global.cli.storagePool.disable.diskType": CONST_ACSTOR_ALL.lower()}
                )

        config_settings.extend(
            _get_cluster_state_fields(
                is_elasticSan_enabled,
                is_azureDisk_enabled,
                is_ephemeralDisk_localssd_enabled,
                is_ephemeralDisk_nvme_enabled,
            )
        )

        # Add the new resource values for ioEngine and hugepages.
        config_settings.extend(
            get_desired_resource_value_args(
                storage_pool_type,
                storage_pool_option,
                current_core_value,
                is_azureDisk_enabled,
                is_elasticSan_enabled,
                is_ephemeralDisk_localssd_enabled,
                is_ephemeralDisk_nvme_enabled,
                None,
                False,
            )
        )
        # Creating the set of config settings which
        # are required to demarcate that the disabling
        # process is completed. This config variable
        # will be used after the disabling operation is completed.
        update_settings = [
            {"global.cli.activeControl": True},
            {"global.cli.storagePool.disable.validation": False},
            {"global.cli.storagePool.disable.type": ""},
            {"global.cli.storagePool.disable.active": False},
            {"global.cli.storagePool.disable.diskType": ""},
            # Ensure that all the install storagepool fields are turned off.
            {"global.cli.storagePool.install.create": False},
            {"global.cli.storagePool.install.name": ""},
            {"global.cli.storagePool.install.size": ""},
            {"global.cli.storagePool.install.type": ""},
            {"global.cli.storagePool.install.diskType": ""},
        ]

        disable_op_failure = False
        try:
            result = k8s_extension_custom_mod.update_k8s_extension(
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
            LongRunningOperation(cmd.cli_ctx)(result)
            # Set the types of storagepool type states in the cluster
            # based on whether the previous operation succeeded or failed.
            update_settings.extend(
                _get_cluster_state_fields(
                    is_elasticSan_enabled,
                    is_azureDisk_enabled,
                    is_ephemeralDisk_localssd_enabled,
                    is_ephemeralDisk_nvme_enabled,
                )
            )

            # Revoke role assignments if we are disabling ElasticSAN storagepool type.
            if storage_pool_type == CONST_STORAGE_POOL_TYPE_ELASTIC_SAN and is_elasticSan_enabled:
                perform_role_operations_on_managed_rg(
                    cmd,
                    subscription_id,
                    node_resource_group,
                    kubelet_identity_object_id,
                    False
                )
        except Exception as disable_ex: # pylint: disable=broad-except
            logger.error(
                "Failure observed while disabling Azure Container Storage storagepool type: %s.\nError: %s"
                "Resetting cluster state.", storage_pool_type, disable_ex
            )

            update_settings.extend(default_resource_args)
            update_settings.extend(default_cluster_settings)
            disable_op_failure = True

        # Since we are just resetting the cluster state,
        # we are going to perform a non waiting operation.
        k8s_extension_custom_mod.update_k8s_extension(
            cmd,
            client,
            resource_group,
            cluster_name,
            CONST_EXT_INSTALLATION_NAME,
            "managedClusters",
            configuration_settings=update_settings,
            yes=True,
            no_wait=True,
        )

        if not disable_op_failure:
            logger.warning("Azure Container Storage storagepool type %s has been disabled.", storage_pool_type)


def _perform_validations_before_disable(
    cmd,
    client,
    k8s_extension_custom_mod,
    resource_group,
    cluster_name,
    storage_pool_type,
    storage_pool_option,
    is_elasticSan_enabled,
    is_azureDisk_enabled,
    is_ephemeralDisk_localssd_enabled,
    is_ephemeralDisk_nvme_enabled,
):
    pool_option = ""
    if storage_pool_type == CONST_STORAGE_POOL_TYPE_EPHEMERAL_DISK:
        if storage_pool_option is not None:
            pool_option = storage_pool_option.lower()
        else:
            if is_ephemeralDisk_nvme_enabled:
                pool_option = CONST_STORAGE_POOL_OPTION_NVME.lower()
            elif is_ephemeralDisk_localssd_enabled:
                pool_option = CONST_STORAGE_POOL_OPTION_SSD.lower()

    cluster_settings = _get_cluster_state_fields(
        is_elasticSan_enabled,
        is_azureDisk_enabled,
        is_ephemeralDisk_localssd_enabled,
        is_ephemeralDisk_nvme_enabled,
    )
    config_settings = [
        {"global.cli.storagePool.disable.validation": True},
        {"global.cli.storagePool.disable.type": storage_pool_type},
        {"global.cli.storagePool.disable.active": False},
        {"global.cli.storagePool.disable.diskType": pool_option.lower()},
        # Ensure that all the install storagepool fields are turned off.
        {"global.cli.activeControl": True},
        {"global.cli.storagePool.install.create": False},
        {"global.cli.storagePool.install.name": ""},
        {"global.cli.storagePool.install.size": ""},
        {"global.cli.storagePool.install.type": ""},
        {"global.cli.storagePool.install.diskType": ""},
    ]

    config_settings.extend(cluster_settings)

    try:
        result = k8s_extension_custom_mod.update_k8s_extension(
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

        long_op_result = LongRunningOperation(cmd.cli_ctx)(result)
        if long_op_result.provisioning_state == "Succeeded":
            logger.warning("Validation succeeded. Continuing Azure Container Storage disable operation...")
    except Exception as ex:  # pylint: disable=broad-except
        config_settings = [
            {"global.cli.storagePool.disable.validation": False},
            {"global.cli.storagePool.disable.type": ""},
            {"global.cli.storagePool.disable.active": False},
            {"global.cli.storagePool.disable.diskType": ""},
            # Ensure that all the install storagepool fields are turned off.
            {"global.cli.activeControl": True},
            {"global.cli.storagePool.install.create": False},
            {"global.cli.storagePool.install.name": ""},
            {"global.cli.storagePool.install.size": ""},
            {"global.cli.storagePool.install.type": ""},
            {"global.cli.storagePool.install.diskType": ""},
        ]

        cluster_settings = _get_cluster_state_fields(
            is_elasticSan_enabled,
            is_azureDisk_enabled,
            is_ephemeralDisk_localssd_enabled,
            is_ephemeralDisk_nvme_enabled,
        )

        config_settings.extend(cluster_settings)

        err_msg = (
            "Validation failed. "
            "Please ensure that storagepools are not being used. "
            "Unable to perform disable Azure Container Storage operation. "
            "Resetting cluster state."
        )

        if storage_pool_type != CONST_ACSTOR_ALL:
            err_msg = (
                "Validation failed. "
                f"Please ensure that storagepools of type {storage_pool_type} are not being used. "
                f"Unable to perform disable Azure Container Storage operation. "
                "Resetting cluster state."
            )

        k8s_extension_custom_mod.update_k8s_extension(
            cmd,
            client,
            resource_group,
            cluster_name,
            CONST_EXT_INSTALLATION_NAME,
            "managedClusters",
            configuration_settings=config_settings,
            yes=True,
            no_wait=True,
        )

        if "pre-upgrade hooks failed" in str(ex):
            raise UnknownError(err_msg) from ex
        raise UnknownError(
            "Validation failed. Unable to perform Azure Container Storage operation. Resetting cluster state."
        ) from ex


def _get_cluster_state_fields(
    is_elasticSan_enabled,
    is_azureDisk_enabled,
    is_ephemeralDisk_localssd_enabled,
    is_ephemeralDisk_nvme_enabled,
):

    cluster_settings = [
        {"global.cli.storagePool.azureDisk.enabled": is_azureDisk_enabled},
        {"global.cli.storagePool.elasticSan.enabled": is_elasticSan_enabled},
        {"global.cli.storagePool.ephemeralDisk.nvme.enabled": is_ephemeralDisk_nvme_enabled},
        {"global.cli.storagePool.ephemeralDisk.temp.enabled": is_ephemeralDisk_localssd_enabled},
    ]

    return cluster_settings
