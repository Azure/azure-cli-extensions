# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long

from knack.arguments import CLIArgumentType
from ._validators import get_datetime_type


def load_arguments(self, _):

    from azure.cli.core.commands.parameters import get_resource_name_completion_list

    acct_name_type = CLIArgumentType(options_list=['--account-name', '-n'], help='The storage account name.',
                                     id_part='name',
                                     completer=get_resource_name_completion_list('Microsoft.Storage/storageAccounts'))
    or_policy_type = CLIArgumentType(
        options_list=['--policy', '-p'],
        help='The object replication policy definition between two storage accounts, in JSON format. '
             'Multiple rules can be defined in one policy.'
    )
    policy_id_type = CLIArgumentType(
        options_list=['--policy-id'],
        help='The ID of object replication policy or "default" if the policy ID is unknown.'
    )
    rule_id_type = CLIArgumentType(
        options_list=['--rule-id', '-r'],
        help='Rule Id is auto-generated for each new rule on destination account. It is required '
             'for put policy on source account.'
    )
    prefix_math_type = CLIArgumentType(
        nargs='+', arg_group='Filters',
        help='Optional. Filter the results to replicate only blobs whose names begin with the specified '
             'prefix.'
    )
    min_creation_time_type = CLIArgumentType(
        options_list=['--min-creation-time', '-t'], arg_group='Filters', type=get_datetime_type(True),
        help="Blobs created after the time will be replicated to the destination. It must be in datetime format "
             "'yyyy-MM-ddTHH:mm:ssZ'. Example: 2020-02-19T16:05:00Z")

    with self.argument_context('storage account or-policy') as c:
        c.argument('account_name', acct_name_type, id_part=None)
        c.argument('object_replication_policy_id', policy_id_type)
        c.argument('policy_id', policy_id_type)
        c.argument('source_account', options_list=['--source-account', '-s'],
                   help='The source storage account name. Required when no --policy provided.')
        c.argument('destination_account', options_list=['--destination-account', '-d'],
                   help='The destination storage account name. Required when no --policy provided.')
        c.argument('properties', or_policy_type)
        c.argument('prefix_match', prefix_math_type)
        c.argument('min_creation_time', min_creation_time_type)

    for item in ['create', 'update']:
        with self.argument_context('storage account or-policy {}'.format(item),
                                   arg_group="Object Replication Policy Rule") as c:
            c.argument('rule_id', help='Rule Id is auto-generated for each new rule on destination account. It is '
                                       'required for put policy on source account.')
            c.argument('source_container', options_list=['--source-container'],
                       help='The source storage container name. Required when no --policy provided.')
            c.argument('destination_container', options_list=['--destination-container'],
                       help='The destination storage container name. Required when no --policy provided.')

    with self.argument_context('storage account or-policy update') as c:
        c.argument('account_name', acct_name_type, id_part=None)
        c.argument('properties', or_policy_type)

    with self.argument_context('storage account or-policy rule') as c:
        c.argument('policy_id', policy_id_type)
        c.argument('source_container', options_list=['--source-container', '-s'],
                   help='The source storage container name.')
        c.argument('destination_container', options_list=['--destination-container', '-d'],
                   help='The destination storage container name.')
        c.argument('rule_id', rule_id_type)
