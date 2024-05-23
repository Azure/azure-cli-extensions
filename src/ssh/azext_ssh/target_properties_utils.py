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

    # Properties for the target machine
    os_type = None
    agent_version = None
    tags = None

    # Calls the appropriate function based on resource type to get the OS type and tags of the target machine
    if op_info.resource_type.lower() == "microsoft.compute/virtualmachines":
        os_type, tags = _get_azure_vm_properties(cmd, op_info.resource_group_name, op_info.vm_name)
    elif op_info.resource_type.lower() == "microsoft.hybridcompute/machines":
        os_type, agent_version, tags = _get_arc_server_properties(cmd, op_info.resource_group_name, op_info.vm_name)
    elif op_info.resource_type.lower() == "microsoft.connectedvmwarevsphere/virtualmachines":
        os_type, agent_version, tags = _get_connected_vmware_properties(cmd, op_info.resource_group_name, op_info.vm_name)

    check_valid_os_type(os_type, agent_version, op_info)
    op_info.set_azure_resource_tags(tags)
    return

# This function is used to get the properties needed from an Azure VM 
def _get_azure_vm_properties(cmd, resource_group_name, vm_name):
    from azure.cli.core.commands import client_factory
    from azure.cli.core import profiles

    vm = None
    os_type = None
    tags = None

    # pylint: disable=broad-except
    try:
        # Retrieves the VM object \\
        compute_client = client_factory.get_mgmt_service_client(cmd.cli_ctx, profiles.ResourceType.MGMT_COMPUTE)
        vm = compute_client.virtual_machines.get(resource_group_name, vm_name)
    except Exception:
        return None

    if vm and vm.storage_profile and vm.storage_profile.os_disk and vm.storage_profile.os_disk.os_type:
        os_type = vm.storage_profile.os_disk.os_type
    if vm and vm.tags:
        tags = vm.tags

    return os_type, tags


# This function is used to get the properties needed needed from an Azure Arc Server
def _get_arc_server_properties(cmd, resource_group_name, vm_name):
    from .aaz.latest.hybrid_compute.machine import Show as ArcServerShow

    arc_server = None
    os_type = None
    agent_version = None
    tags = None

    get_args = {
        'resource_group': resource_group_name,
        'machine_name': vm_name
    }
    # pylint: disable=broad-except
    try:
        # Retrieves the Arc Server object
        arc_server = ArcServerShow(cli_ctx=cmd.cli_ctx)(command_args=get_args)
    except Exception:
        return None, None

    if arc_server and arc_server.get('osName', None):
        os_type = arc_server.get('osName')
    elif arc_server and arc_server.get('properties', None):
        os_type = arc_server.get('properties').get('osType', None)

    if arc_server and arc_server.get('properties'):
        agent_version = arc_server.get('properties').get('agentVersion')

    if arc_server and arc_server.get('tags', None):
        tags = arc_server.get('tags')

    return os_type, agent_version, tags

# This function is used to get the properties needed from a Connected VMware VM
def _get_connected_vmware_properties(cmd, resource_group_name, vm_name):
    from .aaz.latest.connected_v_mwarev_sphere.virtual_machine import Show as VMwarevSphereShow

    vmware = None
    os_type = None
    agent_version = None
    tags = None
    
    get_args = {
        'resource_group': resource_group_name,
        'virtual_machine_name': vm_name
    }
    # pylint: disable=broad-except
    try:
        # Retrieves the Connected VMware VM object
        vmware = VMwarevSphereShow(cli_ctx=cmd.cli_ctx)(command_args=get_args)
    except Exception:
        return None, None

    if vmware and vmware.get("osProfile") and vmware.get("osProfile").get("osType"):
        os_type = vmware.get("osProfile").get("osType")

    if vmware and vmware.get("properties") and vmware.get("properties").get('guestAgentProfile') and\
       vmware.get("properties").get('guestAgentProfile').get('agentVersion'):
        agent_version = vmware.get("properties").get('guestAgentProfile').get('agentVersion')

    if vmware and vmware.get("tags"):
        tags = vmware.get('tags')

    return os_type, agent_version, tags


# This function is used to check if the OS type is valid and if the authentication options are valid for that OS
def check_valid_os_type(os_type, agent_version, op_info):
    if os_type:
        logger.debug("Target OS Type: %s", os_type)
        telemetry.add_extension_event('ssh', {'Context.Default.AzureCLI.TargetOSType': os_type})

    if os_type and os_type.lower() == 'windows' and not op_info.local_user:
        colorama.init()
        error_message = "SSH Login using AAD credentials is not currently supported for Windows."
        recommendation = colorama.Fore.YELLOW + "Please provide --local-user." + colorama.Style.RESET_ALL
        raise azclierror.RequiredArgumentMissingError(error_message, recommendation)

    if op_info.is_arc() and agent_version:
        try:
            major, minor, _, _ = agent_version.split('.', 4)
            if int(major) < const.AGENT_MINIMUM_VERSION_MAJOR or int(minor) < const.AGENT_MINIMUM_VERSION_MINOR:
                logger.warning("The version of the Arc Agent, %s running on the target machine "
                            "is not compatible with this version of the ssh extension. "
                            "Please update to the latest version.", agent_version)
        except Exception:
            return
    return