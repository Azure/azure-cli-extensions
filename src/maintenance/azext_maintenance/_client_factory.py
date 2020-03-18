# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


def _maintenance_client_factory(cli_ctx, **_):
    from azext_maintenance.vendored_sdks import MaintenanceManagementClient
    from azure.cli.core.commands.client_factory import get_mgmt_service_client
    return get_mgmt_service_client(cli_ctx, MaintenanceManagementClient)


def cf_maintenance_configurations(cli_ctx, _):
    return _maintenance_client_factory(cli_ctx).maintenance_configurations


def cf_maintenance_updates(cli_ctx, _):
    return _maintenance_client_factory(cli_ctx).updates


def cf_configuration_assignments(cli_ctx, _):
    return _maintenance_client_factory(cli_ctx).configuration_assignments


def cf_apply_updates(cli_ctx, _):
    return _maintenance_client_factory(cli_ctx).apply_updates
