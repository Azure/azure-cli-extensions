# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from ._client_factory import network_client_factory


# region IpGroup
def create_ip_groups(cmd, resource_group_name, ip_groups_name, ip_addresses, location=None, tags=None):
    IpGroup = cmd.get_models('IpGroup')
    client = network_client_factory(cmd.cli_ctx).ip_groups

    ip_groups = IpGroup(location=location, ip_addresses=ip_addresses, tags=tags)

    return client.create_or_update(resource_group_name, ip_groups_name, ip_groups)


def list_ip_groups(cmd, resource_group_name=None):
    client = network_client_factory(cmd.cli_ctx).ip_groups

    if resource_group_name is not None:
        return client.list_by_resource_group(resource_group_name)

    return client.list()


def update_ip_groups(cmd, instance, ip_addresses=None, tags=None):
    with cmd.update_context(instance) as c:
        c.set_param('tags', tags)
        c.set_param('ip_addresses', ip_addresses)

    return instance
# endregion
