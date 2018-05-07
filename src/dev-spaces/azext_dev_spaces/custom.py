# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from __future__ import print_function
import os
import platform
import subprocess
import tempfile
from knack.log import get_logger
from knack.util import CLIError

logger = get_logger(__name__)


# pylint:disable=no-member,too-many-lines,too-many-locals,too-many-statements


def aks_use_dev_spaces(cluster_name, resource_group_name, space_name='default'):  # pylint: disable=line-too-long
    """
    Use Azure Dev Spaces with a managed Kubernetes cluster.

    :param cluster_name: Name of the target AKS cluster.
    :type cluster_name: String
    :param resource_group_name: Name of the target AKS cluster's resource group.
    :type resource_group_name: String
    :param space_name: The isolated space in the cluster to develop in.
    :type space_name: String
    """

    azds_tool = 'Azure Dev Spaces CLI'
    should_install_vsce = False
    system = platform.system()
    if system == 'Windows':
        # Windows
        # Dev Connect Install Path (WinX)
        azds_cli = os.path.join(os.environ["ProgramW6432"],
                                "Microsoft SDKs", "Azure",
                                "Azure Dev Spaces CLI (Preview)", "azds.exe")
        setup_file = os.path.join(_create_tmp_dir(), 'azds-winx-setup.exe')
        setup_url = "https://aka.ms/get-azds-windows-az"
        setup_args = [setup_file]
    elif system == 'Darwin':
        # OSX
        azds_cli = 'azds'
        setup_file = os.path.join(_create_tmp_dir(), 'azds-osx-setup.sh')
        setup_url = "https://aka.ms/get-azds-osx-az"
        setup_args = ['bash', setup_file]
    else:
        raise CLIError('Platform not supported: {}.'.format(system))

    should_install_vsce = not _is_dev_connect_installed(azds_cli)

    if should_install_vsce:
        # Install VSCE
        logger.info('Installing Dev Spaces commands...')
        from six.moves.urllib.request import urlretrieve
        urlretrieve(setup_url, setup_file)
        try:
            subprocess.call(
                setup_args, universal_newlines=True, stdin=None, stdout=None, stderr=None, shell=False)
        except PermissionError as ex:
            raise CLIError('Installing {} tooling needs permissions: {}'.format(azds_tool, ex))
        finally:
            os.remove(setup_file)
        if not _is_dev_connect_installed(azds_cli):
            raise CLIError("{} not installed properly. Visit 'https://aka.ms/get-azds' \
            for Azure Dev Spaces.".format(azds_tool))

    should_create_dev = False
    from subprocess import PIPE
    retCode = subprocess.call(
        [azds_cli, 'resource', 'select', '-n', cluster_name, '-g', resource_group_name],
        stderr=PIPE)
    if retCode == 1:
        should_create_dev = True

    if should_create_dev:
        subprocess.call(
            [azds_cli, 'resource', 'create', '--aks-name', cluster_name, '--aks-resource-group',
             resource_group_name],
            universal_newlines=True)


def aks_remove_dev_spaces(cluster_name, resource_group_name, prompt=False):  # pylint: disable=line-too-long
    """
    Remove Azure Dev Spaces from a managed Kubernetes cluster.

    :param cluster_name: Name of the target AKS cluster.
    :type cluster_name: String
    :param resource_group_name: Name of the target AKS cluster's resource group.
    :type resource_group_name: String
    :param prompt: Do not prompt for confirmation.
    :type prompt: bool
    """

    azds_tool = 'Azure Dev Spaces CLI'
    system = platform.system()
    if system == 'Windows':
        # Windows
        azds_cli = os.path.join(os.environ["ProgramW6432"],
                                "Microsoft SDKs", "Azure",
                                "Azure Dev Spaces CLI (Preview)", "azds.exe")
    elif system == 'Darwin':
        # OSX
        azds_cli = 'azds'
    else:
        raise CLIError('Platform not supported: {}.'.format(system))

    if not _is_dev_connect_installed(azds_cli):
        raise CLIError("{} not installed properly. Use 'az aks use-dev-spaces' \
        commands for Azure Dev Spaces.".format(azds_tool))

    remove_command_arguments = [azds_cli, 'resource', 'rm', '--name',
                                cluster_name, '--resource-group',
                                resource_group_name]
    if prompt:
        remove_command_arguments.append('-f')
    subprocess.call(
        remove_command_arguments, universal_newlines=True)


def _create_tmp_dir():
    tmp_dir = tempfile.mkdtemp()
    return tmp_dir


def _is_dev_connect_installed(vsce_cli):
    try:
        from subprocess import PIPE, Popen
        Popen([vsce_cli], stdout=PIPE, stderr=PIPE)
    except OSError:
        return False
    return True
