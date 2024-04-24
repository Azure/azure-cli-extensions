# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import os
import datetime
import oschmod

from azure.cli.core.style import Style, print_styled_text

from azure.cli.core import azclierror
from knack import log
from . import file_utils
from . import connectivity_utils

logger = log.get_logger(__name__)


class SSHSession():
    # pylint: disable=too-many-instance-attributes
    def __init__(self, resource_group_name, vm_name, ssh_ip, public_key_file,
                 private_key_file, use_private_ip, local_user, cert_file, port,
                 ssh_client_folder, ssh_args, delete_credentials, resource_type,
                 ssh_proxy_folder, credentials_folder, winrdp, yes_without_prompt):
        self.resource_group_name = resource_group_name
        self.vm_name = vm_name
        self.ip = ssh_ip
        self.use_private_ip = use_private_ip
        self.local_user = local_user
        self.port = port
        self.ssh_args = ssh_args
        self.delete_credentials = delete_credentials
        self.resource_type = resource_type
        self.winrdp = winrdp
        self.proxy_path = None
        self.relay_info = None
        self.new_service_config = False
        self.yes_without_prompt = yes_without_prompt
        self.public_key_file = os.path.abspath(public_key_file) if public_key_file else None
        self.private_key_file = os.path.abspath(private_key_file) if private_key_file else None
        self.cert_file = os.path.abspath(cert_file) if cert_file else None
        self.ssh_client_folder = os.path.abspath(ssh_client_folder) if ssh_client_folder else None
        self.ssh_proxy_folder = os.path.abspath(ssh_proxy_folder) if ssh_proxy_folder else None
        self.credentials_folder = os.path.abspath(credentials_folder) if credentials_folder else None

    def is_arc(self):
        if self.resource_type in ["Microsoft.HybridCompute/machines",
                                  "Microsoft.ConnectedVMwarevSphere/virtualMachines",
                                  "Microsoft.ScVmm/virtualMachines",
                                  "Microsoft.AzureStackHCI/virtualMachines"]:
            return True
        return False

    def get_host(self):
        if not self.is_arc() and self.ip:
            return self.ip

        if self.is_arc() and self.vm_name:
            return self.vm_name

        raise azclierror.BadRequestError("Unable to determine host.")

    # build args behaves different depending on the resource type
    def build_args(self):
        private_key = []
        port_arg = []
        certificate = []
        proxy_command = []
        if self.private_key_file:
            private_key = ["-i", self.private_key_file]
        if self.cert_file:
            certificate = ["-o", "CertificateFile=\"" + self.cert_file + "\""]
        if self.is_arc():
            if self.port:
                proxy_command = ["-o", f"ProxyCommand=\"{self.proxy_path}\" -p {self.port}"]
            else:
                proxy_command = ["-o", f"ProxyCommand=\"{self.proxy_path}\""]
        else:
            if self.port:
                port_arg = ["-p", self.port]
        return proxy_command + private_key + certificate + port_arg


