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
import oras.client
import tarfile
from glob import glob

import colorama

from azure.cli.core.style import Style, print_styled_text
from azure.core.exceptions import ResourceNotFoundError, HttpResponseError
from azure.cli.core import telemetry
from azure.cli.core import azclierror
from azure.mgmt.core.tools import resource_id, parse_resource_id
from azure.cli.core.commands.client_factory import get_subscription_id
from knack import log
from knack.prompting import prompt_y_n

from . import file_utils
from . import constants as consts

logger = log.get_logger(__name__)


# Get the Access Details to connect to Arc Connectivity platform from the HybridConnectivity RP
def get_relay_information(cmd, resource_group, vm_name, resource_type,
                          certificate_validity_in_seconds, port, yes_without_prompt):
    if not certificate_validity_in_seconds or \
       certificate_validity_in_seconds > consts.RELAY_INFO_MAXIMUM_DURATION_IN_SECONDS:
        certificate_validity_in_seconds = consts.RELAY_INFO_MAXIMUM_DURATION_IN_SECONDS

    namespace = resource_type.split('/', 1)[0]
    arc_type = resource_type.split('/', 1)[1]
    resource_uri = resource_id(subscription=get_subscription_id(cmd.cli_ctx), resource_group=resource_group,
                               namespace=namespace, type=arc_type, name=vm_name)

    cred = None
    new_service_config = False
    try:
        cred = _list_credentials(cmd, resource_uri, certificate_validity_in_seconds)
    except ResourceNotFoundError:
        _create_default_endpoint(cmd, resource_uri)
    except HttpResponseError as e:
        if e.reason != "Precondition Failed":
            raise azclierror.UnclassifiedUserFault(f"Unable to retrieve relay information. Failed with error: {str(e)}")
    except Exception as e:
        raise azclierror.UnclassifiedUserFault(f"Unable to retrieve relay information. Failed with error: {str(e)}")

    if not cred:
        _create_service_configuration(cmd, resource_uri, port, yes_without_prompt)
        new_service_config = True
        try:
            cred = _list_credentials(cmd, resource_uri, certificate_validity_in_seconds)
        except Exception as e:
            raise azclierror.UnclassifiedUserFault(f"Unable to get relay information. Failed with error: {str(e)}")
        _handle_relay_connection_delay(cmd, "Setting up service configuration")
    else:
        if not _check_service_configuration(cmd, resource_uri, port):
            _create_service_configuration(cmd, resource_uri, port, yes_without_prompt)
            new_service_config = True
            try:
                cred = _list_credentials(cmd, resource_uri, certificate_validity_in_seconds)
            except Exception as e:
                raise azclierror.UnclassifiedUserFault(f"Unable to get relay information. Failed with error: {str(e)}")
            _handle_relay_connection_delay(cmd, "Setting up service configuration")
    return (cred, new_service_config)


def _check_service_configuration(cmd, resource_uri, port):
    from .aaz.latest.hybrid_connectivity.endpoint.service_configuration import Show as ShowServiceConfig
    show_service_config_args = {
        'endpoint_name': 'default',
        'resource_uri': resource_uri,
        'service_configuration_name': 'SSH'
    }
    serviceConfig = None
    # pylint: disable=broad-except
    try:
        serviceConfig = ShowServiceConfig(cli_ctx=cmd.cli_ctx)(command_args=show_service_config_args)
    except Exception:
        # If for some reason the request for Service Configuration fails,
        # we will still attempt to get relay information and connect. If the service configuration
        # is not setup correctly, the connection will fail.
        # The more likely scenario is that the request failed with a "Authorization Error",
        # in case the user isn't an owner/contributor.
        return True
    if port:
        return serviceConfig['port'] == int(port)

    if serviceConfig['port'] != 22:
        logger.warning("The Service Configuration endpoint is set to a non-default port. "
                       "To either update the Service Configuration or connect using the non-default port, "
                       "please use the -Port parameter")
    return True


def _create_default_endpoint(cmd, resource_uri):
    from .aaz.latest.hybrid_connectivity.endpoint import Create as CreateHybridConnectivityEndpoint
    vm_name = parse_resource_id(resource_uri)["name"]
    resource_group = parse_resource_id(resource_uri)["resource_group"]
    create_endpoint_args = {
        'endpoint_name': 'default',
        'resource_uri': resource_uri,
        'type': 'default'
    }
    try:
        endpoint = CreateHybridConnectivityEndpoint(cli_ctx=cmd.cli_ctx)(command_args=create_endpoint_args)
    except HttpResponseError as e:
        colorama.init()
        if e.reason == "Forbidden":
            raise azclierror.UnauthorizedError(f"Client is not authorized to create a default connectivity "
                                               f"endpoint for \'{vm_name}\' in Resource Group \'{resource_group}\'. "
                                               f"This is a one-time operation that must be performed by "
                                               f"an account with Owner or Contributor role to allow "
                                               f"connections to the target resource.")
        raise azclierror.UnclassifiedUserFault(f"Failed to create default endpoint for the target Arc Server. "
                                               f"\nError: {str(e)}")
    except Exception as e:
        colorama.init()
        raise azclierror.UnclassifiedUserFault(f"Failed to create default endpoint for the target Arc Server. "
                                               f"\nError: {str(e)}")

    return endpoint


