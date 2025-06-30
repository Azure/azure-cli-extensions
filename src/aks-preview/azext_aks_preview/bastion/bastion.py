import asyncio
import json
import os
import socket
import subprocess
import sys
import time
from urllib.parse import urlparse

import psutil
import yaml
from azure.cli.command_modules.acs._consts import DecoratorEarlyExitException
from azure.cli.core.azclierror import (
    CLIInternalError,
    InvalidArgumentValueError,
    ResourceNotFoundError,
)
from azure.mgmt.core.tools import (
    is_valid_resource_id,
    is_valid_resource_name,
    parse_resource_id,
)
from knack.log import get_logger
from knack.prompting import prompt_y_n

logger = get_logger(__name__)


def aks_bastion_get_bastion_name(bastion, nrg):
    """Get the bastion resource name from the provided name or node resource group."""

    # validate provided bastion
    if bastion:
        if is_valid_resource_id(bastion):
            return parse_resource_id(bastion)["name"]
        if is_valid_resource_name(bastion):
            return bastion
    logger.warning(
        "No valid bastion resource provided: '%s'. Attempting to locate one in the node resource group.",
        bastion if bastion else "None",
    )

    # find bastion from the node resource group
    result = subprocess.run(
        [
            "az",
            "network",
            "bastion",
            "list",
            "--resource-group",
            nrg,
            "--output",
            "json",
        ],
        capture_output=True,
        text=True,
    )
    bastions = json.loads(result.stdout)
    if len(bastions) == 0:
        raise ResourceNotFoundError("No bastion found in the node resource group.")
    if len(bastions) > 1:
        logger.warning(
            "Multiple bastions found in the node resource group. Using the first one."
        )
    bastion = bastions[0]["name"]
    logger.debug("Using bastion resource: %s", bastion)
    return bastion


def aks_bastion_get_local_port(port):
    """Get an available local port for the bastion tunnel."""

    # validate provided port
    if port:
        if not (1 <= port <= 65535):
            raise InvalidArgumentValueError(
                f"Invalid port number: {port}. Port must be between 1 and 65535."
            )
        # check if the port is already in use
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            try:
                s.bind(("", port))
            except OSError as e:
                raise InvalidArgumentValueError(f"Port {port} is already in use: {e}")
        return port

    # find an available port
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("", 0))  # bind to an available port
        port = s.getsockname()[1]
        logger.debug("Using local port: %s", port)
        return port


