# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import os
import platform
import subprocess
import tempfile
import stat
import multiprocessing as mp
import time
import re
import oschmod

from knack import log
from azure.cli.core import azclierror

from . import file_utils
from . import constants as const

logger = log.get_logger(__name__)


def start_ssh_connection(relay_info, proxy_path, vm_name, ip, username, cert_file, private_key_file, port,
                         is_arc, ssh_client_path, ssh_args, delete_privkey):

    if not ssh_client_path:
        ssh_client_path = _get_ssh_path()
    ssh_arg_list = []
    if ssh_args:
        ssh_arg_list = ssh_args
    env = os.environ.copy()

    ssh_client_log_file_arg = []
    # delete_privkey is only true for injected commands in the portal one click ssh experience
    if delete_privkey and (cert_file or private_key_file):
        if '-E' in ssh_arg_list:
            # This condition should rarely be true
            index = ssh_arg_list.index('-E')
            log_file = ssh_arg_list[index + 1]
        else:
            if cert_file:
                log_dir = os.path.dirname(cert_file)
            elif private_key_file:
                log_dir = os.path.dirname(private_key_file)
            log_file_name = 'ssh_client_log_' + str(os.getpid())
            log_file = os.path.join(log_dir, log_file_name)
            ssh_client_log_file_arg = ['-E', log_file]

        if '-v' not in ssh_arg_list and '-vv' not in ssh_arg_list and '-vvv' not in ssh_arg_list:
            ssh_client_log_file_arg = ssh_client_log_file_arg + ['-v']

    if is_arc:
        env['SSHPROXY_RELAY_INFO'] = relay_info
        if port:
            pcommand = f"ProxyCommand={proxy_path} -p {port}"
        else:
            pcommand = f"ProxyCommand={proxy_path}"
        args = ["-o", pcommand] + _build_args(cert_file, private_key_file, None)
        host = _get_host(username, vm_name)
    else:
        host = _get_host(username, ip)
        args = _build_args(cert_file, private_key_file, port)

    command = [ssh_client_path, host]
    command = command + args + ssh_client_log_file_arg + ssh_arg_list

    # If delete_privkey flag is true, we will try to clean the private key file and the certificate file
    # once the connection has been established. If it's not possible to open the log file, we default to
    # waiting for about 2 minutes once the ssh process starts before cleaning up the files.
    if delete_privkey and (cert_file or private_key_file):
        if os.path.isfile(log_file):
            file_utils.delete_file(log_file, f"Couldn't delete existing log file {log_file}", True)
        cleanup_process = mp.Process(target=_do_cleanup, args=(private_key_file, cert_file, log_file))
        cleanup_process.start()

    logger.debug("Running ssh command %s", ' '.join(command))
    subprocess.call(command, shell=platform.system() == 'Windows', env=env)

    # If the cleanup process is still alive once the ssh process is terminated, we terminate it and make
    # sure the private key and certificate are deleted.
    if delete_privkey and (cert_file or private_key_file):
        if cleanup_process.is_alive():
            cleanup_process.terminate()
            time.sleep(1)
        _do_cleanup(private_key_file, cert_file)


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


def write_ssh_config(relay_info, proxy_path, vm_name, ip, username,
                     cert_file, private_key_file, port, is_arc, config_path, overwrite, resource_group):

    common_lines = []
    common_lines.append("\tUser " + username)
    if cert_file:
        common_lines.append("\tCertificateFile " + cert_file)
    if private_key_file:
        common_lines.append("\tIdentityFile " + private_key_file)

    lines = [""]
    if is_arc:
        if cert_file:
            relay_info_dir = os.path.dirname(cert_file)
        elif private_key_file:
            relay_info_dir = os.path.dirname(private_key_file)
        else:
            relay_info_dir = tempfile.mkdtemp(prefix="ssharcrelayinfo")
        relay_info_path = os.path.join(relay_info_dir, "relay_info")
        file_utils.write_to_file(relay_info_path, 'w', relay_info,
                                 f"Couldn't write relay information to file {relay_info_path}", 'utf-8')
        oschmod.set_mode(relay_info_path, stat.S_IRUSR)

        lines.append("Host " + resource_group + "-" + vm_name)
        lines = lines + common_lines
        if port:
            lines.append("\tProxyCommand " + proxy_path + " " + "-r " + relay_info_path + " " + "-p " + port)
        else:
            lines.append("\tProxyCommand " + proxy_path + " " + "-r " + relay_info_path)
    else:
        if resource_group and vm_name:
            lines.append("Host " + resource_group + "-" + vm_name)
            lines.append("\tHostName " + ip)
            lines = lines + common_lines
            if port:
                lines.append("\tPort " + port)

        # default to all hosts for config
        if not ip:
            ip = "*"

        lines.append("Host " + ip)
        lines = lines + common_lines
        if port:
            lines.append("\tPort " + port)

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


def _get_host(username, target):
    return username + "@" + target


def _build_args(cert_file, private_key_file, port):
    private_key = []
    port_arg = []
    certificate = []
    if private_key_file:
        private_key = ["-i", private_key_file]
    if port:
        port_arg = ["-p", port]
    if cert_file:
        certificate = ["-o", "CertificateFile=" + cert_file]
    return private_key + certificate + port_arg


def _do_cleanup(private_key_file, cert_file, log_file=None):
    if os.environ.get("AZUREPS_HOST_ENVIRONMENT") != "cloud-shell/1.0":
        raise azclierror.BadRequestError("Can't delete private key file. "
                                         "The --delete-private-key flag set to True, "
                                         "but this is not an Azure Cloud Shell session.")
    if log_file:
        t0 = time.time()
        match = False
        while (time.time() - t0) < const.CLEANUP_TOTAL_TIME_LIMIT_IN_SECONDS and not match:
            time.sleep(const.CLEANUP_TIME_INTERVAL_IN_SECONDS)
            try:
                with open(log_file, 'r') as ssh_client_log:
                    for line in ssh_client_log:
                        if re.search("debug1: Authentication succeeded", line):
                            match = True
                ssh_client_log.close()
            except:
                t1 = time.time() - t0
                if t1 < const.CLEANUP_TOTAL_TIME_LIMIT_IN_SECONDS:
                    time.sleep(const.CLEANUP_TOTAL_TIME_LIMIT_IN_SECONDS - t1)

    if private_key_file and os.path.isfile(private_key_file):
        file_utils.delete_file(private_key_file, f"Failed to delete private key file '{private_key_file}'. ")

    if cert_file and os.path.isfile(cert_file):
        file_utils.delete_file(cert_file, f"Failed to delete certificate file '{cert_file}'. ")
