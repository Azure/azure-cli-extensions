# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.mgmt.core.tools import parse_resource_id

from knack import log

logger = log.get_logger(__name__)


def get_ssh_ip(cmd, resource_group, vm_name, use_private_ip):
    from .aaz.latest.network.public_ip import Show as PublicIpShow
    from .aaz.latest.network.nic import Show as InterfaceShow
    from azure.cli.command_modules.vm.operations.vm import VMShow

    command_args = {
        'resource_group': resource_group,
        'vm_name': vm_name
    }
    vm = VMShow(cli_ctx=cmd.cli_ctx)(command_args=command_args)

    private_ips = []

    for nic_ref in vm.get('networkProfile', {}).get('networkInterfaces', []):
        parsed_id = parse_resource_id(nic_ref.get('id'))
        get_args = {
            'name': parsed_id['name'],
            'resource_group': parsed_id['resource_group']
        }
        nic = InterfaceShow(cli_ctx=cmd.cli_ctx)(command_args=get_args)
        for ip_config in nic["ipConfigurations"]:
            if use_private_ip and ip_config.get("privateIPAddress", None):
                return ip_config["privateIPAddress"]
            public_ip_ref = ip_config.get("publicIPAddress", None)
            if public_ip_ref and public_ip_ref.get("id", None):
                parsed_ip_id = parse_resource_id(public_ip_ref["id"])
                api_args = {
                    'name': parsed_ip_id['name'],
                    'resource_group': parsed_ip_id['resource_group']
                }
                public_ip = PublicIpShow(cli_ctx=cmd.cli_ctx)(command_args=api_args)
                if public_ip and public_ip.get("ipAddress", None):
                    return public_ip["ipAddress"]
            if ip_config.get("privateIPAddress", None):
                private_ips.append(ip_config["privateIPAddress"])

    if len(private_ips) > 0:
        logger.warning("No public IP detected, attempting private IP (you must bring your own connectivity).")
        logger.warning("Use --prefer-private-ip to avoid this message.")
        return private_ips[0]

    return None
