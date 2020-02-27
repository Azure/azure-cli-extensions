# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long
# pylint: disable=too-many-lines
# pylint: disable=too-many-statements

from azure.cli.core.commands.parameters import (
    tags_type,
    resource_group_name_type,
    get_location_type
)
from azext_account.action import (
    AddBody
)


def load_arguments(self, _):

    with self.argument_context('account subscription create-csp-subscription') as c:
        c.argument('billing_account_name', id_part=None, help='The name of the Microsoft Customer Agreement billing account for which you want to create the subscription.')
        c.argument('customer_name', id_part=None, help='The name of the customer.')
        c.argument('display_name', id_part=None, help='The friendly name of the subscription.')
        c.argument('sku_id', id_part=None, help='The SKU ID of the Azure plan. Azure plan determines the pricing and service-level agreement of the subscription.  Use 001 for Microsoft Azure Plan and 002 for Microsoft Azure Plan for DevTest.')
        c.argument('reseller_id', id_part=None, help='Reseller ID, basically MPN Id.')
        c.argument('service_provider_id', id_part=None, help='Service provider ID, basically MPN Id.')

    with self.argument_context('account subscription create-subscription') as c:
        c.argument('billing_account_name', id_part=None, help='The name of the Microsoft Customer Agreement billing account for which you want to create the subscription.')
        c.argument('billing_profile_name', id_part=None, help='The name of the billing profile in the billing account for which you want to create the subscription.')
        c.argument('invoice_section_name', id_part=None, help='The name of the invoice section in the billing account for which you want to create the subscription.')
        c.argument('body', id_part=None, help='The subscription creation parameters.', action=AddBody, nargs='+')

    with self.argument_context('account subscription rename') as c:
        c.argument('subscription_name', id_part=None, help='New subscription name')

    with self.argument_context('account subscription create-subscription-in-enrollment-account') as c:
        c.argument('enrollment_account_name', id_part=None, help='The name of the enrollment account to which the subscription will be billed.')
        c.argument('body', id_part=None, help='The subscription creation parameters.', action=AddBody, nargs='+')

    with self.argument_context('account subscription cancel') as c:
        pass

    with self.argument_context('account subscription enable') as c:
        pass

    with self.argument_context('account subscription-operation show') as c:
        c.argument('operation_id', id_part=None, help='The operation ID, which can be found from the Location field in the generate recommendation response header.')

    with self.argument_context('account operations list') as c:
        pass
