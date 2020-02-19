# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


def example_name_or_id_validator(cmd, namespace):
    from azure.cli.core.commands.client_factory import get_subscription_id
    from msrestazure.tools import is_valid_resource_id, resource_id
    if namespace.storage_account:
        if not is_valid_resource_id(namespace.RESOURCE):
            namespace.storage_account = resource_id(
                subscription=get_subscription_id(cmd.cli_ctx),
                resource_group=namespace.resource_group_name,
                namespace='Microsoft.Storage',
                type='storageAccounts',
                name=namespace.storage_account)


def parse_managed_resource_group(cmd, namespace):
    """Parse managed resource_group which can be either resource group name or id"""
    from msrestazure.tools import is_valid_resource_id
    from azure.cli.core.commands.client_factory import get_subscription_id

    if namespace.managed_resource_group and not is_valid_resource_id(
            namespace.managed_resource_group):
        namespace.managed_resource_group = '/subscriptions/' + get_subscription_id(
            cmd.cli_ctx) + '/resourceGroups/' + namespace.managed_resource_group
