# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core.commands import client_factory
from azure.cli.core import profiles
from msrestazure import tools
from knack.prompting import prompt_y_n
from . import bastion_utils


from knack import log

logger = log.get_logger(__name__)


def get_ssh_ip(cmd, resource_group, vm_name, use_private_ip, op_info):
    compute_client = client_factory.get_mgmt_service_client(cmd.cli_ctx, profiles.ResourceType.MGMT_COMPUTE)
    vm_client = compute_client.virtual_machines
    from .aaz.latest.network.public_ip import Show as PublicIpShow
    from .aaz.latest.network.nic import Show as InterfaceShow

    vm = vm_client.get(resource_group, vm_name)

    private_ips = [] 

    for nic_ref in vm.network_profile.network_interfaces:
        parsed_id = tools.parse_resource_id(nic_ref.id)
        get_args = {
            'name': parsed_id['name'],
            'resource_group': parsed_id['resource_group']
        }
        nic = InterfaceShow(cli_ctx=cmd.cli_ctx)(command_args=get_args)
        op_info.network_interface = nic
        for ip_config in nic["ipConfigurations"]:
            if use_private_ip and ip_config.get("privateIPAddress", None):
                return ip_config["privateIPAddress"], nic
            public_ip_ref = ip_config.get("publicIPAddress", None)
            if public_ip_ref and public_ip_ref.get("id", None):
                parsed_ip_id = tools.parse_resource_id(public_ip_ref["id"])
                api_args = {
                    'name': parsed_ip_id['name'],
                    'resource_group': parsed_ip_id['resource_group']
                }
                public_ip = PublicIpShow(cli_ctx=cmd.cli_ctx)(command_args=api_args)
                if public_ip and public_ip.get("ipAddress", None):
                    return public_ip["ipAddress"], nic
            else:
                if not op_info.bastion:
                    prompt = (f"There is no public IP associated with this VM." 
                    " Would you like to connect to your VM through Developer Bastion? To learn more,"
                    f" please visit {bastion_utils.BastionSku.QuickStartLink}")
                    if prompt_y_n(prompt):
                        op_info.bastion  = True
                        logger.warning("Use --bastion to avoid this message.")
                        return None, nic
            if ip_config.get("privateIPAddress", None):
                private_ips.append(ip_config["privateIPAddress"])

    if len(private_ips) > 0 and not op_info.bastion:
        logger.warning("No public IP detected and connection through Developer Bastion was denied, attempting private IP (you must bring your own connectivity).")
        logger.warning("Use --prefer-private-ip to avoid this message.")
        return private_ips[0], nic

    return None, nic