def _create_service_configuration(cmd, resource_uri, port, yes_without_prompt):
    from .aaz.latest.hybrid_connectivity.endpoint.service_configuration import Create as CreateServiceConfig
    prompt = (f"The port {port} that you are trying to connect to is not allowed "
              f"for SSH connections for this resource. Would you like to update "
              f"the current Service Configuration in the endpoint to allow connections to port {port}?")
    if not port:
        port = '22'
        prompt = ("Port 22 is not allowed for SSH connections in this resource. Would you like to update "
                  "the current Service Configuration in the endpoint to allow connections to port 22? If you "
                  "would like to update the Service Configuration to allow connections to a different port, "
                  "please provide the -Port parameter or manually set up the Service Configuration.")
    if not yes_without_prompt and not prompt_y_n(prompt):
        raise azclierror.ClientRequestError(f"SSH connection is not enabled in the target port {port}.")

    create_service_conf_args = {
        'endpoint_name': 'default',
        'resource_uri': resource_uri,
        'service_configuration_name': 'SSH',
        'port': int(port),
        'service_name': 'SSH'
    }
    try:
        serviceConfig = CreateServiceConfig(cli_ctx=cmd.cli_ctx)(command_args=create_service_conf_args)
    except HttpResponseError as e:
        colorama.init()
        vm_name = parse_resource_id(resource_uri)["name"]
        resource_group = parse_resource_id(resource_uri)["resource_group"]
        if e.reason == "Forbidden":
            raise azclierror.UnauthorizedError(f"Client is not authorized to create or update the Service "
                                               f"Configuration endpoint for \'{vm_name}\' in the Resource "
                                               f"Group \'{resource_group}\'. This is an operation that "
                                               f"must be performed by an account with Owner or Contributor "
                                               f"role to allow SSH connections to the specified port {port}.")
        raise azclierror.UnclassifiedUserFault(f"Failed to create service configuration to allow SSH "
                                               f"connections to port {port} on the endpoint for {vm_name} "
                                               f"in the Resource Group {resource_group}\nError: {str(e)}")
    except Exception as e:
        raise azclierror.UnclassifiedUserFault(f"Failed to create service configuration to allow SSH connections "
                                               f"to port {port} on the endpoint for {vm_name} in the Resource "
                                               f"Group {resource_group}\nError: {str(e)}")
    return serviceConfig


def _list_credentials(cmd, resource_uri, certificate_validity_in_seconds):
    from .aaz.latest.hybrid_connectivity.endpoint import ListCredential

    list_cred_args = {
        'endpoint_name': 'default',
        'resource_uri': resource_uri,
        'expiresin': int(certificate_validity_in_seconds),
        'service_name': "SSH"
    }

    return ListCredential(cli_ctx=cmd.cli_ctx)(command_args=list_cred_args)


# Downloads client side proxy to connect to Arc Connectivity Platform
def get_client_side_proxy(arc_proxy_folder):

    client_operating_system = _get_client_operating_system()
    client_architecture = _get_client_architeture()
    install_location = _get_proxy_install_location(arc_proxy_folder, operating_system, architecture)
    install_dir = os.path.dirname(install_location)

    # Only download new proxy if it doesn't exist already
    if not os.path.isfile(install_location):
        t0 = time.time()
        # download the proxy
        proxy_package_dir = _download_proxy_from_MAR_to_temp_folder()
        # todo: have a finally block to delete from temp folder if this fails

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
            older_version_location = _get_older_version_proxy_path(install_dir)
            older_version_files = glob(older_version_location)
            for f in older_version_files:
                file_utils.delete_file(f, f"failed to delete older version file {f}", warning=True)

        # move proxy package to install location
        _move_proxy_package_to_install_dir(proxy_package_dir, install_dir)

    return install_location


