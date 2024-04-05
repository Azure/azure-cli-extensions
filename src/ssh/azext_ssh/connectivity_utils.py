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

        _download_proxy_license(arc_proxy_folder)

    return install_location


def _get_proxy_filename_and_url(arc_proxy_folder):
    import platform
    operating_system = platform.system()
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

    # define the request url and install location based on the os and architecture.
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


def _download_proxy_license(proxy_dir):
    if not proxy_dir:
        proxy_dir = os.path.join('~', ".clientsshproxy")
    license_uri = f"{consts.CLIENT_PROXY_STORAGE_URL}/{consts.CLIENT_PROXY_RELEASE}/LICENSE.txt"
    license_install_location = os.path.expanduser(os.path.join(proxy_dir, "LICENSE.txt"))

    notice_uri = f"{consts.CLIENT_PROXY_STORAGE_URL}/{consts.CLIENT_PROXY_RELEASE}/ThirdPartyNotice.txt"
    notice_install_location = os.path.expanduser(os.path.join(proxy_dir, "ThirdPartyNotice.txt"))

    _get_and_write_proxy_license_files(license_uri, license_install_location, "License")
    _get_and_write_proxy_license_files(notice_uri, notice_install_location, "Third Party Notice")


def _get_and_write_proxy_license_files(uri, install_location, target_name):
    try:
        license_content = _download_from_uri(uri)
        file_utils.write_to_file(file_path=install_location,
                                 mode='wb',
                                 content=license_content,
                                 error_message=f"Failed to create {target_name} file at {install_location}.")
    # pylint: disable=broad-except
    except Exception:
        logger.warning("Failed to download Connection Proxy %s file from %s.", target_name, uri)

    print_styled_text((Style.SUCCESS, f"SSH Connection Proxy {target_name} saved to {install_location}."))


def _download_from_uri(request_uri):
    response_content = None
    with urllib.request.urlopen(request_uri) as response:
        response_content = response.read()
        response.close()

    if response_content is None:
        raise azclierror.ClientRequestError(f"Failed to download file from {request_uri}")

    return response_content


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
