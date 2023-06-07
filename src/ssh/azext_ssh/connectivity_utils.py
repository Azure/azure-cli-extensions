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
from azure.core.exceptions import ResourceNotFoundError, HttpResponseError
from azure.cli.core import telemetry
from azure.cli.core import azclierror
from azure.mgmt.core.tools import resource_id, parse_resource_id
from azure.cli.core.commands.client_factory import get_subscription_id
from azure.cli.core.commands import LongRunningOperation
from knack import log
from knack.prompting import prompt_y_n

from . import file_utils
from . import constants as consts

logger = log.get_logger(__name__)


# Get the Access Details to connect to Arc Connectivity platform from the HybridConnectivity RP
def get_relay_information(cmd, resource_group, vm_name, resource_type, certificate_validity_in_seconds, port):
    from .aaz.latest.hybrid_connectivity.endpoint import ListCredential

    if not certificate_validity_in_seconds or \
       certificate_validity_in_seconds > consts.RELAY_INFO_MAXIMUM_DURATION_IN_SECONDS:
        certificate_validity_in_seconds = consts.RELAY_INFO_MAXIMUM_DURATION_IN_SECONDS

    namespace = resource_type.split('/', 1)[0]
    arc_type = resource_type.split('/', 1)[1]
    resource_uri = resource_id(subscription=get_subscription_id(cmd.cli_ctx), resource_group=resource_group,
                                 namespace=namespace, type=arc_type, name=vm_name)
    
    cred = None
    try: 
        cred = _list_credentials(cmd, resource_uri, certificate_validity_in_seconds)
    except ResourceNotFoundError:
        _create_default_endpoint(cmd, resource_uri)
    except HttpResponseError as e:
        if e.reason != "Precondition Failed":
            raise azclierror.UnclassifiedUserFault(f"Unable to get relay information. Failed with error: {str(e)}")
    except Exception as e:
        raise azclierror.UnclassifiedUserFault(f"Unable to get relay information. Failed with error: {str(e)}")

    if not cred:
        _create_service_configuration(cmd, resource_uri, port)
        try:
            cred = _list_credentials(cmd, resource_uri, certificate_validity_in_seconds)
        except Exception as e:
            raise azclierror.UnclassifiedUserFault(f"Unable to get relay information. Failed with error: {str(e)}")
        _handle_relay_connection_delay(cmd)
    else:
        if not _check_service_configuration(cmd, resource_uri, port):
            _create_service_configuration(cmd, resource_uri, port)
            try:
                cred = _list_credentials(cmd, resource_uri, certificate_validity_in_seconds)
            except Exception as e:
                raise azclierror.UnclassifiedUserFault(f"Unable to get relay information. Failed with error: {str(e)}")
            _handle_relay_connection_delay(cmd)
    return cred


def _check_service_configuration(cmd, resource_uri, port):
    from .aaz.latest.hybrid_connectivity.endpoint.service_configuration import Show as ShowServiceConfig
    show_service_config_args = {
        'endpoint_name': 'default',
        'resource_uri': resource_uri,
        'service_configuration_name': 'SSH'
    }
    serviceConfig = None
    try:
        serviceConfig = ShowServiceConfig(cli_ctx=cmd.cli_ctx)(command_args=show_service_config_args)
    except Exception:
        # If for some reason the request for Service Configuration fails,
        # we will still attempt to get relay information and connect. If the service configuration
        # is not setup correctly, the connection will fail.
        # The more likely scenario is that the request failed with a "Authorization Error",
        # in case the user isn't an owner/contributor.
        return None
    if port:
        return serviceConfig['port'] == int(port)
    else:
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
             raise azclierror.UnauthorizedError("Client is not authorized to create the default connectivity " +
                                               f"endpoint for \'{vm_name}\' in Resource Group \'{resource_group}\'. " +
                                               "This is a one-time operation that must be performed by someone with " +
                                               "Owner or Contributor role to allow connections to the target resource.",
                                               consts.RECOMMENDATION_FAILED_TO_CREATE_ENDPOINT)
        raise azclierror.UnclassifiedUserFault(f"Unable to create Default Endpoint for {vm_name} in {resource_group}."
                                               f"\nError: {str(e)}",
                                               consts.RECOMMENDATION_FAILED_TO_CREATE_ENDPOINT)
    except Exception as e:
        colorama.init()
        raise azclierror.UnclassifiedUserFault(f"Unable to create Default Endpoint for {vm_name} in {resource_group}."
                                               f"\nError: {str(e)}",
                                               consts.RECOMMENDATION_FAILED_TO_CREATE_ENDPOINT)
    
    return endpoint


def _create_service_configuration(cmd, resource_uri, port):
    from .aaz.latest.hybrid_connectivity.endpoint.service_configuration import Create as CreateServiceConfig
    if not port:
        port = '22'
    if not prompt_y_n(f"Current service configuration doesn't allow SSH connection to port {port}. Would you like to add it?") and port != '22':
        raise azclierror.ClientRequestError(f"No ssh permission for port {port}. If you want to connect to this port follow intructions on this doc: aka.ms/ssharc.")
            
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
             raise azclierror.UnauthorizedError("Client is not authorized to create a new service configuration " +
                                                f"to allow SSH connection to port {port} on default endpoint for " +
                                                f"\'{vm_name}\' in Resource Group \'{resource_group}\'. " +
                                                "This is a one-time operation that must be performed by someone " +
                                                "with Owner or Contributor role to allow SSH connections on a " +
                                                "specific port in the target resource.",
                                                consts.RECOMMENDATION_FAILED_TO_CREATE_ENDPOINT)
        
        raise azclierror.UnclassifiedUserFault(f"Unable to create Service Configuration for " +
                                               f"{vm_name} in {resource_group} to allow SSH connection to port {port}."
                                               f"\nError: {str(e)}",
                                               consts.RECOMMENDATION_FAILED_TO_CREATE_ENDPOINT)
    except:
        raise azclierror.UnclassifiedUserFault(f"Unable to create Service Configuration for " +
                                               f"{vm_name} in {resource_group} to allow SSH connection to port {port}."
                                               f"\nError: {str(e)}",
                                               consts.RECOMMENDATION_FAILED_TO_CREATE_ENDPOINT)
    return serviceConfig


def _list_credentials(cmd, resource_uri, certificate_validity_in_seconds):
    from .aaz.latest.hybrid_connectivity.endpoint import ListCredential

    list_cred_args = {
        'endpoint_name': 'default',
        'resource_uri': resource_uri,
        'expiresin':certificate_validity_in_seconds,
        'service_name': "SSH"
    }

    return ListCredential(cli_ctx=cmd.cli_ctx)(command_args=list_cred_args)  


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


def _handle_relay_connection_delay(cmd):
    # relay has retry delay after relay connection is lost
    # must sleep for at least as long as the delay
    # otherwise the ssh connection will fail
    progress_bar = cmd.cli_ctx.get_progress_controller(True)
    for x in range(0, consts.RELAY_CONNECTION_DELAY_IN_SECONDS + 1):
        interval = float(1/consts.RELAY_CONNECTION_DELAY_IN_SECONDS)
        progress_bar.add(message='Service configuration setup:',
                            value=interval * x, total_val=1.0)
        time.sleep(1)
    progress_bar.add(message='Service configuration setup: complete', 
                        value=1.0, total_val=1.0)
    progress_bar.end()
