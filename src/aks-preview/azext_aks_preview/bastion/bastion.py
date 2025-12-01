# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import asyncio
import os
import shutil
import socket
import subprocess
import sys
from typing import List, TextIO
from urllib.parse import urlparse

import psutil
import yaml
from azure.cli.command_modules.acs._consts import DecoratorEarlyExitException
from azure.cli.core.azclierror import (CLIInternalError,
                                       InvalidArgumentValueError,
                                       ResourceNotFoundError)
from azure.cli.core.util import run_az_cmd
from azure.mgmt.core.tools import (is_valid_resource_id,
                                   is_valid_resource_name, parse_resource_id)
from knack.log import get_logger
from knack.prompting import prompt_y_n

logger = get_logger(__name__)


# pylint: disable=too-few-public-methods
class BastionResource:
    def __init__(self, name, resource_group):
        self.name = name
        self.resource_group = resource_group


def aks_bastion_parse_bastion_resource(
    bastion: str, resource_groups: List[str]
) -> BastionResource:
    """Get the bastion resource name from the provided name or node resource group."""

    # validate provided bastion
    if bastion:
        if is_valid_resource_id(bastion):
            parsed_id = parse_resource_id(bastion)
            return BastionResource(
                name=parsed_id["name"], resource_group=parsed_id["resource_group"]
            )
        if is_valid_resource_name(bastion):
            for resource_group in resource_groups:
                logger.debug(
                    "Checking bastion '%s' in resource group '%s'.",
                    bastion,
                    resource_group,
                )
                # check if the bastion exists in the provided resource group
                result = run_az_cmd(
                    [
                        "network",
                        "bastion",
                        "show",
                        "--resource-group",
                        resource_group,
                        "--name",
                        bastion,
                        "--output",
                        "json",
                    ],
                    out_file=TextIO(),
                )
                if result.exit_code != 0:
                    logger.debug(
                        "Failed to find bastion '%s' in resource group '%s'. Error: %s",
                        bastion,
                        resource_group,
                        result.error,
                    )
                    continue
                logger.debug(
                    "Found bastion resource: %s in resource group: %s",
                    bastion,
                    resource_group,
                )
                return BastionResource(name=bastion, resource_group=resource_group)
    logger.warning(
        "No valid bastion resource provided: '%s'. Attempting to locate one from resource groups: '%s'.",
        bastion,
        resource_groups,
    )

    # list bastions in the provided resource groups
    for resource_group in resource_groups:
        logger.debug("Searching for bastion in resource group '%s'.", resource_group)
        result = run_az_cmd(
            [
                "network",
                "bastion",
                "list",
                "--resource-group",
                resource_group,
                "--output",
                "json",
            ],
            out_file=TextIO(),
        )
        if result.exit_code != 0:
            logger.debug(
                "Failed to list bastions in resource group '%s'. Error: %s",
                resource_group,
                result.error,
            )
            continue
        bastions = result.result
        if len(bastions) > 1:
            logger.warning(
                "Multiple bastions found in the node resource group. Using the first one."
            )
        logger.debug(
            "Using bastion resource: %s in resource group: %s",
            bastions[0]["name"],
            resource_group,
        )
        return BastionResource(name=bastions[0]["name"], resource_group=resource_group)
    raise ResourceNotFoundError(
        "No bastion found in the provided resource groups: "
        f"{', '.join(resource_groups)}. Please provide a valid bastion name or resource ID."
    )


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
    result = run_az_cmd(["extension", "list", "--output", "json"], out_file=TextIO())
    if result.exit_code != 0:
        raise CLIInternalError(
            f"Failed to list installed extensions: {result.error}"
        )
    for ext in result.result:
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
    result = run_az_cmd(["extension", "add", "--name", "bastion"], out_file=TextIO())
    if result.exit_code != 0:
        raise CLIInternalError(f"Failed to install bastion extension: {result.error}")


