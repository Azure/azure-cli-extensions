# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import os
import platform
import subprocess
import time
import multiprocessing as mp
from azext_ssh import file_utils

from knack import log
from azure.cli.core import azclierror

logger = log.get_logger(__name__)

CLEANUP_TOTAL_TIME_LIMIT_IN_SECONDS = 120
CLEANUP_TIME_INTERVAL_IN_SECONDS = 10
CLEANUP_AWAIT_TERMINATION_IN_SECONDS = 30


def start_ssh_connection(port, ssh_args, ip, username, cert_file, private_key_file, delete_keys, delete_cert):

    ssh_arg_list = []
    if ssh_args:
        ssh_arg_list = ssh_args

    log_file = None
    if delete_keys or delete_cert:
        if '-E' not in ssh_arg_list and set(['-v', '-vv', '-vvv']).isdisjoint(ssh_arg_list):
            # If the user either provides his own client log file (-E) or
            # wants the client log messages to be printed to the console (-vvv/-vv/-v),
            # we should not use the log files to check for connection success.
            log_file_dir = os.path.dirname(cert_file)
            log_file_name = 'ssh_client_log_' + str(os.getpid())
            log_file = os.path.join(log_file_dir, log_file_name)
            ssh_arg_list = ['-E', log_file, '-v'] + ssh_arg_list
        # Create a new process that will wait until the connection is established and then delete keys.
        cleanup_process = mp.Process(target=_do_cleanup, args=(delete_keys, delete_cert, cert_file, private_key_file,
                                     log_file, True))
        cleanup_process.start()

    command = [_get_ssh_path(), _get_host(username, ip)]
    command = command + _build_args(cert_file, private_key_file, port) + ssh_arg_list

    logger.debug("Running ssh command %s", ' '.join(command))
    subprocess.call(command, shell=platform.system() == 'Windows')

    if delete_keys or delete_cert:
        if cleanup_process.is_alive():
            cleanup_process.terminate()
            # wait for process to terminate
            t0 = time.time()
            while cleanup_process.is_alive() and (time.time() - t0) < CLEANUP_AWAIT_TERMINATION_IN_SECONDS:
                time.sleep(1)

        # Make sure all files have been properly removed.
        _do_cleanup(delete_keys, delete_cert, cert_file, private_key_file)
        if log_file:
            file_utils.delete_file(log_file, f"Couldn't delete temporary log file {log_file}. ", True)
        if delete_keys:
            temp_dir = os.path.dirname(cert_file)
            file_utils.delete_folder(temp_dir, f"Couldn't delete temporary folder {temp_dir}", True)


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


def get_ssh_cert_validity(cert_file):
    info = get_ssh_cert_info(cert_file)
    for line in info:
        if "Valid:" in line:
            return line.strip()
    return None


def write_ssh_config(config_path, resource_group, vm_name, overwrite, port,
                     ip, username, cert_file, private_key_file, delete_keys, delete_cert):

    if delete_keys or delete_cert:
        # Warn users to delete credentials once config file is no longer being used.
        # If user provided keys, only ask them to delete the certificate.
        path_to_delete = os.path.dirname(cert_file)
        items_to_delete = " (id_rsa, id_rsa.pub, id_rsa.pub-aadcert.pub)"
        if not delete_keys:
            path_to_delete = cert_file
            items_to_delete = ""
        validity = get_ssh_cert_validity(cert_file)
        validity_warning = ""
        if validity:
            validity_warning = f" {validity.lower()}"
        logger.warning("%s contains sensitive information%s%s\n"
                       "Please delete it once you no longer need this config file. ",
                       path_to_delete, items_to_delete, validity_warning)

    lines = [""]

    if resource_group and vm_name:
        lines.append("Host " + resource_group + "-" + vm_name)
        lines.append("\tUser " + username)
        lines.append("\tHostName " + ip)
        if cert_file:
            lines.append("\tCertificateFile " + cert_file)
        if private_key_file:
            lines.append("\tIdentityFile " + private_key_file)
        if port:
            lines.append("\tPort " + port)

    # default to all hosts for config
    if not ip:
        ip = "*"

    lines.append("Host " + ip)
    lines.append("\tUser " + username)
    if cert_file:
        lines.append("\tCertificateFile " + cert_file)
    if private_key_file:
        lines.append("\tIdentityFile " + private_key_file)
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


def _get_host(username, ip):
    return username + "@" + ip


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


def _do_cleanup(delete_keys, delete_cert, cert_file, private_key, log_file=None, wait=False):
    # if there is a log file, use it to check for the connection success
    if log_file:
        t0 = time.time()
        match = False
        while (time.time() - t0) < CLEANUP_TOTAL_TIME_LIMIT_IN_SECONDS and not match:
            time.sleep(CLEANUP_TIME_INTERVAL_IN_SECONDS)
            try:
                with open(log_file, 'r') as ssh_client_log:
                    match = "debug1: Authentication succeeded" in ssh_client_log.read()
                    ssh_client_log.close()
            except:
                # If there is an exception, wait for a little bit and try again
                time.sleep(CLEANUP_TIME_INTERVAL_IN_SECONDS)

    elif wait:
        # if we are not checking the logs, but still want to wait for connection before deleting files
        time.sleep(CLEANUP_TOTAL_TIME_LIMIT_IN_SECONDS)

    # TO DO: Once arc changes are merged, delete relay information as well
    if delete_keys and private_key:
        public_key = private_key + '.pub'
        file_utils.delete_file(private_key, f"Couldn't delete private key {private_key}. ", True)
        file_utils.delete_file(public_key, f"Couldn't delete public key {public_key}. ", True)
    if delete_cert and cert_file:
        file_utils.delete_file(cert_file, f"Couldn't delete certificate {cert_file}. ", True)
