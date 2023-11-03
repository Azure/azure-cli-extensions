# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


def cf_cosmosdb_preview(cli_ctx, *_):
    from azure.cli.core.commands.client_factory import get_mgmt_service_client
    from azext_cosmosdb_preview.vendored_sdks.azure_mgmt_cosmosdb import CosmosDBManagementClient
    return get_mgmt_service_client(cli_ctx, CosmosDBManagementClient)


def cf_service(cli_ctx, _):
    return cf_cosmosdb_preview(cli_ctx).service


def cf_cassandra_cluster(cli_ctx, _):
    return cf_cosmosdb_preview(cli_ctx).cassandra_clusters


def cf_cassandra_data_center(cli_ctx, _):
    return cf_cosmosdb_preview(cli_ctx).cassandra_data_centers


def cf_mongo_db_resources(cli_ctx, _):
    return cf_cosmosdb_preview(cli_ctx).mongo_db_resources


def cf_sql_resources(cli_ctx, _):
    return cf_cosmosdb_preview(cli_ctx).sql_resources


def cf_gremlin_resources(cli_ctx, _):
    return cf_cosmosdb_preview(cli_ctx).gremlin_resources


def cf_table_resources(cli_ctx, _):
    return cf_cosmosdb_preview(cli_ctx).table_resources


# cosmosdb account
def cf_db_accounts(cli_ctx, _):
    return cf_cosmosdb_preview(cli_ctx).database_accounts


# restorable sql and mongodb collections
def cf_restorable_sql_containers(cli_ctx, _):
    return cf_cosmosdb_preview(cli_ctx).restorable_sql_containers


def cf_restorable_mongodb_collections(cli_ctx, _):
    return cf_cosmosdb_preview(cli_ctx).restorable_mongodb_collections


# restorable gremlin databases/graphs
def cf_restorable_gremlin_databases(cli_ctx, _):
    return cf_cosmosdb_preview(cli_ctx).restorable_gremlin_databases


def cf_restorable_gremlin_graphs(cli_ctx, _):
    return cf_cosmosdb_preview(cli_ctx).restorable_gremlin_graphs


def cf_restorable_gremlin_resources(cli_ctx, _):
    return cf_cosmosdb_preview(cli_ctx).restorable_gremlin_resources


# restorable tables
def cf_restorable_tables(cli_ctx, _):
    return cf_cosmosdb_preview(cli_ctx).restorable_tables


def cf_restorable_table_resources(cli_ctx, _):
    return cf_cosmosdb_preview(cli_ctx).restorable_table_resources


def cf_restorable_database_accounts(cli_ctx, _):
    return cf_cosmosdb_preview(cli_ctx).restorable_database_accounts


def cf_data_transfer_job(cli_ctx, _):
    return cf_cosmosdb_preview(cli_ctx).data_transfer_jobs


def cf_mongo_cluster_job(cli_ctx, _):
    return cf_cosmosdb_preview(cli_ctx).mongo_clusters
