# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


def cf_migrate(cli_ctx, *_):
    from azure.cli.core.commands.client_factory import get_mgmt_service_client
    from .vendored_sdks.migrate import AzureMigrate
    return get_mgmt_service_client(cli_ctx, AzureMigrate)


def cf_location(cli_ctx, *_):
    return cf_migrate(cli_ctx).location


def cf_assessment_options(cli_ctx, *_):
    return cf_migrate(cli_ctx).assessment_options


def cf_projects(cli_ctx, *_):
    return cf_migrate(cli_ctx).projects


def cf_machines(cli_ctx, *_):
    return cf_migrate(cli_ctx).machines


def cf_groups(cli_ctx, *_):
    return cf_migrate(cli_ctx).groups


def cf_assessments(cli_ctx, *_):
    return cf_migrate(cli_ctx).assessments


def cf_assessed_machines(cli_ctx, *_):
    return cf_migrate(cli_ctx).assessed_machines


def cf_operations(cli_ctx, *_):
    return cf_migrate(cli_ctx).operations
