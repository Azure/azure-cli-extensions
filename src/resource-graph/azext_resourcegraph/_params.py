# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long, unused-import


from azure.cli.core.commands.parameters import get_generic_completion_list
from azure.cli.core.commands.parameters import get_three_state_flag
from azure.cli.core.commands.parameters import tags_type

_QUERY_EXAMPLES = [
    '''summarize count()''',
    '''project name, type, location | order by name asc''',
    '''where type =~ 'Microsoft.Compute/virtualMachines' | project name, location, type | order by name desc''',
    '''where type =~ 'Microsoft.Compute/virtualMachines' | project name, location''',
    '''summarize count() by subscriptionId''',
    '''summarize count() by subscriptionId, location''',
    '''where type =~ 'Microsoft.Compute/virtualMachines' | summarize count() by tostring(properties.storageProfile.osDisk.osType)''',
    '''where type =~ 'Microsoft.Compute/virtualMachines'  and properties.storageProfile.osDisk.osType =~ 'Windows' | project name''',
    '''where name contains 'sql'| project location, name''',
    '''where isnotempty(tags) and tags != '{}' | project tags''',
    '''where isnotempty(tags.environment) | project name, Environment=tags.environment | limit 10'''
]


def load_arguments(self, _):
    with self.argument_context('graph query') as c:
        c.argument('graph_query', options_list=['--graph-query', '--q', '-q'], required=True,
                   completer=get_generic_completion_list(_QUERY_EXAMPLES), help='Resource Graph query to execute.')
        c.argument('first', options_list=['--first'], required=False, type=int, default=None,
                   help='The maximum number of objects to return. Accepted range: 1-1000. Default value is 100.')
        c.argument('skip', options_list=['--skip'], required=False, type=int, default=None,
                   help='Ignores the first N objects and then gets the remaining objects. Default value is 0.')
        c.argument('subscriptions', options_list=['--subscriptions', '-s'], nargs='*', required=False, default=None,
                   help='List of subscriptions to run query against. By default all accessible subscriptions are queried.')
        c.argument('management_groups', options_list=['--management-groups', '-m'], nargs='*', required=False, default=None,
                   help='List of management groups to run query against.')
        c.argument('skip_token', options_list=['--skip-token'], type=str, required=False, default=None,
                   help='Skip token to get the next page of the query if applicable.')
        c.argument('allow_partial_scopes', options_list=['--allow-partial-scopes', '-a'],
                   arg_type=get_three_state_flag(), required=False, default=False,
                   help='Indicates if query should succeed when only partial number of subscription underneath can be processed by server.')

    with self.argument_context('graph shared-query') as c:
        c.argument('graph_query', options_list=['--graph-query', '--q', '-q'],
                   completer=get_generic_completion_list(_QUERY_EXAMPLES), help='Resource Graph query to execute.')
        c.argument('resource_name', options_list=['--name', '-n'], help='Name of the graph shared query.')
        c.argument('tags', tags_type)
        c.argument('description', options_list=['-d', '--description'], help='Description of the graph shared query.')
        c.ignore('location')
