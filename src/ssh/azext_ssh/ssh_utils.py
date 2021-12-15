# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import os
import platform
import subprocess
import stat
import multiprocessing as mp
import time
import datetime
import oschmod

from knack import log
from azure.cli.core import azclierror
from azure.cli.core import telemetry

from . import file_utils
from . import arc_utils
from . import constants as const

logger = log.get_logger(__name__)


def start_ssh_connection(relay_info, proxy_path, vm_name, ip, username, cert_file, private_key_file, port,
                         is_arc, delete_keys, delete_cert, public_key_file, ssh_client_path, ssh_args,
                         delete_credentials):

    if not ssh_client_path:
        ssh_client_path = _get_ssh_path()

    ssh_arg_list = []
    if ssh_args:
        ssh_arg_list = ssh_args

    env = os.environ.copy()

    if is_arc:
        env['SSHPROXY_RELAY_INFO'] = arc_utils.arc_format_relay_info_string(relay_info)
        if port:
            pcommand = f"ProxyCommand={proxy_path} -p {port}"
        else:
            pcommand = f"ProxyCommand={proxy_path}"
        args = ["-o", pcommand] + _build_args(cert_file, private_key_file, None)
        host = _get_host(username, vm_name)
    else:
        host = _get_host(username, ip)
        args = _build_args(cert_file, private_key_file, port)

    if not cert_file and not private_key_file:
        # In this case, even if delete_credentials is true, there is nothing to clean-up.
        delete_credentials = False

    log_file, ssh_arg_list, cleanup_process = _start_cleanup(cert_file, private_key_file,
                                                             public_key_file, delete_credentials,
                                                             delete_keys, delete_cert, ssh_arg_list)

    command = [ssh_client_path, host]
    command = command + args + ssh_arg_list

    connection_duration = time.time()

    logger.debug("Running ssh command %s", ' '.join(command))
    subprocess.call(command, shell=platform.system() == 'Windows', env=env)

    connection_duration = (time.time() - connection_duration) / 60

    ssh_connection_data = {'Context.Default.AzureCLI.SSHConnectionDurationInMinutes': connection_duration}
    if log_file and _get_connection_status(log_file):
        ssh_connection_data['Context.Default.AzureCLI.SSHConnectionStatus'] = "Success"
    telemetry.add_extension_event('ssh', ssh_connection_data)

    _terminate_cleanup(delete_keys, delete_cert, delete_credentials, cleanup_process, cert_file,
                       private_key_file, public_key_file, log_file)


def create_ssh_keyfile(private_key_file):
    command = [_get_ssh_path("ssh-keygen"), "-f", private_key_file, "-t", "rsa", "-q", "-N", ""]
    logger.debug("Running ssh-keygen command %s", ' '.join(command))
    subprocess.call(command, shell=platform.system() == 'Windows')


def get_ssh_cert_info(cert_file):
    command = [_get_ssh_path("ssh-keygen"), "-L", "-f", cert_file]
    logger.debug("Running ssh-keygen command %s", ' '.join(command))
    return subprocess.check_output(command, shell=platform.system() == 'Windows').decode().splitlines()


def _get_ssh_cert_validity(cert_file):
    if cert_file:
        info = get_ssh_cert_info(cert_file)
        for line in info:
            if "Valid:" in line:
                return line.strip()
    return None


def _get_certificate_start_and_end_times(cert_file):
    validity_str = _get_ssh_cert_validity(cert_file)
    times = None
    if validity_str and "Valid: from " in validity_str and " to " in validity_str:
        times = validity_str.replace("Valid: from ", "").split(" to ")
        t0 = datetime.datetime.fromisoformat(times[0])
        t1 = datetime.datetime.fromisoformat(times[1])
        times = (t0, t1)
    return times


def get_certificate_lifetime(cert_file):
    times = _get_certificate_start_and_end_times(cert_file)
    lifetime = None
    if times:
        lifetime = times[1] - times[0]
    return lifetime


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
                     cert_file, private_key_file, port, is_arc, delete_keys, delete_cert, _,
                     config_path, overwrite, resource_group, credentials_folder):

    common_lines = []
    common_lines.append("\tUser " + username)
    if cert_file:
        common_lines.append("\tCertificateFile \"" + cert_file + "\"")
    if private_key_file:
        common_lines.append("\tIdentityFile \"" + private_key_file + "\"")

    lines = [""]
    relay_info_path = None
    relay_info_filename = None
    if is_arc:
        relay_info_path, relay_info_filename = _prepare_relay_info_file(relay_info, credentials_folder,
                                                                        vm_name, resource_group)

        lines.append("Host " + resource_group + "-" + vm_name)
        lines.append("\tHostName " + vm_name)
        lines = lines + common_lines
        if port:
            lines.append("\tProxyCommand \"" + proxy_path + "\" " + "-r \"" + relay_info_path + "\" " + "-p " + port)
        else:
            lines.append("\tProxyCommand \"" + proxy_path + "\" " + "-r \"" + relay_info_path + "\"")
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

    _issue_config_cleanup_warning(delete_cert, delete_keys, is_arc, cert_file, relay_info_filename, relay_info_path)


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


