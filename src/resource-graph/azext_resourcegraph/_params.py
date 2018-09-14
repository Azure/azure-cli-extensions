# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long


from azure.cli.core.commands.parameters import get_generic_completion_list

_QUERY_EXAMPLES = [
    ''' summarize count()''',
    ''' project name, type, location | order by name asc''',
    ''' where type =~ 'Microsoft.Compute/virtualMachines' | project name, location, type | order by name desc''',
    ''' where type =~ 'Microsoft.Compute/virtualMachines' | project name, location''',
    ''' summarize count() by subscriptionId''',
    ''' summarize count() by subscriptionId, location''',
    ''' where type =~ 'Microsoft.Compute/virtualMachines' | summarize count() by tostring(properties.storageProfile.osDisk.osType)''',
    ''' where type =~ 'Microsoft.Compute/virtualMachines'  and properties.storageProfile.osDisk.osType =~ 'Windows' | project name''',
    ''' where name contains 'sql'| project location, name''',
    ''' where isnotempty(tags) and tags != '{}' | project tags''',
    ''' where isnotempty(tags.environment) | project name, Environment=tags.environment | limit 10'''
]


def load_arguments(self, _):
    with self.argument_context('graph query') as c:
        c.argument('graph_query', options_list=['--graph-query', '--q', '-q'], required=True, completer=get_generic_completion_list(_QUERY_EXAMPLES), help='Resource Graph query to execute.')
        c.argument('first', options_list=['--first'], required=False, type=int, default=100, help='The maximum number of objects to return. Accepted range: 1-5000.')
        c.argument('skip', options_list=['--skip'], required=False, type=int, default=0, help='Ignores the first N objects and then gets the remaining objects.')
        c.argument('subscriptions', options_list=['--subscriptions', '-s'], nargs='*', required=False, default=None, help='List of subscriptions to run query against. By default all accessible subscriptions are queried.')
