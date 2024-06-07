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
        from .aaz.latest.network.bastion import Show
        bastion = Show(cli_ctx=cmd.cli_ctx)(command_args={
            "resource_group": op_info.resource_group_name,
            "name": "N-europe-test-vnet-bastion"
        })
        return bastion
    except Exception:
        print("Error")
    

def _get_ssh_path(ssh_command="ssh"):
    import os

    if platform.system() == "Windows":
        arch_data = platform.architecture()
        is_32bit = arch_data[0] == "32bit"
        sys_path = "SysNative" if is_32bit else "System32"
        system_root = os.environ["SystemRoot"]
        system32_path = os.path.join(system_root, sys_path)
        ssh_path = os.path.join(system32_path, "openSSH", (ssh_command + ".exe"))
        logger.debug("Platform architecture: %s", str(arch_data))
        logger.debug("System Root: %s", system_root)
        logger.debug("Attempting to run ssh from path %s", ssh_path)

        if not os.path.isfile(ssh_path):
            raise ValidationError("Could not find " + ssh_command + ".exe. Is the OpenSSH client installed?")
    elif platform.system() in ("Linux", "Darwin"):
        import shutil

        ssh_path = shutil.which(ssh_command)
        if not ssh_path:
            raise UnrecognizedArgumentError(f"{ssh_command} not found in path. Is the OpenSSH client installed?")
    else:
        err_msg = "Platform is not supported for this command. Supported platforms: Windows, Darwin, Linux"
        raise UnrecognizedArgumentError(err_msg)

    return ssh_path

def _get_host(username, ip):
    return username + "@" + ip


def _get_azext_module(extension_name, module_name):
    try:
        # adding the installed extension in the path
        from azure.cli.core.extension.operations import add_extension_to_path
        add_extension_to_path(extension_name)
        # import the extension module
        from importlib import import_module
        azext_custom = import_module(module_name)
        return azext_custom
    except ImportError as ie:
        raise CLIInternalError(ie) from ie


def _build_args(cert_file, private_key_file):
    private_key, certificate = [], []
    if private_key_file:
        private_key = ["-i", private_key_file]
    if cert_file:
        certificate = ["-o", "CertificateFile=" + cert_file]
    return private_key + certificate


def ssh_bastion_host(cmd, op_info, 
                     username=None, ssh_key=None):
    import os
    from .aaz.latest.network.bastion import Show

    bastion = show_bastion(cmd, op_info)

    if bastion['sku']['name'] == BastionSku.Basic.value or bastion['sku']['name'] == BastionSku.Standard.value:
        raise InvalidArgumentValueError("SSH to Bastion host is only supported for Developer Sku. Higher level skus are not supported.")

    if not op_info.port:
        op_info.port = 22

    # ip_connect = _is_ipconnect_request(bastion, op_info.resource_id)
    ip_connect = False
    if ip_connect:
        if int(op_info.port) not in [22, 3389]:
            raise UnrecognizedArgumentError("Custom ports are not allowed. Allowed ports for Tunnel with IP connect is \
                                             22, 3389.")
        target_resource_id = f"/subscriptions/{get_subscription_id(cmd.cli_ctx)}/resourceGroups/{op_info.resource_group_name}" \
                             f"/providers/Microsoft.Network/bh-hostConnect/20.238.21.78"
    else:
        target_resource_id = op_info.resource_id

    _validate_resourceid(target_resource_id)
    print("valid")
    bastion_endpoint = _get_data_pod(cmd, op_info.port, target_resource_id, bastion)

    tunnel_server = _get_tunnel(cmd, bastion, bastion_endpoint, target_resource_id, op_info.port)
    if ip_connect:
        tunnel_server.set_host_name(target_ip_address)
    print("tunnel created")
    t = threading.Thread(target=_start_tunnel, args=(tunnel_server,))
    t.daemon = True
    t.start()
    print("tunnel started")

    cert_folder = tempfile.mkdtemp(prefix="aadsshcert")
    if not os.path.isdir(cert_folder):
        os.makedirs(cert_folder)
    custom.ssh_cert(cmd, cert_path=os.path.join(cert_folder, "id_rsa.pub-aadcert.pub"))
    private_key_file = os.path.join(cert_folder, "id_rsa")
    cert_file = os.path.join(cert_folder, "id_rsa.pub-aadcert.pub")
    username = ssh_utils.get_ssh_cert_principals(cert_file)[0]
    command = [_get_ssh_path(), _get_host(username, "localhost")]
    command = command + _build_args(cert_file, private_key_file)

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




# ============================= Tunnel Logic ============================= #
def _get_tunnel(cmd, bastion, bastion_endpoint, vm_id, resource_port, port=None):
    from .tunnel import TunnelServer

    if port is None:
        port = 0  # will auto-select a free port from 1024-65535
    tunnel_server = TunnelServer(cmd.cli_ctx, "localhost", port, bastion, bastion_endpoint, vm_id, resource_port)

    return tunnel_server

def _start_tunnel(tunnel_server):
    tunnel_server.start_server()