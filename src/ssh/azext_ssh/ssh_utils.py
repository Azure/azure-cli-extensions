# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import os
import platform
import subprocess
import multiprocessing as mp
import time
import datetime
import re
import colorama

from colorama import Fore
from colorama import Style

from knack import log
from azure.cli.core import azclierror
from azure.cli.core import telemetry

from . import file_utils
from . import connectivity_utils
from . import constants as const

logger = log.get_logger(__name__)


def start_ssh_connection(op_info, delete_keys, delete_cert):
    try:
        # Initialize these so that if something fails in the try block before these
        # are initialized, then the finally block won't fail.
        cleanup_process = None
        log_file = None
        connection_status = None

        ssh_arg_list = []
        if op_info.ssh_args:
            ssh_arg_list = op_info.ssh_args

        env = os.environ.copy()
        if op_info.is_arc():
            env['SSHPROXY_RELAY_INFO'] = connectivity_utils.format_relay_info_string(op_info.relay_info)

        # Get ssh client before starting the clean up process in case there is an error in getting client.
        command = [_get_ssh_client_path('ssh', op_info.ssh_client_folder), op_info.get_host()]

        if not op_info.cert_file and not op_info.private_key_file:
            # In this case, even if delete_credentials is true, there is nothing to clean-up.
            op_info.delete_credentials = False

        log_file, ssh_arg_list, cleanup_process = _start_cleanup(op_info.cert_file, op_info.private_key_file,
                                                                 op_info.public_key_file, op_info.delete_credentials,
                                                                 delete_keys, delete_cert, ssh_arg_list)
        command = command + op_info.build_args() + ssh_arg_list

        connection_duration = time.time()
        logger.debug("Running ssh command %s", ' '.join(command))

        # pylint: disable=subprocess-run-check
        try:
            if set(['-v', '-vv', '-vvv']).isdisjoint(ssh_arg_list) or log_file:
                connection_status = subprocess.run(command, shell=platform.system() == 'Windows', env=env,
                                                   stderr=subprocess.PIPE, encoding='utf-8')
            else:
                # Logs are sent to stderr. In that case, we shouldn't capture stderr.
                connection_status = subprocess.run(command, shell=platform.system() == 'Windows', env=env)
        except OSError as e:
            colorama.init()
            raise azclierror.BadRequestError(f"Failed to run ssh command with error: {str(e)}.",
                                             const.RECOMMENDATION_SSH_CLIENT_NOT_FOUND)

        connection_duration = (time.time() - connection_duration) / 60
        ssh_connection_data = {'Context.Default.AzureCLI.SSHConnectionDurationInMinutes': connection_duration}
        if connection_status and connection_status.returncode == 0:
            ssh_connection_data['Context.Default.AzureCLI.SSHConnectionStatus'] = "Success"
        telemetry.add_extension_event('ssh', ssh_connection_data)

    finally:
        # Even if something fails between the creation of the credentials and the end of the ssh connection, we
        # want to make sure that all credentials are cleaned up, and that the clean up process is terminated.
        _terminate_cleanup(delete_keys, delete_cert, op_info.delete_credentials, cleanup_process, op_info.cert_file,
                           op_info.private_key_file, op_info.public_key_file, log_file, connection_status)


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


def create_ssh_keyfile(private_key_file, ssh_client_folder=None):
    sshkeygen_path = _get_ssh_client_path("ssh-keygen", ssh_client_folder)
    command = [sshkeygen_path, "-f", private_key_file, "-t", "rsa", "-q", "-N", ""]
    logger.debug("Running ssh-keygen command %s", ' '.join(command))
    try:
        subprocess.call(command)
    except OSError as e:
        colorama.init()
        raise azclierror.BadRequestError(f"Failed to create ssh key file with error: {str(e)}.",
                                         const.RECOMMENDATION_SSH_CLIENT_NOT_FOUND)


def get_ssh_cert_info(cert_file, ssh_client_folder=None):
    sshkeygen_path = _get_ssh_client_path("ssh-keygen", ssh_client_folder)
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


def _print_error_messages_from_ssh_log(log_file, connection_status, delete_cert):
    with open(log_file, 'r', encoding='utf-8') as ssh_log:
        log_text = ssh_log.read()
        log_lines = log_text.splitlines()
        if ("debug1: Authentication succeeded" not in log_text and
            not re.search("^Authenticated to .*\n", log_text, re.MULTILINE)) \
           or (connection_status and connection_status.returncode):
            for line in log_lines:
                if "debug1:" not in line:
                    print(line)

            # This connection fails when using our generated certificates.
            # Only throw error if conection fails with AAD login.
            if "Permission denied (publickey)." in log_text and delete_cert:
                # pylint: disable=bare-except
                # pylint: disable=too-many-boolean-expressions
                # Check if OpenSSH client and server versions are incompatible
                try:
                    regex = 'OpenSSH.*_([0-9]+)\\.([0-9]+)'
                    local_major, local_minor = re.findall(regex, log_lines[0])[0]
                    remote_major, remote_minor = re.findall(regex,
                                                            file_utils.get_line_that_contains("remote software version",
                                                                                              log_lines))[0]
                    local_major = int(local_major)
                    local_minor = int(local_minor)
                    remote_major = int(remote_major)
                    remote_minor = int(remote_minor)
                except:
                    ssh_log.close()
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
        ssh_log.close()


