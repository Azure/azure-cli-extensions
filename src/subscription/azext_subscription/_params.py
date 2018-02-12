# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core.commands.parameters import get_enum_type


# pylint: disable=line-too-long
def load_arguments(self, _):
    with self.argument_context('account subscription-definition create') as c:
        c.argument('offer_type', required=True, help='The offer type of the subscription. For example, MS-AZR-0017P (EnterpriseAgreement) and MS-AZR-0148P (EnterpriseAgreement devTest) are available.', arg_type=get_enum_type(['MS-AZR-0017P', 'MS-AZR-0148P']))
        c.argument('subscription_display_name', help='The subscription display name of the subscription definition.')

    for scope in ['account subscription-definition create', 'account subscription-definition show']:
        with self.argument_context(scope) as c:
            c.argument('subscription_definition_name', options_list=['--name', '-n'], help='Name of the subscription definition.')
