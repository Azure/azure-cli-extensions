# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

def cf_functionapp(cli_ctx, *_):

    from azure.cli.core.commands.client_factory import get_mgmt_service_client
    from azext_functionapp.vendored_sdks import WebSiteManagementClient
    return get_mgmt_service_client(cli_ctx, WebSiteManagementClient)
