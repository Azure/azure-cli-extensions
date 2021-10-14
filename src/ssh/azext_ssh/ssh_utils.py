# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import os
import platform
import subprocess

from knack import log
from azure.cli.core import azclierror

logger = log.get_logger(__name__)


def start_ssh_connection(port, ssh_args, ip, username, cert_file, private_key_file):
    ssh_arg_list = []
    if ssh_args:
        ssh_arg_list = ssh_args
    command = [_get_ssh_path(), _get_host(username, ip)]
    command = command + _build_args(cert_file, private_key_file, port) + ssh_arg_list
    logger.debug("Running ssh command %s", ' '.join(command))
    subprocess.call(command, shell=platform.system() == 'Windows')


def create_ssh_keyfile(private_key_file):
    command = [_get_ssh_path("ssh-keygen"), "-f", private_key_file, "-t", "rsa", "-q", "-N", ""]
    logger.debug("Running ssh-keygen command %s", ' '.join(command))
    subprocess.call(command, shell=platform.system() == 'Windows')


def get_ssh_cert_info(cert_file):
    command = [_get_ssh_path("ssh-keygen"), "-L", "-f", cert_file]
    logger.debug("Running ssh-keygen command %s", ' '.join(command))
    return subprocess.check_output(command, shell=platform.system() == 'Windows').decode().splitlines()


def get_ssh_cert_principals(cert_file):
    info = get_ssh_cert_info(cert_file)
    principals = []
    in_principal = False
    for line in info:
        if ":" in line:
            in_principal = False
        if "Principals:" in line:
            in_principal = True
            continue
        if in_principal:
            principals.append(line.strip())

    return principals


def write_ssh_config(config_path, resource_group, vm_name, overwrite,
                     ip, username, cert_file, private_key_file):

    lines = [""]

    if resource_group and vm_name:
        lines.append("Host " + resource_group + "-" + vm_name)
        lines.append("\tUser " + username)
        lines.append("\tHostName " + ip)
        lines.append("\tCertificateFile " + cert_file)
        if private_key_file:
            lines.append("\tIdentityFile " + private_key_file)

    # default to all hosts for config
    if not ip:
        ip = "*"

    lines.append("Host " + ip)
    lines.append("\tUser " + username)
    lines.append("\tCertificateFile " + cert_file)
    if private_key_file:
        lines.append("\tIdentityFile " + private_key_file)

    if overwrite:
        mode = 'w'
    else:
        mode = 'a'

    with open(config_path, mode) as f:
        f.write('\n'.join(lines))


def _get_ssh_path(ssh_command="ssh"):
    ssh_path = ssh_command

    if platform.system() == 'Windows':
        arch_data = platform.architecture()
        is_32bit = arch_data[0] == '32bit'
        sys_path = 'SysNative' if is_32bit else 'System32'
        system_root = os.environ['SystemRoot']
        system32_path = os.path.join(system_root, sys_path)
        ssh_path = os.path.join(system32_path, "openSSH", (ssh_command + ".exe"))
        logger.debug("Platform architecture: %s", str(arch_data))
        logger.debug("System Root: %s", system_root)
        logger.debug("Attempting to run ssh from path %s", ssh_path)

        if not os.path.isfile(ssh_path):
            raise azclierror.UnclassifiedUserFault(
                "Could not find " + ssh_command + ".exe.",
                "https://docs.microsoft.com/en-us/windows-server/administration/openssh/openssh_install_firstuse")

    return ssh_path


def _get_host(username, ip):
    return username + "@" + ip


def _build_args(cert_file, private_key_file, port):
    private_key = []
    port_arg = []
    if private_key_file:
        private_key = ["-i", private_key_file]
    if port:
        port_arg = ["-p", port]
    certificate = ["-o", "CertificateFile=" + cert_file]
    return private_key + certificate + port_arg
