# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from .._resourceTypeValidation import (
    ZoneRedundancyValidationResult,
    register_resource_type,
)
from knack.log import get_logger


# pylint: disable=too-few-public-methods
@register_resource_type("microsoft.network")
class microsoft_network:
    @staticmethod
    def validate(resource):  # pylint: disable=too-many-return-statements,too-many-branches
        resourceType = resource["type"]
        resourceSubType = resourceType[resourceType.index("/") + 1:]

        _logger = get_logger("microsoft_network")
        _logger.debug("Validating Microsoft.Network resource type: %s", resourceSubType)

        # Application Gateways
        if resourceSubType == "applicationgateways":
            zones = resource.get("zones") or []
            if len(zones) > 1:
                return ZoneRedundancyValidationResult.Yes
            return ZoneRedundancyValidationResult.No

        # Azure Firewalls
        if resourceSubType == "azurefirewalls":
            zones = resource.get("zones") or []
            if len(zones) > 1 and resource["sku"]["capacity"] > 1:
                return ZoneRedundancyValidationResult.Yes
            return ZoneRedundancyValidationResult.No

        # Network Connections
        if resourceSubType == "connections":
            # Network connections depend on the configuration of the
            # Virtual Network Gateway
            return ZoneRedundancyValidationResult.Dependent

        # DNS Zones
        if resourceSubType == "dnszones":
            # Azure DNS is a global service, zone redundant by default
            return ZoneRedundancyValidationResult.Always

        # Front Doors
        if resourceSubType == "frontdoors":
            # Front Door is a global resources and always zone redundant
            return ZoneRedundancyValidationResult.Always

        # Load Balancers
        if resourceSubType == "loadbalancers":
            frontend_ip_configs = (
                resource["properties"].get("frontendIPConfigurations") or []
            )
            zones = frontend_ip_configs[0].get("zones") or []
            if len(zones) > 1:
                return ZoneRedundancyValidationResult.Yes
            return ZoneRedundancyValidationResult.No

        # Local Network Gateways
        if resourceSubType == "localnetworkgateways":
            # Local network gateways depend on the configuration of the VPN
            # Gateway
            return ZoneRedundancyValidationResult.Dependent

        # NAT Gateways
        if resourceSubType == "natgateways":
            zones = resource.get("zones") or []
            if len(zones) > 1:
                return ZoneRedundancyValidationResult.Yes
            return ZoneRedundancyValidationResult.No

        # Network Interfaces
        if resourceSubType == "networkinterfaces":
            # Network interfaces are in the zone of the virtual machines
            # they are attached to
            return ZoneRedundancyValidationResult.Dependent

        # Network Security Groups
        if resourceSubType == "networksecuritygroups":
            return ZoneRedundancyValidationResult.Always

        # Network Watchers, flowslogs, packetcaptures
        if (
            resourceSubType == "networkwatchers"
            or resourceSubType == "networkwatchers/flowlogs"
            or resourceSubType == "networkwatchers/packetcaptures"
        ):
            # Network watchers are zone redundant by default
            return ZoneRedundancyValidationResult.Always

        # Private DNS Zones
        if resourceSubType == "privatednszones":
            # Private DNS zones are zone redundant by default
            # https://learn.microsoft.com/azure/dns/private-dns-resiliency
            return ZoneRedundancyValidationResult.Always

        # Private DNS Zone Virtual Network Links
        if resourceSubType == "privatednszones/virtualnetworklinks":
            return ZoneRedundancyValidationResult.Always

        # Private Endpoints
        if resourceSubType == "privateendpoints":
            return ZoneRedundancyValidationResult.Always

        # Public IP Addresses
        if resourceSubType == "publicipaddresses":
            zones = resource.get("zones") or []
            if resource["sku"]["name"] in ["Standard"] and len(zones) > 1:
                return ZoneRedundancyValidationResult.Yes
            return ZoneRedundancyValidationResult.No

        # Public IP Prefixes
        if resourceSubType == "publicipprefixes":
            zones = resource.get("zones") or []
            if len(zones) > 1:
                return ZoneRedundancyValidationResult.Yes
            return ZoneRedundancyValidationResult.No

        # Virtual Networks
        if resourceSubType == "virtualnetworks":
            # Virtual networks span all availability zones in a region.
            # https://learn.microsoft.com/azure/virtual-network/virtual-networks-overview#virtual-networks-and-availability-zones
            return ZoneRedundancyValidationResult.Always

        # Virtual Network Gateways
        if resourceSubType == "virtualnetworkgateways":
            sku = resource["properties"]["sku"]["name"]
            if sku.endswith("AZ"):
                return ZoneRedundancyValidationResult.Yes
            return ZoneRedundancyValidationResult.No

        return ZoneRedundancyValidationResult.Unknown
