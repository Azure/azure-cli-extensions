# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from __future__ import print_function
from knack.log import get_logger
from azext_dns.dns.dns_management_client import DnsManagementClient
from azext_dns.dns.models import (Zone)
from azure.cli.core.commands.client_factory import get_mgmt_service_client


logger = get_logger(__name__)


def create_dns_zone(client, resource_group_name, zone_name, location='global', tags=None,
                    if_none_match=False, zone_type='Public', resolution_vnets=None, registration_vnets=None):
    zone = Zone(location=location, tags=tags)

    if hasattr(zone, 'zone_type'):
        zone.zone_type = zone_type
        zone.registration_virtual_networks = registration_vnets
        zone.resolution_virtual_networks = resolution_vnets

    return client.create_or_update(resource_group_name, zone_name, zone, if_none_match='*' if if_none_match else None)


def update_dns_zone(instance, tags=None, zone_type=None, resolution_vnets=None, registration_vnets=None):

    if tags is not None:
        instance.tags = tags

    if zone_type:
        instance.zone_type = zone_type

    if resolution_vnets == ['']:
        instance.resolution_virtual_networks = None
    elif resolution_vnets:
        instance.resolution_virtual_networks = resolution_vnets

    if registration_vnets == ['']:
        instance.registration_virtual_networks = None
    elif registration_vnets:
        instance.registration_virtual_networks = registration_vnets

    return instance


def list_dns_zones(cmd, resource_group_name=None):
    ncf = get_mgmt_service_client(cmd.cli_ctx, DnsManagementClient).zones
    if resource_group_name:
        return ncf.list_by_resource_group(resource_group_name)
    return ncf.list()
