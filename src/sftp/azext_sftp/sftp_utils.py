# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import colorama
import os
import platform
import subprocess
import time
import signal
import datetime

from knack import log
from azure.cli.core import azclierror

from . import constants as const

logger = log.get_logger(__name__)


def _build_sftp_command(op_info):
    """Build the SFTP command with all necessary arguments."""
    destination = op_info.get_destination()
    command = [
        get_ssh_client_path("sftp", op_info.ssh_client_folder),
        "-o", "PasswordAuthentication=no",
        "-o", "StrictHostKeyChecking=no",
        "-o", "UserKnownHostsFile=/dev/null",
        "-o", "PubkeyAcceptedKeyTypes=rsa-sha2-256-cert-v01@openssh.com,rsa-sha2-256",
        "-o", "LogLevel=ERROR"
    ]
    command.extend(op_info.build_args())

    if op_info.sftp_args:
        sftp_arg_list = op_info.sftp_args.split(' ') if isinstance(op_info.sftp_args, str) else op_info.sftp_args
        command.extend(sftp_arg_list)

    command.append(destination)
    return command


def _handle_process_interruption(sftp_process):
    """Handle keyboard interruption of SFTP process."""
    logger.info("Connection interrupted by user (KeyboardInterrupt)")
    if not sftp_process:
        return

    if platform.system() == "Windows":
        sftp_process.send_signal(signal.CTRL_BREAK_EVENT)
    else:
        sftp_process.terminate()

    try:
        sftp_process.wait(timeout=5)
    except (subprocess.TimeoutExpired, OSError):
        pass


def _execute_sftp_process(command, env, creationflags):
    """Execute the SFTP process."""
    sftp_process = subprocess.Popen(
        command, env=env, encoding='utf-8', creationflags=creationflags
    )
    try:
        return_code = sftp_process.wait()
        return sftp_process, return_code
    except KeyboardInterrupt:
        _handle_process_interruption(sftp_process)
        return sftp_process, None


def _attempt_connection(command, env, creationflags, op_info, attempt_num):  # pylint: disable=unused-argument
    """Attempt a single SFTP connection."""
    connection_start_time = time.time()
    try:
        logger.debug("Running SFTP command (attempt %d): %s", attempt_num, ' '.join(command))

        _, return_code = _execute_sftp_process(command, env, creationflags)

        if return_code is None:  # KeyboardInterrupt occurred
            return False, None, None

        if return_code == 0:
            connection_duration = time.time() - connection_start_time
            logger.debug("SFTP connection successful in %.2f seconds", connection_duration)
            return True, connection_duration, None

        logger.warning("SFTP connection failed with return code: %d", return_code)
        return False, time.time() - connection_start_time, None

    except OSError as e:
        connection_duration = time.time() - connection_start_time
        error_msg = f"Failed to start SFTP connection: {str(e)}"
        return False, connection_duration, error_msg


def start_sftp_connection(op_info):
    """Start an SFTP connection using the provided session information."""
    try:
        env = os.environ.copy()
        retry_attempts_allowed = 2
        command = _build_sftp_command(op_info)
        logger.debug("SFTP command: %s", ' '.join(command))

        creationflags = subprocess.CREATE_NEW_PROCESS_GROUP if platform.system() == "Windows" else 0

        for attempt in range(retry_attempts_allowed + 1):
            result = _attempt_connection(command, env, creationflags, op_info, attempt + 1)
            successful, duration, error_msg = result

            if successful:
                return
            if duration is None:  # KeyboardInterrupt
                return

            if error_msg:  # OSError occurred
                if attempt >= retry_attempts_allowed:
                    raise azclierror.UnclassifiedUserFault(error_msg, const.RECOMMENDATION_SSH_CLIENT_NOT_FOUND)
                logger.warning("%s. Retrying...", error_msg)

            if duration is not None:
                logger.debug("Connection attempt %d duration: %.2f seconds", attempt + 1, duration)
            if attempt < retry_attempts_allowed:
                time.sleep(1)

        raise azclierror.UnclassifiedUserFault(
            "Failed to establish SFTP connection after multiple attempts.",
            "Please check your network connection, credentials, and that the SFTP server is accessible."
        )

    except KeyboardInterrupt:
        logger.info("SFTP connection interrupted by user")
        print("\nSFTP session exited cleanly.")


