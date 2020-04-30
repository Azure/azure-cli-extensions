# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


def cf_log_analytics_solution(cli_ctx, *_):
    from azure.cli.core.commands.client_factory import get_mgmt_service_client
    from .vendored_sdks.operationsmanagement import OperationsManagementClient
    return get_mgmt_service_client(cli_ctx, OperationsManagementClient, provider_name="Microsoft.OperationsManagement",
                                   resource_type="solutions", resource_name="")


def cf_solutions(cli_ctx, *_):
    return cf_log_analytics_solution(cli_ctx, *_).solutions
