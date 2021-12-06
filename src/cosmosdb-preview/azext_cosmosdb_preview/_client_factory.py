# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


def cf_cosmosdb_preview(cli_ctx, *_):
    from azure.cli.core.commands.client_factory import get_mgmt_service_client
    from azext_cosmosdb_preview.vendored_sdks.azure_mgmt_cosmosdb import CosmosDBManagementClient
    return get_mgmt_service_client(cli_ctx, CosmosDBManagementClient)


def cf_graph_resources(cli_ctx, _):
    return cf_cosmosdb_preview(cli_ctx).graph_resources


def cf_service(cli_ctx, _):
    return cf_cosmosdb_preview(cli_ctx).service


def cf_cassandra_cluster(cli_ctx, _):
    return cf_cosmosdb_preview(cli_ctx).cassandra_clusters


def cf_cassandra_data_center(cli_ctx, _):
    return cf_cosmosdb_preview(cli_ctx).cassandra_data_centers
