# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core.commands import client_factory
from azure.cli.core import profiles
from msrestazure import tools

from knack import log

logger = log.get_logger(__name__)


def get_ssh_ip(cmd, resource_group, vm_name, use_private_ip):
    compute_client = client_factory.get_mgmt_service_client(cmd.cli_ctx, profiles.ResourceType.MGMT_COMPUTE)
    network_client = client_factory.get_mgmt_service_client(cmd.cli_ctx, profiles.ResourceType.MGMT_NETWORK)
    vm_client = compute_client.virtual_machines
    nic_client = network_client.network_interfaces
    ip_client = network_client.public_ip_addresses

    vm = vm_client.get(resource_group, vm_name)

    private_ips = []

    for nic_ref in vm.network_profile.network_interfaces:
        parsed_id = tools.parse_resource_id(nic_ref.id)
        nic = nic_client.get(parsed_id['resource_group'], parsed_id['name'])
        for ip_config in nic.ip_configurations:
            if use_private_ip and ip_config.private_ip_address:
                return ip_config.private_ip_address
            public_ip_ref = ip_config.public_ip_address
            if public_ip_ref and public_ip_ref.id:
                parsed_ip_id = tools.parse_resource_id(public_ip_ref.id)
                public_ip = ip_client.get(parsed_ip_id['resource_group'], parsed_ip_id['name'])
                if public_ip and public_ip.ip_address:
                    return public_ip.ip_address
            if ip_config.private_ip_address:
                private_ips += ip_config.private_ip_address

    if len(private_ips) > 0:
        logger.warning("No public IP detected, attempting private IP (you must bring your own connectivity).")
        logger.warning("Use --prefer-private-ip to avoid this message.")
        return private_ips[0]

    return None
