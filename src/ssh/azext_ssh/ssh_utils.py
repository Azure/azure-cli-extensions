# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import os
import platform
import subprocess
import time
import datetime
import re
import sys
import colorama

from knack import log
from azure.cli.core import azclierror
from azure.cli.core import telemetry
from azure.cli.core.style import Style, print_styled_text

from . import file_utils
from . import connectivity_utils
from . import constants as const

logger = log.get_logger(__name__)


def start_ssh_connection(op_info, delete_keys, delete_cert):
    try:
        ssh_arg_list = []
        if op_info.ssh_args:
            ssh_arg_list = op_info.ssh_args

        # Redirecting stderr:
        # 1. Read SSH logs to determine if authentication was successful so credentials can be deleted
        # 2. Read SSHProxy error messages to print friendly error messages for well known errors.
        # When connecting to a local user on a host with a banner, output gets messed up if stderr redirected.
        # If user expects logs to be printed, do not redirect logs. In some ocasions output gets messed up.
        redirect_stderr = set(['-v', '-vv', '-vvv']).isdisjoint(ssh_arg_list) and \
            (delete_cert or op_info.delete_credentials)
        if redirect_stderr:
            ssh_arg_list = ['-v'] + ssh_arg_list

        env = os.environ.copy()
        if op_info.is_arc():
            env['SSHPROXY_RELAY_INFO'] = connectivity_utils.format_relay_info_string(op_info.relay_info)

        retry_attempt = 0
        retry_attempts_allowed = 0
        successful_connection = False
        ssh_process = None
        connection_duration = None

        # Get ssh client before starting the clean up process in case there is an error in getting client.
        command = [get_ssh_client_path('ssh', op_info.ssh_client_folder), op_info.get_host(), "-l", op_info.local_user]

        command = command + op_info.build_args() + ssh_arg_list
        logger.debug("Running ssh command %s", ' '.join(command))

        while (retry_attempt <= retry_attempts_allowed and not successful_connection):
            service_config_delay_error_logs = False
            if retry_attempt == 1:
                logger.warning("SSH connection failed, possibly caused by new service configuration setup. "
                               "Retrying the connection in %d seconds.", const.RETRY_DELAY_IN_SECONDS)
                time.sleep(const.RETRY_DELAY_IN_SECONDS)
            connection_duration = time.time()
            try:
                # pylint: disable=consider-using-with
                if redirect_stderr:
                    ssh_process = subprocess.Popen(command, stderr=subprocess.PIPE, env=env, encoding='utf-8')
                    service_config_delay_error_logs = _check_ssh_logs_for_common_errors(ssh_process, op_info,
                                                                                        delete_cert, delete_keys)
                else:
                    ssh_process = subprocess.Popen(command, env=env, encoding='utf-8')
                    _wait_to_delete_credentials(ssh_process, op_info, delete_cert, delete_keys)
            except OSError as e:
                colorama.init()
                raise azclierror.BadRequestError(f"Failed to run ssh command with error: {str(e)}.",
                                                 const.RECOMMENDATION_SSH_CLIENT_NOT_FOUND)

            connection_duration = (time.time() - connection_duration) / 60
            if ssh_process and ssh_process.poll() == 0:
                successful_connection = True
            if op_info.new_service_config and \
                    (service_config_delay_error_logs or (ssh_process.poll() == 255 and not redirect_stderr)):
                retry_attempts_allowed = 1
                if retry_attempt == 1:
                    logger.warning("SSH connection failure could still be due to Service Configuration update. "
                                   "Please re-run command.")
            retry_attempt += 1

    finally:
        ssh_connection_data = {'Context.Default.AzureCLI.SSHConnectionDurationInMinutes': connection_duration}
        if successful_connection:
            ssh_connection_data['Context.Default.AzureCLI.SSHConnectionStatus'] = "Success"
        telemetry.add_extension_event('ssh', ssh_connection_data)
        # Even if something fails between the creation of the credentials and the end of the ssh connection, we
        # want to make sure that all credentials are cleaned up.
        do_cleanup(delete_keys, delete_cert, op_info.delete_credentials,
                   op_info.cert_file, op_info.private_key_file, op_info.public_key_file)