def aks_bastion_set_kubeconfig(kubeconfig_path, port):
    """Update the kubeconfig file to point to the local port."""

    logger.debug("Updating kubeconfig file: %s to use port: %s", kubeconfig_path, port)
    with open(kubeconfig_path, "r") as f:
        data = yaml.load(f, Loader=yaml.SafeLoader)
    current_context = data["current-context"]
    current_cluster = ""
    for context in data["contexts"]:
        if context["name"] == current_context:
            current_cluster = context["context"]["cluster"]

    for cluster in data["clusters"]:
        if cluster["name"] == current_cluster:
            server = cluster["cluster"]["server"]
            hostname = urlparse(server).hostname
            # update the server URL to point to the local port
            cluster["cluster"]["server"] = f"https://localhost:{port}/"
            # set the tls-server-name to the hostname
            cluster["cluster"]["tls-server-name"] = hostname
            break
    with open(kubeconfig_path, "w") as f:
        yaml.dump(data, f)


async def aks_bastion_runner(
    bastion_resource, port, mc_id, kubeconfig_path, test_hook=None
):
    """Run the bastion tunnel and subshell in parallel, cancelling the other if one completes."""

    task1 = asyncio.create_task(
        _aks_bastion_launch_tunnel(bastion_resource, port, mc_id)
    )
    if test_hook:
        task2 = asyncio.create_task(
            _aks_bastion_test_hook(kubeconfig_path, port, kubectl_path=test_hook)
        )
    else:
        task2 = asyncio.create_task(_aks_bastion_launch_subshell(kubeconfig_path, port))

    _, pending = await asyncio.wait([task1, task2], return_when=asyncio.FIRST_COMPLETED)

    for task in pending:
        task.cancel()

    # Wait for the cancellations to finish
    await asyncio.gather(*pending, return_exceptions=True)


def aks_batsion_clean_up():
    pass


def _aks_bastion_get_az_cmd_name():
    """Get the name of the az command based on system platform."""

    if sys.platform.startswith("win"):
        return "az.cmd"
    return "az"


def _aks_bastion_get_current_shell_cmd():
    """Get the current shell command being used by the parent process."""

    ppid = os.getppid()
    parent = psutil.Process(ppid)
    parent_name = parent.name()
    logger.debug("Immediate parent process: %s (PID: %s)", parent_name, ppid)

    # On Windows, Azure CLI is often invoked as az.cmd, which means the immediate parent
    # is cmd.exe but the actual user shell (PowerShell) is the grandparent process
    if not sys.platform.startswith("win"):
        logger.debug("Using parent process name as shell: %s", parent_name)
        return parent_name

    return _get_windows_shell_cmd(parent, parent_name)


def _get_windows_shell_cmd(parent, parent_name):
    """Get the shell command on Windows, handling az.cmd wrapper scenarios."""
    try:
        parent_exe = parent.exe()
        logger.debug("Parent executable path: %s", parent_exe)

        # If the immediate parent is cmd.exe, check if it's wrapping az.cmd for PowerShell
        if "cmd" in parent_name.lower():
            return _handle_cmd_parent(parent)

        # For direct PowerShell processes (not wrapped by cmd)
        if "pwsh" in parent_name.lower() or "powershell" in parent_name.lower():
            return _handle_powershell_parent(parent_exe, parent_name)

        logger.debug("Other Windows shell detected: %s", parent_name)
        return parent_exe if parent_exe else parent_name

    except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
        logger.debug("Cannot access parent process details: %s", e)
        return parent_name


def _handle_cmd_parent(parent):
    """Handle case where immediate parent is cmd.exe - check for PowerShell grandparent."""
    try:
        # Get the grandparent process (parent of cmd.exe)
        grandparent = parent.parent()
        if not grandparent:
            return "cmd"

        grandparent_name = grandparent.name()
        logger.debug("Detected grandparent process: %s (PID: %s)", grandparent_name, grandparent.pid)

        # If grandparent is PowerShell, that's the actual user shell
        if "pwsh" in grandparent_name.lower() or "powershell" in grandparent_name.lower():
            return _get_powershell_executable(grandparent)

        logger.debug("Grandparent is not PowerShell - using cmd as target shell")
        return "cmd"

    except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
        # If we can't access grandparent, assume cmd is the actual shell
        logger.debug("Cannot access grandparent process: %s - using cmd as target shell", e)
        return "cmd"


