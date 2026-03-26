# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long

from azure.cli.core.commands.parameters import get_three_state_flag


def load_arguments(self, _):

    with self.argument_context('zones validate') as c:
        c.argument('resource_group_names', options_list=['--resource-groups', '-g'], help='Name of the resource groups, comma separated.', required=False)
        c.argument('tags', options_list=['--tags'], help='Filter resources based on tags.', required=False)
        c.argument('omit_dependent', options_list=['--omit-dependent'], help='Omit dependent resources from validation.', arg_type=get_three_state_flag(), required=False)
