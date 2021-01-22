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

    from azext_account.generated._client_factory import cf_subscription
    account_subscription = CliCommandType(
        operations_tmpl='azext_account.vendored_sdks.subscription.operations._subscription_operations#SubscriptionOperations.{}',
        client_factory=cf_subscription)
    with self.command_group('account subscription', account_subscription, client_factory=cf_subscription, is_experimental=True) as g:
        g.custom_command('rename', 'account_subscription_rename')
        g.custom_command('cancel', 'account_subscription_cancel', confirmation=True)
        g.custom_command('enable', 'account_subscription_enable')
        g.custom_command('list', 'account_subscription_list')
        g.custom_show_command('show', 'account_subscription_show')
        g.custom_command('list-location', 'account_subscription_list_location')

    from azext_account.generated._client_factory import cf_tenant
    account_tenant = CliCommandType(
        operations_tmpl='azext_account.vendored_sdks.subscription.operations._tenant_operations#TenantOperations.{}',
        client_factory=cf_tenant)
    with self.command_group('account tenant', account_tenant, client_factory=cf_tenant, is_experimental=True) as g:
        g.custom_command('list', 'account_tenant_list')

    from azext_account.generated._client_factory import cf_alias
    account_alias = CliCommandType(
        operations_tmpl='azext_account.vendored_sdks.subscription.operations._alias_operations#AliasOperations.{}',
        client_factory=cf_alias)
    with self.command_group('account alias', account_alias, client_factory=cf_alias, is_experimental=True) as g:
        g.custom_command('list', 'account_alias_list')
        g.custom_show_command('show', 'account_alias_show')
        g.custom_command('create', 'account_alias_create', supports_no_wait=True)
        g.custom_command('delete', 'account_alias_delete')
        g.custom_wait_command('wait', 'account_alias_show')
