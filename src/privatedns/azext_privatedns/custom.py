# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long
from __future__ import print_function
from knack.log import get_logger
from azure.cli.core.commands.client_factory import get_mgmt_service_client
from azext_privatedns.privatedns.private_dns_management_client import PrivateDnsManagementClient
from azext_privatedns.privatedns.models import (PrivateZone, VirtualNetworkLink)


logger = get_logger(__name__)


def list_privatedns_zones(cmd, resource_group_name=None):
    ncf = get_mgmt_service_client(cmd.cli_ctx, PrivateDnsManagementClient).private_zones
    if resource_group_name:
        return ncf.list_by_resource_group(resource_group_name)
    return ncf.list()


def create_privatedns_zone(client, resource_group_name, private_zone_name, tags=None):
    zone = PrivateZone(location='global', tags=tags)
    return client.create_or_update(resource_group_name, private_zone_name, zone, if_none_match='*')


def update_privatedns_zone(instance, tags=None):
    if tags is not None:
        instance.tags = tags
    return instance


def create_privatedns_link(client, resource_group_name, private_zone_name, virtual_network_link_name, virtual_network, registration_enabled, tags=None):
    link = VirtualNetworkLink(location='global', tags=tags)

    if registration_enabled is not None:
        link.registration_enabled = registration_enabled

    if virtual_network is not None:
        link.virtual_network = virtual_network

    return client.create_or_update(resource_group_name, private_zone_name, virtual_network_link_name, link, if_none_match='*')


def update_privatedns_link(instance, registration_enabled=None, tags=None):
    if registration_enabled is not None:
        instance.registration_enabled = registration_enabled

    if tags is not None:
        instance.tags = tags

    return instance
