# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azext_aks_preview.azurecontainerstorage._consts import (
    CONST_STORAGE_POOL_TYPE_AZURE_DISK,
    CONST_STORAGE_POOL_TYPE_EPHEMERAL_DISK,
)

from azure.cli.core.azclierror import (
    ArgumentUsageError,
    InvalidArgumentValueError,
    MutuallyExclusiveArgumentError,
)

import re


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
            storage_pool_type,
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
    storage_pool_type,
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

    if storage_pool_type is not None:
        raise MutuallyExclusiveArgumentError(
            'Conflicting flags. Cannot define --storage-pool-type value '
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
                "Invalid --storage-pool-name values. "
                "Accepted values are lowercase alphanumeric characters, "
                "'-' or '.', and must start and end with an alphanumeric character.")

    if storage_pool_type != CONST_STORAGE_POOL_TYPE_AZURE_DISK and \
       storage_pool_sku is not None:
        raise ArgumentUsageError('Cannot set --storage-pool-sku when --storage-pool-type is not azureDisk')

    if storage_pool_type != CONST_STORAGE_POOL_TYPE_EPHEMERAL_DISK and \
       storage_pool_option is not None:
        raise ArgumentUsageError('Cannot set --storage-pool-option when --storage-pool-type is not ephemeralDisk')

    if storage_pool_size is not None:
        pattern = r'^\d+(?:Gi|Ti)$'
        match = re.match(pattern, storage_pool_size)
        if match is None:
            raise ArgumentUsageError(
                'Value for --storage-pool-size should be defined '
                'with size followed by Gi or Ti. e.g. 512Gi or 2Ti'
            )
