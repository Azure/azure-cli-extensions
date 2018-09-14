# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core.profiles import CustomResourceType


CUSTOM_DATA_STORAGE = CustomResourceType('azext_storage_preview.vendored_sdks.azure_storage', None)
CUSTOM_MGMT_STORAGE = CustomResourceType('azext_storage_preview.vendored_sdks.azure_mgmt_storage',
                                         'StorageManagementClient')
CUSTOM_MGMT_STORAGE_PREVIEW = CustomResourceType('azext_storage_preview.vendored_sdks.azure_mgmt_preview_storage',
                                                 'StorageManagementClient')