def write_ssh_config(config_info, delete_keys, delete_cert):
    # if delete cert is true, then this is AAD login.
    config_text = config_info.get_config_text(delete_cert)
    _issue_config_cleanup_warning(delete_cert, delete_keys, config_info.is_arc(),
                                  config_info.cert_file, config_info.relay_info_path,
                                  config_info.ssh_client_folder)
    if config_info.overwrite:
        mode = 'w'
    else:
        mode = 'a'
    with open(config_info.config_path, mode, encoding='utf-8') as f:
        f.write('\n'.join(config_text))


def _check_ssh_logs_for_common_errors(ssh_sub, op_info, delete_cert, delete_keys):
    log_list = []
    connection_established = False
    t0 = time.time()
    service_config_delay_error = False
    next_line = ssh_sub.stderr.readline()
    while next_line:
        log_list.append(next_line)
        if not next_line.startswith("debug1:") and \
           not next_line.startswith("debug2:") and \
           not next_line.startswith("debug3:") and \
           not next_line.startswith("Authenticated "):
            sys.stderr.write(next_line)
            _check_for_known_errors(next_line, delete_cert, log_list)
            if not service_config_delay_error:
                service_config_delay_error = check_for_service_config_delay_error(next_line)

        if "debug1: Entering interactive session." in next_line:
            connection_established = True
            do_cleanup(delete_keys, delete_cert, op_info.delete_credentials,
                       op_info.cert_file, op_info.private_key_file, op_info.public_key_file)

        if not connection_established and \
                time.time() - t0 > const.CLEANUP_TOTAL_TIME_LIMIT_IN_SECONDS:
            do_cleanup(delete_keys, delete_cert, op_info.delete_credentials,
                       op_info.cert_file, op_info.private_key_file, op_info.public_key_file)

        next_line = ssh_sub.stderr.readline()

    ssh_sub.wait()
    return service_config_delay_error


def _wait_to_delete_credentials(ssh_sub, op_info, delete_cert, delete_keys):
    # wait for 2 minutes. If the process isn't closed until then, delete credentials.
    if delete_cert or op_info.delete_credentials:
        t0 = time.time()
        while (time.time() - t0) < const.CLEANUP_TOTAL_TIME_LIMIT_IN_SECONDS:
            if ssh_sub.poll() is not None:
                break
            time.sleep(1)

        do_cleanup(delete_keys, delete_cert, op_info.delete_credentials,
                   op_info.cert_file, op_info.private_key_file, op_info.public_key_file)

    ssh_sub.wait()


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


def get_certificate_start_and_end_times(cert_file, ssh_client_folder=None):
    validity_str = _get_ssh_cert_validity(cert_file, ssh_client_folder)
    times = None
    if validity_str and "Valid: from " in validity_str and " to " in validity_str:
        times = validity_str.replace("Valid: from ", "").split(" to ")
        t0 = datetime.datetime.strptime(times[0], '%Y-%m-%dT%X')
        t1 = datetime.datetime.strptime(times[1], '%Y-%m-%dT%X')
        times = (t0, t1)
    return times


def get_certificate_lifetime(cert_file, ssh_client_folder=None):
    times = get_certificate_start_and_end_times(cert_file, ssh_client_folder)
    lifetime = None
    if times:
        lifetime = times[1] - times[0]
    return lifetime


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


