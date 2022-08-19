# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import re

from knack.log import get_logger
from knack.util import CLIError

from azure.cli.core.commands.client_factory import get_subscription_id
from azure.cli.core.util import sdk_no_wait

from azext_fleet._client_factory import CUSTOM_MGMT_FLEET
from azext_fleet._resourcegroup import get_rg_location
from azext_fleet._helpers import print_or_merge_credentials


logger = get_logger(__name__)


def create_fleet(cmd,
                 client,
                 resource_group_name,
                 name,
                 dns_name_prefix=None,
                 location=None,
                 tags=None,
                 no_wait=False):
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
    if dns_name_prefix is None:
        subscription_id = get_subscription_id(cmd.cli_ctx)
        # Use subscription id to provide uniqueness and prevent DNS name clashes
        name_part = re.sub('[^A-Za-z0-9-]', '', name)[0:10]
        if not name_part[0].isalpha():
            name_part = (str('a') + name_part)[0:10]
        resource_group_part = re.sub('[^A-Za-z0-9-]', '', resource_group_name)[0:16]
        dns_name_prefix = f'{name_part}-{resource_group_part}-{subscription_id[0:6]}'

    fleetHubProfile = FleetHubProfile(dns_prefix=dns_name_prefix)
    rg_location = get_rg_location(cmd.cli_ctx, resource_group_name)
    if location is None:
        location = rg_location

    fleet = Fleet(
        location=location,
        tags=tags,
        hub_profile=fleetHubProfile
    )

    return sdk_no_wait(no_wait, client.begin_create_or_update, resource_group_name, name, fleet)


def patch_fleet(cmd,
                client,
                resource_group_name,
                name,
                tags=None):
    FleetPatch = cmd.get_models(
        "FleetPatch",
        resource_type=CUSTOM_MGMT_FLEET,
        operation_group="fleets"
    )
    fleetPatch = FleetPatch(tags=tags)
    return client.update(resource_group_name, name, None, fleetPatch)


def get_fleet(cmd,  # pylint: disable=unused-argument
              client,
              resource_group_name,
              name):
    logger.info('Getting fleet: %s for resource group: %s', name, resource_group_name)
    return client.get(resource_group_name, name)


def list_fleet_by_resource_group(cmd,  # pylint: disable=unused-argument
                                 client,
                                 resource_group_name):
    logger.info('Listing fleet for resource group: %s', resource_group_name)
    return client.list_by_resource_group(resource_group_name)


def list_fleet_by_subscription(cmd,  # pylint: disable=unused-argument
                               client):
    subscription_id = get_subscription_id(cmd.cli_ctx)
    logger.info('Listing fleet for subscription id: %s', subscription_id)
    return client.list()


def delete_fleet(cmd,  # pylint: disable=unused-argument
                 client,
                 resource_group_name,
                 name,
                 no_wait=False):
    return sdk_no_wait(no_wait, client.begin_delete, resource_group_name, name)


def get_credentials(cmd,  # pylint: disable=unused-argument
                    client,
                    resource_group_name,
                    name,
                    path=os.path.join(os.path.expanduser(
                        '~'), '.kube', 'config'),
                    overwrite_existing=False,
                    context_name=None):
    credentialResults = client.list_credentials(resource_group_name, name)
    if not credentialResults:
        raise CLIError("No Kubernetes credentials found.")

    try:
        kubeconfig = credentialResults.kubeconfigs[0].value.decode(
            encoding='UTF-8')
        print_or_merge_credentials(
            path, kubeconfig, overwrite_existing, context_name)
    except (IndexError, ValueError):
        raise CLIError("Fail to find kubeconfig file.")


def join_fleet_member(cmd,
                      client,
                      resource_group_name,
                      name,
                      fleet_name,
                      member_cluster_id,
                      no_wait=False):
    FleetMember = cmd.get_models(
        "FleetMember",
        resource_type=CUSTOM_MGMT_FLEET,
        operation_group="fleet_members"
    )
    fleetMember = FleetMember(cluster_resource_id=member_cluster_id)
    return sdk_no_wait(no_wait, client.begin_create_or_update, resource_group_name, fleet_name, name, fleetMember)


def list_fleet_member(cmd,  # pylint: disable=unused-argument
                      client,
                      resource_group_name,
                      fleet_name):
    logger.info('Listing fleet member(s) for fleet: %s for resource group: %s', fleet_name, resource_group_name)
    return client.list_by_fleet(resource_group_name, fleet_name)


def get_fleet_member(cmd,  # pylint: disable=unused-argument
                     client,
                     resource_group_name,
                     fleet_name,
                     name):
    return client.get(resource_group_name, fleet_name, name)


def remove_fleet_member(cmd,  # pylint: disable=unused-argument
                        client,
                        resource_group_name,
                        fleet_name,
                        name,
                        no_wait=False):
    return sdk_no_wait(no_wait, client.begin_delete, resource_group_name, fleet_name, name)
