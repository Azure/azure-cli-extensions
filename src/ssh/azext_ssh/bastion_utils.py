# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from enum import Enum
from azure.cli.core.azclierror  import InvalidArgumentValueError, UnrecognizedArgumentError
from knack.log import get_logger
from msrestazure.tools import is_valid_resource_id
from azure.cli.core.commands.client_factory import get_subscription_id
from enum import Enum
from msrestazure.tools import is_valid_resource_id



class BastionSku(Enum):

    Basic = "Basic"
    Standard = "Standard"
    Developer = "Developer"
    QuickConnect = "QuickConnect"

def show_bastion(cmd, op_info):
    from .aaz.latest.network.bastion import Show
    try:
        from .aaz.latest.network.bastion import Show
        bastion = Show(cli_ctx=cmd.cli_ctx)(command_args={
            "resource_group": op_info.resource_group_name,
            "name": "testVM-vnet-bastion"
        })
        
        print(bastion)
    except Exception:
        print("Error")
    

def ssh_bastion_host(cmd, target_ip_address, resource_group_name, bastion_host_name,op_info, 
                     username=None, ssh_key=None):
    import os
    from .aaz.latest.network.bastion import Show

    bastion = Show(cli_ctx=cmd.cli_ctx)(command_args={
        "resource_group": resource_group_name,
        "name": bastion_host_name
    })
    if bastion['sku']['name'] == BastionSku.Basic.value or bastion['sku']['name'] == BastionSku.Standard.value:
        raise InvalidArgumentValueError("SSH to Bastion host is only supported for Developer Sku. Higher level skus are not supported.")

    if not op_info.port:
        op_info.port = 22

    ip_connect = _is_ipconnect_request(bastion, op_info.resource_id)
    if ip_connect:
        if int(op_info.port) not in [22, 3389]:
            raise UnrecognizedArgumentError("Custom ports are not allowed. Allowed ports for Tunnel with IP connect is \
                                             22, 3389.")
        target_resource_id = f"/subscriptions/{get_subscription_id(cmd.cli_ctx)}/resourceGroups/{resource_group_name}" \
                             f"/providers/Microsoft.Network/bh-hostConnect/{target_ip_address}"
    else:
        target_resource_id = op_info.resource_id 

    _validate_resourceid(target_resource_id)
    bastion_endpoint = _get_data_pod(cmd, op_info.port, target_resource_id, bastion)
    print(bastion_endpoint)

def _is_ipconnect_request(bastion, target_ip_address):
    if 'enableIpConnect' in bastion and bastion['enableIpConnect'] is True and target_ip_address:
        return True

    return False

def _validate_resourceid(target_resource_id):
    if not is_valid_resource_id(target_resource_id):
        err_msg = "Please enter a valid resource ID. If this is not working, " \
                  "try opening the JSON view of your resource (in the Overview tab), and copying the full resource ID."
        raise InvalidArgumentValueError(err_msg)

def _get_data_pod(cmd, port, target_resource_id, bastion):
    from azure.cli.core._profile import Profile
    from azure.cli.core.util import should_disable_connection_verify
    import requests

    profile = Profile(cli_ctx=cmd.cli_ctx)
    auth_token, _, _ = profile.get_raw_token()
    content = {
        'resourceId': target_resource_id,
        'bastionResourceId': bastion['id'],
        'vmPort': port,
        'azToken': auth_token[1],
        'connectionType': 'nativeclient'
    }
    headers = {'Content-Type': 'application/json'}

    web_address = f"https://{bastion['dnsName']}/api/connection"
    response = requests.post(web_address, json=content, headers=headers,
                            verify=not should_disable_connection_verify())

    return response.content.decode("utf-8")
