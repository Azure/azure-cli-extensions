# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

def cf_cosmosdb_pitr(cli_ctx, *_):
    from azure.cli.core.commands.client_factory import get_mgmt_service_client
    from azext_cosmosdb_pitr.vendored_sdks.azure_mgmt_cosmosdb import CosmosDBManagementClient
    return get_mgmt_service_client(cli_ctx, CosmosDBManagementClient)


def cf_db_accounts(cli_ctx, _):
    return cf_cosmosdb_pitr(cli_ctx).database_accounts


def cf_restorable_database_accounts(cli_ctx, _):
    return cf_cosmosdb_pitr(cli_ctx).restorable_database_accounts


def cf_restorable_sql_databases(cli_ctx, _):
    return cf_cosmosdb_pitr(cli_ctx).restorable_sql_databases


def cf_restorable_sql_containers(cli_ctx, _):
    return cf_cosmosdb_pitr(cli_ctx).restorable_sql_containers


def cf_restorable_sql_resources(cli_ctx, _):
    return cf_cosmosdb_pitr(cli_ctx).restorable_sql_resources


def cf_restorable_mongodb_databases(cli_ctx, _):
    return cf_cosmosdb_pitr(cli_ctx).restorable_mongodb_databases


def cf_restorable_mongodb_collections(cli_ctx, _):
    return cf_cosmosdb_pitr(cli_ctx).restorable_mongodb_collections


def cf_restorable_mongodb_resources(cli_ctx, _):
    return cf_cosmosdb_pitr(cli_ctx).restorable_mongodb_resources
