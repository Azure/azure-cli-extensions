# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core import azclierror
from azure.cli.core.commands.client_factory import get_subscription_id
from msrestazure.tools import is_valid_resource_id, resource_id


def storage_account_name_or_id_validator(cmd, namespace):
    """
    Validator for storage account name or resource ID.
    Converts storage account name to full resource ID if needed.
    """
    if hasattr(namespace, 'storage_account') and namespace.storage_account:
        if not is_valid_resource_id(namespace.storage_account):
            if not hasattr(namespace, 'resource_group_name') or not namespace.resource_group_name:
                raise azclierror.RequiredArgumentMissingError(
                    "When providing storage account name, --resource-group is required. "
                    "Alternatively, provide the full resource ID."
                )
            namespace.storage_account = resource_id(
                subscription=get_subscription_id(cmd.cli_ctx),
                resource_group=namespace.resource_group_name,
                namespace='Microsoft.Storage',
                type='storageAccounts',
                name=namespace.storage_account
            )
