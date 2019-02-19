# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long

def load_arguments(self, _):
    with self.argument_context('anf') as c:
        c.argument('resource_group', options_list=['--resource-group', '-g'], required=True, help='The name of the resource group')

    with self.argument_context('anf') as c:
        c.argument('account_name', options_list=['--account-name', '-a'], required=True, help='The name of the ANF account')

    with self.argument_context('anf') as c:
        c.argument('pool_name', options_list=['--pool-name', '-p'], required=True, help='The name of the ANF pool')

    with self.argument_context('anf') as c:
        c.argument('volume_name', options_list=['--volume-name', '-v'], required=True, help='The name of the ANF volume')

    with self.argument_context('anf') as c:
        c.argument('snapshot_name', options_list=['--snapshot-name', '-s'], required=True, help='The name of the ANF snapshot')

    with self.argument_context('anf') as c:
        c.argument('tag', options_list=['--tags'], required=False, help='A list of space separated tags to apply to the account')
