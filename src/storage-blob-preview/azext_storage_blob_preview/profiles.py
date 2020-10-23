# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core.profiles import CustomResourceType

CUSTOM_DATA_STORAGE_BLOB = CustomResourceType('azext_storage_blob_preview.vendored_sdks.azure_storage_blob',
                                              'BlobClient')
CUSTOM_MGMT_STORAGE = CustomResourceType('azext_storage_blob_preview.vendored_sdks.azure_mgmt_storage',
                                         'StorageManagementClient')
