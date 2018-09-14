# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.help_files import helps

# pylint: disable=line-too-long

helps['graph'] = """
    type: group
    short-summary: Query the resources managed by Azure Resource Manager.
"""

helps['graph query'] = """
    type: command
    short-summary: Query the resources managed by Azure Resource Manager.
    long-summary: >
        Learn more about the query syntax here: https://aka.ms/AzureResourceGraph-QueryLanguage
    parameters:
        - name: --graph-query --q -q
          type: string
          short-summary: "Resource Graph query to execute."
        - name: --first
          type: int
          short-summary: "The maximum number of objects to return. Accepted range: 1-5000."
        - name: --skip
          type: int
          short-summary: Ignores the first N objects and then gets the remaining objects.
        - name: --subscriptions -s
          type: string
          short-summary: List of subscriptions to run query against. By default all accessible subscriptions are queried.
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
            az graph query -q "where type =~ "Microsoft.Compute" | project name, tags" --subscriptions 11111111-1111-1111-1111-111111111111, 22222222-2222-2222-2222-222222222222
"""
