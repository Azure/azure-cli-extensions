# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import colorama

from azure.cli.core import telemetry
from azure.cli.core import azclierror
from knack import log
from . import constants as const

logger = log.get_logger(__name__)


# Send target OS type telemetry and check if authentication options are valid for that OS.
def handle_target_machine_properties(cmd, op_info):

    properties = get_properties(cmd, op_info.resource_type.lower(), op_info.resource_group_name, op_info.vm_name)
    if properties:
        os_type = parse_os_type(properties, op_info.resource_type.lower())
        agent_version = parse_agent_version(properties, op_info.resource_type.lower())
    else:
        os_type, agent_version = None, None
    check_valid_os_type(os_type, op_info)
    check_valid_agent_version(agent_version, op_info)


def get_properties(cmd, resource_type, resource_group_name, vm_name):
    if resource_type == "microsoft.compute/virtualmachines":
        return _request_azure_vm_properties(cmd, resource_group_name, vm_name)
    if resource_type == "microsoft.hybridcompute/machines":
        return _request_arc_server_properties(cmd, resource_group_name, vm_name)
    if resource_type == "microsoft.connectedvmwarevsphere/virtualmachines":
        return _request_connected_vmware_properties(cmd, resource_group_name, vm_name)


# This function is used to get the properties needed from an Azure VM
def _request_azure_vm_properties(cmd, resource_group_name, vm_name):
    from azure.cli.core.commands import client_factory
    from azure.cli.core import profiles
    # pylint: disable=broad-except
    try:
        # Retrieves the VM object \\
        compute_client = client_factory.get_mgmt_service_client(cmd.cli_ctx, profiles.ResourceType.MGMT_COMPUTE)
        return compute_client.virtual_machines.get(resource_group_name, vm_name)
    except Exception:
        return None


# This function is used to get the properties needed needed from an Azure Arc Server
def _request_arc_server_properties(cmd, resource_group_name, vm_name):
    from .aaz.latest.hybrid_compute.machine import Show as ArcServerShow
    # pylint: disable=broad-except
    try:
        get_args = {'resource_group': resource_group_name, 'machine_name': vm_name}
        # Retrieves the Arc Server object
        return ArcServerShow(cli_ctx=cmd.cli_ctx)(command_args=get_args)
    except Exception:
        return None


# This function is used to get the properties needed from a Connected VMware VM
def _request_connected_vmware_properties(cmd, resource_group_name, vm_name):
    from .aaz.latest.connected_v_mwarev_sphere.virtual_machine import Show as VMwarevSphereShow

    # pylint: disable=broad-except
    try:
        get_args = {'resource_group': resource_group_name, 'machine_name': vm_name}
        # Retrieves the Connected VMware VM object
        return VMwarevSphereShow(cli_ctx=cmd.cli_ctx)(command_args=get_args)
    except Exception:
        return None


def parse_os_type(properties, resource_type):
    if resource_type == "microsoft.compute/virtualmachines":
        if (properties.storage_profile and properties.storage_profile.os_disk and
                properties.storage_profile.os_disk.os_type):

            return properties.storage_profile.os_disk.os_type

    elif resource_type == "microsoft.hybridcompute/machines":
        if properties.get('osName', None):
            return properties.get('osName')
        if properties.get('properties', None):
            return properties.get('properties').get('osType', None)

    elif resource_type == "microsoft.connectedvmwarevsphere/virtualmachines":
        if properties.get("osProfile") and properties.get("osProfile").get("osType"):
            return properties.get("osProfile").get("osType")


def parse_agent_version(properties, resource_type):
    if resource_type == "microsoft.compute/virtualmachines":
        return None

    if resource_type == "microsoft.hybridcompute/machines":
        if properties.get('properties'):
            return properties.get('properties').get('agentVersion')

    if resource_type == "microsoft.connectedvmwarevsphere/virtualmachines":
        if properties.get("properties") and properties.get("properties").get('guestAgentProfile') and\
                properties.get("properties").get('guestAgentProfile').get('agentVersion'):

            return properties.get("properties").get('guestAgentProfile').get('agentVersion')


# This function is used to check if the OS type is valid and if the authentication options are valid for that OS
def check_valid_os_type(os_type, op_info):
    if os_type:
        logger.debug("Target OS Type: %s", os_type)
        telemetry.add_extension_event('ssh', {'Context.Default.AzureCLI.TargetOSType': os_type})

    if os_type and os_type.lower() == 'windows' and not op_info.local_user:
        colorama.init()
        error_message = "SSH Login using AAD credentials is not currently supported for Windows."
        recommendation = colorama.Fore.YELLOW + "Please provide --local-user." + colorama.Style.RESET_ALL
        raise azclierror.RequiredArgumentMissingError(error_message, recommendation)


def check_valid_agent_version(agent_version, op_info):
    # pylint: disable=broad-except
    if op_info.is_arc() and agent_version:
        try:
            major, minor, _, _ = agent_version.split('.', 4)
            if int(major) < const.AGENT_MINIMUM_VERSION_MAJOR or int(minor) < const.AGENT_MINIMUM_VERSION_MINOR:
                logger.warning(
                    "The version of the Arc Agent, %s running on the target machine "
                    "is not compatible with this version of the ssh extension. "
                    "Please update to the latest version.", agent_version
                )
        except Exception:
            return
