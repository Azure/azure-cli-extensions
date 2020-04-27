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
    with self.command_group('account subscription', account_subscription, client_factory=cf_subscription) as g:
        g.custom_command('create', 'account_subscription_create_subscription', supports_no_wait=True)
        g.custom_command('rename', 'account_subscription_rename')
        g.custom_command('cancel', 'account_subscription_cancel', confirmation=True)
        g.custom_command('enable', 'account_subscription_enable')
        g.custom_command('create-csp', 'account_subscription_create_csp_subscription', supports_no_wait=True)
        g.custom_command('create-in-enrollment-account', 'account_subscription_create_subscription_in_enrollment_account', supports_no_wait=True)
