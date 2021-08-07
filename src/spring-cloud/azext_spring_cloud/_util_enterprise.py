# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=wrong-import-order

from .vendored_sdks.appplatform.v2022_05_01_preview import AppPlatformManagementClient
from .vendored_sdks.appplatform.v2020_07_01 import (
    AppPlatformManagementClient as AppPlatformManagementClient_20200701)
from azure.cli.core.commands.client_factory import get_mgmt_service_client

def is_enterprise_tier(cmd, resource_group, name):
    resource = get_mgmt_service_client(cmd.cli_ctx, AppPlatformManagementClient_20200701).services.get(resource_group, name)
    return resource.sku.name == 'E0'

def get_client(cmd):
    return get_mgmt_service_client(cmd.cli_ctx, AppPlatformManagementClient)