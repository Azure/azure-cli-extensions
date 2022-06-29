# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import time
import stat
import os
import urllib.request
import json
import base64
from glob import glob

import colorama

from azure.cli.core.style import Style, print_styled_text
from azure.core.exceptions import ResourceNotFoundError
from azure.cli.core import telemetry
from azure.cli.core import azclierror
from azure.mgmt.core.tools import resource_id
from azure.cli.core.commands.client_factory import get_subscription_id
from knack import log

from . import file_utils
from . import constants as consts

logger = log.get_logger(__name__)


# Get the Access Details to connect to Arc Connectivity platform from the HybridConnectivity RP
def get_relay_information(cmd, resource_group, vm_name, certificate_validity_in_seconds):
    from azext_ssh._client_factory import cf_endpoint
    client = cf_endpoint(cmd.cli_ctx)

    if not certificate_validity_in_seconds or \
       certificate_validity_in_seconds > consts.RELAY_INFO_MAXIMUM_DURATION_IN_SECONDS:
        certificate_validity_in_seconds = consts.RELAY_INFO_MAXIMUM_DURATION_IN_SECONDS

    try:
        t0 = time.time()
        result = client.list_credentials(resource_group_name=resource_group, machine_name=vm_name,
                                         endpoint_name="default", expiresin=certificate_validity_in_seconds)
        time_elapsed = time.time() - t0
        telemetry.add_extension_event('ssh', {'Context.Default.AzureCLI.SSHListCredentialsTime': time_elapsed})
    except ResourceNotFoundError:
        logger.debug("Default Endpoint couldn't be found. Trying to create Default Endpoint.")
        _create_default_endpoint(cmd, resource_group, vm_name, client)
        try:
            t0 = time.time()
            result = client.list_credentials(resource_group_name=resource_group, machine_name=vm_name,
                                             endpoint_name="default", expiresin=certificate_validity_in_seconds)
            time_elapsed = time.time() - t0
            telemetry.add_extension_event('ssh', {'Context.Default.AzureCLI.SSHListCredentialsTime': time_elapsed})
        except Exception as e:
            raise azclierror.ClientRequestError(f"Request for Azure Relay Information Failed:\n{str(e)}")
    except Exception as e:
        raise azclierror.ClientRequestError(f"Request for Azure Relay Information Failed:\n{str(e)}")
    return result


def _create_default_endpoint(cmd, resource_group, vm_name, client):
    az_resource_id = resource_id(subscription=get_subscription_id(cmd.cli_ctx), resource_group=resource_group,
                                 namespace="Microsoft.HybridCompute", type="machines", name=vm_name)
    endpoint_resource = {"id": az_resource_id, "type_properties_type": "default"}
    try:
        client.create_or_update(resource_group, vm_name, "default", endpoint_resource)
    except Exception as e:
        colorama.init()
        raise azclierror.UnauthorizedError(f"Unable to create Default Endpoint for {vm_name} in {resource_group}."
                                           f"\nError: {str(e)}",
                                           colorama.Fore.YELLOW + "Contact Owner/Contributor of the resource."
                                           + colorama.Style.RESET_ALL)


# Downloads client side proxy to connect to Arc Connectivity Platform
def get_client_side_proxy(arc_proxy_folder):

    request_uri, install_location, older_version_location = _get_proxy_filename_and_url(arc_proxy_folder)
    install_dir = os.path.dirname(install_location)

    # Only download new proxy if it doesn't exist already
    if not os.path.isfile(install_location):
        t0 = time.time()
        # download the executable
        try:
            with urllib.request.urlopen(request_uri) as response:
                response_content = response.read()
                response.close()
        except Exception as e:
            raise azclierror.ClientRequestError(f"Failed to download client proxy executable from {request_uri}. "
                                                "Error: " + str(e)) from e
        time_elapsed = time.time() - t0

        proxy_data = {
            'Context.Default.AzureCLI.SSHProxyDownloadTime': time_elapsed,
            'Context.Default.AzureCLI.SSHProxyVersion': consts.CLIENT_PROXY_VERSION
        }
        telemetry.add_extension_event('ssh', proxy_data)

        # if directory doesn't exist, create it
        if not os.path.isdir(install_dir):
            file_utils.create_directory(install_dir, f"Failed to create client proxy directory '{install_dir}'. ")
        # if directory exists, delete any older versions of the proxy
        else:
            older_version_files = glob(older_version_location)
            for f in older_version_files:
                file_utils.delete_file(f, f"failed to delete older version file {f}", warning=True)

        # write executable in the install location
        file_utils.write_to_file(install_location, 'wb', response_content, "Failed to create client proxy file. ")
        os.chmod(install_location, os.stat(install_location).st_mode | stat.S_IXUSR)
        print_styled_text((Style.SUCCESS, f"SSH Client Proxy saved to {install_location}"))

    return install_location


def _get_proxy_filename_and_url(arc_proxy_folder):
    import platform
    operating_system = platform.system()
    machine = platform.machine()

    logger.debug("Platform OS: %s", operating_system)
    logger.debug("Platform architecture: %s", machine)

    if machine.endswith('64'):
        architecture = 'amd64'
    elif machine.endswith('86'):
        architecture = '386'
    elif machine == '':
        raise azclierror.BadRequestError("Couldn't identify the platform architecture.")
    else:
        raise azclierror.BadRequestError(f"Unsuported architecture: {machine} is not currently supported")

    # define the request url and install location based on the os and architecture
    proxy_name = f"sshProxy_{operating_system.lower()}_{architecture}"
    request_uri = (f"{consts.CLIENT_PROXY_STORAGE_URL}/{consts.CLIENT_PROXY_RELEASE}"
                   f"/{proxy_name}_{consts.CLIENT_PROXY_VERSION}")
    install_location = proxy_name + "_" + consts.CLIENT_PROXY_VERSION.replace('.', '_')
    older_location = proxy_name + "*"

    if operating_system == 'Windows':
        request_uri = request_uri + ".exe"
        install_location = install_location + ".exe"
        older_location = older_location + ".exe"
    elif operating_system not in ('Linux', 'Darwin'):
        raise azclierror.BadRequestError(f"Unsuported OS: {operating_system} platform is not currently supported")

    if not arc_proxy_folder:
        install_location = os.path.expanduser(os.path.join('~', os.path.join(".clientsshproxy", install_location)))
        older_location = os.path.expanduser(os.path.join('~', os.path.join(".clientsshproxy", older_location)))
    else:
        install_location = os.path.join(arc_proxy_folder, install_location)
        older_location = os.path.join(arc_proxy_folder, older_location)

    return request_uri, install_location, older_location


def format_relay_info_string(relay_info):
    relay_info_string = json.dumps(
        {
            "relay": {
                "namespaceName": relay_info.namespace_name,
                "namespaceNameSuffix": relay_info.namespace_name_suffix,
                "hybridConnectionName": relay_info.hybrid_connection_name,
                "accessKey": relay_info.access_key,
                "expiresOn": relay_info.expires_on
            }
        })
    result_bytes = relay_info_string.encode("ascii")
    enc = base64.b64encode(result_bytes)
    base64_result_string = enc.decode("ascii")
    return base64_result_string
