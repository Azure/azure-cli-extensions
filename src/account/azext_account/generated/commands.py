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

    from azext_acconut.generated._client_factory import cf_subscription
    account_subscription = CliCommandType(
        operations_tmpl='azext_account.vendored_sdks.subscription.operations._subscription_operations#SubscriptionOperations.{}',
        client_factory=cf_subscription)
    with self.command_group('account subscription', account_subscription, client_factory=cf_subscription) as g:
        g.custom_command('create-subscription', 'account_subscription_create_subscription', supports_no_wait=True)
        g.custom_command('create-subscription-in-enrollment-account', 'account_subscription_create_subscription_in_enrollment_account', supports_no_wait=True)
        g.custom_command('create-csp-subscription', 'account_subscription_create_csp_subscription', supports_no_wait=True)
        g.custom_command('rename', 'account_subscription_rename')
        g.custom_command('cancel', 'account_subscription_cancel')
        g.custom_command('enable', 'account_subscription_enable')
        g.wait_command('wait');

    from azext_acconut.generated._client_factory import cf_subscription_operation
    account_subscription_operation = CliCommandType(
        operations_tmpl='azext_account.vendored_sdks.subscription.operations._subscription_operation_operations#SubscriptionOperationOperations.{}',
        client_factory=cf_subscription_operation)
    with self.command_group('account subscription-operation', account_subscription_operation, client_factory=cf_subscription_operation) as g:
        g.custom_show_command('show', 'account_subscription_operation_show')

    from azext_acconut.generated._client_factory import cf_operation
    account_operation = CliCommandType(
        operations_tmpl='azext_account.vendored_sdks.subscription.operations._operation_operations#OperationOperations.{}',
        client_factory=cf_operation)
    with self.command_group('account operation', account_operation, client_factory=cf_operation) as g:
        g.custom_command('list', 'account_operation_list')
