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

    from azext_account.manual._client_factory import cf_subscriptions
    account_subscriptions = CliCommandType(
        operations_tmpl='azext_account.vendored_sdks.subscription.operations._subscription_operations#SubscriptionOperations.{}',
        client_factory=cf_subscriptions)
    with self.command_group('account subscription', account_subscriptions, client_factory=cf_subscriptions, is_experimental=True) as g:
        g.custom_command('list', 'account_subscription_list')
        g.custom_show_command('show', 'account_subscription_show')
        g.custom_command('list-location', 'account_subscription_list_location')

    from azext_account.manual._client_factory import cf_tenants
    account_tenants = CliCommandType(
        operations_tmpl='azext_account.vendored_sdks.subscription.operations._tenants_operations#TenantsOperations.{}',
        client_factory=cf_tenants)
    with self.command_group('account tenant', account_tenants, client_factory=cf_tenants, is_experimental=True) as g:
        g.custom_command('list', 'account_tenant_list')

    from azext_account.manual._client_factory import cf_subscription
    account_subscription = CliCommandType(
        operations_tmpl='azext_account.vendored_sdks.subscription.operations._subscription_operations#SubscriptionOperations.{}',
        client_factory=cf_subscription)
    with self.command_group('account', account_subscription, client_factory=cf_subscription) as g:
        g.command('accept-ownership-status', 'accept_ownership_status')
