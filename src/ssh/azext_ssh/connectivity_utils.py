# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import time
import os
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


# Downloads client side proxy to connect to Arc Connectivity Platform
def install_client_side_proxy(arc_proxy_folder):

    client_operating_system = _get_client_operating_system()
    client_architecture = _get_client_architeture()
    install_dir = _get_proxy_install_dir(arc_proxy_folder)
    proxy_name = _get_proxy_filename(client_operating_system, client_architecture)
    install_location = os.path.join(install_dir, proxy_name)

    # Only download new proxy if it doesn't exist already
    if not os.path.isfile(install_location):
        if not os.path.isdir(install_dir):
            file_utils.create_directory(install_dir, f"Failed to create client proxy directory '{install_dir}'.")
        # if directory exists, delete any older versions of the proxy
        else:
            older_version_location = _get_older_version_proxy_path(
                install_dir,
                client_operating_system,
                client_architecture)
            older_version_files = glob(older_version_location)
            for f in older_version_files:
                file_utils.delete_file(f, f"failed to delete older version file {f}", warning=True)

        _download_proxy_from_MCR(install_dir, proxy_name, client_operating_system, client_architecture)
        _check_proxy_installation(install_dir, proxy_name)

    return install_location


def _download_proxy_from_MCR(dest_dir, proxy_name, operating_system, architecture):
    mar_target = f"{consts.CLIENT_PROXY_MCR_TARGET}/{operating_system.lower()}/{architecture}/ssh-proxy"
    logger.debug("Downloading Arc Connectivity Proxy from %s in Microsoft Artifact Regristy.", mar_target)

    client = oras.client.OrasClient()
    t0 = time.time()

    try:
        response = client.pull(target=f"{mar_target}:{consts.CLIENT_PROXY_VERSION}", outdir=dest_dir)
    except Exception as e:
        raise azclierror.CLIInternalError(
            f"Failed to download Arc Connectivity proxy with error {str(e)}. Please try again.")

    time_elapsed = time.time() - t0

    proxy_data = {
        'Context.Default.AzureCLI.SSHProxyDownloadTime': time_elapsed,
        'Context.Default.AzureCLI.SSHProxyVersion': consts.CLIENT_PROXY_VERSION
    }
    telemetry.add_extension_event('ssh', proxy_data)

    proxy_package_path = _get_proxy_package_path_from_oras_response(response)
    _extract_proxy_tar_files(proxy_package_path, dest_dir, proxy_name)
    file_utils.delete_file(proxy_package_path, f"Failed to delete {proxy_package_path}. Please delete manually.", True)


def _get_proxy_package_path_from_oras_response(pull_response):
    if not isinstance(pull_response, list):
        raise azclierror.CLIInternalError(
            "Attempt to download Arc Connectivity Proxy returned unnexpected result. Please try again.")

    if len(pull_response) != 1:
        for r in pull_response:
            file_utils.delete_file(r, f"Failed to delete {r}. Please delete it manually.", True)
        raise azclierror.CLIInternalError(
            "Attempt to download Arc Connectivity Proxy returned unnexpected result. Please try again.")

    proxy_package_path = pull_response[0]

    if not os.path.isfile(proxy_package_path):
        raise azclierror.CLIInternalError("Unable to download Arc Connectivity Proxy. Please try again.")

    logger.debug("Proxy package downloaded to %s", proxy_package_path)

    return proxy_package_path


def _extract_proxy_tar_files(proxy_package_path, install_dir, proxy_name):
    with tarfile.open(proxy_package_path, 'r:gz') as tar:
        members = []
        for member in tar.getmembers():
            if member.isfile():
                filenames = member.name.split('/')

                if len(filenames) != 2:
                    tar.close()
                    file_utils.delete_file(
                        proxy_package_path,
                        f"Failed to delete {proxy_package_path}. Please delete it manually.",
                        True)
                    raise azclierror.CLIInternalError(
                        "Attempt to download Arc Connectivity Proxy returned unnexpected result. Please try again.")

                member.name = filenames[1]

                if member.name.startswith('sshproxy'):
                    member.name = proxy_name
                elif member.name.lower() not in ['license.txt', 'thirdpartynotice.txt']:
                    tar.close()
                    file_utils.delete_file(
                        proxy_package_path,
                        f"Failed to delete {proxy_package_path}. Please delete it manually.",
                        True)
                    raise azclierror.CLIInternalError(
                        "Attempt to download Arc Connectivity Proxy returned unnexpected result. Please try again.")

                members.append(member)

        tar.extractall(members=members, path=install_dir)


def _check_proxy_installation(install_dir, proxy_name):
    proxy_filepath = os.path.join(install_dir, proxy_name)
    if os.path.isfile(proxy_filepath):
        print_styled_text((Style.SUCCESS, f"Successfuly installed SSH Connectivity Proxy file {proxy_filepath}"))
    else:
        raise azclierror.CLIInternalError(
            "Failed to install required SSH Arc Connectivity Proxy. "
            f"Couldn't find expected file {proxy_filepath}. Please try again.")

    license_files = ["LICENSE.txt", "ThirdPartyNotice.txt"]
    for file in license_files:
        file_location = os.path.join(install_dir, file)
        if os.path.isfile(file_location):
            print_styled_text(
                (Style.SUCCESS,
                 f"Successfuly installed SSH Connectivity Proxy License file {file_location}"))
        else:
            logger.warning(
                "Failed to download Arc Connectivity Proxy license file %s. Clouldn't find expected file %s. "
                "This won't affect your connection.", file, file_location)


def _get_proxy_filename(operating_system, architecture):
    if operating_system.lower() == 'darwin' and architecture == '386':
        raise azclierror.BadRequestError("Unsupported Darwin OS with 386 architecture.")
    proxy_filename = \
        f"sshProxy_{operating_system.lower()}_{architecture}_{consts.CLIENT_PROXY_VERSION.replace('.', '_')}"
    if operating_system.lower() == 'windows':
        proxy_filename += '.exe'
    return proxy_filename


def _get_older_version_proxy_path(install_dir, operating_system, architecture):
    proxy_name = f"sshProxy_{operating_system.lower()}_{architecture}_*"
    return os.path.join(install_dir, proxy_name)


def _get_proxy_install_dir(arc_proxy_folder):
    if not arc_proxy_folder:
        return os.path.expanduser(os.path.join('~', ".clientsshproxy"))
    return arc_proxy_folder


def _get_client_architeture():
    import platform
    machine = platform.machine()
    architecture = None

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

    return architecture


def _get_client_operating_system():
    import platform
    operating_system = platform.system()

    logger.debug("Platform OS: %s", operating_system)

    if operating_system.lower() not in ('linux', 'darwin', 'windows'):
        raise azclierror.BadRequestError(f"Unsuported OS: {operating_system} platform is not currently supported")
    return operating_system
