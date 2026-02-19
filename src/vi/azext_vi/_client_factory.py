# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core.commands.client_factory import get_mgmt_service_client


def cf_vi(cli_ctx, *_):
    from .vendored_sdks import VIManagementClient
    return get_mgmt_service_client(cli_ctx, VIManagementClient)
