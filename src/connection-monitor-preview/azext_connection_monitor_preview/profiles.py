# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core.profiles import CustomResourceType

CUSTOM_NW_CONNECTION_MONITOR = CustomResourceType('azext_connection_monitor_preview.vendored_sdks',
                                                  'NetworkManagementClient')
