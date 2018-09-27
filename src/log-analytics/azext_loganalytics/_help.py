# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.help_files import helps

# pylint: disable=line-too-long

helps['monitor log-analytics'] = """
    type: group
    short-summary: Commands for querying data in Log Analytics workspaces.
"""

helps['monitor log-analytics query'] = """
    type: command
    short-summary: Query a Log Analytics workspace.
    examples:
      - name: Execute a simple query over past 3.5 days.
        text: |
          az monitor log-analytics query -w b8317023-66e4-4edc-8a5b-7c002b22f92f --analytics-query "AzureActivity | summarize count() by bin(timestamp, 1h)" -t P3DT12H
"""
