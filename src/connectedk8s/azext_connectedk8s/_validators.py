# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import azext_connectedk8s._constants as consts


from os import name
from azure.cli.core.azclierror import ArgumentUsageError
from azure.cli.core.azclierror import (
    InvalidArgumentValueError,
    ArgumentUsageError
)
import re


def example_name_or_id_validator(cmd, namespace):
    # Example of a storage account name or ID validator.
    from azure.cli.core.commands.client_factory import get_subscription_id
    from msrestazure.tools import is_valid_resource_id, resource_id
    if namespace.storage_account:
        if not is_valid_resource_id(namespace.RESOURCE):
            namespace.storage_account = resource_id(
                subscription=get_subscription_id(cmd.cli_ctx),
                resource_group=namespace.resource_group_name,
                namespace='Microsoft.Storage',
                type='storageAccounts',
                name=namespace.storage_account
            )


def validate_private_link_properties(namespace):
    if not namespace.enable_private_link and namespace.private_link_scope_resource_id:
        raise ArgumentUsageError("Conflicting private link parameters received. The parameter \
            '--private-link-scope-resource-id' should not be set if '--enable-private-link' is passed as null or \
                False.")
    if namespace.enable_private_link is True and not namespace.private_link_scope_resource_id:
        raise ArgumentUsageError("The parameter '--private-link-scope-resource-id' was not provided. It is mandatory \
            to pass this parameter for enabling private link on the connected cluster resource.")


def override_client_request_id_header(cmd, namespace):
    if namespace.correlation_id is not None:
        cmd.cli_ctx.data['headers'][consts.Client_Request_Id_Header] = namespace.correlation_id
    else:
        cmd.cli_ctx.data['headers'][consts.Client_Request_Id_Header] = consts.Default_Onboarding_Source_Tracking_Guid


def validate_gateway_properties(namespace):
    if namespace.enable_gateway is False and namespace.gateway_resource_id != "":
        raise ArgumentUsageError("Conflicting gateway parameters received. The parameter '--gateway-resource-id' should not be set only if '--enable-gateway' is set to true.")
    if namespace.enable_gateway is True and namespace.gateway_resource_id != "":
        gateway_armid_pattern = r"^/subscriptions/[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}/resourceGroups/[a-zA-Z0-9_-]+/providers/Microsoft\.HybridCompute/gateways/[a-zA-Z0-9_-]+$"
        if not re.match(gateway_armid_pattern, namespace.gateway_resource_id):
            raise InvalidArgumentValueError(str.format(consts.Gateway_ArmId_Is_Invalid, namespace.gateway_resource_id))
    if namespace.enable_gateway is True and namespace.gateway_resource_id == "":
        raise ArgumentUsageError("The parameter '--gateway-resource-id' was not provided. It is mandatory to pass this parameter for enabling gateway on the connected cluster resource.")


def validate_gateway_updates(namespace):
    if namespace.enable_gateway and namespace.disable_gateway:
        raise ArgumentUsageError("Cannot specify both --enable-gateway and --disable-gateway simultaneously.")
    if namespace.enable_gateway and namespace.gateway_resource_id == "":
        raise ArgumentUsageError("The parameter '--gateway-resource-id' was not provided. It is mandatory to pass this parameter for enabling gateway on the connected cluster resource.")