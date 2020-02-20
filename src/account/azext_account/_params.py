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

    with self.argument_context('account subscription cancel') as c:
        pass

    with self.argument_context('account subscription rename') as c:
        c.argument('subscription_name', id_part=None, help='New subscription name')

    with self.argument_context('account subscription enable') as c:
        pass

    with self.argument_context('account subscription list-locations') as c:
        pass

    with self.argument_context('account subscription get') as c:
        pass

    with self.argument_context('account subscription list') as c:
        pass

    with self.argument_context('account subscription-operation get') as c:
        c.argument('operation_id', id_part=None, help='The operation ID, which can be found from the Location field in the generate recommendation response header.')

    with self.argument_context('account subscription-factory create-subscription') as c:
        c.argument('billing_account_name', id_part=None, help='The name of the Microsoft Customer Agreement billing account for which you want to create the subscription.')
        c.argument('billing_profile_name', id_part=None, help='The name of the billing profile in the billing account for which you want to create the subscription.')
        c.argument('invoice_section_name', id_part=None, help='The name of the invoice section in the billing account for which you want to create the subscription.')
        c.argument('display_name', id_part=None, help='The friendly name of the subscription.')
        c.argument('billing_profile_id', id_part=None, help='The ARM ID of the billing profile for which you want to create the subscription.')
        c.argument('sku_id', id_part=None, help='The SKU ID of the Azure plan. Azure plan determines the pricing and service-level agreement of the subscription.  Use 001 for Microsoft Azure Plan and 002 for Microsoft Azure Plan for DevTest.')
        c.argument('cost_center', id_part=None, help='If set, the cost center will show up on the Azure usage and charges file.')
        c.argument('owner', id_part=None, help='If specified, the AD principal will get owner access to the subscription, along with the user who is performing the create subscription operation')
        c.argument('management_group_id', id_part=None, help='The identifier of the management group to which this subscription will be associated.')
        c.argument('additional_parameters', id_part=None, help='Additional, untyped parameters to support custom subscription creation scenarios.')
        c.argument('reseller_id', id_part=None, help='Reseller ID, basically MPN Id.')
        c.argument('service_provider_id', id_part=None, help='Service provider ID, basically MPN Id.')
        c.argument('owners', id_part=None, help='The list of principals that should be granted Owner access on the subscription. Principals should be of type User, Service Principal or Security Group.', action=AddOwners, nargs='+')
        c.argument('offer_type', arg_type=get_enum_type(['MS-AZR-0017P', 'MS-AZR-0148P']), id_part=None, help='The offer type of the subscription. For example, MS-AZR-0017P (EnterpriseAgreement) and MS-AZR-0148P (EnterpriseAgreement devTest) are available. Only valid when creating a subscription in a enrollment account scope.')

    with self.argument_context('account subscription-factory create-csp-subscription') as c:
        c.argument('billing_account_name', id_part=None, help='The name of the Microsoft Customer Agreement billing account for which you want to create the subscription.')
        c.argument('customer_name', id_part=None, help='The name of the customer.')
        c.argument('display_name', id_part=None, help='The friendly name of the subscription.')
        c.argument('billing_profile_id', id_part=None, help='The ARM ID of the billing profile for which you want to create the subscription.')
        c.argument('sku_id', id_part=None, help='The SKU ID of the Azure plan. Azure plan determines the pricing and service-level agreement of the subscription.  Use 001 for Microsoft Azure Plan and 002 for Microsoft Azure Plan for DevTest.')
        c.argument('cost_center', id_part=None, help='If set, the cost center will show up on the Azure usage and charges file.')
        c.argument('owner', id_part=None, help='If specified, the AD principal will get owner access to the subscription, along with the user who is performing the create subscription operation')
        c.argument('management_group_id', id_part=None, help='The identifier of the management group to which this subscription will be associated.')
        c.argument('additional_parameters', id_part=None, help='Additional, untyped parameters to support custom subscription creation scenarios.')
        c.argument('reseller_id', id_part=None, help='Reseller ID, basically MPN Id.')
        c.argument('service_provider_id', id_part=None, help='Service provider ID, basically MPN Id.')
        c.argument('owners', id_part=None, help='The list of principals that should be granted Owner access on the subscription. Principals should be of type User, Service Principal or Security Group.', action=AddOwners, nargs='+')
        c.argument('offer_type', arg_type=get_enum_type(['MS-AZR-0017P', 'MS-AZR-0148P']), id_part=None, help='The offer type of the subscription. For example, MS-AZR-0017P (EnterpriseAgreement) and MS-AZR-0148P (EnterpriseAgreement devTest) are available. Only valid when creating a subscription in a enrollment account scope.')

    with self.argument_context('account subscription-factory create-subscription-in-enrollment-account') as c:
        c.argument('enrollment_account_name', id_part=None, help='The name of the enrollment account to which the subscription will be billed.')
        c.argument('display_name', id_part=None, help='The friendly name of the subscription.')
        c.argument('billing_profile_id', id_part=None, help='The ARM ID of the billing profile for which you want to create the subscription.')
        c.argument('sku_id', id_part=None, help='The SKU ID of the Azure plan. Azure plan determines the pricing and service-level agreement of the subscription.  Use 001 for Microsoft Azure Plan and 002 for Microsoft Azure Plan for DevTest.')
        c.argument('cost_center', id_part=None, help='If set, the cost center will show up on the Azure usage and charges file.')
        c.argument('owner', id_part=None, help='If specified, the AD principal will get owner access to the subscription, along with the user who is performing the create subscription operation')
        c.argument('management_group_id', id_part=None, help='The identifier of the management group to which this subscription will be associated.')
        c.argument('additional_parameters', id_part=None, help='Additional, untyped parameters to support custom subscription creation scenarios.')
        c.argument('reseller_id', id_part=None, help='Reseller ID, basically MPN Id.')
        c.argument('service_provider_id', id_part=None, help='Service provider ID, basically MPN Id.')
        c.argument('owners', id_part=None, help='The list of principals that should be granted Owner access on the subscription. Principals should be of type User, Service Principal or Security Group.', action=AddOwners, nargs='+')
        c.argument('offer_type', arg_type=get_enum_type(['MS-AZR-0017P', 'MS-AZR-0148P']), id_part=None, help='The offer type of the subscription. For example, MS-AZR-0017P (EnterpriseAgreement) and MS-AZR-0148P (EnterpriseAgreement devTest) are available. Only valid when creating a subscription in a enrollment account scope.')

    with self.argument_context('account subscription-operation list') as c:
        pass

    with self.argument_context('account operation list') as c:
        pass

    with self.argument_context('account tenant list') as c:
        pass