class ConfigSession():
    # pylint: disable=too-many-instance-attributes
    def __init__(self, config_path, resource_group_name, vm_name, ssh_ip,
                 public_key_file, private_key_file, overwrite, use_private_ip,
                 local_user, cert_file, port, resource_type, credentials_folder,
                 ssh_proxy_folder, ssh_client_folder, yes_without_prompt):
        self.config_path = os.path.abspath(config_path)
        self.resource_group_name = resource_group_name
        self.vm_name = vm_name
        self.ip = ssh_ip
        self.overwrite = overwrite
        self.use_private_ip = use_private_ip
        self.local_user = local_user
        self.port = port
        self.resource_type = resource_type
        self.proxy_path = None
        self.relay_info = None
        self.relay_info_path = None
        self.yes_without_prompt = yes_without_prompt
        self.public_key_file = os.path.abspath(public_key_file) if public_key_file else None
        self.private_key_file = os.path.abspath(private_key_file) if private_key_file else None
        self.cert_file = os.path.abspath(cert_file) if cert_file else None
        self.ssh_client_folder = os.path.abspath(ssh_client_folder) if ssh_client_folder else None
        self.ssh_proxy_folder = os.path.abspath(ssh_proxy_folder) if ssh_proxy_folder else None
        self.credentials_folder = os.path.abspath(credentials_folder) if credentials_folder else None

    def is_arc(self):
        if self.resource_type in ["Microsoft.HybridCompute/machines",
                                  "Microsoft.ConnectedVMwarevSphere/virtualMachines"]:
            return True
        return False

    def get_config_text(self, is_aad):
        lines = [""]
        if self.is_arc():
            self.relay_info_path = self._create_relay_info_file()
            lines = lines + self._get_arc_entry(is_aad)
        else:
            if self.resource_group_name and self.vm_name and self.ip:
                lines = lines + self._get_rg_and_vm_entry(is_aad)
            # default to all hosts for config
            if not self.ip:
                self.ip = "*"
            lines = lines + self._get_ip_entry(is_aad)
        return lines

    def _get_arc_entry(self, is_aad):
        lines = []
        if is_aad:
            lines.append("Host " + self.resource_group_name + "-" + self.vm_name)
        else:
            lines.append("Host " + self.resource_group_name + "-" + self.vm_name + "-" + self.local_user)
        lines.append("\tHostName " + self.vm_name)
        lines.append("\tUser " + self.local_user)
        if self.cert_file:
            lines.append("\tCertificateFile \"" + self.cert_file + "\"")
        if self.private_key_file:
            lines.append("\tIdentityFile \"" + self.private_key_file + "\"")
        if self.port:
            lines.append("\tProxyCommand \"" + self.proxy_path + "\" " + "-r \"" + self.relay_info_path + "\" "
                         + "-p " + self.port)
        else:
            lines.append("\tProxyCommand \"" + self.proxy_path + "\" " + "-r \"" + self.relay_info_path + "\"")
        return lines

    def _get_rg_and_vm_entry(self, is_aad):
        lines = []
        if is_aad:
            lines.append("Host " + self.resource_group_name + "-" + self.vm_name)
        else:
            lines.append("Host " + self.resource_group_name + "-" + self.vm_name + "-" + self.local_user)
        lines.append("\tUser " + self.local_user)
        lines.append("\tHostName " + self.ip)
        if self.cert_file:
            lines.append("\tCertificateFile \"" + self.cert_file + "\"")
        if self.private_key_file:
            lines.append("\tIdentityFile \"" + self.private_key_file + "\"")
        if self.port:
            lines.append("\tPort " + self.port)
        return lines

    def _get_ip_entry(self, is_aad):
        lines = []
        if is_aad:
            lines.append("Host " + self.ip)
        else:
            lines.append("Host " + self.ip + "-" + self.local_user)
            lines.append("\tHostName " + self.ip)
        lines.append("\tUser " + self.local_user)
        if self.cert_file:
            lines.append("\tCertificateFile \"" + self.cert_file + "\"")
        if self.private_key_file:
            lines.append("\tIdentityFile \"" + self.private_key_file + "\"")
        if self.port:
            lines.append("\tPort " + self.port)
        return lines

    def _create_relay_info_file(self):
        relay_info_dir = self.credentials_folder
        relay_info_filename = None
        if not os.path.isdir(relay_info_dir):
            os.makedirs(relay_info_dir)

        if self.vm_name and self.resource_group_name:
            relay_info_filename = self.resource_group_name + "-" + self.vm_name + "-relay_info"

        relay_info_path = os.path.join(relay_info_dir, relay_info_filename)
        # Overwrite relay_info if it already exists in that folder.
        file_utils.delete_file(relay_info_path, f"{relay_info_path} already exists, and couldn't be overwritten.")
        file_utils.write_to_file(relay_info_path, 'w', connectivity_utils.format_relay_info_string(self.relay_info),
                                 f"Couldn't write relay information to file {relay_info_path}.", 'utf-8')
        oschmod.set_mode(relay_info_path, 0o644)
        # pylint: disable=broad-except
        try:
            # pylint: disable=unsubscriptable-object
            expiration = datetime.datetime.fromtimestamp(self.relay_info['expiresOn'])
            expiration = expiration.strftime("%Y-%m-%d %I:%M:%S %p")
            print_styled_text((Style.SUCCESS, f"Generated relay information {relay_info_path} is valid until "
                                              f"{expiration} in local time."))
        except Exception as e:
            logger.warning("Couldn't determine relay information expiration. Error: %s", str(e))

        return relay_info_path
