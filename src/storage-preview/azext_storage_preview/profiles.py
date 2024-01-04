# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core.profiles import CustomResourceType


CUSTOM_DATA_STORAGE = CustomResourceType('azext_storage_preview.vendored_sdks.azure_storage', None)
CUSTOM_DATA_STORAGE_ADLS = CustomResourceType('azext_storage_preview.vendored_sdks.azure_adls_storage_preview', None)
CUSTOM_MGMT_STORAGE = CustomResourceType('azext_storage_preview.vendored_sdks.azure_mgmt_storage',
                                         'StorageManagementClient')
CUSTOM_DATA_STORAGE_FILESHARE = CustomResourceType('azext_storage_preview.vendored_sdks.azure_storagev2.fileshare',
                                                   None)
CUSTOM_DATA_STORAGE_FILEDATALAKE = CustomResourceType('azext_storage_preview.vendored_sdks.azure_storage_filedatalake',
                                                      None)
CUSTOM_DATA_STORAGE_BLOB = CustomResourceType('azext_storage_preview.vendored_sdks.azure_storagev2.blob', None)