def _move_proxy_package_to_install_dir(proxy_package_dir, install_dir, operating_system, architecture):
    # move sshproxy to install directory
    proxy_name = f"sshProxy_{operating_system.lower()}_{architecture}_{consts.CLIENT_PROXY_VERSION.replace('.', '_')}" 
    source = os.path.join(proxy_package_dir, "sshproxy")
    destination = os.path.join(install_dir, proxy_name)
    if operating_system.lower() == 'Windows'
        source = source + ".exe"
        destination = destination + ".exe"
    file_utils.move_file(source, destination)

    # move License to install directory
    source = os.path.join(proxy_package_dir, "LICENSE")
    destination = os.path.join(install_dir, "LICENSE")
    file_utils.move_file(source, destination)

    #delete temp folder? or let the finally block do it?
    source = os.path.join(proxy_package_dir, "ThirdPartyNotice")
    destination = os.path.join(install_dir, "ThirdPartyNotice")
    file_utils.move_file(source, destination)


def _download_proxy_from_MAR_to_temp_folder(operating_system, architecture):
    mar_target = f"{consts.CLIENT_PROXY_MAR_TARGET}/{operating_system.lower()}/{architecture}/ssh-proxy"
    temp_dir = tempfile.mkdtemp(prefix="azsshproxy")
    
    client = oras.client.OrasClient()
    response = client.pull(target=f"{mar_target}:{consts.CLIENT_PROXY_VERSION}", outdir=temp_dir)
    
    proxy_package_dir = response[0]
    # TO DO: check that response is valid

    with tarfile.open(proxy_package_dir, 'r:gz') as tar:
        tar.extractall(path=proxy_package_dir)

    logger.debug(f"Downloaded proxy to {proxy_package_dir}")


def _get_older_version_proxy_path(install_dir):
    proxy_name = f"sshProxy_{operating_system.lower()}_{architecture}_*"
    return os.path.join(install_dir, proxy_name)


def _get_proxy_install_location(arc_proxy_folder, operating_system, architecture):
    proxy_name = f"sshProxy_{operating_system.lower()}_{architecture}"
    install_location = proxy_name + "_" + consts.CLIENT_PROXY_VERSION.replace('.', '_')

    if not arc_proxy_folder:
        install_location = os.path.expanduser(os.path.join('~', os.path.join(".clientsshproxy", install_location)))
    else:
        install_location = os.path.join(arc_proxy_folder, install_location)

    return install_location


def _get_client_architeture():
    import platform
    machine = platform.machine()

    logger.debug("Platform OS: %s", operating_system)
    logger.debug("Platform architecture: %s", machine)

    if "arm64" in machine.lower() or "aarch64" in machine.lower():
        architecture = 'arm64'
    elif machine.endswith('64'):
        architecture = 'amd64'
    elif machine.endswith('86'):
        architecture = '386'
    elif machine == '':
        raise azclierror.BadRequestError("Couldn't identify the platform architecture.")
    else:
        raise azclierror.BadRequestError(f"Unsuported architecture: {machine} is not currently supported")
    
    return architeture


def _get_client_operating_system():
    import platform
    operating_system = platform.system()

    if operating_system.lower() not in ('linux', 'darwin', 'windows'):
        raise azclierror.BadRequestError(f"Unsuported OS: {operating_system} platform is not currently supported")
    return operating_system


def format_relay_info_string(relay_info):
    relay_info_string = json.dumps(
        {
            "relay": {
                "namespaceName": relay_info['namespaceName'],
                "namespaceNameSuffix": relay_info['namespaceNameSuffix'],
                "hybridConnectionName": relay_info['hybridConnectionName'],
                "accessKey": relay_info['accessKey'],
                "expiresOn": relay_info['expiresOn'],
                "serviceConfigurationToken": relay_info['serviceConfigurationToken']
            }
        })
    result_bytes = relay_info_string.encode("ascii")
    enc = base64.b64encode(result_bytes)
    base64_result_string = enc.decode("ascii")
    return base64_result_string


def _handle_relay_connection_delay(cmd, message):
    # relay has retry delay after relay connection is lost
    # must sleep for at least as long as the delay
    # otherwise the ssh connection will fail
    progress_bar = cmd.cli_ctx.get_progress_controller(True)
    for x in range(0, consts.SERVICE_CONNECTION_DELAY_IN_SECONDS + 1):
        interval = float(1 / consts.SERVICE_CONNECTION_DELAY_IN_SECONDS)
        progress_bar.add(message=f"{message}:",
                         value=interval * x, total_val=1.0)
        time.sleep(1)
    progress_bar.add(message=f"{message}: complete",
                     value=1.0, total_val=1.0)
    progress_bar.end()

'''
def download_proxy_from_MAR():
    client = oras.client.OrasClient()
    res = client.pull(target="mcr.microsoft.com/azureconnectivity/proxy/darwin/amd64/ssh-proxy:1.3.026973", outdir=".")
    with tarfile.open(res[0], 'r:gz') as tar:
        print(tar.getnames())
        tar.extractall(path='.')
'''