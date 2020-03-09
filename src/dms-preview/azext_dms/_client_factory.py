# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


def dms_client_factory(cli_ctx, **_):
    from azure.cli.core.commands.client_factory import get_mgmt_service_client
    from azext_dms.vendored_sdks.datamigration import DataMigrationServiceClient
    return get_mgmt_service_client(cli_ctx, DataMigrationServiceClient)


def dms_cf_projects(cli_ctx, *_):
    return dms_client_factory(cli_ctx).projects


def dms_cf_tasks(cli_ctx, *_):
    return dms_client_factory(cli_ctx).tasks


def dms_cf_service_tasks(cli_ctx, *_):
    return dms_client_factory(cli_ctx).service_tasks
