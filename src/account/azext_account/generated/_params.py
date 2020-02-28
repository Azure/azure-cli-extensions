# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long
# pylint: disable=too-many-lines
# pylint: disable=too-many-statements

from azure.cli.core.commands.parameters import (
    get_enum_type
)
from azext_account.action import (
    AddOwners
)


def load_arguments(self, _):

    with self.argument_context('account subscription create-subscription') as c:
        c.argument('billing_account_name', help='The name of the Microsoft Customer Agreement billing account for which you want to create the subscription.')
        c.argument('billing_profile_name', help='The name of the billing profile in the billing account for which you want to create the subscription.')
        c.argument('invoice_section_name', help='The name of the invoice section in the billing account for which you want to create the subscription.')
        c.argument('body_display_name', help='The friendly name of the subscription.')
        c.argument('body_sku_id', help='The SKU ID of the Azure plan. Azure plan determines the pricing and service-level agreement of the subscription.  Use 001 for Microsoft Azure Plan and 002 for Microsoft Azure Plan for DevTest.')
        c.argument('body_cost_center', help='If set, the cost center will show up on the Azure usage and charges file.')
        c.argument('body_owner', help='Active Directory Principal who’ll get owner access on the new subscription.', action=AddOwners, nargs='+')
        c.argument('body_management_group_id', help='The identifier of the management group to which this subscription will be associated.')

    with self.argument_context('account subscription create-subscription-in-enrollment-account') as c:
        c.argument('enrollment_account_name', help='The name of the enrollment account to which the subscription will be billed.')
        c.argument('body_display_name', help='The display name of the subscription.')
        c.argument('body_management_group_id', help='The Management Group Id.')
        c.argument('body_owners', help='The list of principals that should be granted Owner access on the subscription. Principals should be of type User, Service Principal or Security Group.', action=AddOwners, nargs='+')
        c.argument('body_offer_type', arg_type=get_enum_type(['MS-AZR-0017P', 'MS-AZR-0148P']), help='The offer type of the subscription. For example, MS-AZR-0017P (EnterpriseAgreement) and MS-AZR-0148P (EnterpriseAgreement devTest) are available. Only valid when creating a subscription in a enrollment account scope.')

    with self.argument_context('account subscription create-csp-subscription') as c:
        c.argument('billing_account_name', help='The name of the Microsoft Customer Agreement billing account for which you want to create the subscription.')
        c.argument('customer_name', help='The name of the customer.')
        c.argument('body_display_name', help='The friendly name of the subscription.')
        c.argument('body_sku_id', help='The SKU ID of the Azure plan. Azure plan determines the pricing and service-level agreement of the subscription.  Use 001 for Microsoft Azure Plan and 002 for Microsoft Azure Plan for DevTest.')
        c.argument('body_reseller_id', help='Reseller ID, basically MPN Id.')

    with self.argument_context('account subscription rename') as c:
        c.argument('body_subscription_name', help='New subscription name')

    with self.argument_context('account subscription cancel') as c:
        pass

    with self.argument_context('account subscription enable') as c:
        pass

    with self.argument_context('account subscription-operation show') as c:
        c.argument('operation_id', help='The operation ID, which can be found from the Location field in the generate recommendation response header.')

    with self.argument_context('account operations list') as c:
        pass
