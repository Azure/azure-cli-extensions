# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=too-many-lines
# pylint: disable=too-many-statements
# pylint: disable=protected-access

import platform
import subprocess
import tempfile
import threading
import time
import json
import uuid

import requests
from enum import Enum
from azure.cli.core.azclierror import ValidationError, InvalidArgumentValueError, RequiredArgumentMissingError, \
    UnrecognizedArgumentError, CLIInternalError, ClientRequestError
from azure.cli.core.commands.client_factory import get_subscription_id
from knack.log import get_logger
from msrestazure.tools import is_valid_resource_id
from .aaz.latest.network.bastion import Create as _BastionCreate
from . import custom
from . import ssh_utils

logger = get_logger(__name__)


class BastionSku(Enum):

    Basic = "Basic"
    Standard = "Standard"
    Developer = "Developer"
    QuickConnect = "QuickConnect"

def show_bastion(cmd, op_info):
    from .aaz.latest.network.bastion import Show
    try:
        bastion = Show(cli_ctx=cmd.cli_ctx)(command_args={
            "resource_group": op_info.resource_group_name,
            "name": "northeurope-vm-vnet-bastion" # Make sure op_info has the attribute 'bastion_name'
        })
        print(bastion)
        # Check if the IP configurations exist and are not empty
        properties = bastion.get("properties", {})
        ip_configurations = properties.get("ipConfigurations", [])

        # Check if the IP configurations exist and are not empty
        if ip_configurations:
            print("IP Configurations:", ip_configurations)
        else:
            print("No IP configurations found.")

        return bastion
    except Exception as e:
        print("Error:", str(e))


def _get_host(username, ip):
    return username + "@" + ip

def ssh_bastion_host(cmd, op_info):
    import os
    from .aaz.latest.network.bastion import Show

    bastion = show_bastion(cmd, op_info)

    if bastion['sku']['name'] not in [BastionSku.Developer.value, BastionSku.QuickConnect.value]:
        raise InvalidArgumentValueError("SSH to Bastion host is only supported for Developer and QuickConnect Skus.")

    if not op_info.port:
        op_info.port = 22

    target_resource_id = op_info.resource_id
    
    bastion_endpoint = _get_data_pod(cmd, op_info.port, target_resource_id, bastion)
    tunnel_server = _get_tunnel(cmd, bastion, bastion_endpoint, target_resource_id, op_info.port)
    
    t = threading.Thread(target=_start_tunnel, args=(tunnel_server,))
    t.daemon = True
    t.start()

    command = [ ssh_utils.get_ssh_client_path(), _get_host(op_info.local_user, "localhost")]
    command = command + op_info.build_args()
    command = command + ["-p", str(tunnel_server.local_port)]
    command = command + ["-o", "StrictHostKeyChecking=no", "-o", "UserKnownHostsFile=/dev/null"]
    command = command + ["-o", "LogLevel=Error"]
    logger.debug("Running ssh command %s", " ".join(command))

    try:
        subprocess.call(command, shell=platform.system() == "Windows")
    except Exception as ex:
        raise CLIInternalError(ex) from ex
    finally:
        tunnel_server.cleanup()


def _is_ipconnect_request(bastion, target_ip_address):
    if 'enableIpConnect' in bastion and bastion['enableIpConnect'] is True and target_ip_address:
        return True

    return False

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




# ============================= Tunnel Logic ============================= #
def _get_tunnel(cmd, bastion, bastion_endpoint, vm_id, resource_port, port=None):
    from .tunnel import TunnelServer

    if port is None:
        port = 0  # will auto-select a free port from 1024-65535
    tunnel_server = TunnelServer(cmd.cli_ctx, "localhost", port, bastion, bastion_endpoint, vm_id, resource_port)

    return tunnel_server

def _start_tunnel(tunnel_server):
    tunnel_server.start_server()