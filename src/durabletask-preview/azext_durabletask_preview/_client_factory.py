# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

def cf_durabletask(cli_ctx, *_):
    from azure.cli.core.commands.client_factory import get_mgmt_service_client
    from azext_durabletask.vendored_sdks import DurabletaskMgmtClient
    return get_mgmt_service_client(cli_ctx, DurabletaskMgmtClient)


def cf_durabletask_namespaces(cli_ctx, *_):
    return cf_durabletask(cli_ctx).namespaces


def cf_durabletask_taskhubs(cli_ctx, *_):
    return cf_durabletask(cli_ctx).task_hubs
