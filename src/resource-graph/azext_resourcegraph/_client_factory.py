# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


def cf_resource_graph(cli_ctx, _):
    from azure.cli.core.commands.client_factory import get_mgmt_service_client
    from .vendored_sdks.resourcegraph import ResourceGraphClient
    return get_mgmt_service_client(cli_ctx, ResourceGraphClient)


def cf_resource_graph_graph_query(cli_ctx, _):
    return cf_resource_graph(cli_ctx, _).graph_query