def _do_cleanup(delete_keys, delete_cert, cert_file, private_key, public_key, log_file=None, wait=False):
    if log_file:
        t0 = time.time()
        match = False
        while (time.time() - t0) < const.CLEANUP_TOTAL_TIME_LIMIT_IN_SECONDS and not match:
            time.sleep(const.CLEANUP_TIME_INTERVAL_IN_SECONDS)
            try:
                with open(log_file, 'r') as ssh_client_log:
                    match = "debug1: Authentication succeeded" in ssh_client_log.read()
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
        cleanup_process = mp.Process(target=_do_cleanup, args=(delete_keys or delete_credentials,
                                                               delete_cert or delete_credentials,
                                                               cert_file, private_key_file, public_key_file,
                                                               log_file, True))
        cleanup_process.start()

    return log_file, ssh_arg_list, cleanup_process


def _terminate_cleanup(delete_keys, delete_cert, delete_credentials, cleanup_process, cert_file,
                       private_key_file, public_key_file, log_file):
    if delete_keys or delete_cert or delete_credentials:
        if cleanup_process.is_alive():
            cleanup_process.terminate()
            # wait for process to terminate
            t0 = time.time()
            while cleanup_process.is_alive() and (time.time() - t0) < const.CLEANUP_AWAIT_TERMINATION_IN_SECONDS:
                time.sleep(1)

        # Make sure all files have been properly removed.
        _do_cleanup(delete_keys or delete_credentials, delete_cert or delete_credentials,
                    cert_file, private_key_file, public_key_file)
        if log_file:
            file_utils.delete_file(log_file, f"Couldn't delete temporary log file {log_file}. ", True)
        if delete_keys:
            # This is only true if keys were generated, so they must be in a temp folder.
            temp_dir = os.path.dirname(cert_file)
            file_utils.delete_folder(temp_dir, f"Couldn't delete temporary folder {temp_dir}", True)


def _prepare_relay_info_file(relay_info, credentials_folder, vm_name, resource_group):
    # create the custom folder
    relay_info_dir = credentials_folder
    if not os.path.isdir(relay_info_dir):
        os.makedirs(relay_info_dir)

    if vm_name and resource_group:
        relay_info_filename = resource_group + "-" + vm_name + "-relay_info"

    relay_info_path = os.path.join(relay_info_dir, relay_info_filename)
    # Overwrite relay_info if it already exists in that folder.
    file_utils.delete_file(relay_info_path, f"{relay_info_path} already exists, and couldn't be overwritten.")
    file_utils.write_to_file(relay_info_path, 'w', arc_utils.arc_format_relay_info_string(relay_info),
                             f"Couldn't write relay information to file {relay_info_path}.", 'utf-8')
    oschmod.set_mode(relay_info_path, stat.S_IRUSR)

    # Print the expiration of the relay information f
    expiration = datetime.datetime.fromtimestamp(relay_info.expires_on)
    print(f"Generated file with Relay Information {relay_info_path} is valid until {expiration}.\n")

    return relay_info_path, relay_info_filename


def _issue_config_cleanup_warning(delete_cert, delete_keys, is_arc, cert_file, relay_info_filename, relay_info_path):
    if delete_cert:
        print(f"Generated SSH certificate {cert_file} is valid until",
              f"{_get_certificate_start_and_end_times(cert_file)[1]}.\n")

    if delete_keys or delete_cert or is_arc:
        # Warn users to delete credentials once config file is no longer being used.
        # If user provided keys, only ask them to delete the certificate.
        if is_arc:
            if delete_keys and delete_cert:
                path_to_delete = os.path.dirname(cert_file)
                items_to_delete = f" (id_rsa, id_rsa.pub, id_rsa.pub-aadcert.pub, {relay_info_filename})"
            elif delete_cert:
                path_to_delete = os.path.dirname(cert_file)
                relay_partial_path = relay_info_path.replace(path_to_delete, "")
                items_to_delete = f" (id_rsa.pub-aadcert.pub, {relay_partial_path})"
            else:
                path_to_delete = relay_info_path
                items_to_delete = ""
        else:
            path_to_delete = os.path.dirname(cert_file)
            items_to_delete = " (id_rsa, id_rsa.pub, id_rsa.pub-aadcert.pub)"
            if not delete_keys:
                path_to_delete = cert_file
                items_to_delete = ""

        print(f"{path_to_delete} contains sensitive information{items_to_delete}. "
              "Please delete it once you no longer need this config file.\n")


def _get_connection_status(log_file):
    try:
        with open(log_file, 'r') as ssh_client_log:
            match = "debug1: Authentication succeeded" in ssh_client_log.read()
            ssh_client_log.close()
    except:
        return False
    return match
