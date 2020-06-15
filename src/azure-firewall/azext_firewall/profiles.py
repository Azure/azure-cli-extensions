# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core.profiles import CustomResourceType

CUSTOM_FIREWALL = CustomResourceType('azext_firewall.vendored_sdks.v2019_11_01', 'NetworkManagementClient')
CUSTOM_FIREWALL_POLICY = CustomResourceType('azext_firewall.vendored_sdks.v2020_05_01', 'NetworkManagementClient')
