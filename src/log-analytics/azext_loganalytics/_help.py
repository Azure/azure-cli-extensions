# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.help_files import helps

# pylint: disable=line-too-long

helps['monitor log-analytics'] = """
    type: group
git    short-summary: Commands for querying data in Log Analytics workspaces.
"""

helps['monitor log-analytics query'] = """
    type: command
    short-summary: Query a Log Analytics workspace.
    parameters:
        - workspace: --workspace -w
          type: string
          short-summary: GUID of the Log Analytics workspace.
        - analytics-query: --analytics-query
          type: string
          short-summary: Query to execute over the Log Analytics data.
        - timespan: --timespan -t
          type: string
          short-summary: Timespan over which to query data. Defaults to all data.
        - workspaces: --workspaces
          type: array
          short-summary: Additional workspaces to union data for querying. Specify additional workspace IDs separated by commas.
    examples:
        - name: Execute a simple query over past 3.5 days.
          text: |
            az monitor log-analytics query -w b8317023-66e4-4edc-8a5b-7c002b22f92f --analytics-query "AzureActivity | summarize count() by bin(timestamp, 1h)" -t P3DT12H
"""
