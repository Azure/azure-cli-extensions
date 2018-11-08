# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core.profiles import CustomResourceType

CUSTOM_VNET_TAP = CustomResourceType('azext_vnettap.vendored_sdks', 'NetworkManagementClient')
