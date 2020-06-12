# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core.profiles import CustomResourceType

CUSTOM_VWAN = CustomResourceType('azext_vwan.vendored_sdks.v2018_08_01', 'NetworkManagementClient')
CUSTOM_VHUB_ROUTE_TABLE = CustomResourceType('azext_vwan.vendored_sdks.v2020_04_01', 'NetworkManagementClient')
