# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import colorama

from knack import log
from azure.cli.core import telemetry, azclierror
from azure.mgmt.resource import ResourceManagementClient
from azure.cli.core.commands.client_factory import get_mgmt_service_client

from . import constants as consts

logger = log.get_logger(__name__)


def _list_types_of_resources_with_provided_name(cmd, op_info):
    resource_client = get_mgmt_service_client(cmd.cli_ctx, ResourceManagementClient)
    resources = resource_client.resources.list_by_resource_group(
        op_info.resource_group_name,
        filter=f"name eq '{op_info.vm_name}'")
    resource_types_present = set()

    while True:
        try:
            resource = resources.next()
            if resource.type.lower() in consts.SUPPORTED_RESOURCE_TYPES:
                resource_types_present.add(resource.type.lower())
        except StopIteration:
            break

    return resource_types_present


def decide_resource_type(cmd, op_info):

    # If the user provides an IP address the target will be treated as an Azure VM even if it is an
    # Arc Server. Which just means that the Connectivity Proxy won't be used to establish connection.
    if op_info.ip:
        return "Microsoft.Compute/virtualMachines"

    # Set of resource types in target resource group of resources that match vm_name
    types_in_rg = _list_types_of_resources_with_provided_name(cmd, op_info)
    target_resource_type = None

    if op_info.resource_type and op_info.resource_type != consts.ARC_RESOURCE_TYPE_PLACEHOLDER:
        if op_info.resource_type.lower() in consts.LEGACY_SUPPORTED_RESOURCE_TYPES:
            op_info.resource_type = consts.RESOURCE_PROVIDER_TO_RESOURCE_TYPE[op_info.resource_type.lower()]
        if op_info.resource_type.lower() in types_in_rg:
            target_resource_type = consts.RESOURCE_TYPE_LOWER_CASE_TO_CORRECT_CASE[op_info.resource_type.lower()]
        else:
            raise azclierror.ResourceNotFoundError(
                f"Unable to find resource {op_info.vm_name} of type "
                f"{consts.RESOURCE_TYPE_LOWER_CASE_TO_CORRECT_CASE[op_info.resource_type.lower()]} "
                f"under the resource group {op_info.resource_group_name}",
                consts.RECOMMENDATION_RESOURCE_NOT_FOUND)

    else:
        if op_info.resource_type == consts.ARC_RESOURCE_TYPE_PLACEHOLDER:
            types_in_rg.discard("microsoft.compute/virtualmachines")

        if len(types_in_rg) > 1:
            raise azclierror.BadRequestError(f"{op_info.resource_group_name} has more than one valid target with the "
                                             f"same name: {op_info.vm_name}.",
                                             colorama.Fore.YELLOW + "Please provide a --resource-type." +
                                             colorama.Style.RESET_ALL)

        if len(types_in_rg) < 1:
            raise azclierror.ResourceNotFoundError(f"A valid resource {op_info.vm_name} in the resource group "
                                                   f"{op_info.resource_group_name} was not found. ",
                                                   consts.RECOMMENDATION_RESOURCE_NOT_FOUND)

        target_resource_type = consts.RESOURCE_TYPE_LOWER_CASE_TO_CORRECT_CASE[types_in_rg.pop().lower()]

    telemetry.add_extension_event('ssh', {'Context.Default.AzureCLI.TargetResourceType': target_resource_type})
    logger.debug("Target Resource Type: %s", target_resource_type)
    return target_resource_type
