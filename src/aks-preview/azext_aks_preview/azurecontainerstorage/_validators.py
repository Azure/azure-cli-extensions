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
    MutuallyExclusiveArgumentError,
)

import re

def validate_azure_container_storage_params(
    enable_azure_container_storage,
    disable_azure_container_storage,
    storage_pool_type,
    storage_pool_sku,
    storage_pool_option,
    storage_pool_size,
):
    if enable_azure_container_storage and disable_azure_container_storage:
        raise MutuallyExclusiveArgumentError(
            'Conflicting flags. Cannot set --enable-azure-container-storage '
            'and --disable-azure-container-storage together.'
        )

    if disable_azure_container_storage:
        if storage_pool_type is not None:
            raise MutuallyExclusiveArgumentError(
                'Conflicting flags. Cannot define --pool-type value '
                'when --disable-azure-container-storage is set.'
            )

        if storage_pool_sku is not None:
            raise MutuallyExclusiveArgumentError(
                'Conflicting flags. Cannot define --pool-sku value '
                'when --disable-azure-container-storage is set.'
            )

        if storage_pool_size is not None:
            raise MutuallyExclusiveArgumentError(
                'Conflicting flags. Cannot define --pool-size value '
                'when --disable-azure-container-storage is set.'
            )

        if storage_pool_option is not None:
            raise MutuallyExclusiveArgumentError(
                'Conflicting flags. Cannot define --pool-option value '
                'when --disable-azure-container-storage is set.'
            )

        return

    if storage_pool_type != CONST_STORAGE_POOL_TYPE_AZURE_DISK and \
       storage_pool_sku is not None:
        raise ArgumentUsageError('Cannot set --pool-sku when --pool-type is not azureDisk')

    if storage_pool_type != CONST_STORAGE_POOL_TYPE_EPHEMERAL_DISK and \
       storage_pool_sku is not None:
        raise ArgumentUsageError('Cannot set --pool-option when --pool-type is not ephemeralDisk')

    if storage_pool_size is not None:
        pattern = r'^\d+(?:Gi|Ti)$'
        match = re.match(pattern, storage_pool_size)
        if match is None:
            raise ArgumentUsageError(
                'Value for --pool-size should be defined '
                'with size followed by Gi or Ti. e.g. 512Gi or 2Ti'
            )