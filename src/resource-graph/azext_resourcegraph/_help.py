# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.help_files import helps

# pylint: disable=line-too-long

helps['graph'] = """
    type: group
    short-summary: Query the resources managed by Azure Resource Manager.
    long-summary: >
        Run 'az graph query --help' for detailed help.
"""

helps['graph query'] = """
    type: command
    short-summary: Query the resources managed by Azure Resource Manager.
    long-summary: >
        See https://aka.ms/AzureResourceGraph-QueryLanguage to learn more about query language and browse examples
    parameters:
        - name: --graph-query --q -q
          type: string
          short-summary: "Resource Graph query to execute."
        - name: --first
          type: int
          short-summary: "The maximum number of objects to return. Accepted range: 1-1000."
        - name: --skip
          type: int
          short-summary: Ignores the first N objects and then gets the remaining objects.
        - name: --subscriptions -s
          type: string
          short-summary: List of subscriptions to run query against. By default all accessible subscriptions are queried.
        - name: --management-groups -m
          type: string
          short-summary: List of management groups to run query against.
        - name: --skip-token
          type: string
          short-summary: Skip token to get the next page of the query if applicable.
        - name: --allow-partial-scopes -a
          type: bool
          short-summary: Indicates if query should succeed when only partial number of subscription underneath can be processed by server.
    examples:
        - name: Query resources requesting a subset of resource fields.
          text: >
            az graph query -q "project id, name, type, location, tags"
        - name: Query resources with field selection, filtering and summarizing.
          text: >
            az graph query -q "project id, type, location | where type =~ 'Microsoft.Compute/virtualMachines' | summarize count() by location | top 3 by count_"
        - name: Request a subset of results, skipping 20 items and getting the next 10.
          text: >
            az graph query -q "where type =~ "Microsoft.Compute" | project name, tags" --first 10 --skip 20
        - name: Choose subscriptions to query.
          text: >
            az graph query -q "where type =~ "Microsoft.Compute" | project name, tags" --subscriptions 11111111-1111-1111-1111-111111111111 22222222-2222-2222-2222-222222222222
        - name: Choose management groups to query.
          text: >
            az graph query -q "where type =~ "Microsoft.Compute" | project name, tags" --management-groups aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb --allow-partial-scopes
        - name: Query with the skip token.
          text: >
            az graph query -q "where type =~ "Microsoft.Compute" | project name, tags" --skip-token skip_token_value_from_previous_query_response
"""


helps['graph shared-query'] = """
    type: group
    short-summary: Manage shared query of Azure resource graph.
"""


helps['graph shared-query create'] = """
    type: command
    short-summary: Create a shared query.
    examples:
        - name: Create a shared query requesting a subset of resource fields.
          text: >
            az graph shared-query create -g MyResourceGroup -n MySharedQuery -q "project id, name, type, location, tags" -d "requesting a subset of resource fields." --tags key=value
"""


helps['graph shared-query delete'] = """
    type: command
    short-summary: Delete a shared query.
"""


helps['graph shared-query show'] = """
    type: command
    short-summary: Show the properties of a shared query.
"""


helps['graph shared-query list'] = """
    type: command
    short-summary: List all shared query in a resource group.
    examples:
        - name: List all shared query in a resource group.
          text: >
            az graph shared-query list -g MyResourceGroup
"""
