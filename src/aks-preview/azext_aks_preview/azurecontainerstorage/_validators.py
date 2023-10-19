# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azext_aks_preview.azurecontainerstorage._consts import (
    CONST_STORAGE_POOL_OPTION_SSD,
    CONST_STORAGE_POOL_SKU_PREMIUM_LRS,
    CONST_STORAGE_POOL_SKU_PREMIUM_ZRS,
    CONST_STORAGE_POOL_TYPE_AZURE_DISK,
    CONST_STORAGE_POOL_TYPE_EPHEMERAL_DISK,
    CONST_STORAGE_POOL_TYPE_ELASTIC_SAN,
)

from azure.cli.core.azclierror import (
    ArgumentUsageError,
    InvalidArgumentValueError,
    MutuallyExclusiveArgumentError,
)

from knack.log import get_logger
import re

elastic_san_supported_skus = [
    CONST_STORAGE_POOL_SKU_PREMIUM_LRS,
    CONST_STORAGE_POOL_SKU_PREMIUM_ZRS,
]

logger = get_logger(__name__)


def validate_nodepool_names_with_cluster_nodepools(nodepool_names, agentpool_details):
    nodepool_list = nodepool_names.split(',')
    for nodepool in nodepool_list:
        if nodepool not in agentpool_details:
            raise InvalidArgumentValueError(
                'Nodepool: {} not found. '
                'Please provide existing nodepool names in --azure-container-storage-nodepools.'
                '\nUse command `az nodepool list` to get the list of nodepools in the cluster.'
                '\nAborting installation of Azure Container Storage.'
                .format(nodepool)
            )


def validate_azure_container_storage_params(
    enable_azure_container_storage,
    disable_azure_container_storage,
    storage_pool_name,
    storage_pool_type,
    storage_pool_sku,
    storage_pool_option,
    storage_pool_size,
    nodepool_list,
):
    if enable_azure_container_storage and disable_azure_container_storage:
        raise MutuallyExclusiveArgumentError(
            'Conflicting flags. Cannot set --enable-azure-container-storage '
            'and --disable-azure-container-storage together.'
        )

    if disable_azure_container_storage:
        _validate_disable_azure_container_storage_params(
            storage_pool_name,
            storage_pool_sku,
            storage_pool_option,
            storage_pool_size,
            nodepool_list,
        )

    elif enable_azure_container_storage:
        _validate_enable_azure_container_storage_params(
            storage_pool_name,
            storage_pool_type,
            storage_pool_sku,
            storage_pool_option,
            storage_pool_size,
        )


def _validate_disable_azure_container_storage_params(
    storage_pool_name,
    storage_pool_sku,
    storage_pool_option,
    storage_pool_size,
    nodepool_list,
):
    if storage_pool_name is not None:
        raise MutuallyExclusiveArgumentError(
            'Conflicting flags. Cannot define --storage-pool-name value '
            'when --disable-azure-container-storage is set.'
        )

    if storage_pool_sku is not None:
        raise MutuallyExclusiveArgumentError(
            'Conflicting flags. Cannot define --storage-pool-sku value '
            'when --disable-azure-container-storage is set.'
        )

    if storage_pool_size is not None:
        raise MutuallyExclusiveArgumentError(
            'Conflicting flags. Cannot define --storage-pool-size value '
            'when --disable-azure-container-storage is set.'
        )

    if storage_pool_option is not None:
        raise MutuallyExclusiveArgumentError(
            'Conflicting flags. Cannot define --storage-pool-option value '
            'when --disable-azure-container-storage is set.'
        )

    if nodepool_list is not None:
        raise MutuallyExclusiveArgumentError(
            'Conflicting flags. Cannot define --azure-container-storage-nodepools value '
            'when --disable-azure-container-storage is set.'
        )


def _validate_enable_azure_container_storage_params(
    storage_pool_name,
    storage_pool_type,
    storage_pool_sku,
    storage_pool_option,
    storage_pool_size,
):
    if storage_pool_name is not None:
        pattern = r'[a-z0-9]([-a-z0-9]*[a-z0-9])?(\.[a-z0-9]([-a-z0-9]*[a-z0-9])?)*'
        is_pool_name_valid = re.fullmatch(pattern, storage_pool_name)
        if not is_pool_name_valid:
            raise InvalidArgumentValueError(
                "Invalid --storage-pool-name value. "
                "Accepted values are lowercase alphanumeric characters, "
                "'-' or '.', and must start and end with an alphanumeric character.")

    if storage_pool_sku is not None:
        if storage_pool_type == CONST_STORAGE_POOL_TYPE_EPHEMERAL_DISK:
            raise ArgumentUsageError('Cannot set --storage-pool-sku when --enable-azure-container-storage is ephemeralDisk.')
        elif storage_pool_type == CONST_STORAGE_POOL_TYPE_ELASTIC_SAN and \
                storage_pool_sku not in elastic_san_supported_skus:
            supported_skus_str = ", ".join(elastic_san_supported_skus)
            raise ArgumentUsageError(
                'Invalid --storage-pool-sku value. '
                'Supported value for --storage-pool-sku are {0} '
                'when --enable-azure-container-storage is set to elasticSan.'
                .format(supported_skus_str)
            )

    if storage_pool_type != CONST_STORAGE_POOL_TYPE_EPHEMERAL_DISK and \
       storage_pool_option is not None:
        raise ArgumentUsageError('Cannot set --storage-pool-option when --enable-azure-container-storage is not ephemeralDisk.')

    if storage_pool_type == CONST_STORAGE_POOL_TYPE_EPHEMERAL_DISK and \
       storage_pool_option == CONST_STORAGE_POOL_OPTION_SSD:
        raise ArgumentUsageError(
            '--storage-pool-option Temp storage (SSD) currently not supported.'
        )

    if storage_pool_size is not None:
        pattern = r'^\d+(\.\d+)?[GT]i$'
        match = re.match(pattern, storage_pool_size)
        if match is None:
            raise ArgumentUsageError(
                'Value for --storage-pool-size should be defined '
                'with size followed by Gi or Ti e.g. 512Gi or 2Ti.'
            )

        else:
            if storage_pool_type == CONST_STORAGE_POOL_TYPE_ELASTIC_SAN:
                pool_size_qty = float(storage_pool_size[:-2])
                pool_size_unit = storage_pool_size[-2:]

                if (
                    (pool_size_unit == "Gi" and pool_size_qty < 1024) or
                    (pool_size_unit == "Ti" and pool_size_qty < 1)
                ):
                    raise ArgumentUsageError(
                        'Value for --storage-pool-size must be at least 1Ti when '
                        '--enable-azure-container-storage is elasticSan.')

            elif storage_pool_type == CONST_STORAGE_POOL_TYPE_EPHEMERAL_DISK:
                logger.warning(
                    'Storage pools using Ephemeral disk use all capacity available on the local device. '
                    ' --storage-pool-size will be ignored.'
                )