def _handle_powershell_parent(parent_exe, parent_name):
    """Handle direct PowerShell parent process."""
    logger.debug("Direct PowerShell parent detected")
    return _get_powershell_executable_from_path() or parent_exe or parent_name


def _get_powershell_executable(grandparent):
    """Get PowerShell executable, preferring pwsh over powershell."""
    logger.debug("Grandparent is PowerShell - using PowerShell as target shell")
    powershell_cmd = _get_powershell_executable_from_path()
    if powershell_cmd:
        return powershell_cmd

    # If we can't find pwsh/powershell in PATH, use the detected grandparent
    logger.debug("PowerShell not found in PATH, using detected grandparent executable")
    return grandparent.exe() if grandparent.exe() else grandparent.name()


def _get_powershell_executable_from_path():
    """Try to find PowerShell executable in PATH, preferring pwsh over powershell."""
    pwsh_path = shutil.which("pwsh")
    if pwsh_path:
        logger.debug("Found pwsh at: %s", pwsh_path)
        return "pwsh"

    powershell_path = shutil.which("powershell")
    if powershell_path:
        logger.debug("Found powershell at: %s", powershell_path)
        return "powershell"

    return None


def _aks_bastion_prepare_shell_cmd(kubeconfig_path):
    """Prepare the shell command to launch a subshell with KUBECONFIG set."""

    shell_cmd = _aks_bastion_get_current_shell_cmd()
    updated_shell_cmd = shell_cmd

    # Handle different shell types
    if shell_cmd.endswith("bash") and os.path.exists(os.path.expanduser("~/.bashrc")):
        updated_shell_cmd = (
            f"""{shell_cmd} -c '{shell_cmd} --rcfile <(cat ~/.bashrc; """
            f"""echo "export KUBECONFIG={kubeconfig_path}")'"""
        )
    elif shell_cmd in ["pwsh", "powershell"] or "pwsh" in shell_cmd.lower() or "powershell" in shell_cmd.lower():
        # PowerShell: Set environment variable and start new session
        # Use proper PowerShell syntax for setting environment variables
        escaped_path = kubeconfig_path.replace("'", "''")  # Escape single quotes for PowerShell
        if shell_cmd == "pwsh" or "pwsh" in shell_cmd.lower():
            updated_shell_cmd = f'pwsh -NoExit -Command "$env:KUBECONFIG=\'{escaped_path}\'"'
        else:
            updated_shell_cmd = f'powershell -NoExit -Command "$env:KUBECONFIG=\'{escaped_path}\'"'
    elif shell_cmd == "cmd" or "cmd" in shell_cmd.lower():
        # CMD: Set environment variable and keep session open
        updated_shell_cmd = f'cmd /k "set KUBECONFIG={kubeconfig_path}"'

    return shell_cmd, updated_shell_cmd


def _aks_bastion_restore_shell(shell_cmd):
    """Restore the shell settings after the subshell exits."""

    if shell_cmd.endswith("bash"):
        subprocess.run(["stty", "sane"], stdin=sys.stdin)
    # PowerShell and CMD on Windows typically don't need special restoration
    # as they handle terminal state management internally


async def _aks_bastion_launch_subshell(kubeconfig_path, port):
    """Launch a subshell with the KUBECONFIG environment variable set to the provided path."""
    subshell_process = None
    try:
        if await _aks_bastion_validate_tunnel(port):
            logger.debug("Bastion tunnel is set up successfully.")
        else:
            raise CLIInternalError(
                f"Bastion tunnel failed to set up on port {port}. Please check the logs for more details."
            )

        env = os.environ.copy()
        env.update({"KUBECONFIG": kubeconfig_path})
        shell_cmd, updated_shell_cmd = _aks_bastion_prepare_shell_cmd(kubeconfig_path)
        logger.warning(
            "Launching subshell with command '%s'. Setting env var KUBECONFIG to '%s'.",
            updated_shell_cmd,
            kubeconfig_path,
        )
        logger.warning(
            "Use exit or Ctrl-D (i.e. EOF) to exit the subshell."
        )
        subshell_process = await asyncio.subprocess.create_subprocess_shell(
            cmd=updated_shell_cmd,
            stdin=None,
            stdout=None,
            stderr=None,
            shell=True,
            env=env,
        )
        logger.info("Subshell launched with PID: %s", subshell_process.pid)

        # subshell process must not exit unless it encounters a failure or is deliberately shut down
        await subshell_process.wait()
        logger.debug("Subshell exited with code: %s", subshell_process.returncode)
    except asyncio.CancelledError:
        # attempt to terminate the subshell process gracefully
        if subshell_process is not None:
            logger.info("Subshell was cancelled. Terminating...")
            subshell_process.terminate()
            try:
                await asyncio.wait_for(subshell_process.wait(), timeout=5)
                logger.info("Subshell exited cleanly after termination.")
            except asyncio.TimeoutError:
                logger.warning(
                    "Subshell did not exit after SIGTERM. Sending SIGKILL..."
                )
                subshell_process.kill()
                await asyncio.wait_for(subshell_process.wait(), timeout=5)
                logger.warning(
                    "Subshell forcefully killed with code %s",
                    subshell_process.returncode,
                )
                _aks_bastion_restore_shell(shell_cmd)
        else:
            logger.warning("Subshell was cancelled before it could be launched.")