def _get_ssh_client_path(ssh_command="ssh", ssh_client_folder=None):
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
                Fore.YELLOW + "Make sure OpenSSH is installed correctly: "
                "https://docs.microsoft.com/en-us/windows-server/administration/openssh/openssh_install_firstuse . "
                "Or use --ssh-client-folder to provide folder path with ssh executables. " + Style.RESET_ALL)

    return ssh_path


def do_cleanup(delete_keys, delete_cert, cert_file, private_key, public_key, log_file=None, wait=False):
    if log_file:
        t0 = time.time()
        match = False
        while (time.time() - t0) < const.CLEANUP_TOTAL_TIME_LIMIT_IN_SECONDS and not match:
            time.sleep(const.CLEANUP_TIME_INTERVAL_IN_SECONDS)
            # pylint: disable=bare-except
            # pylint: disable=anomalous-backslash-in-string
            try:
                with open(log_file, 'r', encoding='utf-8') as ssh_client_log:
                    log_text = ssh_client_log.read()
                    # The "debug1:..." message doesn't seems to exist in OpenSSH 3.9
                    match = ("debug1: Authentication succeeded" in log_text or
                             re.search("^Authenticated to .*\n", log_text, re.MULTILINE))
                    ssh_client_log.close()
            except:
                # If there is an exception, wait for a little bit and try again
                time.sleep(const.CLEANUP_TIME_INTERVAL_IN_SECONDS)

    elif wait:
        # if we are not checking the logs, but still want to wait for connection before deleting files
        time.sleep(const.CLEANUP_TOTAL_TIME_LIMIT_IN_SECONDS)

    if delete_keys and private_key:
        file_utils.delete_file(private_key, f"Couldn't delete private key {private_key}. ", True)
    if delete_keys and public_key:
        file_utils.delete_file(public_key, f"Couldn't delete public key {public_key}. ", True)
    if delete_cert and cert_file:
        file_utils.delete_file(cert_file, f"Couldn't delete certificate {cert_file}. ", True)


def _start_cleanup(cert_file, private_key_file, public_key_file, delete_credentials, delete_keys,
                   delete_cert, ssh_arg_list):
    log_file = None
    cleanup_process = None
    if delete_keys or delete_cert or delete_credentials:
        if '-E' not in ssh_arg_list and set(['-v', '-vv', '-vvv']).isdisjoint(ssh_arg_list):
            # If the user either provides his own client log file (-E) or
            # wants the client log messages to be printed to the console (-vvv/-vv/-v),
            # we should not use the log files to check for connection success.
            if cert_file:
                log_dir = os.path.dirname(cert_file)
            elif private_key_file:
                log_dir = os.path.dirname(private_key_file)
            log_file_name = 'ssh_client_log_' + str(os.getpid())
            log_file = os.path.join(log_dir, log_file_name)
            ssh_arg_list = ['-E', log_file, '-v'] + ssh_arg_list
        # Create a new process that will wait until the connection is established and then delete keys.
        cleanup_process = mp.Process(target=do_cleanup, args=(delete_keys or delete_credentials,
                                                              delete_cert or delete_credentials,
                                                              cert_file, private_key_file, public_key_file,
                                                              log_file, True))
        cleanup_process.start()

    return log_file, ssh_arg_list, cleanup_process


def _terminate_cleanup(delete_keys, delete_cert, delete_credentials, cleanup_process, cert_file,
                       private_key_file, public_key_file, log_file, connection_status):
    try:
        if connection_status and connection_status.stderr:
            if connection_status.returncode != 0:
                # Check if stderr is a proxy error
                regex = ("{\"level\":\"fatal\",\"msg\":\"sshproxy: error copying information from the connection: "
                         ".*\",\"time\":\".*\"}.*")
                if re.search(regex, connection_status.stderr):
                    logger.error("Please make sure SSH port is allowed using \"azcmagent config list\" in the target "
                                 "Arc Server. Ensure SSHD is running on the target machine.")
            print(connection_status.stderr)
    finally:
        if delete_keys or delete_cert or delete_credentials:
            if cleanup_process and cleanup_process.is_alive():
                cleanup_process.terminate()
                # wait for process to terminate
                t0 = time.time()
                while cleanup_process.is_alive() and (time.time() - t0) < const.CLEANUP_AWAIT_TERMINATION_IN_SECONDS:
                    time.sleep(1)

            if log_file and os.path.isfile(log_file):
                _print_error_messages_from_ssh_log(log_file, connection_status, delete_cert)

            # Make sure all files have been properly removed.
            do_cleanup(delete_keys or delete_credentials, delete_cert or delete_credentials,
                       cert_file, private_key_file, public_key_file)
            if log_file:
                file_utils.delete_file(log_file, f"Couldn't delete temporary log file {log_file}. ", True)
            if delete_keys:
                # This is only true if keys were generated, so they must be in a temp folder.
                temp_dir = os.path.dirname(cert_file)
                file_utils.delete_folder(temp_dir, f"Couldn't delete temporary folder {temp_dir}", True)


def _issue_config_cleanup_warning(delete_cert, delete_keys, is_arc, cert_file, relay_info_path, ssh_client_folder):
    if delete_cert:
        colorama.init()
        # pylint: disable=broad-except
        try:
            expiration = get_certificate_start_and_end_times(cert_file, ssh_client_folder)[1]
            expiration = expiration.strftime("%Y-%m-%d %I:%M:%S %p")
            print(Fore.GREEN + f"Generated SSH certificate {cert_file} is valid until {expiration} in local time."
                  + Style.RESET_ALL)
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
