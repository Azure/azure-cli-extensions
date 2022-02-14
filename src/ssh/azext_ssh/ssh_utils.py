# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import os
import platform
import subprocess
import time
import multiprocessing as mp
import datetime
from azext_ssh import file_utils
import logging

from knack import log
from azure.cli.core import azclierror

logger = log.get_logger(__name__)

CLEANUP_TOTAL_TIME_LIMIT_IN_SECONDS = 120
CLEANUP_TIME_INTERVAL_IN_SECONDS = 10
CLEANUP_AWAIT_TERMINATION_IN_SECONDS = 30


def start_ssh_connection(ssh_info, delete_keys, delete_cert):

    ssh_arg_list = []
    if ssh_info.ssh_args:
        ssh_arg_list = ssh_info.ssh_args

    log_file = None
    if delete_keys or delete_cert:
        if '-E' not in ssh_arg_list and set(['-v', '-vv', '-vvv']).isdisjoint(ssh_arg_list):
            # If the user either provides his own client log file (-E) or
            # wants the client log messages to be printed to the console (-vvv/-vv/-v),
            # we should not use the log files to check for connection success.
            log_file_dir = os.path.dirname(ssh_info.cert_file)
            log_file_name = 'ssh_client_log_' + str(os.getpid())
            log_file = os.path.join(log_file_dir, log_file_name)
            ssh_arg_list = ['-E', log_file, '-v'] + ssh_arg_list
        # Create a new process that will wait until the connection is established and then delete keys.
        cleanup_process = mp.Process(target=_do_cleanup, args=(delete_keys, delete_cert, ssh_info.cert_file, ssh_info.private_key_file,
                                     ssh_info.public_key_file, log_file, True))
        cleanup_process.start()

    command = [_get_ssh_client_path(ssh_client_folder=ssh_info.ssh_client_folder), ssh_info.get_host()]
    command = command + ssh_info.build_args() + ssh_arg_list

    logger.debug("Running ssh command %s", ' '.join(command))
    connection_status = subprocess.call(command, shell=platform.system() == 'Windows')

    if log_file:
        _print_error_messages_from_ssh_log(log_file, connection_status)

    if delete_keys or delete_cert:
        if cleanup_process.is_alive():
            cleanup_process.terminate()
            # wait for process to terminate
            t0 = time.time()
            while cleanup_process.is_alive() and (time.time() - t0) < CLEANUP_AWAIT_TERMINATION_IN_SECONDS:
                time.sleep(1)

        # Make sure all files have been properly removed.
        _do_cleanup(delete_keys, delete_cert, ssh_info.cert_file, ssh_info.private_key_file, ssh_info.public_key_file)
        if log_file:
            file_utils.delete_file(log_file, f"Couldn't delete temporary log file {log_file}. ", True)
        if delete_keys:
            temp_dir = os.path.dirname(ssh_info.cert_file)
            file_utils.delete_folder(temp_dir, f"Couldn't delete temporary folder {temp_dir}", True)


def write_ssh_config(config_info, delete_keys, delete_cert):

    if delete_keys or delete_cert:
        # Warn users to delete credentials once config file is no longer being used.
        # If user provided keys, only ask them to delete the certificate.
        path_to_delete = os.path.dirname(config_info.cert_file)
        items_to_delete = " (id_rsa, id_rsa.pub, id_rsa.pub-aadcert.pub)"
        if not delete_keys:
            path_to_delete = config_info.cert_file
            items_to_delete = ""

        expiration = None
        try:
            expiration = get_certificate_start_and_end_times(config_info.cert_file, config_info.ssh_client_folder)[1]
            expiration = expiration.strftime("%Y-%m-%d %I:%M:%S %p")
        except Exception as e:
            logger.warning("Couldn't determine certificate expiration. Error: %s", str(e))

        if expiration:
            logger.warning(f"The generated certificate {config_info.cert_file} is valid until {expiration} in local time.")
        logger.warning(f"{path_to_delete} contains sensitive information{items_to_delete}. "
                       "Please delete it once you no longer this config file.")

    config_text = config_info.get_config_text()

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
    subprocess.call(command, shell=platform.system() == 'Windows')


def get_ssh_cert_info(cert_file, ssh_client_folder=None):
    sshkeygen_path = _get_ssh_client_path("ssh-keygen", ssh_client_folder)
    command = [sshkeygen_path, "-L", "-f", cert_file]
    logger.debug("Running ssh-keygen command %s", ' '.join(command))
    return subprocess.check_output(command, shell=platform.system() == 'Windows').decode().splitlines()


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


def _print_error_messages_from_ssh_log(log_file, connection_status):
    with open(log_file, 'r') as log:
        if "debug1: Authentication succeeded" not in log.read() or connection_status != 0: 
            for line in log.readlines():
                if "debug1:" not in line:
                    print(line)
        log.close()


def _get_ssh_client_path(ssh_command="ssh", ssh_client_folder=None):
    if ssh_client_folder:
        ssh_path = os.path.join(ssh_client_folder, ssh_command)
        if platform.system() == 'Windows':
            ssh_path = ssh_path + '.exe'
        if os.path.isfile(ssh_path):
            logger.debug("Attempting to run %s from path %s", ssh_command, ssh_path)
            return ssh_path

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
        logger.debug("Platform architecture: %s", str(platform.architecture()[0]))
        logger.debug("OS architecture: %s", os_architecture)
        logger.debug("System Root: %s", system_root)
        logger.debug("Attempting to run %s from path %s", ssh_command, ssh_path)

        if not os.path.isfile(ssh_path):
            raise azclierror.UnclassifiedUserFault(
                "Could not find " + ssh_command + ".exe on path " + ssh_path + ". ",
                "https://docs.microsoft.com/en-us/windows-server/administration/openssh/openssh_install_firstuse")

    return ssh_path


def _do_cleanup(delete_keys, delete_cert, cert_file, private_key, public_key, log_file=None, wait=False):
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

    if delete_keys and private_key:
        file_utils.delete_file(private_key, f"Couldn't delete private key {private_key}. ", True)
    if delete_keys and public_key:
        file_utils.delete_file(public_key, f"Couldn't delete public key {public_key}. ", True)
    if delete_cert and cert_file:
        file_utils.delete_file(cert_file, f"Couldn't delete certificate {cert_file}. ", True)
