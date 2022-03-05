# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

def cf_ags(cli_ctx, *_):
    # pylint: disable=unused-argument
    from azure.cli.core.commands.client_factory import get_mgmt_service_client
    from azext_ags.vendored_sdks import DashboardManagementClient
    return get_mgmt_service_client(cli_ctx, DashboardManagementClient)
