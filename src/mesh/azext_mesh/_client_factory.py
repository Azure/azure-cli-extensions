# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


def _cf_sbz(cli_ctx, **_):
    from azure.cli.core.commands.client_factory import get_mgmt_service_client
    from .sbz.mgmt.seabreeze import SeaBreezeManagementClient
    return get_mgmt_service_client(cli_ctx, SeaBreezeManagementClient)


def cf_application(cli_ctx, _):
    return _cf_sbz(cli_ctx).application


def cf_service(cli_ctx, _):
    return _cf_sbz(cli_ctx).service


def cf_replica(cli_ctx, _):
    return _cf_sbz(cli_ctx).replica


def cf_code_package(cli_ctx, _):
    return _cf_sbz(cli_ctx).code_package


def cf_network(cli_ctx, _):
    return _cf_sbz(cli_ctx).network


def cf_volume(cli_ctx, _):
    return _cf_sbz(cli_ctx).volume


def _resource_client_factory(cli_ctx, **_):
    from azure.cli.core.commands.client_factory import get_mgmt_service_client
    from azure.cli.core.profiles import ResourceType
    return get_mgmt_service_client(cli_ctx, ResourceType.MGMT_RESOURCE_RESOURCES)


def cf_deployments(cli_ctx, _):
    return _resource_client_factory(cli_ctx).deployments
