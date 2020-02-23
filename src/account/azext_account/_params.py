# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long
# pylint: disable=too-many-lines
# pylint: disable=too-many-statements

from azure.cli.core.commands.parameters import (
    tags_type,
    get_enum_type,
    resource_group_name_type,
    get_location_type
)
from azext_account.actions import (
    AddOwners,
    AddBody
)


def load_arguments(self, _):

    with self.argument_context('account subscriptions list') as c:
        pass

    with self.argument_context('account subscriptions show') as c:
        pass

    with self.argument_context('account subscriptions rename') as c:
        c.argument('subscription_name', id_part=None, help='New subscription name')

    with self.argument_context('account subscriptions cancel') as c:
        pass

    with self.argument_context('account subscriptions enable') as c:
        pass

    with self.argument_context('account subscription_operation show') as c:
        c.argument('operation_id', id_part=None, help='The operation ID, which can be found from the Location field in the generate recommendation response header.')

    with self.argument_context('account subscription_factory create_csp_subscription') as c:
        c.argument('billing_account_name', id_part=None, help='The name of the Microsoft Customer Agreement billing account for which you want to create the subscription.')
        c.argument('customer_name', id_part=None, help='The name of the customer.')
        c.argument('display_name', id_part=None, help='The friendly name of the subscription.')
        c.argument('sku_id', id_part=None, help='The SKU ID of the Azure plan. Azure plan determines the pricing and service-level agreement of the subscription.  Use 001 for Microsoft Azure Plan and 002 for Microsoft Azure Plan for DevTest.')
        c.argument('reseller_id', id_part=None, help='Reseller ID, basically MPN Id.')
        c.argument('service_provider_id', id_part=None, help='Service provider ID, basically MPN Id.')

    with self.argument_context('account subscription_factory create_subscription_in_enrollment_account') as c:
        c.argument('enrollment_account_name', id_part=None, help='The name of the enrollment account to which the subscription will be billed.')
        c.argument('display_name', id_part=None, help='The display name of the subscription.')
        c.argument('owners', id_part=None, help='The list of principals that should be granted Owner access on the subscription. Principals should be of type User, Service Principal or Security Group.', action=AddOwners, nargs='+')
        c.argument('offer_type', arg_type=get_enum_type(['MS-AZR-0017P', 'MS-AZR-0148P']), id_part=None, help='The offer type of the subscription. For example, MS-AZR-0017P (EnterpriseAgreement) and MS-AZR-0148P (EnterpriseAgreement devTest) are available. Only valid when creating a subscription in a enrollment account scope.')
        c.argument('additional_parameters', id_part=None, help='Additional, untyped parameters to support custom subscription creation scenarios.', nargs='+')

    with self.argument_context('account subscription_factory create_subscription') as c:
        c.argument('billing_account_name', id_part=None, help='The name of the Microsoft Customer Agreement billing account for which you want to create the subscription.')
        c.argument('billing_profile_name', id_part=None, help='The name of the billing profile in the billing account for which you want to create the subscription.')
        c.argument('invoice_section_name', id_part=None, help='The name of the invoice section in the billing account for which you want to create the subscription.')
        c.argument('body', id_part=None, help='The subscription creation parameters.', action=AddBody, nargs='+')

    with self.argument_context('account subscription_operations list') as c:
        pass

    with self.argument_context('account operations list') as c:
        pass

    with self.argument_context('account tenants list') as c:
        pass
