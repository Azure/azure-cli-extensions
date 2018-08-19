# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


def _cf_mesh(cli_ctx, **_):
    from azure.cli.core.commands.client_factory import get_mgmt_service_client
    from .servicefabricmesh.mgmt.servicefabricmesh import ServiceFabricMeshManagementClient
    return get_mgmt_service_client(cli_ctx, ServiceFabricMeshManagementClient)


def cf_mesh_application(cli_ctx, _):
    return _cf_mesh(cli_ctx).application


def cf_mesh_service(cli_ctx, _):
    return _cf_mesh(cli_ctx).service


def cf_mesh_replica(cli_ctx, _):
    return _cf_mesh(cli_ctx).replica


def cf_mesh_code_package(cli_ctx, _):
    return _cf_mesh(cli_ctx).code_package


def cf_mesh_network(cli_ctx, _):
    return _cf_mesh(cli_ctx).network


def cf_mesh_volume(cli_ctx, _):
    return _cf_mesh(cli_ctx).volume


def _resource_client_factory(cli_ctx, **_):
    from azure.cli.core.commands.client_factory import get_mgmt_service_client
    from azure.cli.core.profiles import ResourceType
    return get_mgmt_service_client(cli_ctx, ResourceType.MGMT_RESOURCE_RESOURCES)


def cf_mesh_deployments(cli_ctx, _):
    return _resource_client_factory(cli_ctx).deployments
