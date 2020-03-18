# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


def cf_powerbidedicated(cli_ctx, *_):
    from azure.cli.core.commands.client_factory import get_mgmt_service_client
    from .vendored_sdks.powerbidedicated import PowerBIDedicatedManagementClient
    return get_mgmt_service_client(cli_ctx, PowerBIDedicatedManagementClient)


def cf_capacities(cli_ctx, *_):
    return cf_powerbidedicated(cli_ctx).capacities


def cf_operations(cli_ctx, *_):
    return cf_powerbidedicated(cli_ctx).operations
