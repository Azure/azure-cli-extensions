# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import logging
import os
import ssl
import sys
import stat
import platform
import tarfile
from zipfile import ZipFile

from knack.prompting import prompt_y_n
from knack.util import CLIError
from pathlib import Path
from six.moves.urllib.request import urlopen  # pylint: disable=import-error

logger = logging.getLogger(__name__)

def cf_dapr(cli_ctx, *_):

    from azure.cli.core.commands.client_factory import get_mgmt_service_client
    # TODO: Replace CONTOSO with the appropriate label and uncomment
    # from azure.mgmt.CONTOSO import CONTOSOManagementClient
    # return get_mgmt_service_client(cli_ctx, CONTOSOManagementClient)
    return None

def get_dapr_cli_path():
    dapr_cli_path = os.path.join(Path.home(), "dapr_cli", "dapr")
    if os.path.exists(dapr_cli_path) is False:
        install_dapr_cli()
    return dapr_cli_path


def install_dapr_cli():
    confirmation = dapr_cli_install_has_comfirmed()
    if not confirmation:
        return

    """
    Install the Dapr CLI if it is not already installed.
    """

    print("Installing Dapr CLI...")

    base_download_url = "https://github.com/dapr/cli/releases"
    dapr_cli_version = "v1.9.1" # determine which is the latest version
    arch_type = "amd64" # determine what is the architecture of the system
    os_type = platform.system().lower()
    download_url = ''
    cli_install_dir = ''

    if os_type == "windows":
        dapr_cli_filename = f"dapr_{os_type}_{arch_type}.zip"
    elif os_type == "linux":
        dapr_cli_filename = f"dapr_{os_type}_{arch_type}.tar.gz"
    elif os_type == "darwin":
        dapr_cli_filename = f"dapr_{os_type}_{arch_type}.tar.gz"
    else:
        raise Exception("Unsupported OS type")

    download_url = f"{base_download_url}/download/{dapr_cli_version}/{dapr_cli_filename}"
    logger.debug('Downloading dapr cli to "%s" from "%s"',
                   Path.home(), download_url)

    # directory to hold the oss cli executable
    cli_install_dir = os.path.join(Path.home(), "dapr_cli")
    if not os.path.exists(cli_install_dir):
        os.makedirs(cli_install_dir)

    # download the cli
    try:
        _urlretrieve(download_url, os.path.join(cli_install_dir, dapr_cli_filename))
    except IOError as ex:
        raise CLIError(
            'Connection error while attempting to download client ({})'.format(ex))

    # extract the cli archive
    if os_type == "windows":
        with ZipFile(os.path.join(cli_install_dir, dapr_cli_filename), 'r') as zip:
            zip.extractall()
    else:
        with tarfile.open(os.path.join(cli_install_dir, dapr_cli_filename), "r:gz") as tar:
            tar.extractall(cli_install_dir)

    print('dapr cli downloaded and installed successfully')

def dapr_cli_install_has_comfirmed():
    return prompt_y_n('Are you sure you want to install dapr cli as a prerequisite for this extension?')


def _urlretrieve(url, filename):
    req = urlopen(url, context=_ssl_context())
    with open(filename, "wb") as f:
        f.write(req.read())

def _ssl_context():
    if sys.version_info < (3, 4):
        return ssl.SSLContext(ssl.PROTOCOL_TLSv1)
    return ssl.create_default_context()
