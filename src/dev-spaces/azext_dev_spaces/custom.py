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


# pylint:disable=no-member,too-many-lines,too-many-locals,too-many-statements


def ads_use_dev_spaces(cluster_name, resource_group_name, update=False, space_name=None,
                       endpoint_type='Public', do_not_prompt=False):
    """
    Use Azure Dev Spaces with a managed Kubernetes cluster.

    :param cluster_name: Name of the managed cluster.
    :type cluster_name: String
    :param resource_group_name: Name of resource group. You can configure the default group. \
    Using 'az configure --defaults group=<name>'.
    :type resource_group_name: String
    :param update: Update to the latest Azure Dev Spaces client components.
    :type update: bool
    :param space_name: Name of the new or existing dev space to select. Defaults to an interactive selection experience.
    :type space_name: String
    :param endpoint_type: The endpoint type to be used for a Azure Dev Spaces controller. \
    See https://aka.ms/azds-networking for more information.
    :type endpoint_type: String
    :param do_not_prompt: Do not prompt for confirmation. Requires --space.
    :type do_not_prompt: bool
    """

    azds_cli = _install_dev_spaces_cli(update, do_not_prompt)

    use_command_arguments = [azds_cli, 'use', '--name', cluster_name,
                             '--resource-group', resource_group_name, '--endpoint', endpoint_type]

    if space_name is not None:
        use_command_arguments.append('--space')
        use_command_arguments.append(space_name)

    if do_not_prompt:
        use_command_arguments.append('-y')
    subprocess.call(
        use_command_arguments, universal_newlines=True)


def ads_remove_dev_spaces(cluster_name, resource_group_name, do_not_prompt=False):
    """
    Remove Azure Dev Spaces from a managed Kubernetes cluster.

    :param cluster_name: Name of the managed cluster.
    :type cluster_name: String
    :param resource_group_name: Name of resource group. You can configure the default group. \
    Using 'az configure --defaults group=<name>'.
    :type resource_group_name: String
    :param do_not_prompt: Do not prompt for confirmation.
    :type do_not_prompt: bool
    """

    azds_cli = _install_dev_spaces_cli(False, do_not_prompt)

    remove_command_arguments = [azds_cli, 'remove', '--name', cluster_name,
                                '--resource-group', resource_group_name]
    if do_not_prompt:
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


def _install_dev_spaces_cli(force_install, do_not_prompt):
    azds_tool = 'Azure Dev Spaces CLI'
    should_install_azds = False
    system = platform.system()
    if system == 'Windows':
        # Windows
        # Dev Spaces Install Path (WinX)
        azds_cli = os.path.join(os.environ["ProgramW6432"],
                                "Microsoft SDKs", "Azure",
                                "Azure Dev Spaces CLI", "azds.exe")
        setup_file = os.path.join(_create_tmp_dir(), 'azds-winx-setup.exe')
        setup_url = "https://aka.ms/get-azds-windows-az"
        setup_args = [setup_file]
        if do_not_prompt:
            setup_args.append('/quiet')
    elif system == 'Darwin':
        # OSX
        azds_cli = 'azds'
        setup_file = os.path.join(_create_tmp_dir(), 'azds-osx-setup.sh')
        setup_url = "https://aka.ms/get-azds-mac-az"
        setup_args = ['bash', setup_file]
        if do_not_prompt:
            setup_args.append('-y')
    elif system == 'Linux':
        # Linux
        azds_cli = 'azds'
        setup_file = os.path.join(_create_tmp_dir(), 'azds-linux-setup.sh')
        setup_url = "https://aka.ms/get-azds-linux-az"
        setup_args = ['bash', setup_file]
        if do_not_prompt:
            setup_args.append('-y')
    else:
        raise CLIError('Platform not supported: {}.'.format(system))

    should_install_azds = force_install | (not _is_dev_spaces_installed(azds_cli))

    if should_install_azds:
        # Install AZDS
        logger.warning('Installing Dev Spaces commands...')
        if system == 'Windows':
            logger.warning('A separate window will open to guide you through the installation process.')

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
