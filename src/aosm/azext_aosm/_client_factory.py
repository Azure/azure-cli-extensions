# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core.commands.client_factory import get_mgmt_service_client
from .vendored_sdks import HybridNetworkManagementClient

def cf_aosm(cli_ctx, *_) -> HybridNetworkManagementClient:
    return get_mgmt_service_client(cli_ctx, HybridNetworkManagementClient)
