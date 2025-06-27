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
import sys
import signal

from knack import log
from azure.cli.core import azclierror

from . import constants as const

logger = log.get_logger(__name__)


def start_sftp_connection(op_info):
    """Start an SFTP connection using the provided session information."""
    try:
        env = os.environ.copy()
        retry_attempt = 0
        retry_attempts_allowed = 2  # Allow a couple retries for network issues
        successful_connection = False
        sftp_process = None
        connection_start_time = None
        destination = op_info.get_destination()
        command = [
            get_ssh_client_path("sftp", op_info.ssh_client_folder),
            "-o", "PasswordAuthentication=no",
            "-o", "StrictHostKeyChecking=no",
            "-o", "UserKnownHostsFile=/dev/null",
            "-o", "PubkeyAcceptedKeyTypes=rsa-sha2-256-cert-v01@openssh.com,rsa-sha2-256",
            "-o", "LogLevel=ERROR"  # Reduce verbose output
        ]
        command.extend(op_info.build_args())
        if op_info.sftp_args:
            if isinstance(op_info.sftp_args, str):
                sftp_arg_list = op_info.sftp_args.split(' ')
            else:
                sftp_arg_list = op_info.sftp_args
            command.extend(sftp_arg_list)
        command.append(destination)
        logger.debug("SFTP command: %s", ' '.join(command))
        creationflags = 0
        if platform.system() == "Windows":
            creationflags = subprocess.CREATE_NEW_PROCESS_GROUP
        while retry_attempt <= retry_attempts_allowed and not successful_connection:
            connection_start_time = time.time()
            try:
                print(f"Connecting to SFTP server (attempt {retry_attempt + 1})...")
                logger.debug("Running SFTP command: %s", ' '.join(command))
                # If batch commands are provided, use them as stdin
                batch_input = getattr(op_info, 'sftp_batch_commands', None)
                if batch_input:
                    sftp_process = subprocess.Popen(
                        command, env=env, encoding='utf-8', stdin=subprocess.PIPE, creationflags=creationflags
                    )
                    sftp_process.communicate(input=batch_input)
                    return_code = sftp_process.returncode
                else:
                    sftp_process = subprocess.Popen(
                        command, env=env, encoding='utf-8', creationflags=creationflags
                    )
                    try:
                        return_code = sftp_process.wait()
                    except KeyboardInterrupt:
                        logger.info("Connection interrupted by user (KeyboardInterrupt)")
                        if sftp_process:
                            if platform.system() == "Windows":
                                # Send CTRL_BREAK_EVENT to the process group
                                sftp_process.send_signal(signal.CTRL_BREAK_EVENT)
                            else:
                                sftp_process.terminate()
                            try:
                                sftp_process.wait(timeout=5)
                            except Exception:
                                pass
                        return
                if return_code == 0:
                    successful_connection = True
                    connection_duration = time.time() - connection_start_time
                    logger.debug("SFTP connection successful in %.2f seconds", connection_duration)
                else:
                    logger.warning("SFTP connection failed with return code: %d", return_code)
            except OSError as e:
                error_msg = f"Failed to start SFTP connection: {str(e)}"
                if retry_attempt >= retry_attempts_allowed:
                    raise azclierror.UnclassifiedUserFault(error_msg, const.RECOMMENDATION_SSH_CLIENT_NOT_FOUND)
                else:
                    logger.warning("%s. Retrying...", error_msg)
            connection_duration = time.time() - connection_start_time
            logger.debug("Connection attempt %d duration: %.2f seconds", retry_attempt + 1, connection_duration)
            retry_attempt += 1
            if retry_attempt <= retry_attempts_allowed and not successful_connection:
                time.sleep(1)

        if not successful_connection:
            raise azclierror.UnclassifiedUserFault(
                "Failed to establish SFTP connection after multiple attempts.",
                "Please check your network connection, credentials, and that the SFTP server is accessible."
            )

    except KeyboardInterrupt:
        logger.info("SFTP connection interrupted by user (outer handler)")
        print("\nSFTP session exited cleanly.")
    finally:
        if connection_start_time:
            total_duration = time.time() - connection_start_time
            logger.debug("Total connection session duration: %.2f seconds", total_duration)


def create_ssh_keyfile(private_key_file, ssh_client_folder=None):
    sshkeygen_path = get_ssh_client_path("ssh-keygen", ssh_client_folder)
    command = [sshkeygen_path, "-f", private_key_file, "-t", "rsa", "-q", "-N", ""]
    logger.debug("Running ssh-keygen command %s", ' '.join(command))
    try:
        subprocess.call(command)
    except OSError as e:
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


# Helpers
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
