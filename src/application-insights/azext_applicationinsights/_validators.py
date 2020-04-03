# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=len-as-condition
from knack.util import CLIError
from msrestazure.tools import is_valid_resource_id


def validate_applications(namespace):
    if namespace.resource_group_name:
        if isinstance(namespace.application, list):
            if len(namespace.application) == 1:
                if is_valid_resource_id(namespace.application[0]):
                    raise CLIError("Specify either a full resource id or an application name and resource group.")
            else:
                raise CLIError("Resource group only allowed with a single application name.")


def validate_storage_account_name_or_id(cmd, namespace):
    if namespace.storage_account_id:
        from msrestazure.tools import resource_id
        from azure.cli.core.commands.client_factory import get_subscription_id
        if not is_valid_resource_id(namespace.storage_account_id):
            namespace.storage_account_id = resource_id(
                subscription=get_subscription_id(cmd.cli_ctx),
                resource_group=namespace.resource_group_name,
                namespace='Microsoft.Storage',
                type='storageAccounts',
                name=namespace.storage_account_id
            )


def validate_log_analytic_workspace_name_or_id(cmd, namespace):
    if namespace.workspace_resource_id:
        from msrestazure.tools import resource_id
        from azure.cli.core.commands.client_factory import get_subscription_id
        if not is_valid_resource_id(namespace.workspace_resource_id):
            namespace.workspace_resource_id = resource_id(
                subscription=get_subscription_id(cmd.cli_ctx),
                resource_group=namespace.resource_group_name,
                namespace='microsoft.OperationalInsights',
                type='workspaces',
                name=namespace.workspace_resource_id
            )