def aks_bastion_extension(yes):
    """Check if the Azure Bastion extension is installed, and prompt to install it if not."""

    logger.debug("Checking if the bastion extension is installed...")
    result = subprocess.run(
        ["az", "extension", "list", "--output", "json"],
        check=True,
        capture_output=True,
        text=True,
    )
    extensions = json.loads(result.stdout)
    for ext in extensions:
        if ext["name"] == "bastion":
            logger.debug("Bastion extension is already installed.")
            return True

    msg = "The Azure Bastion extension is not installed. Do you want to install it? [y/n]: "
    if not yes and not prompt_y_n(msg, default="n"):
        raise DecoratorEarlyExitException(
            "Bastion extension is required for this operation. "
            "Please install it using 'az extension add --name bastion'."
        )
    logger.debug("Installing bastion extension...")
    result = subprocess.run(
        ["az", "extension", "add", "--name", "bastion"],
        check=True,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise CLIInternalError(f"Failed to install bastion extension: {result.stderr}")


def aks_bastion_set_kubeconfig(kubeconfig_path, port):
    """Update the kubeconfig file to point to the local port."""

    logger.debug("Updating kubeconfig file: %s to use port: %s", kubeconfig_path, port)
    with open(kubeconfig_path, "r") as f:
        data = yaml.load(f, Loader=yaml.SafeLoader)
    current_context = data["current-context"]
    for cluster in data["clusters"]:
        if cluster["name"] == current_context:
            server = cluster["cluster"]["server"]
            hostname = urlparse(server).hostname
            # update the server URL to point to the local port
            cluster["cluster"]["server"] = f"https://localhost:{port}/"
            # set the tls-server-name to the hostname
            cluster["cluster"]["tls-server-name"] = hostname
            break
    with open(kubeconfig_path, "w") as f:
        yaml.dump(data, f)


async def aks_bastion_runner(nrg, bastion, port, mc_id, kubeconfig_path):
    """Run the bastion tunnel and subshell in parallel, cancelling the other if one completes."""

    task1 = asyncio.create_task(_aks_bastion_launch_tunnel(nrg, bastion, port, mc_id))
    await asyncio.sleep(5)  # give the tunnel some time to establish before launching the subshell
    task2 = asyncio.create_task(_aks_bastion_launch_subshell(kubeconfig_path, port))

    _, pending = await asyncio.wait([task1, task2], return_when=asyncio.FIRST_COMPLETED)

    for task in pending:
        task.cancel()

    # Wait for the cancellations to finish
    await asyncio.gather(*pending, return_exceptions=True)


def aks_batsion_clean_up():
    pass


def _aks_bastion_get_current_shell_cmd():
    """Get the current shell command being used by the parent process."""

    ppid = os.getppid()
    parent = psutil.Process(ppid)
    return parent.cmdline()[0]


def _aks_bastion_prepare_shell_cmd(kubeconfig_path):
    """Prepare the shell command to launch a subshell with KUBECONFIG set."""

    shell_cmd = _aks_bastion_get_current_shell_cmd()
    updated_shell_cmd = shell_cmd
    if shell_cmd.endswith("bash") and os.path.exists(os.path.expanduser("~/.bashrc")):
        updated_shell_cmd = (
            f"""{shell_cmd} -c '{shell_cmd} --rcfile <(cat ~/.bashrc; """
            f"""echo "export KUBECONFIG={kubeconfig_path}")'"""
        )
    return shell_cmd, updated_shell_cmd


def _aks_bastion_restore_shell(shell_cmd):
    """Restore the shell settings after the subshell exits."""

    if shell_cmd.endswith("bash"):
        subprocess.run(["stty", "sane"], stdin=sys.stdin)


async def _aks_bastion_launch_subshell(kubeconfig_path, port):
    """Launch a subshell with the KUBECONFIG environment variable set to the provided path."""

    if _aks_bastion_validate_tunnel(port):
        logger.debug("Bastion tunnel is set up successfully.")
    else:
        raise CLIInternalError(
            f"Bastion tunnel failed to set up on port {port}. Please check the logs for more details."
        )

    env = os.environ.copy()
    env.update({"KUBECONFIG": kubeconfig_path})
    shell_cmd, updated_shell_cmd = _aks_bastion_prepare_shell_cmd(kubeconfig_path)
    logger.info(
        "Launching subshell '%s' with KUBECONFIG set to '%s'",
        updated_shell_cmd,
        kubeconfig_path,
    )
    subshell_process = await asyncio.subprocess.create_subprocess_shell(
        cmd=updated_shell_cmd,
        env=env,
    )
    logger.info("Subshell launched with PID: %s", subshell_process.pid)

    try:
        await subshell_process.wait()
        logger.debug("Subshell exited with code: %s", subshell_process.returncode)
    except asyncio.CancelledError:
        logger.info("Subshell was cancelled. Terminating...")
        subshell_process.terminate()
        try:
            await asyncio.wait_for(subshell_process.wait(), timeout=5)
            logger.info("Subshell exited cleanly after termination.")
        except asyncio.TimeoutError:
            logger.warning("Subshell did not exit after SIGTERM. Sending SIGKILL...")
            subshell_process.kill()
            await subshell_process.wait()
            logger.warning(
                "Subshell forcefully killed with code %s", subshell_process.returncode
            )
            _aks_bastion_restore_shell(shell_cmd)


async def _aks_bastion_launch_tunnel(nrg, bastion, port, mc_id):
    """Launch the bastion tunnel using the provided parameters."""

    cmd = (
        f"az network bastion tunnel --resource-group {nrg} "
        f"--name {bastion} --port {port} --target-resource-id {mc_id} --resource-port 443"
    )
    logger.debug("Creating bastion tunnel with command: %s", cmd)
    tunnel_proces = await asyncio.create_subprocess_shell(
        cmd,
        shell=True,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    logger.info("Tunnel launched with PID: %s", tunnel_proces.pid)

    try:
        stdout, stderr = await tunnel_proces.communicate()
        output = ""
        if stdout:
            output = "stdout: " + stdout.decode()
        if stderr:
            output += " stderr: " + stderr.decode()
        logger.debug("Tunnel process completed with output: %s", output)
    except asyncio.CancelledError:
        logger.info("Tunnel process was cancelled. Terminating...")
        tunnel_proces.terminate()
        stdout, stderr = await tunnel_proces.communicate()
        output = ""
        if stdout:
            output = "stdout: " + stdout.decode()
        if stderr:
            output += " stderr: " + stderr.decode()
        logger.info("Tunnel process exited with output: %s", output)


def _aks_bastion_validate_tunnel(port):
    """Check if the bastion tunnel is active on the specified port."""

    # retry for up to 5 times to check if the port is open
    for attempt in range(5):
        logger.debug(
            "Checking if tunnel is active on port %s (attempt %d)...", port, attempt + 1
        )
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(5)
            try:
                s.connect(("localhost", port))
                logger.info("Tunnel is active on port %s", port)
                return True
            except socket.error as e:
                logger.warning(
                    "Attempt %d: Tunnel is not active on port %s: %s",
                    attempt + 1,
                    port,
                    e,
                )
                time.sleep(1)
    logger.error("Tunnel failed to become active on port %s after 5 attempts.", port)
    return False
