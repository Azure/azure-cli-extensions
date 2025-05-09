# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from .._resourceTypeValidation import ZoneRedundancyValidationResult, register_resource_type
from knack.log import get_logger


@register_resource_type('microsoft.network')
class microsoft_network:

    @staticmethod
    def validate(resource):
        resourceType = resource['type']
        resourceSubType = resourceType[resourceType.index('/') + 1:]

        _logger = get_logger("microsoft_network")
        _logger.debug(
            "Validating Microsoft.Network resource type: %s",
            resourceSubType)

        match resourceSubType:
            case 'applicationgateways':
                zones = resource.get('zones') or []
                if len(zones) > 1:
                    return ZoneRedundancyValidationResult.Yes
                else:
                    return ZoneRedundancyValidationResult.No

            case 'azurefirewalls':
                zones = resource.get('zones') or []
                if len(zones) > 1 and resource['sku']['capacity'] > 1:
                    return ZoneRedundancyValidationResult.Yes
                else:
                    return ZoneRedundancyValidationResult.No

            case 'connections':
                # Network connections depend on the configuration of the
                # Virtual Network Gateway
                return ZoneRedundancyValidationResult.Dependent

            case 'dnszones':
                # Azure DNS is a global service, zone redundant by default
                return ZoneRedundancyValidationResult.Always

            case 'frontdoors':
                # Front Door is a global resources and always zone redundant
                return ZoneRedundancyValidationResult.Always

            case 'loadbalancers':
                frontend_ip_configs = resource['properties'] \
                    .get('frontendIPConfigurations') or []
                zones = frontend_ip_configs[0].get('zones') or []
                if len(zones) > 1:
                    return ZoneRedundancyValidationResult.Yes
                else:
                    return ZoneRedundancyValidationResult.No

            case 'localnetworkgateways':
                # Local network gateways depend on the configuration of the VPN
                # Gateway
                return ZoneRedundancyValidationResult.Dependent

            case 'networkinterfaces':
                # Network interfaces are in the zone of the virtual machines
                # they are attached to
                return ZoneRedundancyValidationResult.Dependent

            case 'networksecuritygroups':
                return ZoneRedundancyValidationResult.Always

            case 'networkwatchers' | 'networkwatchers/flowlogs' | 'networkwatchers/packetcaptures':
                # Network watchers are zone redundant by default
                return ZoneRedundancyValidationResult.Always

            case 'privatednszones':
                # Private DNS zones are zone redundant by default
                # https://learn.microsoft.com/azure/dns/private-dns-resiliency
                return ZoneRedundancyValidationResult.Always

            case 'privatednszones/virtualnetworklinks':
                return ZoneRedundancyValidationResult.Always

            case 'privateendpoints':
                return ZoneRedundancyValidationResult.Always

            case 'publicipaddresses':
                zones = resource.get('zones') or []
                if resource['sku']['name'] in ['Standard'] and len(zones) > 1:
                    return ZoneRedundancyValidationResult.Yes
                else:
                    return ZoneRedundancyValidationResult.No

            case 'virtualnetworks':
                # Virtual networks span all availability zones in a region.
                # https://learn.microsoft.com/azure/virtual-network/virtual-networks-overview#virtual-networks-and-availability-zones
                return ZoneRedundancyValidationResult.Always

            case 'virtualnetworkgateways':
                sku = resource['properties']['sku']['name']
                if sku.endswith('AZ'):
                    return ZoneRedundancyValidationResult.Yes
                else:
                    return ZoneRedundancyValidationResult.No

        return ZoneRedundancyValidationResult.Unknown
