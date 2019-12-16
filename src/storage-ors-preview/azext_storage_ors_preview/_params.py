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
    object_replication_policy_type = CLIArgumentType(options_list=['--policy-id'])

    with self.argument_context('storage account ors-policy') as c:
        c.argument('account_name', acct_name_type)

    with self.argument_context('storage account ors-policy create') as c:
        c.argument('source_account', options_list=['--source-account', '-s'], help='The source storage account name. Required when no --properties provided.')
        c.argument('destination_account', options_list=['--destination-account', '-d'],
                   help='The destination storage account name. Required when no --properties provided.')
        c.argument('policy_id', help='The ID of object replication policy or "default" if the policy ID is unknown.')
        c.argument('properties', help='The object replication policy definition between two storage accounts, in JSON '
                   'format. Multiple rules can be defined in one policy.')

    with self.argument_context('storage account ors-policy create', arg_group="Object Replication Policy Rule") as c:
        c.argument('source_container',
                   help='The source storage container name. Required when no --properties provided.')
        c.argument('destination_container',
                   help='The destination storage container name. Required when no --properties provided.')
        c.argument('tag', nargs='*', help='Optional. Filter the results to replicate blobs with the tag.')
        c.argument('prefix_match', nargs='*',
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

    with self.argument_context('storage account ors-policy rule create', arg_group="Object Replication Policy Rule") as c:
        c.argument('source_container', options_list=['--source-container', '-s'],
                   help='The source storage container name.')
        c.argument('destination_container', options_list=['--destination-container', '-d'],
                   help='The destination storage container name.')
        c.argument('tag', nargs='*', help='Optional. Filter the results to replicate blobs with the tag.')
        c.argument('prefix_match', nargs='*',
                   help='Optional. Filter the results to replicate only blobs whose names begin with the specified '
                        'prefix.')
        c.argument('rule_id', help='Rule Id is auto-generated for each new rule on destination account. It is required '
                                   'for put policy on source account.')