def create_ssh_keyfile(private_key_file, ssh_client_folder=None):
    """Create an SSH key file using ssh-keygen."""
    sshkeygen_path = get_ssh_client_path("ssh-keygen", ssh_client_folder)
    command = [sshkeygen_path, "-f", private_key_file, "-t", "rsa", "-q", "-N", ""]
    logger.debug("Running ssh-keygen command %s", ' '.join(command))
    try:
        subprocess.call(command)
    except OSError as e:
        colorama.init()
        raise azclierror.BadRequestError(f"Failed to create ssh key file with error: {str(e)}.",
                                         const.RECOMMENDATION_SSH_CLIENT_NOT_FOUND)


def get_ssh_cert_principals(cert_file, ssh_client_folder=None):
    """Extract principals from SSH certificate."""
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


def get_ssh_cert_info(cert_file, ssh_client_folder=None):
    """Get SSH certificate information using ssh-keygen."""
    sshkeygen_path = get_ssh_client_path("ssh-keygen", ssh_client_folder)
    command = [sshkeygen_path, "-L", "-f", cert_file]
    logger.debug("Running ssh-keygen command %s", ' '.join(command))
    try:
        return subprocess.check_output(command).decode().splitlines()
    except OSError as e:
        colorama.init()
        raise azclierror.BadRequestError(f"Failed to get certificate info with error: {str(e)}.",
                                         const.RECOMMENDATION_SSH_CLIENT_NOT_FOUND)


_warned_ssh_client_folders = set()


def get_ssh_client_path(ssh_command="ssh", ssh_client_folder=None):
    """Get the path to an SSH client executable."""
    if ssh_client_folder:
        ssh_path = os.path.join(ssh_client_folder, ssh_command)
        if platform.system() == 'Windows':
            ssh_path += '.exe'
        if os.path.isfile(ssh_path):
            logger.debug("Attempting to run %s from path %s", ssh_command, ssh_path)
            return ssh_path
        warn_key = (ssh_command, os.path.abspath(ssh_client_folder))
        if warn_key not in _warned_ssh_client_folders:
            logger.warning("Could not find %s in provided --ssh-client-folder %s. "
                           "Attempting to get pre-installed OpenSSH bits.", ssh_command, ssh_client_folder)
            _warned_ssh_client_folders.add(warn_key)

    if platform.system() != 'Windows':
        return ssh_command

    # Windows-specific logic
    machine = platform.machine()
    if not machine.endswith(('64', '86')):
        if machine == '':
            raise azclierror.BadRequestError("Couldn't identify the OS architecture.")
        raise azclierror.BadRequestError(f"Unsupported OS architecture: {machine} is not currently supported")

    # Determine system path
    is_64bit = machine.endswith('64')
    is_32bit_python = platform.architecture()[0] == '32bit'
    sys_path = 'SysNative' if is_64bit and is_32bit_python else 'System32'

    system_root = os.environ['SystemRoot']
    ssh_path = os.path.join(system_root, sys_path, "openSSH", f"{ssh_command}.exe")

    logger.debug("Platform architecture: %s", platform.architecture()[0])
    logger.debug("OS architecture: %s", '64bit' if is_64bit else '32bit')
    logger.debug("System Root: %s", system_root)
    logger.debug("Attempting to run %s from path %s", ssh_command, ssh_path)

    if not os.path.isfile(ssh_path):
        raise azclierror.UnclassifiedUserFault(
            f"Could not find {ssh_command}.exe on path {ssh_path}. ",
            colorama.Fore.YELLOW + "Make sure OpenSSH is installed correctly: "
            "https://docs.microsoft.com/en-us/windows-server/administration/openssh/openssh_install_firstuse . "
            "Or use --ssh-client-folder to provide folder path with ssh executables. " + colorama.Style.RESET_ALL)

    return ssh_path


def get_certificate_start_and_end_times(cert_file, ssh_client_folder=None):
    """Get start and end times from SSH certificate validity."""
    validity_str = _get_ssh_cert_validity(cert_file, ssh_client_folder)
    times = None
    if validity_str and "Valid: from " in validity_str and " to " in validity_str:
        try:
            times = validity_str.replace("Valid: from ", "").split(" to ")
            t0 = datetime.datetime.strptime(times[0], '%Y-%m-%dT%X')
            t1 = datetime.datetime.strptime(times[1], '%Y-%m-%dT%X')
            times = (t0, t1)
        except (ValueError, TypeError, IndexError):
            # Invalid date format or parsing error
            times = None
    return times


def _get_ssh_cert_validity(cert_file, ssh_client_folder=None):
    """Get validity line from SSH certificate info."""
    if cert_file:
        info = get_ssh_cert_info(cert_file, ssh_client_folder)
        for line in info:
            if "Valid:" in line:
                return line.strip()
    return None
