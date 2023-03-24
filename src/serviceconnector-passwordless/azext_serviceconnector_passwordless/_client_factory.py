# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


# pylint: disable=consider-using-f-string
def cf_connection_cl(cli_ctx, *_):
    from azure.mgmt.servicelinker import ServiceLinkerManagementClient
    from azure.cli.core.commands.client_factory import get_mgmt_service_client, get_az_user_agent
    from azure.core.pipeline import policies
    from .config import NAME, VERSION

    user_agent_policy = policies.UserAgentPolicy(
        user_agent=get_az_user_agent())
    user_agent_policy.add_user_agent(
        "CliExtension/{}({})".format(NAME, VERSION))
    return get_mgmt_service_client(cli_ctx, ServiceLinkerManagementClient,
                                   subscription_bound=False, api_version="2022-11-01-preview",
                                   user_agent_policy=user_agent_policy)


def cf_linker(cli_ctx, *_):
    return cf_connection_cl(cli_ctx).linker


def cf_connector(cli_ctx, *_):
    return cf_connection_cl(cli_ctx).connector
