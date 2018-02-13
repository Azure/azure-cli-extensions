# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long

from azure.cli.core.commands import CliCommandType
from ._client_factory import management_groups_client_factory, management_group_subscriptions_client_factory
from ._exception_handler import managementgroups_exception_handler


def load_command_table(self, _):

    managementgroups_sdk = CliCommandType(
        operations_tmpl='azext_managementgroups.managementgroups.operations.management_groups_operations#ManagementGroupsOperations.{}',
        client_factory=management_groups_client_factory,
        exception_handler=managementgroups_exception_handler)

    managementgroups_subscriptions_sdk = CliCommandType(
        operations_tmpl='azext_managementgroups.managementgroups.operations.management_group_subscriptions_operations#ManagementGroupSubscriptionsOperations.{}',
        client_factory=management_group_subscriptions_client_factory,
        exception_handler=managementgroups_exception_handler)

    managementgroups_update_type = CliCommandType(
        operations_tmpl='azext_managementgroups.custom#{}',
        client_factory=management_group_subscriptions_client_factory,
        exception_handler=managementgroups_exception_handler)

    with self.command_group('account management-group', managementgroups_sdk) as g:
        g.custom_command('list', 'cli_managementgroups_group_list')
        g.custom_command('show', 'cli_managementgroups_group_show')
        g.custom_command('create', 'cli_managementgroups_group_create')
        g.custom_command('delete', 'cli_managementgroups_group_delete')
        g.generic_update_command(
            'update',
            getter_name='cli_managementgroups_group_update_get',
            getter_type=managementgroups_update_type,
            setter_name='cli_managementgroups_group_update_set',
            setter_type=managementgroups_update_type,
            custom_func_name='cli_managementgroups_group_update_custom_func',
            custom_func_type=managementgroups_update_type,
            exception_handler=managementgroups_exception_handler)

    with self.command_group('account management-group subscription', managementgroups_subscriptions_sdk, client_factory=management_group_subscriptions_client_factory) as g:
        g.custom_command('add', 'cli_managementgroups_subscription_add')
        g.custom_command('remove', 'cli_managementgroups_subscription_remove')
