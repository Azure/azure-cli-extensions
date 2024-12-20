# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import colorama
import datetime
import os
import platform
import subprocess
import time

from knack import log
from azure.cli.core import azclierror

from . import constants as const

logger = log.get_logger(__name__)


def start_sftp_connection(op_info):
    try:
        sftp_arg_list = []
        if op_info.sftp_args:
            sftp_arg_list = op_info.sftp_args.split(' ')

        env = os.environ.copy()

        retry_attempt = 0
        retry_attempts_allowed = 0
        successful_connection = False
        sftp_process = None
        connection_duration = None

        # connect with certificate
        destination = [op_info.username + "@" + op_info.host]
        command = ['sftp', "-o PasswordAuthentication=false", "-o PubkeyAcceptedKeyTypes=rsa-sha2-256-cert-v01@openssh.com,rsa-sha2-256"]
        command = command + op_info.build_args() + sftp_arg_list + destination

        while (retry_attempt <= retry_attempts_allowed and not successful_connection):
            connection_duration = time.time()
            try:
                print("Running command: " + ' '.join(command))
                sftp_process = subprocess.Popen(command, env=env, encoding='utf-8', shell=True)
            except OSError as e:
                raise azclierror.UnclassifiedUserFault(f"Failed to start sftp connection with error: {str(e)}.",
                                                       const.RECOMMENDATION_SSH_CLIENT_NOT_FOUND)
            connection_duration = time.time() - connection_duration
            if sftp_process and sftp_process.poll() == 0:
                successful_connection = True
            retry_attempt += 1

    finally:
        print("Connection duration: " + str(connection_duration))


def create_ssh_keyfile(private_key_file, ssh_client_folder=None):
    sshkeygen_path = get_ssh_client_path("ssh-keygen", ssh_client_folder)
    command = [sshkeygen_path, "-f", private_key_file, "-t", "rsa", "-q", "-N", ""]
    logger.debug("Running ssh-keygen command %s", ' '.join(command))
    try:
        subprocess.call(command)
    except OSErrorw as e:
        colorama.init()
        raise azclierror.BadRequestError(f"Failed to create ssh key file with error: {str(e)}.",
                                         const.RECOMMENDATION_SSH_CLIENT_NOT_FOUND)


def get_certificate_start_and_end_times(cert_file, ssh_client_folder=None):
    validity_str = _get_ssh_cert_validity(cert_file, ssh_client_folder)
    times = None
    if validity_str and "Valid: from " in validity_str and " to " in validity_str:
        times = validity_str.replace("Valid: from ", "").split(" to ")
        t0 = datetime.datetime.strptime(times[0], '%Y-%m-%dT%X')
        t1 = datetime.datetime.strptime(times[1], '%Y-%m-%dT%X')
        times = (t0, t1)
    return times


def get_ssh_cert_principals(cert_file, ssh_client_folder=None):
    info = get_ssh_cert_info(cert_file, ssh_client_folder)
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


### Helpers ###
def get_ssh_cert_info(cert_file, ssh_client_folder=None):
    sshkeygen_path = get_ssh_client_path("ssh-keygen", ssh_client_folder)
    command = [sshkeygen_path, "-L", "-f", cert_file]
    logger.debug("Running ssh-keygen command %s", ' '.join(command))
    try:
        return subprocess.check_output(command).decode().splitlines()
    except OSError as e:
        colorama.init()
        raise azclierror.BadRequestError(f"Failed to get certificate info with error: {str(e)}.",
                                         const.RECOMMENDATION_SSH_CLIENT_NOT_FOUND)

def _get_ssh_cert_validity(cert_file, ssh_client_folder=None):
    if cert_file:
        info = get_ssh_cert_info(cert_file, ssh_client_folder)
        for line in info:
            if "Valid:" in line:
                return line.strip()
    return None

def get_ssh_client_path(ssh_command="ssh", ssh_client_folder=None):
    if ssh_client_folder:
        ssh_path = os.path.join(ssh_client_folder, ssh_command)
        if platform.system() == 'Windows':
            ssh_path = ssh_path + '.exe'
        if os.path.isfile(ssh_path):
            logger.debug("Attempting to run %s from path %s", ssh_command, ssh_path)
            return ssh_path
        logger.warning("Could not find %s in provided --ssh-client-folder %s. "
                       "Attempting to get pre-installed OpenSSH bits.", ssh_command, ssh_client_folder)

    ssh_path = ssh_command

    if platform.system() == 'Windows':
        # If OS architecture is 64bit and python architecture is 32bit,
        # look for System32 under SysNative folder.
        machine = platform.machine()
        os_architecture = None
        # python interpreter architecture
        platform_architecture = platform.architecture()[0]
        sys_path = None

        if machine.endswith('64'):
            os_architecture = '64bit'
        elif machine.endswith('86'):
            os_architecture = '32bit'
        elif machine == '':
            raise azclierror.BadRequestError("Couldn't identify the OS architecture.")
        else:
            raise azclierror.BadRequestError(f"Unsuported OS architecture: {machine} is not currently supported")

        if os_architecture == "64bit":
            sys_path = 'SysNative' if platform_architecture == '32bit' else 'System32'
        else:
            sys_path = 'System32'

        system_root = os.environ['SystemRoot']
        system32_path = os.path.join(system_root, sys_path)
        ssh_path = os.path.join(system32_path, "openSSH", (ssh_command + ".exe"))
        logger.debug("Platform architecture: %s", platform_architecture)
        logger.debug("OS architecture: %s", os_architecture)
        logger.debug("System Root: %s", system_root)
        logger.debug("Attempting to run %s from path %s", ssh_command, ssh_path)

        if not os.path.isfile(ssh_path):
            raise azclierror.UnclassifiedUserFault(
                "Could not find " + ssh_command + ".exe on path " + ssh_path + ". ",
                colorama.Fore.YELLOW + "Make sure OpenSSH is installed correctly: "
                "https://docs.microsoft.com/en-us/windows-server/administration/openssh/openssh_install_firstuse . "
                "Or use --ssh-client-folder to provide folder path with ssh executables. " + colorama.Style.RESET_ALL)

    return ssh_path