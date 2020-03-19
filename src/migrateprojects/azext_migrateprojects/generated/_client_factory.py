# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


def cf_migrateprojects(cli_ctx, *_):
    from azure.cli.core.commands.client_factory import get_mgmt_service_client
    from ..vendored_sdks.migrateprojects import AzureMigrateHub
    return get_mgmt_service_client(cli_ctx, AzureMigrateHub)


def cf_database_instance(cli_ctx, *_):
    return cf_migrateprojects(cli_ctx).database_instance


def cf_database(cli_ctx, *_):
    return cf_migrateprojects(cli_ctx).database


def cf_event(cli_ctx, *_):
    return cf_migrateprojects(cli_ctx).event


def cf_machine(cli_ctx, *_):
    return cf_migrateprojects(cli_ctx).machine


def cf_migrate_project(cli_ctx, *_):
    return cf_migrateprojects(cli_ctx).migrate_project


def cf_solution(cli_ctx, *_):
    return cf_migrateprojects(cli_ctx).solution
