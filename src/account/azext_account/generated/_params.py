# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long
# pylint: disable=too-many-lines
# pylint: disable=too-many-statements

from azure.cli.core.commands.parameters import get_enum_type
from ._validators import alias_validator


def load_arguments(self, _):

    with self.argument_context('account subscription rename') as c:
        c.argument('subscription_id', options_list=['--id', '--subscription-id'], help='Subscription Id.')
        c.argument('subscription_name', options_list=['--name', '-n', '--subscription-name'], help='New subscription name')

    with self.argument_context('account subscription cancel') as c:
        c.argument('subscription_id', options_list=['--id', '--subscription-id'], help='Subscription Id.')

    with self.argument_context('account subscription enable') as c:
        c.argument('subscription_id', options_list=['--id', '--subscription-id'], help='Subscription Id.')

    with self.argument_context('account subscription list') as c:
        pass

    with self.argument_context('account subscription show') as c:
        c.argument('subscription_id', options_list=['--id', '--subscription-id'], help='The ID of the target subscription.', id_part='subscription')

    with self.argument_context('account subscription list-location') as c:
        c.argument('subscription_id', options_list=['--id', '--subscription-id'], help='The ID of the target subscription.')

    with self.argument_context('account tenant list') as c:
        pass

    with self.argument_context('account alias list') as c:
        pass

    with self.argument_context('account alias show') as c:
        c.argument('alias_name', options_list=['--name', '-n'], help='Alias Name')

    with self.argument_context('account alias create', validator=alias_validator) as c:
        c.argument('alias_name', options_list=['--name', '-n'], type=str, help='Alias Name')
        c.argument('display_name', type=str, help='The friendly name of the subscription.')
        c.argument('workload', arg_type=get_enum_type(['Production', 'DevTest']), help='The workload type of the '
                   'subscription. It can be either Production or DevTest.')
        c.argument('billing_scope', type=str, help='Billing scope. It determines whether the subscription is Field-Led, Partner-Led or '
                   'LegacyEA')
        c.argument('subscription_id', type=str, help='This parameter can be used to create alias for existing '
                   'subscription ID')

    with self.argument_context('account alias delete') as c:
        c.argument('alias_name', options_list=['--name', '-n'], help='Alias Name')

    with self.argument_context('account alias wait') as c:
        c.argument('alias_name', options_list=['--name', '-n'], help='Alias Name')
