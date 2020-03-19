# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


def cf_logic(cli_ctx, *_):
    from azure.cli.core.commands.client_factory import get_mgmt_service_client
    from ..vendored_sdks.logic import LogicManagementClient
    return get_mgmt_service_client(cli_ctx, LogicManagementClient)


def cf_workflow(cli_ctx, *_):
    return cf_logic(cli_ctx).workflow


def cf_integration_account(cli_ctx, *_):
    return cf_logic(cli_ctx).integration_account
