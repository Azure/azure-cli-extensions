# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import ipaddress
from knack.util import CLIError
from azure.cli.core.azclierror import InvalidArgumentValueError


def validate_failover_policies(ns):
    """ Extracts multiple space-separated failoverPolicies in regionName=failoverPriority format """
    from azure.mgmt.cosmosdb.models import FailoverPolicy
    fp_dict = []
    for item in ns.failover_policies:
        comps = item.split('=', 1)
        fp_dict.append(FailoverPolicy(location_name=comps[0], failover_priority=int(comps[1])))
    ns.failover_policies = fp_dict


def validate_ip_range_filter(ns):
    """ Extracts multiple comma-separated ip rules """
    from azure.mgmt.cosmosdb.models import IpAddressOrRange
    if ns.ip_range_filter is not None:
        ip_rules_list = []
        for item in ns.ip_range_filter:
            for i in item.split(","):
                ip_rules_list.append(IpAddressOrRange(ip_address_or_range=i))
                ns.ip_range_filter = ip_rules_list


def validate_private_endpoint_connection_id(ns):
    if ns.connection_id:
        from azure.cli.core.util import parse_proxy_resource_id
        result = parse_proxy_resource_id(ns.connection_id)
        ns.resource_group_name = result['resource_group']
        ns.account_name = result['name']
        ns.private_endpoint_connection_name = result['child_name_1']

    if not all([ns.account_name, ns.resource_group_name, ns.private_endpoint_connection_name]):
        raise CLIError(None, 'incorrect usage: [--id ID | --name NAME --account-name NAME --resource-group NAME]')

    del ns.connection_id


def validate_capabilities(ns):
    """ Extracts multiple space-separated capabilities """
    from azure.mgmt.cosmosdb.models import Capability
    if ns.capabilities is not None:
        capabilties_list = []
        for item in ns.capabilities:
            capabilties_list.append(Capability(name=item))
        ns.capabilities = capabilties_list


def validate_virtual_network_rules(ns):
    """ Extracts multiple space-separated virtual network rules """
    from azure.mgmt.cosmosdb.models import VirtualNetworkRule
    if ns.virtual_network_rules is not None:
        virtual_network_rules_list = []
        for item in ns.virtual_network_rules:
            virtual_network_rules_list.append(VirtualNetworkRule(id=item))
        ns.virtual_network_rules = virtual_network_rules_list


def validate_gossip_certificates(ns):
    """ Extracts multiple comma-separated certificates """
    if ns.external_gossip_certificates is not None:
        ns.external_gossip_certificates = get_certificates(ns.external_gossip_certificates)


def validate_client_certificates(ns):
    """ Extracts multiple comma-separated certificates """
    if ns.client_certificates is not None:
        ns.client_certificates = get_certificates(ns.client_certificates)


def get_certificates(input_certificates):
    from azext_cosmosdb_preview.vendored_sdks.azure_mgmt_cosmosdb.models import Certificate
    certificates = []
    for item in input_certificates:
        certificate = get_certificate(item)
        certificates.append(Certificate(pem=certificate))
    return certificates


def get_certificate(cert):
    """ Extract certificate from file or from string """
    from azure.cli.core.util import read_file_content
    import os
    certificate = ''
    if cert is not None:
        if os.path.exists(cert):
            certificate = read_file_content(cert)
        else:
            certificate = cert
    else:
        raise InvalidArgumentValueError("""One of the value provided for the certificates is empty.
    Please verify there aren't any spaces.""")
    return certificate


def validate_seednodes(ns):
    """ Extracts multiple comma-separated ipaddresses """
    from azext_cosmosdb_preview.vendored_sdks.azure_mgmt_cosmosdb.models import SeedNode
    if ns.external_seed_nodes is not None:
        seed_nodes = []
        for item in ns.external_seed_nodes:
            try:
                ipaddress.ip_address(item)
            except ValueError as e:
                raise InvalidArgumentValueError("""IP address provided is invalid.
            Please verify if there are any spaces or other invalid characters.""") from e
            seed_nodes.append(SeedNode(ip_address=item))
        ns.external_seed_nodes = seed_nodes


def validate_node_count(ns):
    """ Validate node count is greater than 3"""
    if ns.node_count is not None:
        if int(ns.node_count) < 3:
            raise InvalidArgumentValueError("""Node count cannot be less than 3.""")


def _gen_guid():
    import uuid
    return uuid.uuid4()
