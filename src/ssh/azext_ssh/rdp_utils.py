# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=used-before-assignment

import os
import platform
import subprocess
import time
import psutil

from knack import log
from azure.cli.core import azclierror
from azure.cli.core import telemetry
from azure.cli.core.style import Style, print_styled_text

from . import ssh_utils
from . import connectivity_utils
from . import constants as const
from . import file_utils

logger = log.get_logger(__name__)


def start_rdp_connection(ssh_info, delete_keys, delete_cert):
    try:
        ssh_process = None
        log_list = []
        print_ssh_logs = False
        ssh_success = False
        retry_attempt = 0
        retry_attempts_allowed = 0

        resource_port = 3389
        local_port = _get_open_port()

        while not is_local_port_open(local_port):
            local_port = _get_open_port()

        if ssh_info.ssh_args is None:
            ssh_info.ssh_args = ['-L', f"{local_port}:localhost:{resource_port}", "-N"]
        else:
            ssh_info.ssh_args = ['-L', f"{local_port}:localhost:{resource_port}", "-N"] + ssh_info.ssh_args

        while (retry_attempt <= retry_attempts_allowed and not ssh_success):
            service_config_delay_error = False
            if retry_attempt == 1:
                logger.warning("SSH connection failed, possibly caused by new service configuration setup. "
                               "Retrying the connection in %d seconds.", const.RETRY_DELAY_IN_SECONDS)
                time.sleep(const.RETRY_DELAY_IN_SECONDS)
            ssh_process, print_ssh_logs = start_ssh_tunnel(ssh_info)
            ssh_connection_t0 = time.time()
            ssh_success, log_list, service_config_delay_error = wait_for_ssh_connection(ssh_process, print_ssh_logs)
            if ssh_info.new_service_config and service_config_delay_error and ssh_process.poll() == 255:
                retry_attempts_allowed = 1
                if retry_attempt == 1:
                    logger.warning("SSH connection failure could still be due to Service Configuration update. "
                                   "Please re-run command.")
            retry_attempt += 1

        ssh_utils.do_cleanup(delete_keys, delete_cert, ssh_info.delete_credentials, ssh_info.cert_file,
                             ssh_info.private_key_file, ssh_info.public_key_file)
        if ssh_success and ssh_process.poll() is None:
            call_rdp(local_port)

    finally:
        if ssh_success:
            ssh_connection_data = {'Context.Default.AzureCLI.SSHConnectionDurationInMinutes':
                                   (time.time() - ssh_connection_t0) / 60}
            ssh_connection_data['Context.Default.AzureCLI.SSHConnectionStatus'] = "Success"
            telemetry.add_extension_event('ssh', ssh_connection_data)

        terminate_ssh(ssh_process, log_list, print_ssh_logs)
        ssh_utils.do_cleanup(delete_keys, delete_cert, ssh_info.delete_credentials, ssh_info.cert_file,
                             ssh_info.private_key_file, ssh_info.public_key_file)
        if delete_keys:
            # This is only true if keys were generated, so they must be in a temp folder.
            temp_dir = os.path.dirname(ssh_info.cert_file)
            file_utils.delete_folder(temp_dir, f"Couldn't delete temporary folder {temp_dir}", True)


def call_rdp(local_port):
    from . import _process_helper
    if platform.system() == 'Windows':
        print_styled_text((Style.SUCCESS, "Launching Remote Desktop Connection"))
        print_styled_text((Style.IMPORTANT, "To close this session, close the Remote Desktop Connection window."))
        command = [_get_rdp_path(), f"/v:localhost:{local_port}"]
        _process_helper.launch_and_wait(command)


def is_local_port_open(local_port):
    import socket
    from contextlib import closing
    is_port_open = False
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
        if sock.connect_ex(('', local_port)) == 0:
            logger.info('Port %s is NOT open', local_port)
        else:
            logger.info('Port %s is open', local_port)
            is_port_open = True
        return is_port_open


def _get_open_port():
    import socket
    from contextlib import closing
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
        s.bind(('', 0))
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        return s.getsockname()[1]


