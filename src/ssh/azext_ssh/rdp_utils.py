import os
import platform
import subprocess
import multiprocessing as mp
import os
import psutil
import random

from knack import log

logger = log.get_logger(__name__)

from azure.cli.core import azclierror
from . import ssh_utils
from . import connectivity_utils

def start_rdp_connection(ssh_info, delete_keys, delete_cert):
    resource_port = 3389
    local_port = _get_open_port()

    while not is_local_port_open(local_port):
        local_port = _get_open_port()

    if ssh_info.ssh_args == None:
        ssh_info.ssh_args = ['-L', f"{local_port}:localhost:{resource_port}", "-N"]
    else:
        ssh_info.ssh_args = ['-L', f"{local_port}:localhost:{resource_port}", "-N"] + ssh_info.ssh_args

    rdp_conn, ssh_conn = mp.Pipe()
    rdp_process = mp.Process(target=call_rdp, args=(rdp_conn, local_port))
    rdp_process.start()

    start_ssh_tunnel(ssh_info, ssh_conn)
    
    if rdp_process.is_alive():
        # This is also temporary, because I need to figure out how to kill the process smoothly if needed
        try:
            kill_process(rdp_process.pid)
        except:
            return


def start_ssh_tunnel(op_info, ssh_conn):
    try:
        # About cleanup: For now, since it's windows only, we won't ever need to clear credentials.
        # Unless --force-delete-credentials is used, but let's ignore that for now.
        env = os.environ.copy()
        if op_info.is_arc():
            env['SSHPROXY_RELAY_INFO'] = connectivity_utils.format_relay_info_string(op_info.relay_info)

        # Check if -v/-vv/-vvv is part of the args, if it is print output, if it isn't, add
        print_ssh_logs = False
        if not set(['-v', '-vv', '-vvv']).isdisjoint(op_info.ssh_args):
            print_ssh_logs = True
        else:
            op_info.ssh_args = ['-v'] + op_info.ssh_args
        
        if '-E' in op_info.ssh_args:
            raise azclierror.BadRequestError("Can't use -E ssh parameter when using --winrdp")

        command = [ssh_utils._get_ssh_client_path('ssh', op_info.ssh_client_folder), op_info.get_host()]
        command = command + op_info.build_args() + op_info.ssh_args

        logger.debug(f"Startng SSH tunnel with command: {command}")
        ssh_sub = subprocess.Popen(command, shell=True, stderr=subprocess.PIPE, env=env, universal_newlines=True, encoding='utf-8')
    except Exception as e:
        ssh_conn.send("SSH_FAIL")
        raise e
    
    log_list = []
    while True:
        try:
            next_line = ssh_sub.stderr.readline()
            if print_ssh_logs:
                print(next_line)
            else:
                log_list.append(next_line)
            # Is this message coming from upstream? Check today.
            if "debug1: Entering interactive session." in next_line:
                ssh_conn.send("SSH_OK")
                break
        except:
            ssh_conn.send("SSH_FAIL")

        if ssh_sub.poll() is not None:
            ssh_conn.send("SSH_FAIL")
            return
    
    while True:
        msg = ssh_conn.recv()
        if msg == "RDP_CLOSE":
            kill_process(ssh_sub.pid) 
            break
        
    # printing errors 
    while next_line:
        next_line = ssh_sub.stderr.readline()
        if print_ssh_logs:
            print(next_line)
        else:
            log_list.append(next_line)


def call_rdp(rdp_conn, local_port):
    from azure.cli.command_modules.network._process_helper import launch_and_wait
    while True:
        msg = rdp_conn.recv()
        if msg == "SSH_OK":
            break
        elif msg == "SSH_FAIL":
            return

    if platform.system() == 'Windows':
        command = [_get_rdp_path(), f"/v:localhost:{local_port}"]
        launch_and_wait(command)
        rdp_conn.send("RDP_CLOSE")


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
    process = psutil.Process(pid)
    for proc in process.children(recursive=True):
        proc.kill()
    process.kill()


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