def _check_for_known_errors(error_message, delete_cert, log_lines):
    # This connection fails when using our generated certificates.
    # Only throw error if conection fails with AAD login.
    if "Permission denied (publickey)." in error_message and delete_cert:
        # pylint: disable=bare-except
        # pylint: disable=too-many-boolean-expressions
        # Check if OpenSSH client and server versions are incompatible
        try:
            regex = 'OpenSSH.*_([0-9]+)\\.([0-9]+)'
            local_major, local_minor = re.findall(regex, log_lines[0])[0]
            remote_version_line = file_utils.get_line_that_contains("remote software version", log_lines)
            remote_major, remote_minor = re.findall(regex, remote_version_line)[0]
            local_major = int(local_major)
            local_minor = int(local_minor)
            remote_major = int(remote_major)
            remote_minor = int(remote_minor)
        except:
            return

        if (remote_major < 7 or (remote_major == 7 and remote_minor < 8)) and \
           (local_major > 8 or (local_major == 8 and local_minor >= 8)):
            logger.warning("The OpenSSH server version in the target VM %d.%d is too old. "
                           "Version incompatible with OpenSSH client version %d.%d. "
                           "Refer to https://bugzilla.mindrot.org/show_bug.cgi?id=3351 for more information.",
                           remote_major, remote_minor, local_major, local_minor)

        elif (local_major < 7 or (local_major == 7 and local_minor < 8)) and \
             (remote_major > 8 or (remote_major == 8 and remote_minor >= 8)):
            logger.warning("The OpenSSH client version %d.%d is too old. "
                           "Version incompatible with OpenSSH server version %d.%d in the target VM. "
                           "Refer to https://bugzilla.mindrot.org/show_bug.cgi?id=3351 for more information.",
                           local_major, local_minor, remote_major, remote_minor)

    regex = ("{\"level\":\"fatal\",\"msg\":\"sshproxy: error copying information from the connection: "
             ".*\",\"time\":\".*\"}.*")
    if re.search(regex, error_message):
        logger.error("Please make sure SSH port is allowed using \"azcmagent config list\" in the target "
                     "Arc Server. Ensure SSHD is running on the target machine.\n")


def check_for_service_config_delay_error(error_message):
    service_config_delay_error = False
    regex = "{\"level\":\"fatal\",\"msg\":\"sshproxy: error connecting to the address: 404 Endpoint does not exist.*"
    if re.search(regex, error_message):
        service_config_delay_error = True
    return service_config_delay_error


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


def do_cleanup(delete_keys, delete_cert, delete_credentials, cert_file, private_key, public_key):
    if (delete_keys or delete_credentials) and private_key:
        file_utils.delete_file(private_key, f"Couldn't delete private key {private_key}. ", True)
    if delete_keys and public_key:
        file_utils.delete_file(public_key, f"Couldn't delete public key {public_key}. ", True)
    if (delete_cert or delete_credentials) and cert_file:
        file_utils.delete_file(cert_file, f"Couldn't delete certificate {cert_file}. ", True)
    if delete_keys and cert_file:
        # This is only true if keys were generated, so they must be in a temp folder.
        temp_dir = os.path.dirname(cert_file)
        file_utils.delete_folder(temp_dir, f"Couldn't delete temporary folder {temp_dir}", True)


def _issue_config_cleanup_warning(delete_cert, delete_keys, is_arc, cert_file, relay_info_path, ssh_client_folder):
    if delete_cert:
        # pylint: disable=broad-except
        try:
            expiration = get_certificate_start_and_end_times(cert_file, ssh_client_folder)[1]
            expiration = expiration.strftime("%Y-%m-%d %I:%M:%S %p")
            print_styled_text((Style.SUCCESS,
                               f"Generated SSH certificate {cert_file} is valid until {expiration} in local time."))
        except Exception as e:
            logger.warning("Couldn't determine certificate expiration. Error: %s", str(e))

    if delete_keys or delete_cert or is_arc:
        # Warn users to delete credentials once config file is no longer being used.
        # If user provided keys, only ask them to delete the certificate.
        if is_arc:
            relay_info_filename = os.path.basename(relay_info_path)
            if delete_keys and delete_cert:
                path_to_delete = f"{os.path.dirname(cert_file)} contains"
                items_to_delete = f" (id_rsa, id_rsa.pub, id_rsa.pub-aadcert.pub, {relay_info_filename})"
            elif delete_cert:
                path_to_delete = f"{cert_file} and {relay_info_path} contain"
                items_to_delete = ""
            else:
                path_to_delete = f"{relay_info_path} contains"
                items_to_delete = ""
        else:
            path_to_delete = f"{os.path.dirname(cert_file)} contains"
            items_to_delete = " (id_rsa, id_rsa.pub, id_rsa.pub-aadcert.pub)"
            if not delete_keys:
                path_to_delete = f"{cert_file} contains"
                items_to_delete = ""

        logger.warning("%s sensitive information%s. Please delete it once you no longer "
                       "need this config file.", path_to_delete, items_to_delete)
