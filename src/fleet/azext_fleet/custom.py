# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import re

from knack.util import CLIError

from azure.cli.core.commands.client_factory import get_subscription_id
from azure.cli.core.util import sdk_no_wait

from azext_fleet._client_factory import CUSTOM_MGMT_FLEET
from azext_fleet._helpers import print_or_merge_credentials


def create_fleet(cmd,
                 client,
                 resource_group_name,
                 name,
                 dns_name_prefix=None,
                 location=None,
                 tags=None,
                 no_wait=False):
    fleet_hub_profile_model = cmd.get_models(
        "FleetHubProfile",
        resource_type=CUSTOM_MGMT_FLEET,
        operation_group="fleets"
    )
    fleet_model = cmd.get_models(
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

    fleet_hub_profile = fleet_hub_profile_model(dns_prefix=dns_name_prefix)
    fleet = fleet_model(
        location=location,
        tags=tags,
        hub_profile=fleet_hub_profile
    )

    return sdk_no_wait(no_wait, client.begin_create_or_update, resource_group_name, name, fleet)


def update_fleet(cmd,
                 client,
                 resource_group_name,
                 name,
                 tags=None):
    fleet_patch_model = cmd.get_models(
        "FleetPatch",
        resource_type=CUSTOM_MGMT_FLEET,
        operation_group="fleets"
    )
    fleet_patch = fleet_patch_model(tags=tags)
    return client.update(resource_group_name, name, None, fleet_patch)


def show_fleet(cmd,  # pylint: disable=unused-argument
               client,
               resource_group_name,
               name):
    return client.get(resource_group_name, name)


def list_fleet(cmd,  # pylint: disable=unused-argument
               client,
               resource_group_name=None):
    if resource_group_name:
        return client.list_by_resource_group(resource_group_name)
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
    credential_results = client.list_credentials(resource_group_name, name)
    if not credential_results:
        raise CLIError("No Kubernetes credentials found.")

    try:
        kubeconfig = credential_results.kubeconfigs[0].value.decode(
            encoding='UTF-8')
        print_or_merge_credentials(
            path, kubeconfig, overwrite_existing, context_name)
    except (IndexError, ValueError):
        raise CLIError("Fail to find kubeconfig file.")


def create_fleet_member(cmd,
                        client,
                        resource_group_name,
                        name,
                        fleet_name,
                        member_cluster_id,
                        no_wait=False):
    fleet_member_model = cmd.get_models(
        "FleetMember",
        resource_type=CUSTOM_MGMT_FLEET,
        operation_group="fleet_members"
    )
    fleet_member = fleet_member_model(cluster_resource_id=member_cluster_id)
    return sdk_no_wait(no_wait, client.begin_create_or_update, resource_group_name, fleet_name, name, fleet_member)


def list_fleet_member(cmd,  # pylint: disable=unused-argument
                      client,
                      resource_group_name,
                      fleet_name):
    return client.list_by_fleet(resource_group_name, fleet_name)


def show_fleet_member(cmd,  # pylint: disable=unused-argument
                      client,
                      resource_group_name,
                      fleet_name,
                      name):
    return client.get(resource_group_name, fleet_name, name)


def delete_fleet_member(cmd,  # pylint: disable=unused-argument
                        client,
                        resource_group_name,
                        fleet_name,
                        name,
                        no_wait=False):
    return sdk_no_wait(no_wait, client.begin_delete, resource_group_name, fleet_name, name)
