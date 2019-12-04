# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long

from knack.arguments import CLIArgumentType


def load_arguments(self, _):

    from azure.cli.core.commands.parameters import get_resource_name_completion_list

    acct_name_type = CLIArgumentType(options_list=['--account-name', '-n'], help='The storage account name.',
                                     id_part='name',
                                     completer=get_resource_name_completion_list('Microsoft.Storage/storageAccounts'))
    object_replication_policy_type = CLIArgumentType(options_list=['--policy-id'],
                                                     help='The ID of object replication policy.')

    with self.argument_context('storage account ors-policy create') as c:
        c.argument('source_account', help='The source storage account name. Required when no --properties provided.')
        c.argument('destination_account', help='The destination storage account name. Required when no --properties provided.')
        c.argument('policy_id', help='The ID of object replication policy.')
        c.argument('properties', help='The object replication policy definition between two storage accounts, in JSON '
                   'format. Multiple rules can be defined in one policy.')
        c.argument('source_container', help='The source storage container name. Required when no --properties provided.',
                   arg_group="Obeject Replication Policy Rule")
        c.argument('destination_container', help='The destination storage container name. Required when no --properties provided.',
                   arg_group="Obeject Replication Policy Rule")
        c.argument('tag', nargs='*', help='Optional. Filter the results to replicate blobs with the tag.',
                   arg_group="Obeject Replication Policy Rule")
        c.argument('prefix_match', nargs='*', arg_group="Obeject Replication Policy Rule",
                   help='Optional. Filter the results to replicate only blobs whose names begin with the specified '
                        'prefix.')

    with self.argument_context('storage account ors-policy update') as c:
        c.argument('account_name', help='The name of the storage account within the specified resource group.')
        c.argument('object_replication_policy_id', object_replication_policy_type)
        c.argument('properties', help='The object replication policy definition between two storage accounts, in JSON '
                                      'format. Multiple rules can be defined in one policy.')

    with self.argument_context('storage account ors-policy list') as c:
        c.argument('account_name', acct_name_type, id_part=None)

    with self.argument_context('storage account ors-policy show') as c:
        c.argument('account_name', help='The name of the storage account within the specified resource group.')
        c.argument('object_replication_policy_id', object_replication_policy_type)
