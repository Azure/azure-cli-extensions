# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core.commands.parameters import get_enum_type


# pylint: disable=line-too-long
def load_arguments(self, _):
    with self.argument_context('account create') as c:
        c.argument('enrollment_account_name', options_list=('--enrollment-account-name', '--enrollment-account-object-id'), required=True, help='The name of the enrollment account which should be used to create a subscription.')
        c.argument('offer_type', required=True, help='The offer type of the subscription. For example, MS-AZR-0017P (EnterpriseAgreement) and MS-AZR-0148P (EnterpriseAgreement devTest) are available.', arg_type=get_enum_type(['MS-AZR-0017P', 'MS-AZR-0148P']))
        c.argument('display_name', help='The display name of the subscription.')
        c.argument('owner_object_id', help='The object id(s) of the owner(s) which should be granted access to the new subscription.')
        c.argument('owner_spn', help='The service principal name(s) of the owner(s) which should be granted access to the new subscription.')
        c.argument('owner_upn', help='The user principal name(s) of owner(s) who should be granted access to the new subscription.')
