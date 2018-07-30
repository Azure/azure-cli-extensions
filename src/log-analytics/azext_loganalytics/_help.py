# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.help_files import helps

# pylint: disable=line-too-long

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
        - name:
"""
