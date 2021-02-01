# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.util import CLIError
from azure.cli.core import telemetry
from pkg_resources import parse_version 
import azext_connectedk8s._constants as consts


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

def validate_enable_azure_rbac(k8s_version, guard_client_id, guard_client_secret):
    if parse_version(k8s_version) < parse_version("1.17.0"):
        telemetry.set_exception(fault_type=consts.Enable_Azure_RBAC_Not_Supported_Fault_Type,
                            summary='Enabling Azure RBAC is supported for versions less that 1.17')
        raise CLIError(consts.Enable_Azure_RBAC_Not_Supported_Error)
    if (guard_client_id is None) or (guard_client_secret is None):
        telemetry.set_exception(fault_type=consts.Insufficient_Args_Fault_Type,
                            summary='insufficient args with azure rbac')
        raise CLIError(str.format(consts.Insufficient_Args_Fault_Error, "--client-id, --client-secret", "--enable-azure-arc"))