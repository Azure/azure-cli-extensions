# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


def cf_amg(cli_ctx, subscription, *_):
    # pylint: disable=unused-argument
    from azure.cli.core.commands.client_factory import get_mgmt_service_client
    from azext_amg.vendored_sdks import DashboardManagementClient
    return get_mgmt_service_client(cli_ctx, DashboardManagementClient, subscription_id=subscription)
