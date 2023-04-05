# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import colorama

from azure.cli.core import telemetry
from azure.cli.core import azclierror
from knack import log

logger = log.get_logger(__name__)


# Send target OS type telemetry and check if authentication options are valid for that OS.
def handle_target_os_type(cmd, op_info):

    os_type = None

    if op_info.resource_type.lower() == "microsoft.compute/virtualmachines":
        os_type = _get_azure_vm_os(cmd, op_info.resource_group_name, op_info.vm_name)
    elif op_info.resource_type.lower() == "microsoft.hybridcompute/machines":
        os_type = _get_arc_server_os(cmd, op_info.resource_group_name, op_info.vm_name)
    elif op_info.resource_type.lower() == "microsoft.connectedvmwarevsphere/virtualmachines":
        os_type = _get_connected_vmware_os(cmd, op_info.resource_group_name, op_info.vm_name)

    if os_type:
        logger.debug("Target OS Type: %s", os_type)
        telemetry.add_extension_event('ssh', {'Context.Default.AzureCLI.TargetOSType': os_type})

    # Note 2: This is a temporary check while AAD login is not enabled for Windows.
    if os_type and os_type.lower() == 'windows' and not op_info.local_user:
        colorama.init()
        error_message = "SSH Login using AAD credentials is not currently supported for Windows."
        recommendation = colorama.Fore.YELLOW + "Please provide --local-user." + colorama.Style.RESET_ALL
        raise azclierror.RequiredArgumentMissingError(error_message, recommendation)


def _get_azure_vm_os(cmd, resource_group_name, vm_name):
    from azure.cli.core.commands import client_factory
    from azure.cli.core import profiles
    vm = None
    os_type = None
    # pylint: disable=broad-except
    try:
        compute_client = client_factory.get_mgmt_service_client(cmd.cli_ctx, profiles.ResourceType.MGMT_COMPUTE)
        vm = compute_client.virtual_machines.get(resource_group_name, vm_name)
    except Exception:
        return None

    if vm and vm.storage_profile and vm.storage_profile.os_disk and vm.storage_profile.os_disk.os_type:
        os_type = vm.storage_profile.os_disk.os_type

    return os_type


def _get_arc_server_os(cmd, resource_group_name, vm_name):
    from azext_ssh._client_factory import cf_machine
    client = cf_machine(cmd.cli_ctx)
    arc = None
    os_type = None
    # pylint: disable=broad-except
    try:
        arc = client.get(resource_group_name=resource_group_name, machine_name=vm_name)
    except Exception:
        return None

    if arc and arc.properties and arc.properties and arc.properties.os_name:
        os_type = arc.properties.os_name

    return os_type


def _get_connected_vmware_os(cmd, resource_group_name, vm_name):
    from azext_ssh._client_factory import cf_vmware
    client = cf_vmware(cmd.cli_ctx)
    vmware = None
    os_type = None
    # pylint: disable=broad-except
    try:
        vmware = client.get(resource_group_name=resource_group_name, virtual_machine_name=vm_name)
    except Exception:
        return None

    if vmware and vmware.os_profile and vmware.os_profile.os_type:
        os_type = vmware.os_profile.os_type

    return os_type