async def _aks_bastion_launch_tunnel(bastion_resource, port, mc_id):
    """Launch the bastion tunnel using the provided parameters."""

    tunnel_proces = None
    try:
        az_cmd_name = _aks_bastion_get_az_cmd_name()
        cmd = (
            f"{az_cmd_name} network bastion tunnel --resource-group {bastion_resource.resource_group} "
            f"--name {bastion_resource.name} --port {port} --target-resource-id {mc_id} --resource-port 443"
        )
        logger.warning("Creating bastion tunnel with command: '%s'", cmd)
        tunnel_proces = await asyncio.create_subprocess_exec(
            *(cmd.split()),
            stdin=asyncio.subprocess.DEVNULL,
            stdout=asyncio.subprocess.DEVNULL,
            stderr=asyncio.subprocess.DEVNULL,
            shell=False,
        )
        logger.info("Tunnel launched with PID: %s", tunnel_proces.pid)

        # tunnel process must not exit unless it encounters a failure or is deliberately shut down
        await tunnel_proces.wait()
        logger.error("Bastion tunnel exited with code %s", tunnel_proces.returncode)
    except asyncio.CancelledError:
        # attempt to terminate the tunnel process gracefully
        if tunnel_proces is not None:
            logger.info("Tunnel process was cancelled. Terminating...")
            tunnel_proces.terminate()
            try:
                await asyncio.wait_for(tunnel_proces.wait(), timeout=5)
                logger.info("Tunnel process exited cleanly after termination.")
            except asyncio.TimeoutError:
                logger.warning(
                    "Tunnel process did not exit after SIGTERM. Sending SIGKILL..."
                )
                tunnel_proces.kill()
                await asyncio.wait_for(tunnel_proces.wait(), timeout=5)
                logger.warning(
                    "Tunnel process forcefully killed with code %s",
                    tunnel_proces.returncode,
                )
        else:
            logger.warning("Tunnel process was cancelled before it could be launched.")


async def _aks_bastion_validate_tunnel(port):
    """Check if the bastion tunnel is active on the specified port."""
    # give the tunnel some time to establish before checking the port
    await asyncio.sleep(5)

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
                await asyncio.sleep(5)
    logger.error("Tunnel failed to become active on port %s after 5 attempts.", port)
    return False


async def _aks_bastion_test_hook(kubeconfig_path, port, kubectl_path):
    """Test hook to validate the bastion tunnel and run a kubectl command."""
    if not await _aks_bastion_validate_tunnel(port):
        raise CLIInternalError(f"Bastion tunnel failed to set up on port {port}.")
    kubectl_process = await asyncio.create_subprocess_shell(
        f"{kubectl_path} --kubeconfig {kubeconfig_path} get nodes",
        stdin=asyncio.subprocess.DEVNULL,
        stdout=asyncio.subprocess.DEVNULL,
        stderr=asyncio.subprocess.DEVNULL,
        shell=True,
    )
    await asyncio.wait_for(kubectl_process.wait(), timeout=10)
    if kubectl_process.returncode != 0:
        raise CLIInternalError(
            f"Command kubectl failed with return code {kubectl_process.returncode}. "
        )
