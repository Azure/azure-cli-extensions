# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long
# pylint: disable=too-many-lines
# pylint: disable=too-many-statements
# pylint: disable=too-many-locals
from azure.cli.core.commands import CliCommandType


def load_command_table(self, _):

    from ._client_factory import cf_subscriptions
    account_subscriptions = CliCommandType(
        operations_tmpl='azext_account.vendored_sdks.subscription.operations._subscriptions_operations#SubscriptionsOperations.{}',
        client_factory=cf_subscriptions)
    with self.command_group('account subscriptions', account_subscriptions, client_factory=cf_subscriptions) as g:
        g.custom_command('list', 'account_subscriptions_list')
        g.custom_show_command('show', 'account_subscriptions_show')
        g.custom_command('rename', 'account_subscriptions_rename')
        g.custom_command('cancel', 'account_subscriptions_cancel')
        g.custom_command('enable', 'account_subscriptions_enable')

    from ._client_factory import cf_subscription_operation
    account_subscription_operation = CliCommandType(
        operations_tmpl='azext_account.vendored_sdks.subscription.operations._subscription_operation_operations#SubscriptionOperationOperations.{}',
        client_factory=cf_subscription_operation)
    with self.command_group('account subscription_operation', account_subscription_operation, client_factory=cf_subscription_operation) as g:
        g.custom_show_command('show', 'account_subscription_operation_show')

    from ._client_factory import cf_subscription_factory
    account_subscription_factory = CliCommandType(
        operations_tmpl='azext_account.vendored_sdks.subscription.operations._subscription_factory_operations#SubscriptionFactoryOperations.{}',
        client_factory=cf_subscription_factory)
    with self.command_group('account subscription_factory', account_subscription_factory, client_factory=cf_subscription_factory) as g:
        g.custom_command('create_csp_subscription', 'account_subscription_factory_create_csp_subscription')
        g.custom_command('create_subscription_in_enrollment_account', 'account_subscription_factory_create_subscription_in_enrollment_account')
        g.custom_command('create_subscription', 'account_subscription_factory_create_subscription')

    from ._client_factory import cf_subscription_operations
    account_subscription_operations = CliCommandType(
        operations_tmpl='azext_account.vendored_sdks.subscription.operations._subscription_operations_operations#SubscriptionOperationsOperations.{}',
        client_factory=cf_subscription_operations)
    with self.command_group('account subscription_operations', account_subscription_operations, client_factory=cf_subscription_operations) as g:
        g.custom_command('list', 'account_subscription_operations_list')

    from ._client_factory import cf_operations
    account_operations = CliCommandType(
        operations_tmpl='azext_account.vendored_sdks.subscription.operations._operations_operations#OperationsOperations.{}',
        client_factory=cf_operations)
    with self.command_group('account operations', account_operations, client_factory=cf_operations) as g:
        g.custom_command('list', 'account_operations_list')

    from ._client_factory import cf_tenants
    account_tenants = CliCommandType(
        operations_tmpl='azext_account.vendored_sdks.subscription.operations._tenants_operations#TenantsOperations.{}',
        client_factory=cf_tenants)
    with self.command_group('account tenants', account_tenants, client_factory=cf_tenants) as g:
        g.custom_command('list', 'account_tenants_list')
