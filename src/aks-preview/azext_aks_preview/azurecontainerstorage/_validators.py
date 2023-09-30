# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azext_aks_preview.azurecontainerstorage._consts import (
	CONST_STORAGE_POOL_TYPE_AZURE_DISK,
	CONST_STORAGE_POOL_TYPE_EPHEMERAL_DISK,
)

from azure.cli.core.azclierror import ArgumentUsageError

def validate_azure_container_storage_params(
    storage_pool_type,
    storage_pool_sku,
    storage_pool_option,
):
	if storage_pool_type != CONST_STORAGE_POOL_TYPE_AZURE_DISK and
		storage_pool_sku != None:
		raise ArgumentUsageError('Cannot set --pool-sku when --pool-type is not azureDisk')

	if storage_pool_type != CONST_STORAGE_POOL_TYPE_EPHEMERAL_DISK and
		storage_pool_sku != None:
		raise ArgumentUsageError('Cannot set --pool-option when --pool-type is not ephemeralDisk')