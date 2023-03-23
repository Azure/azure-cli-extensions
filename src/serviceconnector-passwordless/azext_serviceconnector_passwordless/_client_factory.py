# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


def cf_connection_cl(cli_ctx, *_):
    from azure.mgmt.servicelinker import ServiceLinkerManagementClient
    from .client_factory_util import get_mgmt_service_client
    from .config import NAME, VERSION
    cli_ctx.data['command_extension_name'] = NAME
    cli_ctx.data['command_extension_version'] = VERSION
    return get_mgmt_service_client(cli_ctx, ServiceLinkerManagementClient,
                                   subscription_bound=False, api_version="2022-11-01-preview")


def cf_linker(cli_ctx, *_):
    return cf_connection_cl(cli_ctx).linker


def cf_connector(cli_ctx, *_):
    return cf_connection_cl(cli_ctx).connector