def start_ssh_tunnel(op_info):
    # pylint: disable=consider-using-with
    env = os.environ.copy()
    if op_info.is_arc():
        env['SSHPROXY_RELAY_INFO'] = connectivity_utils.format_relay_info_string(op_info.relay_info)

    print_ssh_logs = False
    if not set(['-v', '-vv', '-vvv']).isdisjoint(op_info.ssh_args):
        print_ssh_logs = True

    if '-E' in op_info.ssh_args:
        raise azclierror.BadRequestError("Can't use -E ssh parameter when using --rdp")

    command = [ssh_utils.get_ssh_client_path('ssh', op_info.ssh_client_folder), op_info.get_host(),
               "-l", op_info.local_user]
    if not print_ssh_logs:
        command = command + ['-v']
    command = command + op_info.build_args() + op_info.ssh_args

    logger.debug("Running ssh command %s", ' '.join(command))
    ssh_sub = subprocess.Popen(command, shell=True, stderr=subprocess.PIPE, env=env, encoding='utf-8')
    return ssh_sub, print_ssh_logs


def wait_for_ssh_connection(ssh_sub, print_ssh_logs):
    log_list = []
    ssh_success = False
    service_config_delay_error = False
    while True:
        next_line = ssh_sub.stderr.readline()
        if print_ssh_logs:
            print(next_line, end='')
        else:
            log_list.append(next_line)
        if "debug1: Entering interactive session." in next_line:
            logger.debug("SSH Connection established succesfully.")
            ssh_success = True
            break
        if ssh_sub.poll() is not None:
            logger.debug("SSH Connection failed.")
            ssh_success = False
            break
        if not service_config_delay_error:
            service_config_delay_error = ssh_utils.check_for_service_config_delay_error(next_line)
    return ssh_success, log_list, service_config_delay_error


def terminate_ssh(ssh_process, log_list, print_ssh_logs):
    if ssh_process:
        terminated = False
        if ssh_process.poll() is None:
            kill_process(ssh_process.pid)
            t0 = time.time()
            while ssh_process.poll() is None and (time.time() - t0) < const.RDP_TERMINATE_SSH_WAIT_TIME_IN_SECONDS:
                time.sleep(1)
            terminated = True
        print_error_messages_from_log(log_list, print_ssh_logs, ssh_process, terminated)


def print_error_messages_from_log(log_list, print_ssh_logs, ssh_process, terminated):
    # Read the remaining log messages since the connection was established.
    next_line = ssh_process.stderr.readline()
    while next_line:
        if print_ssh_logs:
            print(next_line, end='')
        else:
            log_list.append(next_line)
        next_line = ssh_process.stderr.readline()

    # If ssh process was not forced to terminate, print potential error messages.
    if ssh_process.returncode != 0 and not print_ssh_logs and not terminated:
        for line in log_list:
            if "debug1:" not in line and line != '':
                print(str(line), end='')


def _get_rdp_path(rdp_command="mstsc"):
    rdp_path = rdp_command
    if platform.system() == 'Windows':
        arch_data = platform.architecture()
        sys_path = 'System32'
        system_root = os.environ['SystemRoot']
        system32_path = os.path.join(system_root, sys_path)
        rdp_path = os.path.join(system32_path, (rdp_command + ".exe"))
        logger.debug("Platform architecture: %s", str(arch_data))
        logger.debug("System Root: %s", system_root)
        logger.debug("Attempting to run rdp from path %s", rdp_path)

        if not os.path.isfile(rdp_path):
            raise azclierror.BadRequestError("Could not find " + rdp_command + ".exe. Is the rdp client installed?")
    else:
        raise azclierror.BadRequestError("Platform is not supported for this command. Supported platforms: Windows")

    return rdp_path


def kill_process(pid):
    try:
        process = psutil.Process(pid)
        for proc in process.children(recursive=True):
            proc.kill()
        process.kill()
    except psutil.NoSuchProcess as e:
        logger.warning("Kill process failed. Process no longer exists: %s", str(e))
