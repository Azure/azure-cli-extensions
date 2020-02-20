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
    with self.command_group('account subscription', account_subscriptions, client_factory=cf_subscriptions) as g:
        g.custom_command('cancel', 'cancel_account_subscription')
        g.custom_command('rename', 'rename_account_subscription')
        g.custom_command('enable', 'enable_account_subscription')
        g.custom_command('list-locations', 'list_locations_account_subscription')
        g.custom_command('get', 'get_account_subscription')
        g.custom_command('list', 'list_account_subscription')

    from ._client_factory import cf_subscription_operation
    account_subscription_operation = CliCommandType(
        operations_tmpl='azext_account.vendored_sdks.subscription.operations._subscription_operation_operations#SubscriptionOperationOperations.{}',
        client_factory=cf_subscription_operation)
    with self.command_group('account subscription-operation', account_subscription_operation, client_factory=cf_subscription_operation) as g:
        g.custom_command('get', 'get_account_subscription_operation')

    from ._client_factory import cf_subscription_factory
    account_subscription_factory = CliCommandType(
        operations_tmpl='azext_account.vendored_sdks.subscription.operations._subscription_factory_operations#SubscriptionFactoryOperations.{}',
        client_factory=cf_subscription_factory)
    with self.command_group('account subscription-factory', account_subscription_factory, client_factory=cf_subscription_factory) as g:
        g.custom_command('create-subscription', 'create_subscription_account_subscription_factory')
        g.custom_command('create-csp-subscription', 'create_csp_subscription_account_subscription_factory')
        g.custom_command('create-subscription-in-enrollment-account', 'create_subscription_in_enrollment_account_account_subscription_factory')

    from ._client_factory import cf_subscription_operations
    account_subscription_operations = CliCommandType(
        operations_tmpl='azext_account.vendored_sdks.subscription.operations._subscription_operations_operations#SubscriptionOperationsOperations.{}',
        client_factory=cf_subscription_operations)
    with self.command_group('account subscription-operation', account_subscription_operations, client_factory=cf_subscription_operations) as g:
        g.custom_command('list', 'list_account_subscription_operation')

    from ._client_factory import cf_operations
    account_operations = CliCommandType(
        operations_tmpl='azext_account.vendored_sdks.subscription.operations._operations_operations#OperationsOperations.{}',
        client_factory=cf_operations)
    with self.command_group('account operation', account_operations, client_factory=cf_operations) as g:
        g.custom_command('list', 'list_account_operation')

    from ._client_factory import cf_tenants
    account_tenants = CliCommandType(
        operations_tmpl='azext_account.vendored_sdks.subscription.operations._tenants_operations#TenantsOperations.{}',
        client_factory=cf_tenants)
    with self.command_group('account tenant', account_tenants, client_factory=cf_tenants) as g:
        g.custom_command('list', 'list_account_tenant')
