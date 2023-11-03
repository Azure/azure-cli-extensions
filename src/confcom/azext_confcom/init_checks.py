# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import ctypes
import os
import sys
import getpass

import docker
from knack.log import get_logger

logger = get_logger(__name__)


def is_linux():
    return sys.platform in ("linux", "linux2")


if is_linux():
    import grp  # pylint: disable=import-error


def is_admin() -> bool:
    admin = False
    try:
        admin = os.getuid() == 0
    except AttributeError:
        admin = ctypes.windll.shell32.IsUserAnAdmin() != 0
    return admin


def is_docker_running() -> bool:
    # check to see if docker is running
    client = None
    out = True
    try:
        client = docker.from_env()
        # need any command that will show the docker daemon is not running
        client.containers.list()
    except docker.errors.DockerException:
        out = False
    finally:
        if client:
            client.close()
    return out


def docker_permissions() -> str:
    docker_group = None
    # check if the user is in the docker group and if not an admin
    if is_linux() and not is_admin():
        client = None
        try:
            docker_group = grp.getgrnam("docker")
            client = docker.from_env()
            # need any command that will show the docker daemon is
            client.containers.list()
        except KeyError:
            return "The docker group was not found"
        except docker.errors.DockerException as e:
            return f"Docker error: {e.args[0]}"
        finally:
            if client:
                client.close()
        if getpass.getuser() not in docker_group.gr_mem:
            return """The current user does not have permission to run Docker.
             Run 'sudo usermod -aG docker' to add them to the docker group."""
    return ""


def run_initial_docker_checks() -> str:
    """Utility function: call the rest of the checks to make sure the environment has prerequisites i.e.
    docker is running and the user is allowed to use it"""
    result = is_docker_running()
    if not result:
        return "The docker process was not found. Please start Docker."

    error_msg = docker_permissions()
    if error_msg:
        return error_msg
    return ""
