# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

def load_arguments(self, _):

    with self.argument_context('account subscription create-subscription') as c:
        c.argument('billing_account_name', help='Custom parameter moooo.....')
