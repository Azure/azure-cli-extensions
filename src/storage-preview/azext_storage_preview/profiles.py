# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core.profiles import CustomResourceType, ResourceType


CUSTOM_DATA_STORAGE = CustomResourceType('azext_storage_preview.azure_storage', None)
# CUSTOM_DATA_STORAGE = ResourceType.DATA_STORAGE
