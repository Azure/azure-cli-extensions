# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from __future__ import print_function
import os
import platform
import subprocess
import tempfile
from six.moves.urllib.request import urlretrieve   # pylint: disable=import-error
from knack.log import get_logger  # pylint: disable=import-error
from knack.util import CLIError  # pylint: disable=import-error

logger = get_logger(__name__)


# pylint:disable=no-member,too-many-lines,too-many-locals,too-many-statements,too-few-public-methods


def ads_use_dev_spaces(cluster_name, resource_group_name, space_name='default', parent_space_name=None, update=False):
    """
    Use Azure Dev Spaces with a managed Kubernetes cluster.

    :param cluster_name: Name of the managed cluster.
    :type cluster_name: String
    :param resource_group_name: Name of resource group. You can configure the default group. \
    Using 'az configure --defaults group=<name>'.
    :type resource_group_name: String
    :param space_name: Name of the dev space to use.
    :type space_name: String
    :param parent_space_name: Name of a parent dev space to inherit from when creating a new dev space. \
    By default, if there is already a single dev space with no parent, the new space inherits from this one.
    :type parent_space_name: String
    :param update: Update Azure Dev Spaces tools.
    :type update: bool
    """

    azds_cli = _install_dev_spaces_cli(update)

    from subprocess import PIPE
    retCode = subprocess.call(
        [azds_cli, 'controller', 'select', '--name', cluster_name, '--resource-group', resource_group_name],
        stderr=PIPE)
    if retCode != 0:
        retCode = subprocess.call(
            [azds_cli, 'controller', 'create', '--target-name', cluster_name, '--target-resource-group',
             resource_group_name, '--name', cluster_name, '--resource-group', resource_group_name],
            universal_newlines=True)
        if retCode != 0:
            return

    retCode = subprocess.call(
        [azds_cli, 'space', 'select', '--name', space_name], stderr=PIPE)
    if retCode == 0:
        return

    create_space_arguments = [azds_cli, 'space', 'create', '--name', space_name]
    if parent_space_name is not None:
        create_space_arguments.append('--parent')
        create_space_arguments.append(parent_space_name)
    subprocess.call(create_space_arguments, universal_newlines=True)


def ads_remove_dev_spaces(cluster_name, resource_group_name, prompt=False):
    """
    Remove Azure Dev Spaces from a managed Kubernetes cluster.

    :param cluster_name: Name of the managed cluster.
    :type cluster_name: String
    :param resource_group_name: Name of resource group. You can configure the default group. \
    Using 'az configure --defaults group=<name>'.
    :type resource_group_name: String
    :param prompt: Do not prompt for confirmation.
    :type prompt: bool
    """

    azds_cli = _install_dev_spaces_cli(False)

    remove_command_arguments = [azds_cli, 'controller', 'delete', '--name',
                                cluster_name, '--resource-group', resource_group_name]
    if prompt:
        remove_command_arguments.append('-y')
    subprocess.call(
        remove_command_arguments, universal_newlines=True)


def _create_tmp_dir():
    tmp_dir = tempfile.mkdtemp()
    return tmp_dir


def _is_dev_spaces_installed(vsce_cli):
    try:
        from subprocess import PIPE, Popen
        Popen([vsce_cli], stdout=PIPE, stderr=PIPE)
    except OSError:
        return False
    return True


def _install_dev_spaces_cli(force_install):
    azds_tool = 'Azure Dev Spaces CLI'
    should_install_azds = False
    system = platform.system()
    if system == 'Windows':
        # Windows
        # Dev Spaces Install Path (WinX)
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
        setup_url = "https://aka.ms/get-azds-mac-az"
        setup_args = ['bash', setup_file]
    elif system == 'Linux':
        # Linux
        azds_cli = 'azds'
        setup_file = os.path.join(_create_tmp_dir(), 'azds-linux-setup.sh')
        setup_url = "https://aka.ms/get-azds-linux-az"
        setup_args = ['bash', setup_file]
    else:
        raise CLIError('Platform not supported: {}.'.format(system))

    should_install_azds = force_install | (not _is_dev_spaces_installed(azds_cli))

    if should_install_azds:
        # Install AZDS
        logger.info('Installing Dev Spaces (Preview) commands...')
        urlretrieve(setup_url, setup_file)
        try:
            subprocess.call(
                setup_args, universal_newlines=True, stdin=None, stdout=None, stderr=None, shell=False)
        except OSError as ex:
            raise CLIError('Installing {} tooling needs permissions: {}'.format(azds_tool, ex))
        finally:
            os.remove(setup_file)
        if not _is_dev_spaces_installed(azds_cli):
            raise CLIError("{} not installed properly. Visit 'https://aka.ms/get-azds' for Azure Dev Spaces."
                           .format(azds_tool))

    return azds_cli
