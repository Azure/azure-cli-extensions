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
    
    # TO DO:
    # A lot of the functions for getting the relay information are written down here, 
    # but we need to make it work.
    # What I think it's the best way to handle retrieving the relay information is the following steps:

    # - Call list credential
    #   - if it throws a resource not found that means the endpoint doesn't exist
    #       - create endpoint (fail if user is not owner/contributor)
    #       - create service config (fail is user is not owner/contributor, prompt user for confirmation)
    #       - call list credential again
    #   - if it throws a "precondition failed" that means the service config doesn't exist
    #       - create service config (fail is user is not owner/contributor, prompt user for confirmation)
    #       - call list credential again
    #   - list credential call suceeds
    #       - ensure that the provided port matches the allowed port in service configuration
    #           - if it doesn't prompt user for confirmation if they want to repair the port
    #           - if it does, return credential

    # This is just how I think it's the best way to do this. I've been trying to figure out the best way to 
    # minimize calls to the ACRP. If you think of a better way to do this feel free to try it.

def _check_and_fix_service_configuration(cmd, resource_uri, port):
    from .aaz.latest.hybrid_connectivity.endpoint.service_configuration import Show as ShowServiceConfig
    show_service_config_args = {
        'endpoint_name': 'default',
        'resource_uri': resource_uri,
        'service_configuration_name': 'SSH'
    }
    serviceConfig = None
    try:
        serviceConfig = ShowServiceConfig(cli_ctx=cmd.cli_ctx)(command_args=show_service_config_args)
    except ResourceNotFoundError:
        _get_or_create_endpoint(cmd, resource_uri)
        serviceConfig = _create_service_configuration(cmd, resource_uri, port)
    except Exception:
        # If for some reason the request for Service Configuration fails,
        # we will still attempt to get relay information and connect. If the service configuration
        # is not setup correctly, the connection will fail.
        # The more likely scenario is that the request failed with a "Authorization Error",
        # in case the user isn't an owner/contributor.
        return
    
    #if serviceConfig['port'] != int(port):
    #    raise azclierror.ForbiddenError(f"The provided port {port} is not configured to allow SSH connections.",
    #                                    consts.RECOMMENDATION_FAILED_TO_CREATE_ENDPOINT)
    #check if SSH configuration matches port
    #if it doesn't match port, offer to fix it


def _get_or_create_endpoint(cmd, resource_uri):
    from .aaz.latest.hybrid_connectivity.endpoint import Show as ShowEndpoint
    show_endpoint_args = {
        'endpoint_name': 'default',
        'resource_uri': resource_uri,
    }
    try:
        ShowEndpoint(cli_ctx=cmd.cli_ctx)(command_args=show_endpoint_args)
    except ResourceNotFoundError:
        _create_default_endpoint(cmd, resource_uri)
    except Exception as e:
        # if for some reason the request for endpoint fails, we will still try to move
        # forward. 
        return


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
    if port != '22' and not prompt_y_n(f"Current service configuration doesn't allow SSH connection to port {port}. Would you like to add it?"):
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

def _list_cretendials(cmd, resource_uri, certificate_validity_in_seconds):
    from .aaz.latest.hybrid_connectivity.endpoint import ListCredential

    list_cred_args = {
        'endpoint_name': 'default',
        'resource_uri': resource_uri,
        'expiresin':certificate_validity_in_seconds,
        'service_name': "SSH"
    }

    ListCredential(cli_ctx=cmd.cli_ctx)(command_args=list_cred_args)  

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
    # Add service config token to formated string
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
