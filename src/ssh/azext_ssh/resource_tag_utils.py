# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core import azclierror
from knack import log

logger = log.get_logger(__name__)
# Checking Port and Resource Tag argument and fetching appropiate tag


def _handle_os_type_for_tag(cmd, op_info):
    tags = {}
    server_error = False

    # Warning about two parameters for port (Port, Resource Tag)
    if op_info.port and op_info.resource_tag:
        logger.warning("Warning: Both --port and --resource-tag arguments were specified."
                            "The --port option will take precedence and the --resource-tag will be ignored."
                            "To use the port number from the --resource-tag, please omit the --port argument.")
        return
    # Only port is specified, use port
    if op_info.port:
        return
    # Retrieving machine's resource tags
    if op_info.resource_type.lower() == "microsoft.compute/virtualmachines":
        tags, server_error = _check_azure_vm_tag(cmd, op_info.resource_group_name, op_info.vm_name, tags)
    elif op_info.resource_type.lower() == "microsoft.hybridcompute/machines":
        tags, server_error = _check_arc_server_tag(cmd, op_info.resource_group_name, op_info.vm_name, tags)
    elif op_info.resource_type.lower() == "microsoft.connectedvmwarevsphere/virtualmachines":
        tags, server_error = _check_connected_vmware_tag(cmd, op_info.resource_group_name, op_info.vm_name, tags)

    if server_error:
        logger.warning("Failed to retrieve resource tags from the server. Using default port 22.")
        op_info.port = "22"
        return
    # Checking for proper Resource Tag configurations
    def validate_and_set_port(tag_name="SSHPort"):
        port_num = tags.get(tag_name)
        if port_num and port_num.isdigit() and int(port_num) < 65535:
            op_info.port = port_num

        else:
            raise azclierror.InvalidArgumentValueError(
                f"Port '{port_num}' from resource tag '{tag_name}' was used for this command. "
                "If this is incorrect, use the --port parameter or contact your administrator to correct the resource tag value. "
                "Port numbers must not be empty, must not contain letters or special characters, and cannot exceed 65535.")
    # Checking if there is a specified resource tag
    if op_info.resource_tag:
        if op_info.resource_tag in tags:
            validate_and_set_port(op_info.resource_tag)
        else:
            raise azclierror.InvalidArgumentValueError(
                f"Resource tag name '{op_info.resource_tag}' cannot be found. Contact your administrator to ensure the tag is valid."
            )
    # Checking if there is a SSHPort Tag for default checking, else default port
    elif "SSHPort" in tags:
        validate_and_set_port("SSHPort")
    return

def _check_azure_vm_tag(cmd, resource_group_name, vm_name, tags):
    from azure.cli.core.commands import client_factory
    from azure.cli.core import profiles
    try:
        compute_client = client_factory.get_mgmt_service_client(cmd.cli_ctx, profiles.ResourceType.MGMT_COMPUTE)
        vm = compute_client.virtual_machines.get(resource_group_name, vm_name)
    except Exception:
        return {}, True    
    if vm and vm.tags:
        tags = vm.tags
    return tags, False


def _check_arc_server_tag(cmd, resource_group_name, vm_name, tags):
    from .aaz.latest.hybrid_compute.machine import Show as ArcServerShow
    get_args = {
    'resource_group': resource_group_name,
    'machine_name': vm_name
    }
    # pylint: disable=broad-except
    try:
        arc_server = ArcServerShow(cli_ctx=cmd.cli_ctx)(command_args=get_args)
    except Exception:
        return {}, True

    # Parsing Logic
    if arc_server and arc_server.get('tags', None):
        tags = arc_server.get('tags')
    return tags, False


def _check_connected_vmware_tag(cmd, resource_group_name, vm_name, tags):
    from .aaz.latest.connected_v_mwarev_sphere.virtual_machine import Show as VMwarevSphereShow
    get_args = {
        'resource_group': resource_group_name,
        'virtual_machine_name': vm_name
    }
    # pylint: disable=broad-except
    try:
        vmware = VMwarevSphereShow(cli_ctx=cmd.cli_ctx)(command_args=get_args)
    except Exception:
        return {}, True

    if vmware and vmware.get("tags"):
        tags = vmware.get('tags')
    return tags, False
