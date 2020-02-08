# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack import log
from knack import util
import os
import platform
import subprocess


logger = log.get_logger(__name__)


def start_ssh_connection(username, ip, cert_file, private_key_file, ssh_params):
    ssh_params = ssh_params or []
    command = []
    command.append(_get_ssh_path())
    command.append(_get_host(username, ip))
    command = command + _build_args(cert_file, private_key_file)
    command = command + ssh_params
    logger.debug("Running ssh command " + ' '.join(command))
    subprocess.call(command, shell=True)

def _get_ssh_path():
    if platform.system() == 'Windows':
        arch_data = platform.architecture()
        is_32bit = arch_data[0] == '32bit'
        sys_path = 'SysNative' if is_32bit else 'System32'
        system32_path = os.path.join(os.environ['SystemRoot'], sys_path)
        ssh_path = os.path.join(system32_path, "openSSH", "ssh.exe")
        logger.debug("Platform architecture: " + str(arch_data))
        logger.debug("System Root: " + os.environ['SystemRoot'])
        logger.debug("Attempting to run ssh from path " + ssh_path)

        if not os.path.isfile(ssh_path):
            raise util.CLIError("Could not find ssh.exe. Is the OpenSSH client installed?")
        return ssh_path
    else:
        return "ssh"


def _get_host(username, ip):
    return username + "@" + ip


def _build_args(cert_file, private_key_file):
    private_key = ["-i", private_key_file]
    certificate = ["-o", "CertificateFile=" + cert_file]
    return private_key + certificate