import os
import platform
import subprocess
import multiprocessing as mp
import os
import psutil
import queue
import threading

import colorama
from colorama import Fore
from colorama import Style

from knack import log

logger = log.get_logger(__name__)

from azure.cli.core import azclierror
from . import ssh_utils
from . import connectivity_utils

def start_rdp_connection(ssh_info, delete_keys, delete_cert):
    try:
        resource_port = 3389
        local_port = _get_open_port()

        while not is_local_port_open(local_port):
            local_port = _get_open_port()

        if ssh_info.ssh_args == None:
            ssh_info.ssh_args = ['-L', f"{local_port}:localhost:{resource_port}", "-N"]
        else:
            ssh_info.ssh_args = ['-L', f"{local_port}:localhost:{resource_port}", "-N"] + ssh_info.ssh_args

        q = queue.Queue()
        rdp_thread = threading.Thread(target=call_rdp, args=(q, local_port))
        print("Start RDP Thread")
        rdp_thread.start()
        #rdp_conn, ssh_conn = mp.Pipe()
        #rdp_process = mp.Process(target=call_rdp, args=(rdp_conn, local_port))
        #rdp_process.start()

        ssh_process, print_ssh_logs = start_ssh_tunnel(ssh_info, q)
        ssh_sucess, log_list = wait_for_ssh_connection(ssh_process, print_ssh_logs, q)
        
        # whether the connection succeeds or fails, we will want to clean-up credentials either way
        ssh_utils.do_cleanup(delete_keys, delete_cert, ssh_info.cert_file, ssh_info.private_key_file, ssh_info.public_key_file)
        
        if ssh_sucess:
            wait_for_rdp_conclusion(q, ssh_process)
        
        print_error_messages_from_log(log_list, print_ssh_logs, ssh_process)
        
    finally:
        ssh_utils.do_cleanup(delete_keys, delete_cert, ssh_info.cert_file, ssh_info.private_key_file, ssh_info.public_key_file)
        #if rdp_process and rdp_process.is_alive():
        #    kill_process(rdp_process.pid)
        #if ssh_process and ssh_process.poll():
        #    kill_process(ssh_process.pid)


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


def start_ssh_tunnel(op_info, q):
    try:
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
        # It seems like "universal newlines and shell might not be necessary. Continue with further testing."
        ssh_sub = subprocess.Popen(command, shell=True, universal_newlines=True, stderr=subprocess.PIPE, env=env, encoding='utf-8')

        return ssh_sub, print_ssh_logs
    
    except Exception as e:
        q.put("SSH_FAIL")
        raise e


def wait_for_ssh_connection(ssh_sub, print_ssh_logs, q):
    log_list = []
    ssh_sucess = False
    while True:
        next_line = ssh_sub.stderr.readline()
        if print_ssh_logs:
            print(next_line)
        else:
            log_list.append(next_line)
        if "debug1: Entering interactive session." in next_line:
            q.put("SSH_OK")
            print(q)
            ssh_sucess = True
            break

        if ssh_sub.poll() is not None:
            q.put("SSH_FAIL")
            ssh_sucess = False
            break

    return ssh_sucess, log_list


def wait_for_rdp_conclusion(q, ssh_process):
    while True:
        msg = q.get()
        if msg == "RDP_CLOSE":
            #kill_process(ssh_process.pid)
            #without shell, .terminate() is enough
            ssh_process.terminate()
            break
        # check if ssh_process is still alive?
        # Is that eve necessary? If we ctrl+c, will it close the thread?
        

def print_error_messages_from_log(log_list, print_ssh_logs, ssh_process):
    # Finish reading logs
    next_line = ssh_process.stderr.readline()
    while next_line:
        if print_ssh_logs:
            print(next_line)
        else:
            log_list.append(next_line)
        next_line = ssh_process.stderr.readline()
    
    # Print error messages on log
    # If ssh_process is terminated, then the return code is not 0. See about that.
    if ssh_process.returncode != 0 and not print_ssh_logs:
        for line in log_list:
            if "debug1:" not in line:
                print(line)


def call_rdp(q, local_port):
    from azure.cli.command_modules.network._process_helper import launch_and_wait
    print("rdp waiting")
    # Wait for SSH connection
    while True:
        #msg = rdp_conn.recv()
        msg = q.get()
        if msg == "SSH_OK":
            break
        elif msg == "SSH_FAIL":
            return

    # Launch RDP process
    if platform.system() == 'Windows':
        colorama.init()
        print(Fore.GREEN + f"Launching Remote Desktop Connection" + Style.RESET_ALL)
        command = [_get_rdp_path(), f"/v:localhost:{local_port}"]
        launch_and_wait(command)
        #rdp_conn.send("RDP_CLOSE")
        q.put("RDP_CLOSE")


# Cut "get ssh path into get system32 folder and get ssh path?"
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

