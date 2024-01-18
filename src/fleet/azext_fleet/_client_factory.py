# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core.commands.client_factory import get_mgmt_service_client
from azure.cli.core.profiles import (
    CustomResourceType,
    ResourceType
)

CUSTOM_MGMT_FLEET = CustomResourceType('azext_fleet.vendored_sdks', 'ContainerServiceFleetMgmtClient')


# container service clients
def get_container_service_client(cli_ctx, subscription_id=None):
    return get_mgmt_service_client(cli_ctx, CUSTOM_MGMT_FLEET, subscription_id=subscription_id)


def cf_fleets(cli_ctx, *_):
    return get_container_service_client(cli_ctx).fleets


def cf_fleet_members(cli_ctx, *_):
    return get_container_service_client(cli_ctx).fleet_members


def cf_update_runs(cli_ctx, *_):
    return get_container_service_client(cli_ctx).update_runs


def cf_fleet_update_strategies(cli_ctx, *_):
    return get_container_service_client(cli_ctx).fleet_update_strategies


def get_resource_groups_client(cli_ctx, subscription_id=None):
    return get_mgmt_service_client(
        cli_ctx, ResourceType.MGMT_RESOURCE_RESOURCES, subscription_id=subscription_id).resource_groups
