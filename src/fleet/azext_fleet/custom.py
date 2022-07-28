# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.log import get_logger

from azure.cli.core.util import sdk_no_wait

from azext_fleet._client_factory import CUSTOM_MGMT_FLEET
from azext_fleet._resourcegroup import get_rg_location


logger = get_logger(__name__)


def create_fleet(cmd,
                 client,
                 resource_group_name,
                 name,
                 dns_name_prefix,
                 location=None,
                 tags=None,
                 no_wait=False):
    logger.info('in create fleets1')
    FleetHubProfile = cmd.get_models(
        "FleetHubProfile",
        resource_type=CUSTOM_MGMT_FLEET,
        operation_group="fleets"
    )
    Fleet = cmd.get_models(
        "Fleet",
        resource_type=CUSTOM_MGMT_FLEET,
        operation_group="fleets"
    )
    fleetHubProfile = FleetHubProfile(dns_prefix=dns_name_prefix)
    rg_location = get_rg_location(cmd.cli_ctx, resource_group_name)
    if location is None:
        location = rg_location
    logger.info('in create fleets5')
    logger.error(location)
    fleet = Fleet(
        location=location,
        tags=tags,
        hub_profile=fleetHubProfile
    )
    logger.info('in create fleets6')

    return sdk_no_wait(no_wait, client.begin_create_or_update, resource_group_name, name, fleet)


def delete_fleet(cmd,  # pylint: disable=unused-argument
                 client,
                 resource_group_name,
                 name,
                 no_wait=False):
    logger.info('in delete fleets')
    return sdk_no_wait(no_wait, client.begin_delete, resource_group_name, name)


def join_fleet_member(cmd,
                      client,
                      resource_group_name,
                      name,
                      member_cluster_id,
                      member_name=None,
                      no_wait=False):
    logger.info('in create fleetmember')
    FleetMember = cmd.get_models(
        "FleetMember",
        resource_type=CUSTOM_MGMT_FLEET,
        operation_group="fleet_members"
    )

    if member_name is None:
        member_name = member_cluster_id.split('/')[-1]

    fleetMember = FleetMember(cluster_resource_id=member_cluster_id)
    return sdk_no_wait(no_wait, client.begin_create_or_update, resource_group_name, name, member_name, fleetMember)


def list_fleet_member(cmd,  # pylint: disable=unused-argument
                      client,
                      resource_group_name,
                      name):
    return client.list_by_fleet(resource_group_name, name)


def remove_fleet_member(cmd,  # pylint: disable=unused-argument
                        client,
                        resource_group_name,
                        name,
                        member_name,
                        no_wait=False):
    return sdk_no_wait(no_wait, client.begin_delete, resource_group_name, name, member_name)
