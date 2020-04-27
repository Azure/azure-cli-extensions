# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import os
import platform
import subprocess

from knack import log
from knack import util

from . import file_utils

logger = log.get_logger(__name__)


def start_ssh_connection(ip, username, cert_file, private_key_file):
    command = [_get_ssh_path(), _get_host(username, ip)]
    command = command + _build_args(cert_file, private_key_file)
    logger.debug("Running ssh command %s", ' '.join(command))
    subprocess.call(command, shell=True)


def write_ssh_config(config_path, resource_group, vm_name,
                     ip, username, cert_file, private_key_file):
    file_utils.make_dirs_for_file(config_path)
    lines = []
    if resource_group and vm_name:
        lines.append("Host " + resource_group + "-" + vm_name)
        lines.append("\tUser " + username)
        lines.append("\tHostName " + ip)
        lines.append("\tCertificateFile " + cert_file)
        lines.append("\tIdentityFile " + private_key_file)

    lines.append("Host " + ip)
    lines.append("\tUser " + username)
    lines.append("\tHostName " + ip)
    lines.append("\tCertificateFile " + cert_file)
    lines.append("\tIdentityFile " + private_key_file)

    with open(config_path, 'w') as f:
        f.write('\n'.join(lines))


def _get_ssh_path():
    ssh_path = "ssh"

    if platform.system() == 'Windows':
        arch_data = platform.architecture()
        is_32bit = arch_data[0] == '32bit'
        sys_path = 'SysNative' if is_32bit else 'System32'
        system_root = os.environ['SystemRoot']
        system32_path = os.path.join(system_root, sys_path)
        ssh_path = os.path.join(system32_path, "openSSH", "ssh.exe")
        logger.debug("Platform architecture: %s", str(arch_data))
        logger.debug("System Root: %s", system_root)
        logger.debug("Attempting to run ssh from path %s", ssh_path)

        if not os.path.isfile(ssh_path):
            raise util.CLIError("Could not find ssh.exe. Is the OpenSSH client installed?")

    return ssh_path


def _get_host(username, ip):
    return username + "@" + ip


def _build_args(cert_file, private_key_file):
    private_key = ["-i", private_key_file]
    certificate = ["-o", "CertificateFile=" + cert_file]
    return private_key + certificate
